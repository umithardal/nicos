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
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

"""NICOS GUI history log window."""

from __future__ import absolute_import, division, print_function

import functools
import json
import operator
import os
import sys
from collections import OrderedDict
from time import localtime, mktime, time as currenttime

from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import CompatSettings, DlgUtils, dialogFromUi, \
    enumerateWithProgress, loadUi
from nicos.clients.gui.widgets.plotting import ArbitraryFitter, CosineFitter, \
    ExponentialFitter, GaussFitter, LinearFitter, LorentzFitter, \
    PearsonVIIFitter, PseudoVoigtFitter, SigmoidFitter, TcFitter, ViewPlot
from nicos.core import Param, listof
from nicos.devices.cacheclient import CacheClient
from nicos.guisupport.qt import QAction, QActionGroup, QApplication, QBrush, \
    QByteArray, QCheckBox, QColor, QComboBox, QCompleter, QDateTime, QDialog, \
    QFont, QFrame, QHBoxLayout, QListWidgetItem, QMainWindow, QMenu, \
    QMessageBox, QObject, QSizePolicy, QStatusBar, QStyledItemDelegate, Qt, \
    QTimer, QToolBar, QWidgetAction, pyqtSignal, pyqtSlot
from nicos.guisupport.timeseries import TimeSeries
from nicos.guisupport.trees import BaseDeviceParamTree
from nicos.guisupport.utils import scaledFont
from nicos.protocols.cache import cache_load
from nicos.pycompat import cPickle as pickle, integer_types, iteritems, \
    number_types
from nicos.utils import extractKeyAndIndex, parseDuration, safeName


class NoEditDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        return None


def float_with_default(s, d):
    try:
        return float(s)
    except ValueError:
        return d


def get_time_and_interval(intv):
    itime = parseDuration(intv)
    if itime >= 24 * 3600:
        interval = 30
    elif itime >= 6 * 3600:
        interval = 10
    elif itime >= 3 * 3600:
        interval = 5
    elif itime >= 1800:
        interval = 2
    else:
        interval = 1
    return itime, interval


class View(QObject):
    timeSeriesUpdate = pyqtSignal(object)

    def __init__(self, widget, name, keys_indices, interval, fromtime, totime,
                 yfrom, yto, window, meta, dlginfo, query_func):
        QObject.__init__(self)
        self.name = name
        self.dlginfo = dlginfo

        self.fromtime = fromtime
        self.totime = totime
        self.yfrom = yfrom
        self.yto = yto
        self.window = window

        self._key_indices = {}
        self.uniq_keys = set()
        self.series = OrderedDict()
        self.timer = None

        # + 60 seconds: get all values, also those added while querying
        hist_totime = self.totime or currenttime() + 60
        hist_cache = {}

        iterator = enumerate(keys_indices)
        if fromtime is not None:
            iterator = enumerateWithProgress(keys_indices,
                                             'Querying history...',
                                             force_display=True)

        for _, (key, index, scale, offset) in iterator:
            real_indices = [index]
            history = None
            self.uniq_keys.add(key)

            if fromtime is not None:
                if key not in hist_cache:
                    history = query_func(key, self.fromtime, hist_totime)
                    if not history:
                        from nicos.clients.gui.main import log
                        if log is None:
                            from __main__ import log  # pylint: disable=no-name-in-module
                        log.error('Error getting history for %s.', key)
                        QMessageBox.warning(widget, 'Error',
                                            'Could not get history for %s, '
                                            'there are no values to show.\n'
                                            'Is it spelled correctly?' % key)
                        history = []
                    hist_cache[key] = history
                else:
                    history = hist_cache[key]
                # if the value is a list/tuple and we don't have an index
                # specified, add a plot for each item
                if history:
                    first_value = history[0][1]
                    if not index and isinstance(first_value, (list, tuple)):
                        real_indices = tuple((i,) for i in
                                             range(len(first_value)))
            for index in real_indices:
                name = '%s[%s]' % (key, ','.join(map(str, index))) if index else key
                series = TimeSeries(name, interval, scale, offset, window,
                                    self, meta[0].get(key), meta[1].get(key))
                self.series[key, index] = series
                if history:
                    series.init_from_history(history, fromtime,
                                             totime or currenttime(), index)
                else:
                    series.init_empty()
            self._key_indices.setdefault(key, []).extend(real_indices)

        self.listitem = None
        self.plot = None
        if self.totime is None:
            # add another point with the same value every interval time (but
            # not more often than 11 seconds)
            self.timer = QTimer(self, interval=max(interval, 11) * 1000)
            self.timer.timeout.connect(self.on_timer_timeout)
            self.timer.start()

        self.timeSeriesUpdate.connect(self.on_timeSeriesUpdate)

    def cleanup(self):
        self.plot.cleanup()
        self.plot.deleteLater()
        if self.timer:
            self.timer.stop()
        for series in self.series.values():
            series.signal_obj = None

    def on_timer_timeout(self):
        for series in self.series.values():
            series.synthesize_value()

    def on_timeSeriesUpdate(self, series):
        if self.plot:
            self.plot.pointsAdded(series)

    def newValue(self, vtime, key, op, value):
        if op != '=':
            return
        for index in self._key_indices[key]:
            series = self.series[key, index]
            if index:
                try:
                    v = functools.reduce(operator.getitem, index, value)
                    series.add_value(vtime, v)
                except (TypeError, IndexError):
                    continue
            else:
                series.add_value(vtime, value)


class NewViewDialog(DlgUtils, QDialog):

    def __init__(self, parent, info=None, client=None):
        QDialog.__init__(self, parent)
        DlgUtils.__init__(self, 'History viewer')
        loadUi(self, 'panels/history_new.ui')
        self.client = client

        self.fromdate.setDateTime(QDateTime.currentDateTime())
        self.todate.setDateTime(QDateTime.currentDateTime())

        self.customY.toggled.connect(self.toggleCustomY)
        self.toggleCustomY(False)

        self.simpleTime.toggled.connect(self.toggleSimpleExt)
        self.extTime.toggled.connect(self.toggleSimpleExt)
        self.frombox.toggled.connect(self.toggleSimpleExt)
        self.tobox.toggled.connect(self.toggleSimpleExt)
        self.toggleSimpleExt(True)

        self.simpleTimeSpec.textChanged.connect(self.setIntervalFromSimple)

        self.helpButton.clicked.connect(self.showDeviceHelp)
        self.simpleHelpButton.clicked.connect(self.showSimpleHelp)

        self.devicesFrame.hide()
        self.deviceTree = None
        self.deviceTreeSel = OrderedDict()
        if not client:
            self.devicesExpandBtn.hide()
        else:
            devices = client.getDeviceList()
            devcompleter = QCompleter(devices, self)
            devcompleter.setCompletionMode(QCompleter.InlineCompletion)
            self.devices.setCompleter(devcompleter)

        if info is not None:
            self.devices.setText(info['devices'])
            self.namebox.setText(info['name'])
            self.simpleTime.setChecked(info['simpleTime'])
            self.simpleTimeSpec.setText(info['simpleTimeSpec'])
            self.slidingWindow.setChecked(info['slidingWindow'])
            self.extTime.setChecked(not info['simpleTime'])
            self.frombox.setChecked(info['frombox'])
            self.tobox.setChecked(info['tobox'])
            self.fromdate.setDateTime(QDateTime.fromTime_t(info['fromdate']))
            self.todate.setDateTime(QDateTime.fromTime_t(info['todate']))
            self.interval.setText(info['interval'])
            self.customY.setChecked(info['customY'])
            self.customYFrom.setText(info['customYFrom'])
            self.customYTo.setText(info['customYTo'])

    def on_devicesAllBox_toggled(self, on):
        self.deviceTree.only_explicit = not on
        self.deviceTree._reinit()
        self._syncDeviceTree()

    @pyqtSlot()
    def on_devicesExpandBtn_clicked(self):
        self.devicesExpandBtn.hide()
        self._createDeviceTree()

    blacklist = {'maxage', 'pollinterval', 'lowlevel', 'classes', 'value'}

    def _createDeviceTree(self):
        def param_predicate(name, value, info):
            return name not in self.blacklist and \
                (not info or info.get('userparam', True)) and \
                isinstance(value, (number_types, list, tuple))

        def item_callback(item, parent=None):
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            if parent and item.text(0) == 'status':
                item.setText(1, '0')
            item.setCheckState(0, Qt.Unchecked)
            return True

        self.deviceTree = tree = BaseDeviceParamTree(self)
        tree.device_clause = '"." not in dn'
        tree.param_predicate = param_predicate
        tree.item_callback = item_callback
        tree.setColumnCount(3)
        tree.setHeaderLabels(['Device/Param', 'Index', 'Scale', 'Offset'])
        tree.setClient(self.client)

        tree.setColumnWidth(1, tree.columnWidth(1) // 2)
        tree.setColumnWidth(2, tree.columnWidth(2) // 2)
        tree.setColumnWidth(3, tree.columnWidth(3) // 2)
        tree.resizeColumnToContents(0)
        tree.setColumnWidth(0, tree.columnWidth(0) * 1.5)
        # disallow editing for name column
        tree.setItemDelegateForColumn(0, NoEditDelegate())
        tree.itemChanged.connect(self.on_deviceTree_itemChanged)
        self._syncDeviceTree()

        self.devicesFrame.layout().addWidget(tree)
        self.devicesFrame.show()
        self.resize(self.sizeHint())

    def _syncDeviceTree(self):
        # restore selection from entries in textbox
        if not self.devices.text():
            return

        tree = self.deviceTree
        tree.itemChanged.disconnect(self.on_deviceTree_itemChanged)
        keys_indices = [extractKeyAndIndex(d.strip())
                        for d in self.devices.text().split(',')]
        for key, indices, scale, offset in keys_indices:
            dev, _, param = key.partition('/')
            for i in range(tree.topLevelItemCount()):
                if tree.topLevelItem(i).text(0).lower() == dev:
                    devitem = tree.topLevelItem(i)
                    break
            else:
                continue
            if param == 'value':
                item = devitem
                newkey = devitem.text(0)
            else:
                if not devitem.childCount():
                    tree.on_itemExpanded(devitem)
                for i in range(devitem.childCount()):
                    if devitem.child(i).text(0).lower() == param:
                        item = devitem.child(i)
                        item.parent().setExpanded(True)
                        break
                else:
                    continue
                newkey = devitem.text(0) + '.' + item.text(0)
            suffix = ''.join('[%s]' % i for i in indices)
            if scale != 1:
                suffix += '*%.4g' % scale
            if offset != 0:
                suffix += '%+.4g' % offset
            item.setCheckState(0, Qt.Checked)
            item.setText(1, ','.join(map(str, indices)))
            item.setText(2, '%.4g' % scale)
            item.setText(3, '%.4g' % offset)
            self.deviceTreeSel[newkey] = suffix
        tree.itemChanged.connect(self.on_deviceTree_itemChanged)

    def on_deviceTree_itemChanged(self, item, col):
        key = item.text(0)
        if item.parent():  # a device parameter
            key = item.parent().text(0) + '.' + key
        if item.checkState(0) == Qt.Checked:
            index = item.text(1)
            if not item.text(2):
                item.setText(2, '1')
            if not item.text(3):
                item.setText(3, '0')
            suffix = ''.join('[%s]' % i for i in index.split(',')) \
                if index else ''
            scale = float_with_default(item.text(2), 1)
            offset = float_with_default(item.text(3), 0)
            if scale != 1:
                suffix += '*' + item.text(2)
            if offset != 0:
                suffix += ('+' if offset > 0 else '-') + \
                    item.text(3).strip('+-')
            self.deviceTreeSel[key] = suffix
        else:
            self.deviceTreeSel.pop(key, None)
        self.devices.setText(', '.join((k + v) for (k, v)
                                       in iteritems(self.deviceTreeSel)))

    def showSimpleHelp(self):
        self.showInfo('Please enter a time interval with units like this:\n\n'
                      '30m   (30 minutes)\n'
                      '12h   (12 hours)\n'
                      '1d 6h (30 hours)\n'
                      '3d    (3 days)\n')

    def showDeviceHelp(self):
        self.showInfo(
            'Enter a comma-separated list of device names or '
            'parameters (as "device.parameter").  Example:\n\n'
            'T, T.setpoint\n\nshows the value of device T, and the '
            'value of the T.setpoint parameter.\n\n'
            'More options:\n'
            '- use [i] to select subitems by index, e.g. motor.status[0]\n'
            '- use *x to scale the values by a constant, e.g. '
            'T*100, T.heaterpower\n'
            '- use +x or -x to add an offset to the values, e.g. '
            'T+5 or combined T*100+5\n')

    def toggleCustomY(self, on):
        self.customYFrom.setEnabled(on)
        self.customYTo.setEnabled(on)
        if on:
            self.customYFrom.setFocus()

    def toggleSimpleExt(self, on):
        on = self.simpleTime.isChecked()
        self.simpleTimeSpec.setEnabled(on)
        self.slidingWindow.setEnabled(on)
        self.frombox.setEnabled(not on)
        self.fromdate.setEnabled(not on and self.frombox.isChecked())
        self.tobox.setEnabled(not on)
        self.todate.setEnabled(not on and self.tobox.isChecked())

    def setIntervalFromSimple(self, text):
        try:
            _itime, interval = get_time_and_interval(text)
        except Exception:
            pass
        else:
            self.interval.setText(str(interval))

    def accept(self):
        if self.simpleTime.isChecked():
            try:
                get_time_and_interval(self.simpleTimeSpec.text())
            except ValueError:
                self.showSimpleHelp()
                return
        if self.customY.isChecked():
            try:
                float(self.customYFrom.text())
            except ValueError:
                self.showError('You have to input valid y axis limits.')
                return
            try:
                float(self.customYTo.text())
            except ValueError:
                self.showError('You have to input valid y axis limits.')
                return
        return QDialog.accept(self)

    def infoDict(self):
        return dict(
            devices = self.devices.text(),
            name = self.namebox.text(),
            simpleTime = self.simpleTime.isChecked(),
            simpleTimeSpec = self.simpleTimeSpec.text(),
            slidingWindow = self.slidingWindow.isChecked(),
            frombox = self.frombox.isChecked(),
            tobox = self.tobox.isChecked(),
            fromdate = self.fromdate.dateTime().toTime_t(),
            todate = self.todate.dateTime().toTime_t(),
            interval = self.interval.text(),
            customY = self.customY.isChecked(),
            customYFrom = self.customYFrom.text(),
            customYTo = self.customYTo.text(),
        )


class BaseHistoryWindow(object):

    client = None
    presetdict = None

    def __init__(self):
        loadUi(self, 'panels/history.ui')

        self.user_color = Qt.white
        self.user_font = QFont('Monospace')

        self.views = []
        # stack of views to display
        self.viewStack = []
        # maps watched keys to their views
        self.keyviews = {}
        # current plot object
        self.currentPlot = None
        self.fitclass = LinearFitter
        self.fitfuncmap = {}

        self.enablePlotActions(False)

        self.presetmenu = QMenu('&Presets', self)

        for (name, view) in self.last_views:
            item = QListWidgetItem(name, self.viewList)
            item.setForeground(QBrush(QColor('#aaaaaa')))
            item.setData(Qt.UserRole, view)

        self.menus = None
        self.bar = None

        # NOTE: for this class, automatic connections don't work on PyQt4 >=
        # 4.12 since this class is not derived from QObject. But on older PyQt4
        # and PyQt5, they do work, so we change use the usual naming scheme
        # slightly to avoid double connections.
        self.viewList.currentItemChanged.connect(self.on__viewList_currentItemChanged)
        self.viewList.itemClicked.connect(self.on__viewList_itemClicked)
        self.viewList.itemDoubleClicked.connect(self.on__viewList_itemDoubleClicked)
        self.actionNew.triggered.connect(self.on__actionNew_triggered)
        self.actionEditView.triggered.connect(self.on__actionEditView_triggered)
        self.actionCloseView.triggered.connect(self.on__actionCloseView_triggered)
        self.actionResetView.triggered.connect(self.on__actionResetView_triggered)
        self.actionDeleteView.triggered.connect(self.on__actionDeleteView_triggered)
        self.actionSavePlot.triggered.connect(self.on__actionSavePlot_triggered)
        self.actionPrint.triggered.connect(self.on__actionPrint_triggered)
        self.actionUnzoom.triggered.connect(self.on__actionUnzoom_triggered)
        self.actionLogScale.toggled.connect(self.on__actionLogScale_toggled)
        self.actionAutoScale.toggled.connect(self.on__actionAutoScale_toggled)
        self.actionScaleX.toggled.connect(self.on__actionScaleX_toggled)
        self.actionScaleY.toggled.connect(self.on__actionScaleY_toggled)
        self.actionLegend.toggled.connect(self.on__actionLegend_toggled)
        self.actionSymbols.toggled.connect(self.on__actionSymbols_toggled)
        self.actionLines.toggled.connect(self.on__actionLines_toggled)
        self.actionSaveData.triggered.connect(self.on__actionSaveData_triggered)
        self.actionFitPeak.triggered.connect(self.on__actionFitPeak_triggered)
        self.actionFitArby.triggered.connect(self.on__actionFitArby_triggered)
        self.actionFitPeakGaussian.triggered.connect(self.on__actionFitPeakGaussian_triggered)
        self.actionFitPeakLorentzian.triggered.connect(self.on__actionFitPeakLorentzian_triggered)
        self.actionFitPeakPV.triggered.connect(self.on__actionFitPeakPV_triggered)
        self.actionFitPeakPVII.triggered.connect(self.on__actionFitPeakPVII_triggered)
        self.actionFitTc.triggered.connect(self.on__actionFitTc_triggered)
        self.actionFitCosine.triggered.connect(self.on__actionFitCosine_triggered)
        self.actionFitSigmoid.triggered.connect(self.on__actionFitSigmoid_triggered)
        self.actionFitLinear.triggered.connect(self.on__actionFitLinear_triggered)
        self.actionFitExponential.triggered.connect(self.on__actionFitExponential_triggered)

    def getMenus(self):
        menu = QMenu('&History viewer', self)
        menu.addAction(self.actionNew)
        menu.addSeparator()
        menu.addAction(self.actionSavePlot)
        menu.addAction(self.actionPrint)
        menu.addAction(self.actionAttachElog)
        menu.addAction(self.actionSaveData)
        menu.addSeparator()
        menu.addAction(self.actionEditView)
        menu.addAction(self.actionCloseView)
        menu.addAction(self.actionDeleteView)
        menu.addAction(self.actionResetView)
        menu.addSeparator()
        menu.addAction(self.actionLogScale)
        menu.addAction(self.actionAutoScale)
        menu.addAction(self.actionScaleX)
        menu.addAction(self.actionScaleY)
        menu.addAction(self.actionUnzoom)
        menu.addAction(self.actionLegend)
        menu.addAction(self.actionSymbols)
        menu.addAction(self.actionLines)
        ag = QActionGroup(menu)
        ag.addAction(self.actionFitPeakGaussian)
        ag.addAction(self.actionFitPeakLorentzian)
        ag.addAction(self.actionFitPeakPV)
        ag.addAction(self.actionFitPeakPVII)
        ag.addAction(self.actionFitTc)
        ag.addAction(self.actionFitCosine)
        ag.addAction(self.actionFitSigmoid)
        ag.addAction(self.actionFitLinear)
        ag.addAction(self.actionFitExponential)
        menu.addAction(self.actionFitPeak)
        menu.addAction(self.actionPickInitial)
        menu.addAction(self.actionFitPeakGaussian)
        menu.addAction(self.actionFitPeakLorentzian)
        menu.addAction(self.actionFitPeakPV)
        menu.addAction(self.actionFitPeakPVII)
        menu.addAction(self.actionFitTc)
        menu.addAction(self.actionFitCosine)
        menu.addAction(self.actionFitSigmoid)
        menu.addAction(self.actionFitLinear)
        menu.addAction(self.actionFitExponential)
        menu.addSeparator()
        menu.addAction(self.actionFitArby)
        menu.addSeparator()
        menu.addAction(self.actionClose)
        self._refresh_presets()
        return [menu, self.presetmenu]

    def getToolbars(self):
        if not self.bar:
            bar = QToolBar('History viewer')
            bar.addAction(self.actionNew)
            bar.addAction(self.actionEditView)
            bar.addSeparator()
            bar.addAction(self.actionSavePlot)
            bar.addAction(self.actionPrint)
            bar.addAction(self.actionSaveData)
            bar.addSeparator()
            bar.addAction(self.actionUnzoom)
            bar.addAction(self.actionLogScale)
            bar.addSeparator()
            bar.addAction(self.actionAutoScale)
            bar.addAction(self.actionScaleX)
            bar.addAction(self.actionScaleY)
            bar.addSeparator()
            bar.addAction(self.actionResetView)
            bar.addAction(self.actionDeleteView)
            bar.addSeparator()
            bar.addAction(self.actionFitPeak)
            wa = QWidgetAction(bar)
            self.fitPickCheckbox = QCheckBox(bar)
            self.fitPickCheckbox.setText('Pick')
            self.fitPickCheckbox.setChecked(True)
            self.actionPickInitial.setChecked(True)
            self.fitPickCheckbox.toggled.connect(self.actionPickInitial.setChecked)
            self.actionPickInitial.toggled.connect(self.fitPickCheckbox.setChecked)
            layout = QHBoxLayout()
            layout.setContentsMargins(10, 0, 10, 0)
            layout.addWidget(self.fitPickCheckbox)
            frame = QFrame(bar)
            frame.setLayout(layout)
            wa.setDefaultWidget(frame)
            bar.addAction(wa)
            ag = QActionGroup(bar)
            ag.addAction(self.actionFitPeakGaussian)
            ag.addAction(self.actionFitPeakLorentzian)
            ag.addAction(self.actionFitPeakPV)
            ag.addAction(self.actionFitPeakPVII)
            ag.addAction(self.actionFitTc)
            ag.addAction(self.actionFitCosine)
            ag.addAction(self.actionFitSigmoid)
            ag.addAction(self.actionFitLinear)
            ag.addAction(self.actionFitExponential)
            wa = QWidgetAction(bar)
            self.fitComboBox = QComboBox(bar)
            for a in ag.actions():
                itemtext = a.text().replace('&', '')
                self.fitComboBox.addItem(itemtext)
                self.fitfuncmap[itemtext] = a
            self.fitComboBox.currentIndexChanged.connect(
                self.on__fitComboBox_currentIndexChanged)
            wa.setDefaultWidget(self.fitComboBox)
            bar.addAction(wa)
            bar.addSeparator()
            bar.addAction(self.actionFitArby)
            self.bar = bar
            self.actionFitLinear.trigger()

        return [self.bar]

    def loadSettings(self, settings):
        self.splitterstate = settings.value('splitter', '', QByteArray)
        self.presetdict = {}
        # read new format if present
        settings.beginGroup('presets_new')
        for key in settings.childKeys():
            self.presetdict[key] = json.loads(settings.value(key))
        settings.endGroup()
        # convert old format
        try:
            presetval = settings.value('presets')
            if presetval:
                for (name, value) in presetval.items():
                    if not isinstance(value, bytes):
                        value = value.encode('latin1')
                    self.presetdict[name] = pickle.loads(value)
        except Exception:
            pass
        settings.remove('presets')
        self.last_views = []
        settings.beginGroup('views_new')
        for key in settings.childKeys():
            try:
                info = json.loads(settings.value(key))
                self.last_views.append((key, info))
            except Exception:
                pass
        settings.endGroup()

    def saveSettings(self, settings):
        settings.setValue('splitter', self.splitter.saveState())
        settings.beginGroup('presets_new')
        for (key, info) in self.presetdict.items():
            settings.setValue(key, json.dumps(info))
        settings.endGroup()
        settings.beginGroup('views_new')
        for view in self.views:
            settings.setValue(view.name, json.dumps(view.dlginfo))
        settings.endGroup()

    def openViews(self, views):
        """Open some views given by the specs in *views*, a list of strings.

        Each string can be a comma-separated list of key names, and an optional
        simple time spec (like "1h") separated by a colon.

        If a view spec matches the name of a preset, it is used instead.
        """
        for viewspec in views:
            timespec = '1h'
            if ':' in viewspec:
                viewspec, timespec = viewspec.rsplit(':', 1)
            info = dict(
                name = viewspec,
                devices = viewspec,
                simpleTime = True,
                simpleTimeSpec = timespec,
                slidingWindow = True,
                frombox = False,
                tobox = False,
                fromdate = 0,
                todate = 0,
                interval = '',
                customY = False,
                customYFrom = '',
                customYTo = '',
            )
            self._createViewFromDialog(info)

    def _refresh_presets(self):
        pmenu = self.presetmenu
        pmenu.clear()
        delmenu = QMenu('Delete', self)
        try:
            for preset, info in iteritems(self.presetdict):
                paction = QAction(preset, self)
                pdelaction = QAction(preset, self)
                info = info.copy()

                def launchpreset(on, info=info):
                    self._createViewFromDialog(info)

                def delpreset(on, name=preset, act=paction, delact=pdelaction):
                    pmenu.removeAction(act)
                    delmenu.removeAction(delact)
                    self.presetdict.pop(name, None)
                    self._refresh_presets()

                paction.triggered[bool].connect(launchpreset)
                pmenu.addAction(paction)
                pdelaction.triggered[bool].connect(delpreset)
                delmenu.addAction(pdelaction)
        except AttributeError:
            self.presetdict = {}
        if self.presetdict:
            pmenu.addSeparator()
            pmenu.addMenu(delmenu)
        else:
            pmenu.addAction('(no presets created)')

    def _add_preset(self, name, info):
        if name:
            self.presetdict[name] = info.copy()
            self._refresh_presets()

    def _autoscale(self, x=None, y=None):
        xflag = x if x is not None else self.actionScaleX.isChecked()
        yflag = y if y is not None else self.actionScaleY.isChecked()
        if self.currentPlot:
            self.currentPlot.setAutoScaleFlags(xflag, yflag)
            self.actionAutoScale.setChecked(xflag or yflag)
            self.actionScaleX.setChecked(xflag)
            self.actionScaleY.setChecked(yflag)
            self.currentPlot.update()

    def enablePlotActions(self, on):
        for action in [
            self.actionSavePlot, self.actionPrint, self.actionAttachElog,
            self.actionSaveData, self.actionAutoScale, self.actionScaleX,
            self.actionScaleY, self.actionEditView, self.actionCloseView,
            self.actionDeleteView, self.actionResetView, self.actionUnzoom,
            self.actionLogScale, self.actionLegend, self.actionSymbols,
            self.actionLines, self.actionFitPeak, self.actionFitArby,
        ]:
            action.setEnabled(on)

    def enableAutoScaleActions(self, on):
        for action in [self.actionAutoScale, self.actionScaleX,
                       self.actionScaleY]:
            action.setEnabled(on)

    def on__fitComboBox_currentIndexChanged(self, index):
        self.fitfuncmap[self.fitComboBox.currentText()].trigger()

    def on__viewList_currentItemChanged(self, item, previous):
        if item is None:
            return
        for view in self.views:
            if view.listitem == item:
                self.openView(view)

    def on__viewList_itemClicked(self, item):
        # this handler is needed in addition to currentItemChanged
        # since one can't change the current item if it's the only one
        self.on__viewList_currentItemChanged(item, None)
        # is it a "saved from last time" item?
        info = item.data(Qt.UserRole)
        if info is not None:
            row = self.viewList.row(item)

            do_restore = self.askQuestion('Restore this view from last time?')
            self.viewList.takeItem(row)
            if do_restore:
                self._createViewFromDialog(info, row)

    def on_logYinDomain(self, flag):
        if not flag:
            self.actionLogScale.setChecked(flag)

    def newvalue_callback(self, data):
        (vtime, key, op, value) = data
        if key not in self.keyviews:
            return
        if not value:
            return
        value = cache_load(value)
        for view in self.keyviews[key]:
            view.newValue(vtime, key, op, value)

    def _createViewFromDialog(self, info, row=None):
        if not info['devices'].strip():
            return
        keys_indices = [extractKeyAndIndex(d.strip())
                        for d in info['devices'].split(',')]
        if self.client is not None:
            meta = self._getMetainfo(keys_indices)
        else:
            meta = ({}, {})
        name = info['name']
        if not name:
            name = info['devices']
        if info['simpleTime']:
            name += ' (%s)' % info['simpleTimeSpec']
        window = None
        if info['simpleTime']:
            try:
                itime, _ = get_time_and_interval(info['simpleTimeSpec'])
            except ValueError:
                return
            fromtime = currenttime() - itime
            totime = None
            if info['slidingWindow']:
                window = itime
        else:
            if info['frombox']:
                fromtime = mktime(localtime(info['fromdate']))
            else:
                fromtime = None
            if info['tobox']:
                totime = mktime(localtime(info['todate']))
            else:
                totime = None
        try:
            interval = float(info['interval'])
        except ValueError:
            interval = 5.0
        if info['customY']:
            try:
                yfrom = float(info['customYFrom'])
            except ValueError:
                return
            try:
                yto = float(info['customYTo'])
            except ValueError:
                return
        else:
            yfrom = yto = None
        view = View(self, name, keys_indices, interval, fromtime, totime,
                    yfrom, yto, window, meta, info, self.gethistory_callback)
        self.views.append(view)
        view.listitem = QListWidgetItem(view.name)
        if row is not None:
            self.viewList.insertItem(row, view.listitem)
        else:
            self.viewList.addItem(view.listitem)
        self.openView(view)
        if view.totime is None:
            for key in view.uniq_keys:
                self.keyviews.setdefault(key, []).append(view)
        return view

    def _getMetainfo(self, keys_indices):
        """Collect unit and string<->integer mapping for each key that
        refers to a device main value.
        """
        units = {}
        mappings = {}
        seen = set()
        for key, _, _, _ in keys_indices:
            if key in seen or not key.endswith('/value'):
                continue
            seen.add(key)
            devname = key[:-6]
            devunit = self.client.getDeviceParam(devname, 'unit')
            if devunit:
                units[key] = devunit
            devmapping = self.client.getDeviceParam(devname, 'mapping')
            if devmapping:
                mappings[key] = m = {}
                i = 0
                for k, v in sorted(devmapping.items()):
                    if isinstance(v, integer_types):
                        m[k] = v
                    else:
                        m[k] = i
                        i += 1
        return units, mappings

    def on__actionNew_triggered(self):
        self.showNewDialog()

    def showNewDialog(self, devices=''):
        newdlg = NewViewDialog(self, client=self.client)
        newdlg.devices.setText(devices)
        ret = newdlg.exec_()
        if ret != QDialog.Accepted:
            return
        info = newdlg.infoDict()
        self._createViewFromDialog(info)
        if newdlg.savePreset.isChecked():
            self._add_preset(info['name'], info)

    def newView(self, devices):
        newdlg = NewViewDialog(self)
        newdlg.devices.setText(devices)
        info = newdlg.infoDict()
        self._createViewFromDialog(info)

    def openView(self, view):
        if not view.plot:
            view.plot = ViewPlot(self.plotFrame, self, view)
        self.viewList.setCurrentItem(view.listitem)
        self.setCurrentView(view)

    def setCurrentView(self, view):
        newView = False
        if self.currentPlot:
            self.plotLayout.removeWidget(self.currentPlot)
            self.currentPlot.hide()
        if view is None:
            self.currentPlot = None
            self.enablePlotActions(False)
        else:
            self.currentPlot = view.plot
            try:
                self.viewStack.remove(view)
            except ValueError:
                newView = True
            self.viewStack.append(view)

            self.enablePlotActions(True)
            self.enableAutoScaleActions(view.plot.HAS_AUTOSCALE)
            self.viewList.setCurrentItem(view.listitem)
            self.actionLogScale.setChecked(view.plot.isLogScaling())
            self.actionLegend.setChecked(view.plot.isLegendEnabled())
            self.actionSymbols.setChecked(view.plot.hasSymbols)
            self.actionLines.setChecked(view.plot.hasLines)
            self.plotLayout.addWidget(view.plot)
            if view.plot.HAS_AUTOSCALE:
                from gr.pygr import PlotAxes
                if newView:
                    mask = PlotAxes.SCALE_X | PlotAxes.SCALE_Y
                else:
                    mask = view.plot.plot.autoscale
                if view.yfrom and view.yto:
                    mask &= ~PlotAxes.SCALE_Y
                self._autoscale(x=mask & PlotAxes.SCALE_X,
                                y=mask & PlotAxes.SCALE_Y)
                view.plot.logYinDomain.connect(self.on_logYinDomain)
            view.plot.setSlidingWindow(view.window)
            view.plot.show()

    def on__viewList_itemDoubleClicked(self, item):
        if item:
            self.on__actionEditView_triggered()

    def on__actionEditView_triggered(self):
        view = self.viewStack[-1]
        newdlg = NewViewDialog(self, view.dlginfo, client=self.client)
        newdlg.setWindowTitle('Edit history view')
        ret = newdlg.exec_()
        if ret != QDialog.Accepted:
            return
        info = newdlg.infoDict()
        if newdlg.savePreset.isChecked():
            self._add_preset(info['name'], info)
        self.viewStack.pop()
        row = self.clearView(view)
        new_view = self._createViewFromDialog(info, row)
        if new_view.plot.HAS_AUTOSCALE:
            self._autoscale(True, False)

    def on__actionCloseView_triggered(self):
        view = self.viewStack.pop()
        if self.viewStack:
            self.setCurrentView(self.viewStack[-1])
        else:
            self.setCurrentView(None)
        view.plot = None

    def on__actionResetView_triggered(self):
        view = self.viewStack.pop()
        hassym = view.plot.hasSymbols
        view.plot = None
        self.openView(view)
        self.actionSymbols.setChecked(hassym)
        view.plot.setSymbols(hassym)

    def on__actionDeleteView_triggered(self):
        view = self.viewStack.pop()
        self.clearView(view)
        if self.viewStack:
            self.setCurrentView(self.viewStack[-1])
        else:
            self.setCurrentView(None)

    def clearView(self, view):
        self.views.remove(view)
        row = self.viewList.row(view.listitem)
        self.viewList.takeItem(row)
        if view.totime is None:
            for key in view.uniq_keys:
                self.keyviews[key].remove(view)
        view.cleanup()
        return row

    def on__actionSavePlot_triggered(self):
        filename = self.currentPlot.savePlot()
        if filename:
            self.statusBar.showMessage('View successfully saved to %s.' %
                                       filename)

    def on__actionPrint_triggered(self):
        if self.currentPlot.printPlot():
            self.statusBar.showMessage('View successfully printed.')

    def on__actionUnzoom_triggered(self):
        self.currentPlot.unzoom()

    def on__actionLogScale_toggled(self, on):
        self.currentPlot.setLogScale(on)

    def on__actionAutoScale_toggled(self, on):
        self._autoscale(on, on)

    def on__actionScaleX_toggled(self, on):
        self._autoscale(x=on)

    def on__actionScaleY_toggled(self, on):
        self._autoscale(y=on)

    def on__actionLegend_toggled(self, on):
        self.currentPlot.setLegend(on)

    def on__actionSymbols_toggled(self, on):
        self.currentPlot.setSymbols(on)

    def on__actionLines_toggled(self, on):
        self.currentPlot.setLines(on)

    def on__actionSaveData_triggered(self):
        self.currentPlot.saveData()

    def on__actionFitPeak_triggered(self):
        self.currentPlot.beginFit(self.fitclass, self.actionFitPeak,
                                  self.fitPickCheckbox.isChecked())

    def on__actionFitLinear_triggered(self):
        cbi = self.fitComboBox.findText(self.actionFitLinear.text().replace('&', ''))
        self.fitComboBox.setCurrentIndex(cbi)
        self.fitclass = LinearFitter

    def on__actionFitExponential_triggered(self):
        cbi = self.fitComboBox.findText(self.actionFitExponential.text().replace('&', ''))
        self.fitComboBox.setCurrentIndex(cbi)
        self.fitclass = ExponentialFitter

    def on__actionFitPeakGaussian_triggered(self):
        cbi = self.fitComboBox.findText(self.actionFitPeakGaussian.text().replace('&', ''))
        self.fitComboBox.setCurrentIndex(cbi)
        self.fitclass = GaussFitter

    def on__actionFitPeakLorentzian_triggered(self):
        cbi = self.fitComboBox.findText(self.actionFitPeakLorentzian.text().replace('&', ''))
        self.fitComboBox.setCurrentIndex(cbi)
        self.fitclass = LorentzFitter

    def on__actionFitPeakPV_triggered(self):
        cbi = self.fitComboBox.findText(self.actionFitPeakPV.text().replace('&', ''))
        self.fitComboBox.setCurrentIndex(cbi)
        self.fitclass = PseudoVoigtFitter

    def on__actionFitPeakPVII_triggered(self):
        cbi = self.fitComboBox.findText(self.actionFitPeakPVII.text().replace('&', ''))
        self.fitComboBox.setCurrentIndex(cbi)
        self.fitclass = PearsonVIIFitter

    def on__actionFitTc_triggered(self):
        cbi = self.fitComboBox.findText(self.actionFitTc.text().replace('&', ''))
        self.fitComboBox.setCurrentIndex(cbi)
        self.fitclass = TcFitter

    def on__actionFitCosine_triggered(self):
        cbi = self.fitComboBox.findText(self.actionFitCosine.text().replace('&', ''))
        self.fitComboBox.setCurrentIndex(cbi)
        self.fitclass = CosineFitter

    def on__actionFitSigmoid_triggered(self):
        cbi = self.fitComboBox.findText(self.actionFitSigmoid.text().replace('&', ''))
        self.fitComboBox.setCurrentIndex(cbi)
        self.fitclass = SigmoidFitter

    def on__actionFitArby_triggered(self):
        # no second argument: the "arbitrary" action is not checkable
        self.currentPlot.beginFit(ArbitraryFitter, None,
                                  self.fitPickCheckbox.isChecked())


class HistoryPanel(BaseHistoryWindow, Panel):
    """Provides a panel to show time series plots of any cache values."""

    panelName = 'History viewer'

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        BaseHistoryWindow.__init__(self)

        self.actionClose.setVisible(False)

        self.statusBar = QStatusBar(self)
        policy = self.statusBar.sizePolicy()
        policy.setVerticalPolicy(QSizePolicy.Fixed)
        self.statusBar.setSizePolicy(policy)
        self.statusBar.setSizeGripEnabled(False)
        self.layout().addWidget(self.statusBar)

        self._disconnected_since = 0

        self.splitter.setSizes([20, 80])
        self.splitter.restoreState(self.splitterstate)
        self.client.cache.connect(self.newvalue_callback)
        self.client.disconnected.connect(self.on_client_disconnected)
        self.client.connected.connect(self.on_client_connected)

    def setCustomStyle(self, font, back):
        self.user_font = font
        self.user_color = back

        for view in self.views:
            if view.plot:
                view.plot.setBackgroundColor(back)
                view.plot.update()

        bold = QFont(font)
        bold.setBold(True)
        larger = scaledFont(font, 1.6)
        for view in self.views:
            if view.plot:
                view.plot.setFonts(font, bold, larger)

    def requestClose(self):
        # Always succeeds, but break up circular references so that the panel
        # object can be deleted properly.
        for v in self.views:
            v.plot = None
        self.currentPlot = None
        self.client.cache.disconnect(self.newvalue_callback)
        return True

    def gethistory_callback(self, key, fromtime, totime):
        return self.client.ask('gethistory', key, str(fromtime), str(totime),
                               default=[])

    def on_client_disconnected(self):
        self._disconnected_since = currenttime()

    def on_client_connected(self):
        # If the client was disconnected for longer than a few seconds, refresh
        # all open plots to avoid mysterious "flatlines" for that period.
        if currenttime() - self._disconnected_since < 5:
            return
        old_views, self.viewStack = self.viewStack, []
        for view in old_views:
            info = view.dlginfo
            row = self.clearView(view)
            new_view = self._createViewFromDialog(info, row)
            if new_view.plot.HAS_AUTOSCALE:
                self._autoscale(True, False)

    @pyqtSlot()
    def on_actionAttachElog_triggered(self):
        newdlg = dialogFromUi(self, 'panels/plot_attach.ui')
        suffix = self.currentPlot.SAVE_EXT
        newdlg.filename.setText(
            safeName('history_%s' % self.currentPlot.view.name + suffix))
        ret = newdlg.exec_()
        if ret != QDialog.Accepted:
            return
        descr = newdlg.description.text()
        fname = newdlg.filename.text()
        pathname = self.currentPlot.saveQuietly()
        with open(pathname, 'rb') as fp:
            remotefn = self.client.ask('transfer', fp.read())
        if remotefn is not None:
            self.client.eval('_LogAttach(%r, [%r], [%r])' %
                             (descr, remotefn, fname))
        os.unlink(pathname)


class StandaloneHistoryWindow(DlgUtils, BaseHistoryWindow, QMainWindow):

    newValue = pyqtSignal(object)

    def __init__(self, app):
        QMainWindow.__init__(self, None)
        self.app = app
        self.client = app  # used by the NewViewDialog

        # this is done in Panel.__init__ for the panel version
        self.settings = CompatSettings()
        self.loadSettings(self.settings)

        BaseHistoryWindow.__init__(self)
        self.splitter.setSizes([20, 80])

        DlgUtils.__init__(self, 'History viewer')

        self.actionAttachElog.setVisible(False)

        self.splitter.restoreState(self.splitterstate)

        self.setCentralWidget(self.splitter)
        self.newValue.connect(self.newvalue_callback)

        for toolbar in self.getToolbars():
            self.addToolBar(toolbar)
        for menu in self.getMenus():
            self.menuBar().addMenu(menu)
        self.actionFitLinear.trigger()
        self.statusBar = QStatusBar(self)
        self.setStatusBar(self.statusBar)

    def gethistory_callback(self, key, fromtime, totime):
        return self.app.history(None, key, fromtime, totime)

    def closeEvent(self, event):
        self.saveSettings(self.settings)
        return QMainWindow.closeEvent(self, event)


class StandaloneHistoryApp(CacheClient):

    parameters = {
        'views': Param('Strings specifying views (from command line)',
                       type=listof(str)),
    }

    def doInit(self, mode):
        self._qtapp = QApplication(sys.argv)
        self._qtapp.setOrganizationName('nicos')
        self._qtapp.setApplicationName('history')
        self._window = StandaloneHistoryWindow(self)
        # if no cache was given on the command line...
        if not self._config['cache']:
            dlg = SettingsDialog(self._window)
            dlg.exec_()
            self._setROParam('cache', dlg.cacheBox.currentText())
            self._setROParam('prefix', dlg.prefixEdit.text())
        CacheClient.doInit(self, mode)

    def getDeviceList(self, only_explicit=True, special_clause=None):
        devlist = [key[:-6] for (key, _) in self.query_db('')
                   if key.endswith('/value')]
        if special_clause:
            devlist = [dn for dn in devlist
                       if eval(special_clause, {'dn': dn})]
        return sorted(devlist)

    def getDeviceParam(self, devname, parname):
        return self.get(devname, parname)

    def getDeviceParams(self, devname):
        ldevname = devname.lower()
        index = len(ldevname) + 1
        return {key[index:]: value for (key, value) in self.query_db('')
                if key.startswith(ldevname + '/')}

    def getDeviceParamInfo(self, _):
        return {}  # we can't deliver this info from the cache alone

    def start(self):
        self._startup_done.wait(2)
        self._window.openViews(self.views)
        self._window.show()
        try:
            self._qtapp.exec_()
        except KeyboardInterrupt:
            pass
        self._stoprequest = True

    def _propagate(self, data):
        self._window.newValue.emit(data)


class SettingsDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        loadUi(self, 'panels/history_settings.ui')
        settings = CompatSettings()
        self._caches = settings.value('cachehosts') or []
        prefix = settings.value('keyprefix', 'nicos/')
        self.cacheBox.addItems(self._caches)
        self.prefixEdit.setText(prefix)

    def accept(self):
        settings = CompatSettings()
        cache = self.cacheBox.currentText()
        if cache in self._caches:
            self._caches.remove(cache)
        self._caches.insert(0, cache)
        settings.setValue('cachehosts', self._caches)
        settings.setValue('keyprefix', self.prefixEdit.text())
        QDialog.accept(self)
