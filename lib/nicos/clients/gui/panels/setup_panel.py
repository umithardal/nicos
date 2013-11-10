#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2013 by the NICOS contributors (see AUTHORS)
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

"""NICOS GUI experiment setup window."""

from PyQt4.QtGui import QDialogButtonBox, QListWidgetItem
from PyQt4.QtCore import SIGNAL, Qt

from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi, DlgUtils, decodeAny


def iterChecked(listwidget):
    """Yield checked items in a QListWidget"""
    for i in range(listwidget.count()):
        item = listwidget.item(i)
        if item.checkState() == Qt.Checked:
            yield item


class SetupPanel(Panel, DlgUtils):
    panelName = 'Experiment setup'

    def __init__(self, parent, client):
        Panel.__init__(self, parent, client)
        DlgUtils.__init__(self, 'Setup')
        loadUi(self, 'setup.ui', 'panels')
        self.propdbInfo.setVisible(False)
        self._orig_proposal = None

        if self.client.connected:
            self.on_client_connected()
        self.connect(self.client, SIGNAL('connected'), self.on_client_connected)

    def _update_proposal_info(self):
        values = self.client.eval('session.experiment.proposal, '
                                  'session.experiment.title, '
                                  'session.experiment.users, '
                                  'session.experiment.localcontact, '
                                  'session.experiment.sample.samplename', None)
        if values:
            self._orig_proposal_info = values
            self.proposalNum.setText(values[0])
            self.expTitle.setText(decodeAny(values[1]))
            self.users.setText(decodeAny(values[2]))
            self.localContact.setText(decodeAny(values[3]))
            self.sampleName.setText(decodeAny(values[4]))

    def on_client_connected(self):
        # fill proposal
        self._update_proposal_info()
        # check for capability to ask proposal database
        if self.client.eval('getattr(session.experiment, "propdb", "")', None):
            self.propdbInfo.setVisible(True)
            self.queryDBButton.setVisible(True)
        else:
            self.queryDBButton.setVisible(False)

        # fill setups
        self._setupinfo = self.client.eval('session.getSetupInfo()', {})
        self.basicSetup.clear()
        self.optSetups.clear()
        default_flags = Qt.ItemIsUserCheckable | Qt.ItemIsSelectable | \
            Qt.ItemIsEnabled
        keep = QListWidgetItem('<keep current>', self.basicSetup)
        if self._setupinfo is not None:
            for name, info in sorted(self._setupinfo.items()):
                if info is None:
                    continue
                if info['group'] == 'basic':
                    QListWidgetItem(name, self.basicSetup)
                elif info['group'] == 'optional':
                    item = QListWidgetItem(name, self.optSetups)
                    item.setFlags(default_flags)
                    item.setCheckState(Qt.Unchecked)
        self.basicSetup.setCurrentItem(keep)

        # fill detectors
        detectors = self.client.getDeviceList('nicos.core.device.Measurable')
        self._orig_detlist = self.client.eval('session.experiment.detlist', [])
        for detname in detectors:
            item = QListWidgetItem(detname, self.detectors)
            item.setFlags(default_flags)
            item.setCheckState(Qt.Checked if detname in self._orig_detlist
                               else Qt.Unchecked)

        # fill environment
        envdevs = self.client.getDeviceList('nicos.core.device.Readable')
        self._orig_envlist = self.client.eval('session.experiment.envlist', [])
        for devname in envdevs:
            item = QListWidgetItem(devname, self.sampleenv)
            item.setFlags(default_flags)
            item.setCheckState(Qt.Checked if devname in self._orig_envlist
                               else Qt.Unchecked)

    def on_basicSetup_currentItemChanged(self, item, old):
        if item.text() != '<keep current>':
            self.showSetupInfo(item.text())

    def on_basicSetup_itemClicked(self, item):
        if item.text() != '<keep current>':
            self.showSetupInfo(item.text())

    def on_optSetups_currentItemChanged(self, item, old):
        self.showSetupInfo(item.text())

    def on_optSetups_itemClicked(self, item):
        self.showSetupInfo(item.text())

    def showSetupInfo(self, setup):
        info = self._setupinfo[str(setup)]
        devs = []
        for devname, devconfig in info['devices'].iteritems():
            if not devconfig[1].get('lowlevel'):
                devs.append(devname)
        devs = ', '.join(sorted(devs))
        self.setupDescription.setText(
            '<b>%s</b><br/>%s<br/><br/>'
            'Devices: %s<br/>' % (setup, info['description'], devs))

    def on_queryDBButton_clicked(self, dosomething = True):
        if not dosomething:
            return

        prop = str(self.proposalNum.text())
        title = unicode(self.expTitle.text()).encode('utf-8')
        users = unicode(self.users.text()).encode('utf-8')
        local = unicode(self.localContact.text()).encode('utf-8')
        sample = unicode(self.sampleName.text()).encode('utf-8')

        # read all values from propdb
        try:
            result = self.client.eval('session.experiment._fillProposal(%s,{})' % prop, None)

            if result:
                # now transfer it into gui
                self.expTitle.setText(decodeAny(result.get('title', title)))
                self.users.setText(decodeAny(result.get('user', users)))
                self.localContact.setText(decodeAny(result.get('localcontact', local)))
                self.sampleName.setText(decodeAny(result.get('sample', sample)))
                # check permissions:
                failed = []
                if result.get('permission_security', 'no') != 'yes':
                    failed.append('* Security (Tel. 12699)')
                if result.get('permission_radiation_protection', 'no') != 'yes':
                    failed.append('* Radiation protection (Tel. 14955)')
                if failed:
                    self.showError('Proposal lacks sufficient permissions '\
                                   'to be performed !\n\n' + '\n'.join(failed))
            else:
                self.showInfo('Reading proposaldb failed for an unknown reason.'
                              ' Please check logfiles for hints....')
        except Exception, e:
            self.log.warning(e, exc=1)
            self.showInfo('Reading proposaldb failed for an unknown reason. '
                          'Please check logfiles....\n' + repr(e))


    def on_buttonBox_clicked(self, button):
        if self.buttonBox.buttonRole(button) == QDialogButtonBox.ApplyRole:
            self.applyChanges()
        else:
            self.parentwindow.close()

    def applyChanges(self):
        done = []

        # proposal settings
        prop = str(self.proposalNum.text())
        title = unicode(self.expTitle.text()).encode('utf-8')
        users = unicode(self.users.text()).encode('utf-8')
        local = unicode(self.localContact.text()).encode('utf-8')

        # check conditions
        if self.client.eval('session.experiment.serviceexp', True) and \
            self.client.eval('session.experiment.proptype', 'user') == 'user' and \
            self.client.eval('session.experiment.proposal', '') != prop:
            self.showError('Can not directly switch experiments, please use FinishExperiment first!')
            return

        # do some work
        if prop != self._orig_proposal_info[0]:
            args = {'proposal': prop}
            if local:
                args['localcontact'] = local
            if title:
                args['title'] = title
            if users:
                args['user'] = users
            code = 'NewExperiment(%s)' % ', '.join('%s=%r' % i
                                                   for i in args.items())
            self.client.tell('queue', '', code)
            done.append('New experiment started.')
        else:
            if title != self._orig_proposal_info[1]:
                self.client.tell('queue', '', 'Exp.title = %r' % title)
                done.append('New experiment title set.')
            if users != self._orig_proposal_info[2]:
                self.client.tell('queue', '', 'Exp.users = %r' % users)
                done.append('New users set.')
            if local != self._orig_proposal_info[3]:
                self.client.tell('queue', '', 'Exp.localcontact = %r' % local)
                done.append('New local contact set.')
        sample = unicode(self.sampleName.text()).encode('utf-8')
        if sample != self._orig_proposal_info[4]:
            self.client.tell('queue', '', 'NewSample(%r)' % sample)
            done.append('New sample name set.')

        # new setups
        setups = []
        cmd = 'NewSetup'
        basic = str(self.basicSetup.currentItem().text())
        if basic == '<keep current>':
            cmd = 'AddSetup'
        else:
            setups.append(basic)
        for item in iterChecked(self.optSetups):
            setups.append(str(item.text()))
        if setups:
            self.client.tell('queue', '',
                             '%s(%s)' % (cmd, ', '.join(map(repr, setups))))
            done.append('New setups loaded.')

        # detectors
        new_detlist = [str(item.text()) for item in iterChecked(self.detectors)]
        if set(new_detlist) != set(self._orig_detlist):
            self.client.tell('queue', '',
                             'SetDetectors(%s)' % ', '.join(new_detlist))
            done.append('New standard detectors applied.')
            self._orig_detlist = new_detlist

        # sample env
        new_envlist = [str(item.text()) for item in iterChecked(self.sampleenv)]
        if set(new_envlist) != set(self._orig_envlist):
            self.client.tell('queue', '',
                             'SetEnvironment(%s)' % ', '.join(new_envlist))
            done.append('New standard environment devices applied.')
            self._orig_envlist = new_envlist

        # tell user about everything we did
        if done:
            self.showInfo('\n'.join(done))
        self._update_proposal_info()
