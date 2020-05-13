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

"""NICOS GUI virtual console panel component."""

from __future__ import absolute_import, division, print_function

import io
import sys
from os import path

from nicos.clients.gui.dialogs.traceback import TracebackDialog
from nicos.clients.gui.panels import Panel, showPanel
from nicos.clients.gui.utils import enumerateWithProgress, loadUi, modePrompt
from nicos.guisupport.qt import QAbstractPrintDialog, QDialog, QFileDialog, \
    QMenu, QMessageBox, QPrintDialog, QPrinter, Qt, QTextEdit, pyqtSlot
from nicos.guisupport.utils import setBackgroundColor
from nicos.utils import chunks, findResource


class ConsolePanel(Panel):
    """Provides a console-like interface.

    The commands can be entered and the output from the NICOS daemon is
    displayed.

    Options:

    * ``hasinput`` (default True) -- if set to False, the input box is hidden
      and the console is just an output view.
    * ``hasmenu`` (default True) -- if set to False, the console does not
      provide its menu (containing actions for the output view such as Save
      or Print).
    * ``fulltime`` (default False) -- if set to True, the console shows the
      full (date + time) timestamp for every line, instead of only for errors
      and warnings.
    * ``watermark`` (default empty) -- the path to an image file that should
      be used as a watermark in the console window.
    """

    panelName = 'Console'
    ui = 'panels/console.ui'

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        loadUi(self, self.ui)

        self.commandInput.scrollWidget = self.outView
        self.grepPanel.hide()
        self.grepText.scrollWidget = self.outView
        self.actionLabel.hide()
        self.outView.setActionLabel(self.actionLabel)
        self.commandInput.history = self.cmdhistory
        self.commandInput.completion_callback = self.completeInput
        self.grepNoMatch.setVisible(False)
        self.actionAllowLineWrap.setChecked(self.mainwindow.allowoutputlinewrap)

        client.connected.connect(self.on_client_connected)
        client.message.connect(self.on_client_message)
        client.simmessage.connect(self.on_client_simmessage)
        client.initstatus.connect(self.on_client_initstatus)
        client.mode.connect(self.on_client_mode)
        client.experiment.connect(self.on_client_experiment)

        self.outView.setContextMenuPolicy(Qt.CustomContextMenu)

        self.menu = QMenu('&Output', self)
        self.menu.addAction(self.actionCopy)
        self.menu.addAction(self.actionGrep)
        self.menu.addSeparator()
        self.menu.addAction(self.actionSave)
        self.menu.addAction(self.actionPrint)
        self.menu.addSeparator()
        self.menu.addAction(self.actionAllowLineWrap)
        self.on_actionAllowLineWrap_triggered(
            self.mainwindow.allowoutputlinewrap)

        self.hasinput = bool(options.get('hasinput', True))
        self.inputFrame.setVisible(self.hasinput)
        self.hasmenu = bool(options.get('hasmenu', True))
        if options.get('fulltime', False):
            self.outView.setFullTimestamps(True)
        watermark = options.get('watermark', '')
        if watermark:
            watermark = findResource(watermark)
            if path.isfile(watermark):
                self.outView.setBackgroundImage(watermark)

    def on_outView_customContextMenuRequested(self, point):
        self.menu.popup(self.outView.mapToGlobal(point))

    def setExpertMode(self, expert):
        if not self.hasinput:
            self.inputFrame.setVisible(expert)

    def setViewOnly(self, viewonly):
        self.commandInput.setVisible(not viewonly)
        self.promptLabel.setVisible(not viewonly)

    def loadSettings(self, settings):
        self.cmdhistory = settings.value('cmdhistory') or []

    def saveSettings(self, settings):
        # only save 100 entries of the history
        cmdhistory = self.commandInput.history[-100:]
        settings.setValue('cmdhistory', cmdhistory)

    def getMenus(self):
        if self.hasmenu:
            return [self.menu]
        return []

    def setCustomStyle(self, font, back):
        self.commandInput.idle_color = back
        for widget in (self.outView, self.commandInput):
            widget.setFont(font)
            setBackgroundColor(widget, back)
        self.promptLabel.setFont(font)

    def updateStatus(self, status, exception=False):
        self.commandInput.setStatus(status)

    def completeInput(self, fullstring, lastword):
        try:
            return self.client.ask('complete', fullstring, lastword,
                                   default=[])
        except Exception:
            return []

    def on_client_connected(self):
        self.actionLabel.hide()
        self.outView._currentuser = self.client.login

    def on_client_mode(self, mode):
        self.promptLabel.setText(modePrompt(mode))

    def on_client_initstatus(self, state):
        self.on_client_mode(state['mode'])
        self.outView.clear()
        messages = self.client.ask('getmessages', '10000', default=[])
        total = len(messages) // 2500 + 1
        for _, batch in enumerateWithProgress(chunks(messages, 2500),
                                              text='Synchronizing...',
                                              parent=self, total=total):
            self.outView.addMessages(batch)
        self.outView.scrollToBottom()

    def on_client_message(self, message):
        self.outView.addMessage(message)

    def on_client_simmessage(self, simmessage):
        if simmessage[-1] == '0':
            self.outView.addMessage(simmessage)

    def on_client_experiment(self, data):
        (_, proptype) = data
        if proptype == 'user':
            # only clear history and output when switching TO a user experiment
            self.commandInput.history = []
            # clear everything except the last command with output
            self.outView.clearAlmostEverything()

    def on_outView_anchorClicked(self, url):
        """Called when the user clicks a link in the out view."""
        scheme = url.scheme()
        if scheme == 'exec':
            # Direct execution is too dangerous. Just insert it in the editor.
            if self.inputFrame.isVisible():
                self.commandInput.setText(url.path())
                self.commandInput.setFocus()
        elif scheme == 'edit':
            if self.mainwindow.editor_wintype is None:
                return
            win = self.mainwindow.createWindow(self.mainwindow.editor_wintype)
            panel = win.getPanel('User editor')
            panel.openFile(url.path())
            showPanel(panel)
        elif scheme == 'trace':
            TracebackDialog(self, self.outView, url.path()).show()
        else:
            self.log.warning('Strange anchor in outView: %s', url)

    @pyqtSlot()
    def on_actionPrint_triggered(self):
        printer = QPrinter()
        printdlg = QPrintDialog(printer, self)
        printdlg.setOption(QAbstractPrintDialog.PrintSelection)
        if printdlg.exec_() == QDialog.Accepted:
            self.outView.print_(printer)

    @pyqtSlot()
    def on_actionSave_triggered(self):
        fn = QFileDialog.getSaveFileName(self, 'Save', '', 'All files (*.*)')[0]
        if not fn:
            return
        try:
            fn = fn.encode(sys.getfilesystemencoding())
            with io.open(fn, 'w', encoding='utf-8') as f:
                f.write(self.outView.getOutputString())
        except Exception as err:
            QMessageBox.warning(self, 'Error', 'Writing file failed: %s' % err)

    @pyqtSlot()
    def on_actionCopy_triggered(self):
        self.outView.copy()

    @pyqtSlot()
    def on_actionGrep_triggered(self):
        self.grepPanel.setVisible(True)
        self.grepText.setFocus()

    @pyqtSlot()
    def on_grepClose_clicked(self):
        self.grepPanel.setVisible(False)
        self.commandInput.setFocus()
        self.outView.scrollToBottom()

    def on_grepText_returnPressed(self):
        self.on_grepSearch_clicked()

    def on_grepText_escapePressed(self):
        self.on_grepClose_clicked()

    @pyqtSlot()
    def on_grepSearch_clicked(self):
        st = self.grepText.text()
        if not st:
            return
        found = self.outView.findNext(st, self.grepRegex.isChecked())
        self.grepNoMatch.setVisible(not found)

    @pyqtSlot()
    def on_grepOccur_clicked(self):
        st = self.grepText.text()
        if not st:
            return
        self.outView.occur(st, self.grepRegex.isChecked())

    @pyqtSlot(bool)
    def on_actionAllowLineWrap_triggered(self, checked):
        self.mainwindow.allowoutputlinewrap = checked
        if self.mainwindow.allowoutputlinewrap:
            self.outView.setLineWrapMode(QTextEdit.WidgetWidth)
        else:
            self.outView.setLineWrapMode(QTextEdit.NoWrap)

    def on_commandInput_execRequested(self, script, action):
        if action == 'queue':
            self.client.run(script)
        else:
            self.client.tell('exec', script)
        self.commandInput.setText('')
