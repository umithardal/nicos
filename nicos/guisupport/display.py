#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Module authors:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""
NICOS value display widget.
"""

from __future__ import absolute_import, division, print_function

from os.path import getmtime, isfile
from time import time as currenttime

from nicos.core.status import BUSY, DISABLED, ERROR, NOTREACHED, OK, UNKNOWN, \
    WARN, statuses
from nicos.guisupport.qt import QColor, QFontMetrics, QFrame, QHBoxLayout, \
    QLabel, QPixmap, QSize, Qt, QTimer, QVBoxLayout, QWidget, pyqtSignal, \
    sip
from nicos.guisupport.squeezedlbl import SqueezedLabel
from nicos.guisupport.utils import setBackgroundColor, setBothColors, \
    setForegroundColor
from nicos.guisupport.widget import NicosWidget, PropDef
from nicos.pycompat import escape_html, from_maybe_utf8, text_type
from nicos.utils import findResource

defaultColorScheme = {
    'fore': {
        OK:         QColor('#00ff00'),
        WARN:       QColor('#ffa500'),
        BUSY:       QColor('yellow'),
        NOTREACHED: QColor('red'),
        DISABLED:   QColor('#cccccc'),
        ERROR:      QColor('red'),
        UNKNOWN:    QColor('white'),
    },
    'back': {
        OK:         QColor('black'),
        WARN:       QColor('black'),
        BUSY:       QColor('black'),
        NOTREACHED: QColor('black'),
        DISABLED:   QColor('black'),
        ERROR:      QColor('black'),
        UNKNOWN:    QColor('black'),
    },
    'label': {
        OK:         None,
        WARN:       QColor('#ffa500'),
        BUSY:       None,
        NOTREACHED: QColor('red'),
        DISABLED:   QColor('gray'),
        ERROR:      QColor('red'),
        UNKNOWN:    None,
    },
    'expired':      QColor('gray'),
}

lightColorScheme = {
    'fore': {
        OK:         QColor('#00cc00'),
        WARN:       QColor('black'),
        BUSY:       QColor('black'),
        NOTREACHED: QColor('black'),
        DISABLED:   QColor('black'),
        ERROR:      QColor('black'),
        UNKNOWN:    QColor('black'),
    },
    'back': {
        OK:         QColor('white'),
        WARN:       QColor('#ffa500'),
        BUSY:       QColor('yellow'),
        NOTREACHED: QColor('#ff4444'),
        DISABLED:   QColor('#cccccc'),
        ERROR:      QColor('#ff4444'),
        UNKNOWN:    QColor('white'),
    },
    'label': {
        OK:         None,
        WARN:       QColor('red'),
        BUSY:       None,
        NOTREACHED: QColor('red'),
        DISABLED:   QColor('gray'),
        ERROR:      QColor('red'),
        UNKNOWN:    None,
    },
    'expired':      QColor('#cccccc'),
}

NOT_AVAILABLE = 'n/a'


class SensitiveSMLabel(QLabel):
    """A label that calls back when entered/left by the mouse."""
    def __init__(self, text, parent, enter, leave):
        QLabel.__init__(self, text, parent)
        self._enter = enter
        self._leave = leave

    def enterEvent(self, event):
        self._enter(self, event)

    def leaveEvent(self, event):
        self._leave(self, event)


def nicedelta(t):
    if t < 60:
        return '%d seconds' % int(t)
    elif t < 3600:
        return '%.1f minutes' % (t / 60.)
    else:
        return '%.1f hours' % (t / 3600.)


class ValueLabel(SqueezedLabel):
    """Label that just displays a single value."""

    designer_description = 'A label that just displays a single value'
    # designer_icon = ':/'     # XXX add appropriate icons

    dev = PropDef('dev', str, '', 'NICOS device name, if set, display '
                  'value of this device')
    key = PropDef('key', str, '', 'Cache key to display')
    format = PropDef('format', str, '', 'Python format string to use for the '
                     'value; if "dev" is given this defaults to the '
                     '"fmtstr" set in NICOS')

    def __init__(self, parent, designMode=False, **kwds):
        self._designMode = designMode
        SqueezedLabel.__init__(self, parent, designMode, **kwds)
        if designMode:
            self.setText('(value display)')
        self._callback = lambda value, strvalue: from_maybe_utf8(strvalue)

    def setFormatCallback(self, callback):
        self._callback = callback

    def propertyUpdated(self, pname, value):
        if pname == 'dev':
            if value:
                self.key = value + '.value'
        elif pname == 'key' and self._designMode:
            self.setText('(%s)' % value)
        NicosWidget.propertyUpdated(self, pname, value)

    def registerKeys(self):
        if self.props['dev']:
            self.registerDevice(self.props['dev'], fmtstr=self.props['format'])
        else:
            self.registerKey(self.props['key'], fmtstr=self.props['format'])

    def on_devValueChange(self, dev, value, strvalue, unitvalue, expired):
        if expired:
            setForegroundColor(self, QColor('grey'))
        else:
            setForegroundColor(self, QColor('black'))
            self.setText(self._callback(value, strvalue))


class ValueDisplay(NicosWidget, QWidget):
    """Value display widget with two labels."""

    designer_description = 'A widget with name/value labels'
    designer_icon = ':/table'

    widgetInfo = pyqtSignal(str)

    dev = PropDef('dev', str, '', 'NICOS device name, if set, display '
                  'value of this device')
    key = PropDef('key', str, '', 'Cache key to display (without "nicos/"'
                  ' prefix), set either "dev" or this')
    statuskey = PropDef('statuskey', str, '', 'Cache key to extract status '
                        'information  for coloring value, if "dev" is '
                        'given this is set automatically')
    name = PropDef('name', str, '', 'Name of the value to display above/'
                   'left of the value; if "dev" is given this '
                   'defaults to the device name')
    unit = PropDef('unit', str, '', 'Unit of the value to display next to '
                   'the name; if "dev" is given this defaults to '
                   'the unit set in NICOS')
    format = PropDef('format', str, '', 'Python format string to use for the '
                     'value; if "dev" is given this defaults to the '
                     '"fmtstr" set in NICOS')
    maxlen = PropDef('maxlen', int, -1, 'Maximum length of the value string to '
                     'allow; defaults to no limit')
    width = PropDef('width', int, 8, 'Width of the widget in units of the '
                    'width of one character')
    istext = PropDef('istext', bool, False, 'If given, a "text" font will be '
                     'used for the value instead of the monospaced '
                     'font used for numeric values')
    showName = PropDef('showName', bool, True, 'If false, do not display the '
                       'label for the value name')
    showStatus = PropDef('showStatus', bool, True, 'If false, do not display '
                         'the device status as a color of the value text')
    showExpiration = PropDef('showExpiration', bool, True, 'If true, display '
                             'expired cache values as "n/a"')
    horizontal = PropDef('horizontal', bool, False, 'If true, display name '
                         'label left of the value instead of above it')

    def __init__(self, parent, designMode=False, colorScheme=None, **kwds):
        # keys being watched
        self._mainkeyid = None
        self._statuskeyid = None

        # other current values
        self._isfixed = ''
        # XXX could be taken from devinfo
        self._lastvalue = designMode and '1.4' or None
        self._laststatus = (OK, '')
        self._lastchange = 0
        self._mouseover = False
        self._mousetimer = None
        self._expired = True

        self._colorscheme = colorScheme or defaultColorScheme

        QWidget.__init__(self, parent, **kwds)
        NicosWidget.__init__(self)
        self._statuscolors = self._colorscheme['fore'][UNKNOWN], \
            self._colorscheme['back'][UNKNOWN]
        self._labelcolor = None

    def propertyUpdated(self, pname, value):
        if pname == 'dev':
            if value:
                self.key = value + '.value'
                self.statuskey = value + '.status'
        elif pname == 'width':
            if value < 0:
                self.reinitLayout()
            else:
                onechar = QFontMetrics(self.valueFont).width('0')
                self.valuelabel.setMinimumSize(QSize(onechar * (value + .5), 0))
        elif pname == 'istext':
            self.valuelabel.setFont(value and self.font() or self.valueFont)
            self.width = self.width
        elif pname == 'valueFont':
            self.valuelabel.setFont(self.valueFont)
            self.width = self.width  # update char width calculation
        elif pname == 'showName':
            self.namelabel.setVisible(value)
        elif pname == 'showStatus':
            if not value:
                setBothColors(self.valuelabel,
                              (self._colorscheme['fore'][UNKNOWN],
                               self._colorscheme['back'][UNKNOWN]))
        elif pname == 'horizontal':
            self.reinitLayout()
        if pname in ('dev', 'name', 'unit'):
            self.update_namelabel()
        NicosWidget.propertyUpdated(self, pname, value)

    def initUi(self):
        self.namelabel = QLabel(' ', self, textFormat=Qt.RichText)
        self.update_namelabel()

        valuelabel = SensitiveSMLabel('----', self, self._label_entered,
                                      self._label_left)
        valuelabel.setFrameShape(QFrame.Panel)
        valuelabel.setAlignment(Qt.AlignHCenter)
        valuelabel.setFrameShadow(QFrame.Sunken)
        valuelabel.setAutoFillBackground(True)
        setBothColors(valuelabel, (self._colorscheme['fore'][UNKNOWN],
                                   self._colorscheme['back'][UNKNOWN]))
        valuelabel.setLineWidth(2)
        self.valuelabel = valuelabel
        self.width = 8

        self.reinitLayout()

    def reinitLayout(self):
        # reinitialize UI after switching horizontal/vertical layout
        if self.props['horizontal']:
            new_layout = QHBoxLayout()
            new_layout.addWidget(self.namelabel)
            new_layout.addStretch()
            new_layout.addWidget(self.valuelabel)
            self.namelabel.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        else:
            new_layout = QVBoxLayout()
            new_layout.addWidget(self.namelabel)
            tmplayout = QHBoxLayout()
            if self.width >= 0:
                tmplayout.addStretch()
            tmplayout.addWidget(self.valuelabel)
            if self.width >= 0:
                tmplayout.addStretch()
            new_layout.addLayout(tmplayout)
            self.namelabel.setAlignment(Qt.AlignHCenter)
        if self.layout():
            sip.delete(self.layout())
        new_layout.setContentsMargins(1, 1, 1, 1)  # save space
        self.setLayout(new_layout)

    def registerKeys(self):
        if self.props['dev']:
            self.registerDevice(self.props['dev'],
                                self.props['unit'], self.props['format'])
        else:
            self.registerKey(self.props['key'], self.props['statuskey'],
                             self.props['unit'], self.props['format'])

    def on_devValueChange(self, dev, value, strvalue, unitvalue, expired):
        # check expired values
        self._expired = expired
        self._lastvalue = value
        self._lastchange = currenttime()
        if self.props['maxlen'] > -1:
            self.valuelabel.setText(from_maybe_utf8(
                strvalue[:self.props['maxlen']]))
        else:
            self.valuelabel.setText(from_maybe_utf8(strvalue))
        if self._expired:
            setBothColors(self.valuelabel, (self._colorscheme['fore'][UNKNOWN],
                                            self._colorscheme['expired']))
            if self.props['showExpiration']:
                self.valuelabel.setText(NOT_AVAILABLE)
        elif not self.props['istext']:
            setBothColors(self.valuelabel, (self._colorscheme['fore'][BUSY],
                                            self._colorscheme['back'][BUSY]))
            QTimer.singleShot(1000, self._applystatuscolor)
        else:
            self._applystatuscolor()

    def _applystatuscolor(self):
        if self._expired:
            setBothColors(self.valuelabel, (self._colorscheme['fore'][UNKNOWN],
                                            self._colorscheme['expired']))
        else:
            setBothColors(self.valuelabel, self._statuscolors)
            if self._labelcolor:
                self.namelabel.setAutoFillBackground(True)
                setBackgroundColor(self.namelabel, self._labelcolor)
            else:
                self.namelabel.setAutoFillBackground(False)

    def on_devStatusChange(self, dev, code, status, expired):
        if self.props['showStatus']:
            self._statuscolors = self._colorscheme['fore'][code], \
                self._colorscheme['back'][code]
            self._labelcolor = self._colorscheme['label'][code]
            self._laststatus = code, status
            self._applystatuscolor()

    def on_devMetaChange(self, dev, fmtstr, unit, fixed):
        self._isfixed = fixed and ' (F)'
        self.format = fmtstr
        self.unit = unit or ''

    def update_namelabel(self):
        name = self.props['name'] or self.props['dev'] or self.props['key']
        self.namelabel.setText(
            escape_html(text_type(name)) +
            ' <font color="#888888">%s</font><font color="#0000ff">%s</font> '
            % (escape_html(self.props['unit'].strip()), self._isfixed))

    def _label_entered(self, widget, event, from_mouse=True):
        infotext = '%s = %s' % (self.props['name'] or self.props['dev']
                                or self.props['key'], self.valuelabel.text())
        if self.props['unit'].strip():
            infotext += ' %s' % self.props['unit']
        if self.props['statuskey']:
            try:
                const, msg = self._laststatus
            except ValueError:
                const, msg = self._laststatus, ''
            infotext += ', status is %s: %s' % (statuses.get(const, '?'), msg)
        infotext += ', changed %s ago' % (
            nicedelta(currenttime() - self._lastchange))
        self.widgetInfo.emit(infotext)
        if from_mouse:
            self._mousetimer = QTimer(self, timeout=lambda:
                                      self._label_entered(widget, event, False)
                                      )
            self._mousetimer.start(1000)

    def _label_left(self, widget, event):
        if self._mousetimer:
            self._mousetimer.stop()
            self._mousetimer = None
            self.widgetInfo.emit('')


class PictureDisplay(NicosWidget, QWidget):
    """A display widget to show a picture."""

    designer_description = 'Widget to display a picture file'

    filepath = PropDef('filepath', str, '', 'Path to the picture that should '
                       'be displayed')
    name = PropDef('name', str, '', 'Name (caption) to be displayed above '
                   'the picture')
    refresh = PropDef('refresh', int, 0, 'Interval to check for updates '
                      'in seconds')
    height = PropDef('height', int, 0)
    width = PropDef('width', int, 0)

    def __init__(self, parent=None, designMode=False, **kwds):
        QWidget.__init__(self, parent, **kwds)
        NicosWidget.__init__(self)
        self._last_mtime = None
        self.namelabel = QLabel(self)
        self.namelabel.setAlignment(Qt.AlignHCenter)
        self.piclabel = QLabel(self)
        self.piclabel.setScaledContents(True)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.piclabel, 1)
        self.setLayout(layout)

    def registerKeys(self):
        pass

    def setPicture(self):
        size = QSize(self.props['width'] * self._scale,
                     self.props['height'] * self._scale)
        if isfile(self._filePath):
            pixmap = QPixmap(self._filePath)
        else:
            pixmap = QPixmap(size)
            pixmap.fill()
        if size.isEmpty():
            self.piclabel.setPixmap(pixmap)
        else:
            self.piclabel.setPixmap(pixmap.scaled(size))
            self.piclabel.resize(self.piclabel.sizeHint())

    def updatePicture(self):
        if not isfile(self._filePath):
            return

        # on first iteration self._last_mtime is None -> always setPicture()
        mtime = getmtime(self._filePath)
        if self._last_mtime != mtime:
            self._last_mtime = mtime
            self.setPicture()

    def propertyUpdated(self, pname, value):
        NicosWidget.propertyUpdated(self, pname, value)
        if pname == 'filepath':
            self._filePath = findResource(value)
            self.setPicture()
        elif pname == 'name':
            layout = QVBoxLayout()
            if value:
                layout.addWidget(self.namelabel)
                layout.addSpacing(5)
            layout.addWidget(self.piclabel, 1)
            sip.delete(self.layout())
            self.setLayout(layout)
            self.namelabel.setText(value)
        elif pname in ('width', 'height'):
            self.setPicture()
        elif pname == 'refresh':
            if value:
                self._refreshTimer = QTimer()
                self._refreshTimer.setInterval(value * 1000)
                self._refreshTimer.timeout.connect(self.updatePicture)
                self._refreshTimer.start()
