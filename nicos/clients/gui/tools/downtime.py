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
#   Jens Krueger <jens.krueger@tum.de>
#
# *****************************************************************************

"""Graphical interface to send an instrument downtime report."""

from __future__ import absolute_import, division, print_function

import collections

from nicos.clients.gui.utils import DlgUtils, SettingGroup, loadUi
from nicos.guisupport.qt import QDateTime, QDialog, QDialogButtonBox, QIcon
from nicos.utils.emails import sendMail
from nicos.utils.loggers import NicosLogger


class DownTimeTool(DlgUtils, QDialog):
    toolName = 'DownTimeTool'

    def __init__(self, parent, client, **configs):
        QDialog.__init__(self, parent)
        DlgUtils.__init__(self, self.toolName)
        loadUi(self, 'tools/downtime.ui')
        self.sendBtn = self.buttonBox.addButton('&Send',
                                                QDialogButtonBox.AcceptRole)
        self.sendBtn.setIcon(QIcon(':/mail'))
        self.sendBtn.setDisabled(True)

        self.parentwindow = parent
        self.client = client
        if hasattr(parent, 'mainwindow'):
            self.mainwindow = parent.mainwindow
            self.log = NicosLogger(self.toolName)
            self.log.parent = self.mainwindow.log
        else:
            self.log = configs.get('log', None)
        self.sgroup = SettingGroup(self.toolName)

        self._sender = configs.get('sender', 'anonymous@frm2.tum.de')
        self._receiver = configs.get('receiver', 'useroffice@mlz-garching.de')
        self._mailserver = configs.get('mailserver', '') or \
            self._getDeviceComponent('experiment', 'mailserver', 'smtp.frm2.tum.de')
        self._instrument = configs.get('instrument', '') or \
            self._getDeviceComponent('instrument', 'instrument', 'DEMO')
        t = self.mailheaderText.text().replace('{{instrument}}',
                                               self._instrument)
        self.mailheaderText.setText(t)

        self.startDown.setDateTime(QDateTime.currentDateTime().addSecs(-3600))
        self.endDown.setDateTime(QDateTime.currentDateTime())
        self.errorText.setVisible(False)
        with self.sgroup as settings:
            self.loadSettings(settings)
        self.reasons.clearEditText()

    def loadSettings(self, settings):
        try:
            reasons = settings.value('reasons')
        except TypeError:
            reasons = []
        if reasons:
            self.reasons.addItems(reasons)

    def closeEvent(self, event):
        self.deleteLater()
        self.accept()

    def on_buttonBox_accepted(self):
        self._saveSettings()
        self._sendMail()
        self.accept()

    def on_buttonBox_rejected(self):
        self.reject()
        self.close()

    def on_reasons_editTextChanged(self, text):
        self._enableSend()

    def on_startDown_dateTimeChanged(self, date):
        self._enableSend()

    def on_endDown_dateTimeChanged(self, date):
        self._enableSend()

    def _enableSend(self):
        timeCorrect = self.startDown.dateTime() < self.endDown.dateTime()
        self.sendBtn.setDisabled(not timeCorrect or
                                 not self.reasons.currentText().strip())
        self.errorText.setVisible(not timeCorrect)

    def _getDeviceComponent(self, devname, param, default=''):
        try:
            val = self.client.eval('session.%s.%s' % (devname, param), default)
        except (AttributeError, NameError):
            val = default
        return val

    def _getMailAdresses(self, val):
        ret = []
        for i in val.split(','):
            t = i.strip().partition('<')[-1].rpartition('>')[0]
            ret += [t] if t else [i.strip()]
        return ret

    def _saveSettings(self):
        items = [self.reasons.currentText()] + \
                [self.reasons.itemText(i).strip() for i in
                 range(self.reasons.count())]
        with self.sgroup as settings:
            settings.setValue('reasons', list(collections.Counter(items)))

    def _sendMail(self):
        responsibles = self._getMailAdresses(
            self._getDeviceComponent('instrument', 'responsible'))
        sender = self._sender or self._getDeviceComponent('experiment',
                                                          'mailsender',
                                                          responsibles[0])
        receivers = self._getMailAdresses(self._receiver)
        if responsibles and responsibles[0]:
            receivers += responsibles
        topic = self.mailheaderText.text()
        body = 'The instrument %s had a downtime from %s to %s due to:\n\n%s' %\
               (self._instrument, self.startDown.text(), self.endDown.text(),
                self.reasons.currentText())
        err = sendMail(self._mailserver, receivers, sender, topic, body)
        if err:
            if self.log:
                self.log.error(' - '.join(err))
            self.showError('\n'.join(err))
