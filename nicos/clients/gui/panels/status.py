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

"""NICOS GUI script status panel component."""

from __future__ import absolute_import, division, print_function

from time import time

from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi
from nicos.guisupport.qt import QActionGroup, QColor, QFontMetrics, QIcon, \
    QListWidgetItem, QMenu, QPixmap, QSize, QStyledItemDelegate, Qt, QTimer, \
    QToolBar, pyqtSlot
from nicos.guisupport.utils import setBackgroundColor
from nicos.protocols.daemon import BREAK_AFTER_LINE, BREAK_AFTER_STEP, \
    BREAK_NOW, SIM_STATES, STATUS_IDLEEXC
from nicos.utils import formatEndtime


class ScriptQueue(object):
    def __init__(self, frame, view):
        self._id2item = {}  # mapping from request ID to list widget item
        self._frame = frame
        self._view = view
        self._timer = QTimer(singleShot=True, timeout=self._timeout)

    def _format_item(self, request):
        script = request['script']
        if len(script) > 100:
            return script[:100] + '...'
        return script

    def _timeout(self):
        self._frame.show()

    def append(self, request):
        item = QListWidgetItem(self._format_item(request))
        item.setData(Qt.UserRole, request['reqid'])
        self._id2item[request['reqid']] = item
        self._view.addItem(item)
        # delay showing the frame for 20 msecs, so that it doesn't flicker in
        # and out if the script is immediately taken out of the queue again
        self._timer.start(20)

    def update(self, request):
        item = self._id2item.get(request['reqid'])
        if item:
            text = self._format_item(request)
            item.setText(text)

    def remove(self, reqid):
        item = self._id2item.pop(reqid, None)
        if item is None:
            return
        item = self._view.takeItem(self._view.row(item))
        if not self._id2item:
            self._timer.stop()
            self._frame.hide()
        return item

    def rearrange(self, reqids):
        selected = self._view.currentItem()
        for i in range(self._view.count()-1, -1, -1):
            self._view.takeItem(i)
        for reqid in reqids:
            self._view.addItem(self._id2item[reqid])
        if selected:
            self._view.setCurrentItem(selected)

    def clear(self):
        self._frame.hide()
        self._view.clear()
        self._id2item.clear()

    # pylint: disable=nonzero-method
    def __nonzero__(self):
        return bool(self._id2item)

    __bool__ = __nonzero__


class LineDelegate(QStyledItemDelegate):
    def __init__(self, offset, view):
        QStyledItemDelegate.__init__(self, view)
        self._offset = offset

    def paint(self, painter, option, index):
        QStyledItemDelegate.paint(self, painter, option, index)
        text = index.data(Qt.UserRole)
        rect = option.rect.adjusted(self._offset, 0, 0, 0)
        painter.setPen(QColor('grey'))
        painter.drawText(rect, 0, text)


class ScriptStatusPanel(Panel):
    """Provides a view of the currently executed script.

    The current position within the script is shown with an arrow.  The panel
    also displays queued scripts.

    Options:

    * ``stopcounting`` (default False) -- Configure the stop button behaviour,
      if is set to ``True``, the execution of a script will be aborted,
      otherwise a counting will be finished first before the script will be
      stopped.
    * ``eta`` (default False) - if set to ``True`` the "ETA" (estimated time of
      end of script) will be displayed if the
      :class:`daemon <nicos.services.daemon.NicosDaemon>` is configured to run
      with automatic simulation of the current command.
    """

    panelName = 'Script status'

    SHOW_ETA_STATES =[
        'running',
        'paused'
    ]

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        loadUi(self, 'panels/status.ui')

        self.stopcounting = False
        self.menus = None
        self.bar = None
        self.queueFrame.hide()
        self.statusLabel.hide()
        self.pause_color = QColor('#ffdddd')
        self.idle_color = parent.user_color

        self.script_queue = ScriptQueue(self.queueFrame, self.queueView)
        self.current_line = -1
        self.current_request = {}
        self.curlineicon = QIcon(':/currentline')
        self.errlineicon = QIcon(':/errorline')
        empty = QPixmap(16, 16)
        empty.fill(Qt.transparent)
        self.otherlineicon = QIcon(empty)
        self.traceView.setItemDelegate(LineDelegate(24, self.traceView))

        self.stopcounting = bool(options.get('stopcounting', False))
        if self.stopcounting:
            tooltip = 'Aborts the current executed script'
            self.actionStop.setToolTip(tooltip)
            self.actionStop.setText('Abort current script')
            self.actionStop2.setToolTip(tooltip)

        self.showETA = bool(options.get('eta', False))
        self.etaWidget.hide()

        client.request.connect(self.on_client_request)
        client.processing.connect(self.on_client_processing)
        client.blocked.connect(self.on_client_blocked)
        client.status.connect(self.on_client_status)
        client.initstatus.connect(self.on_client_initstatus)
        client.disconnected.connect(self.on_client_disconnected)
        client.rearranged.connect(self.on_client_rearranged)
        client.updated.connect(self.on_client_updated)
        client.eta.connect(self.on_client_eta)

        bar = QToolBar('Script control')
        bar.setObjectName(bar.windowTitle())
        # unfortunately it is not wise to put a menu in its own dropdown menu,
        # so we have to duplicate the actionBreak and actionStop...
        dropdown1 = QMenu('', self)
        dropdown1.addAction(self.actionBreak)
        dropdown1.addAction(self.actionBreakCount)
        dropdown1.addAction(self.actionFinishEarly)
        self.actionBreak2.setMenu(dropdown1)
        dropdown2 = QMenu('', self)
        dropdown2.addAction(self.actionStop)
        dropdown2.addAction(self.actionFinish)
        dropdown2.addAction(self.actionFinishEarlyAndStop)
        self.actionStop2.setMenu(dropdown2)
        bar.addAction(self.actionBreak2)
        bar.addAction(self.actionContinue)
        bar.addAction(self.actionStop2)
        bar.addAction(self.actionEmergencyStop)
        self.bar = bar
        # self.mainwindow.addToolBar(bar)

        menu = QMenu('&Script control', self)
        menu.addAction(self.actionBreak)
        menu.addAction(self.actionBreakCount)
        menu.addAction(self.actionContinue)
        menu.addAction(self.actionFinishEarly)
        menu.addSeparator()
        menu.addAction(self.actionStop)
        menu.addAction(self.actionFinish)
        menu.addAction(self.actionFinishEarlyAndStop)
        menu.addSeparator()
        menu.addAction(self.actionEmergencyStop)
        self.mainwindow.menuBar().insertMenu(
            self.mainwindow.menuWindows.menuAction(), menu)

        self.activeGroup = QActionGroup(self)
        self.activeGroup.addAction(self.actionBreak)
        self.activeGroup.addAction(self.actionBreak2)
        self.activeGroup.addAction(self.actionBreakCount)
        self.activeGroup.addAction(self.actionContinue)
        self.activeGroup.addAction(self.actionStop)
        self.activeGroup.addAction(self.actionStop2)
        self.activeGroup.addAction(self.actionFinish)
        self.activeGroup.addAction(self.actionFinishEarly)
        self.activeGroup.addAction(self.actionFinishEarlyAndStop)

        self._status = 'idle'

    def setViewOnly(self, viewonly):
        self.activeGroup.setEnabled(not viewonly)

    def setCustomStyle(self, font, back):
        self.idle_color = back
        for widget in (self.traceView, self.queueView):
            widget.setFont(font)
            setBackgroundColor(widget, back)

    def getToolbars(self):
        return [self.bar]

    def getMenus(self):
        return []

    def updateStatus(self, status, exception=False):
        self._status = status

        isconnected = status != 'disconnected'
        self.actionBreak.setEnabled(isconnected and status != 'idle')
        self.actionBreak2.setEnabled(isconnected and status != 'idle')
        self.actionBreak2.setVisible(status != 'paused')
        self.actionBreakCount.setEnabled(isconnected and status != 'idle')
        self.actionContinue.setVisible(status == 'paused')
        self.actionStop.setEnabled(isconnected and status != 'idle')
        self.actionStop2.setEnabled(isconnected and status != 'idle')
        self.actionFinish.setEnabled(isconnected and status != 'idle')
        self.actionFinishEarly.setEnabled(isconnected and status != 'idle')
        self.actionFinishEarlyAndStop.setEnabled(isconnected and status != 'idle')
        self.actionEmergencyStop.setEnabled(isconnected)
        if status == 'paused':
            self.statusLabel.setText('Script is paused.')
            self.statusLabel.show()
            setBackgroundColor(self.traceView, self.pause_color)
        else:
            self.statusLabel.hide()
            setBackgroundColor(self.traceView, self.idle_color)
        self.traceView.update()

        if status == 'idle':
            self.etaWidget.hide()

    def setScript(self, script):
        self.traceView.clear()
        lines = script.splitlines()
        longest = len(str(len(lines)))
        padding = ' ' * (longest + 3)
        height = QFontMetrics(self.traceView.font()).height()
        for (i, line) in enumerate(lines):
            item = QListWidgetItem(self.otherlineicon, padding + line,
                                   self.traceView)
            item.setSizeHint(QSize(-1, height))
            item.setData(Qt.UserRole, '%*d |' % (longest, i+1))
            self.traceView.addItem(item)
        self.current_line = -1

    def setCurrentLine(self, line, error_exit=False):
        if self.current_line != -1:
            item = self.traceView.item(self.current_line - 1)
            if item:
                # when a script has exited with an error, keep indicating the
                # current line, with a red arrow
                if error_exit and line == -1:
                    item.setIcon(self.errlineicon)
                else:
                    item.setIcon(self.otherlineicon)
            self.current_line = -1
        if 0 < line <= self.traceView.count():
            item = self.traceView.item(line - 1)
            item.setIcon(self.curlineicon)
            self.traceView.scrollToItem(item)
            self.current_line = line

    def on_client_request(self, request):
        if 'script' not in request:
            return
        self.script_queue.append(request)

    def on_client_processing(self, request):
        if 'script' not in request:
            return
        new_current_line = -1
        if self.current_request['reqid'] == request['reqid']:
            # on update, set the current line to the same as before
            # (this may be WRONG, but should not in most cases, and it's
            # better than no line indicator at all)
            new_current_line = self.current_line
        self.script_queue.remove(request['reqid'])
        self.setScript(request['script'])
        self.current_request = request
        self.setCurrentLine(new_current_line)

    def on_client_blocked(self, requests):
        for reqid in requests:
            self.script_queue.remove(reqid)

    def on_client_eta(self, data):
        if not self.showETA or self._status not in self.SHOW_ETA_STATES:
            return

        state, eta = data

        if state == SIM_STATES['pending']:
            self.etaWidget.hide()
        elif state == SIM_STATES['running']:
            self.etaLabel.setText('Calculating...')
            self.etaWidget.show()
        elif state == SIM_STATES['success'] and eta > time():
            self.etaLabel.setText(formatEndtime(eta - time()))
            self.etaWidget.show()
        elif state == SIM_STATES['failed']:
            self.etaLabel.setText('Could not calculate ETA')
            self.etaWidget.show()

    def on_client_initstatus(self, state):
        self.setScript(state['script'])
        self.current_request['script'] = state['script']
        self.current_request['reqid'] = None
        self.on_client_status(state['status'])
        for req in state['requests']:
            self.on_client_request(req)
        if self.showETA:
            self.on_client_eta(state['eta'])

    def on_client_status(self, data):
        status, line = data
        if line != self.current_line:
            self.setCurrentLine(line, status == STATUS_IDLEEXC)

    def on_client_disconnected(self):
        self.script_queue.clear()

    def on_client_rearranged(self, items):
        self.script_queue.rearrange(items)

    def on_client_updated(self, request):
        if 'script' not in request:
            return
        self.script_queue.update(request)

    @pyqtSlot()
    def on_actionBreak_triggered(self):
        self.client.tell_action('break', BREAK_AFTER_STEP)

    @pyqtSlot()
    def on_actionBreak2_triggered(self):
        self.on_actionBreak_triggered()

    @pyqtSlot()
    def on_actionBreakCount_triggered(self):
        self.client.tell_action('break', BREAK_NOW)

    @pyqtSlot()
    def on_actionContinue_triggered(self):
        self.client.tell_action('continue')

    @pyqtSlot()
    def on_actionStop_triggered(self):
        if self.stopcounting:
            self.client.tell_action('stop', BREAK_NOW)
        else:
            self.client.tell_action('stop', BREAK_AFTER_STEP)

    @pyqtSlot()
    def on_actionStop2_triggered(self):
        self.on_actionStop_triggered()

    @pyqtSlot()
    def on_actionFinish_triggered(self):
        self.client.tell_action('stop', BREAK_AFTER_LINE)

    @pyqtSlot()
    def on_actionFinishEarly_triggered(self):
        self.client.tell_action('finish')

    @pyqtSlot()
    def on_actionFinishEarlyAndStop_triggered(self):
        self.client.tell_action('stop', BREAK_AFTER_STEP)
        self.client.tell_action('finish')

    @pyqtSlot()
    def on_actionEmergencyStop_triggered(self):
        self.client.tell_action('emergency')

    @pyqtSlot()
    def on_clearQueue_clicked(self):
        if self.client.tell('unqueue', '*'):
            self.script_queue.clear()

    @pyqtSlot()
    def on_deleteQueueItem_clicked(self):
        item = self.queueView.currentItem()
        if not item:
            return
        reqid = item.data(Qt.UserRole)
        if self.client.tell('unqueue', str(reqid)):
            self.script_queue.remove(reqid)

    def moveItem(self, delta):
        rowCount = self.queueView.count()
        IDs = []
        for i in range(rowCount):
            IDs.append(self.queueView.item(i).data(Qt.UserRole))
        curID = self.queueView.currentItem().data(Qt.UserRole)
        i = IDs.index(curID)
        IDs.insert(i + delta, IDs.pop(i))
        self.client.ask('rearrange', IDs)

    @pyqtSlot()
    def on_upButton_clicked(self):
        if self.queueView.currentItem():
            self.moveItem(-1)

    @pyqtSlot()
    def on_downButton_clicked(self):
        if self.queueView.currentItem():
            self.moveItem(+1)
