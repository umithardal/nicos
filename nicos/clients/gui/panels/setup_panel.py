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

"""NICOS GUI experiment setup window."""

from __future__ import absolute_import, division, print_function

from nicos.clients.gui.panels import Panel, PanelDialog
from nicos.clients.gui.utils import loadUi
from nicos.core import ConfigurationError
from nicos.core.params import mailaddress, vec3
from nicos.devices.sxtal.xtal.sxtalcell import SXTalCell
from nicos.guisupport import typedvalue
from nicos.guisupport.qt import QComboBox, QDialog, QDialogButtonBox, QFrame, \
    QHBoxLayout, QLabel, QListWidgetItem, QMessageBox, QPushButton, Qt, \
    pyqtSlot
from nicos.guisupport.widget import NicosWidget
from nicos.pycompat import iteritems, itervalues, listitems
from nicos.utils import decodeAny


def iterChecked(listwidget):
    """Yield checked items in a QListWidget"""
    for i in range(listwidget.count()):
        item = listwidget.item(i)
        if item.checkState() == Qt.Checked:
            yield item


class ExpPanel(Panel):
    """Provides a panel with several input fields for the experiment settings.

    Options:

    * ``new_exp_panel`` -- class name of the panel which should be opened after
      a new experiment has been started.
    * ``finish_exp_panel`` -- class name of the panel which should be opened
      before an experiment is finished.
    """

    panelName = 'Experiment setup'
    ui = 'panels/setup_exp.ui'

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        loadUi(self, self.ui)
        self.propdbInfo.setVisible(False)
        self._orig_proposal = None
        self._new_exp_panel = None
        self._finish_exp_panel = None

        # Additional dialog panels to pop up after NewExperiment() and before
        # FinishExperiment() respectively.
        self._new_exp_panel = options.get('new_exp_panel')
        self._finish_exp_panel = options.get('finish_exp_panel')

        client.connected.connect(self.on_client_connected)
        client.setup.connect(self.on_client_connected)
        client.experiment.connect(self.on_client_experiment)

    def _update_proposal_info(self):
        values = self.client.eval('session.experiment.proposal, '
                                  'session.experiment.title, '
                                  'session.experiment.users, '
                                  'session.experiment.localcontact, '
                                  'session.experiment.sample.samplename, '
                                  'session.experiment.errorbehavior', None)
        if values:
            self._orig_proposal_info = values
            self.proposalNum.setText(values[0])
            self.expTitle.setText(decodeAny(values[1]))
            self.users.setText(decodeAny(values[2]))
            self.localContact.setText(decodeAny(values[3]))
            self.sampleName.setText(decodeAny(values[4]))
            self.errorAbortBox.setChecked(values[5] == 'abort')
        receiverinfo = self.client.eval(
            '__import__("nicos").commands.basic._listReceivers('
            '"nicos.devices.notifiers.Mailer")', {})
        emails = []
        for data in itervalues(receiverinfo):
            for (addr, what) in data:
                if what == 'receiver' and addr not in emails:
                    emails.append(addr)
        self._orig_email = emails
        self.notifEmails.setPlainText(decodeAny('\n'.join(self._orig_email)))
        propinfo = self.client.eval('session.experiment.propinfo', {})
        self._orig_datamails = propinfo.get('user_email', '')
        if not isinstance(self._orig_datamails, list):
            self._orig_datamails = self._orig_datamails.splitlines()
        self.dataEmails.setPlainText(decodeAny('\n'.join(self._orig_datamails)))

    def on_client_connected(self):
        # fill proposal
        self._update_proposal_info()
        # check for new or finish
        if self.client.eval('session.experiment.mustFinish', False):
            self.finishBox.setVisible(True)
            self.newBox.setVisible(False)
        else:
            self.finishBox.setVisible(False)
            self.newBox.setVisible(True)
            self.proposalNum.setText('')  # do not offer "service"
        # check for capability to ask proposal database
        if self.client.eval('getattr(session.experiment, "propdb", "")', None):
            self.propdbInfo.setVisible(True)
            self.queryDBButton.setVisible(True)
        else:
            self.queryDBButton.setVisible(False)
            self.propLabel.setText('Enter a proposal number or name:')
        if self.client.viewonly:
            self.finishButton.setVisible(False)
            self.buttonBox.setStandardButtons(QDialogButtonBox.Close)
        else:
            self.finishButton.setVisible(True)
            self.buttonBox.setStandardButtons(QDialogButtonBox.Apply |
                                              QDialogButtonBox.Close)

    def on_client_experiment(self, data):
        # just reinitialize
        self.on_client_connected()

    def _getProposalInput(self):
        prop = self.proposalNum.text()
        title = self.expTitle.text().encode('utf-8')
        users = self.users.text().encode('utf-8')
        try:
            local = mailaddress(self.localContact.text().encode('utf-8'))
        except ValueError:
            QMessageBox.critical(self, 'Error', 'The local contact entry is '
                                 'not  a valid email address')
            raise ConfigurationError('')
        emails = self.notifEmails.toPlainText().encode('utf-8').strip()
        emails = emails.split(b'\n') if emails else []
        if local and local not in emails:
            emails.append(local)
        dataEmails = self.dataEmails.toPlainText().encode('utf-8').strip()
        dataEmails = dataEmails.split(b'\n') if dataEmails else []
        errorbehavior = 'abort' if self.errorAbortBox.isChecked() else 'report'
        return prop, title, users, local, emails, dataEmails, errorbehavior

    @pyqtSlot()
    def on_finishButton_clicked(self):
        if self._finish_exp_panel:
            dlg = PanelDialog(self, self.client, self._finish_exp_panel,
                              'Finish experiment')
            dlg.exec_()
        if self.client.run('FinishExperiment()', noqueue=True) is None:
            self.showError('Could not finish experiment, a script '
                           'is still running.')

    @pyqtSlot()
    def on_queryDBButton_clicked(self):
        try:
            prop, title, users, _, emails, dataEmails, \
                _ = self._getProposalInput()
        except ConfigurationError:
            return
        sample = self.sampleName.text().encode('utf-8')

        # read all values from propdb
        try:
            result = self.client.eval(
                'session.experiment._fillProposal(%s, {})' % prop, None)

            if result:
                if result['wrong_instrument']:
                    self.showError('Proposal is not for this instrument, '
                                   'please check the proposal number!')
                # now transfer it into gui
                # XXX check: is the result bytes or str on Python 3?
                self.expTitle.setText(decodeAny(result.get('title', title)))
                self.users.setText(decodeAny(result.get('user', users)))
                # XXX: local contact must be email, but proposal db returns
                # only a name
                # self.localContact.setText(decodeAny(result.get('localcontact',
                #                                                local)))
                self.sampleName.setText(decodeAny(result.get('sample',
                                                             sample)))
                self.notifEmails.setPlainText(
                    decodeAny(result.get('user_email', emails)))
                self.dataEmails.setPlainText(
                    '\n'.join(decodeAny(addr) for addr in dataEmails))
                # check permissions:
                failed = []
                yes = 'yes'
                no = 'no'
                if result.get('permission_security', no) != yes:
                    failed.append('* Security (Tel. 12699)')
                if result.get('permission_radiation_protection', no) != yes:
                    failed.append('* Radiation protection (Tel. 14955)')
                if failed and not result['wrong_instrument']:
                    self.showError('Proposal lacks sufficient permissions '
                                   'to be performed!\n\n' + '\n'.join(failed))
            else:
                self.showInfo('Reading proposaldb failed for an unknown '
                              'reason. Please check logfiles for hints.')
        except Exception as e:
            self.log.warning(e, exc=1)
            self.showInfo('Reading proposaldb failed for an unknown reason. '
                          'Please check logfiles....\n' + repr(e))

    def on_buttonBox_clicked(self, button):
        role = self.buttonBox.buttonRole(button)
        if role == QDialogButtonBox.ApplyRole:
            self.applyChanges()
        elif role == QDialogButtonBox.RejectRole:
            self.closeWindow()

    def applyChanges(self):
        done = []

        # proposal settings
        try:
            prop, title, users, local, email, dataEmails, errorbehavior = \
                self._getProposalInput()
        except ConfigurationError:
            return
        email = [_f for _f in email if _f]  # remove empty lines

        # check conditions
        if self.client.eval('session.experiment.serviceexp', True) and \
           self.client.eval('session.experiment.proptype', 'user') == 'user' and \
           self.client.eval('session.experiment.proposal', '') != prop:
            self.showError('Can not directly switch experiments, please use '
                           'FinishExperiment first!')
            return

        script_running = self.mainwindow.current_status != 'idle'

        # do some work
        if prop and prop != self._orig_proposal_info[0]:
            args = {'proposal': prop}
            if local:
                args['localcontact'] = local
            if title:
                args['title'] = title
            if users:
                args['user'] = users
            code = 'NewExperiment(%s)' % ', '.join('%s=%r' % i
                                                   for i in args.items())
            if self.client.run(code, noqueue=True) is None:
                self.showError('Could not start new experiment, a script is '
                               'still running.')
                return
            done.append('New experiment started.')
            if self._new_exp_panel:
                dlg = PanelDialog(self, self.client, self._new_exp_panel,
                                  'New experiment')
                dlg.exec_()
        else:
            if title != self._orig_proposal_info[1]:
                self.client.run('Exp.title = %r' % title)
                done.append('New experiment title set.')
            if users != self._orig_proposal_info[2]:
                self.client.run('Exp.users = %r' % users)
                done.append('New users set.')
            if local != self._orig_proposal_info[3]:
                self.client.run('Exp.localcontact = %r' % local)
                done.append('New local contact set.')
        sample = self.sampleName.text().encode('utf-8')
        if sample != self._orig_proposal_info[4]:
            self.client.run('NewSample(%r)' % sample)
            done.append('New sample name set.')
        if email != self._orig_email:
            self.client.run('SetMailReceivers(%s)' %
                            ', '.join(map(repr, email)))
            done.append('New mail receivers set.')
        if dataEmails != self._orig_datamails:
            self.client.run('SetDataReceivers(%s)' %
                            ', '.join(map(repr, dataEmails)))
            done.append('New data mail receivers set.')
        if errorbehavior != self._orig_proposal_info[5]:
            self.client.run('SetErrorAbort(%s)' % (errorbehavior == 'abort'))
            done.append('New error behavior set.')

        # tell user about everything we did
        if done:
            if script_running:
                done.append('')
                done.append('The changes have been queued since a script '
                            'is currently running.')
            self.showInfo('\n'.join(done))
        self._update_proposal_info()


class AliasWidget(QFrame):
    def __init__(self, parent, name, selections, preselect):
        QFrame.__init__(self, parent)
        self.name = name
        self.selections = selections
        layout = QHBoxLayout()
        layout.addWidget(QLabel(name, self))
        self.combo = QComboBox(self)
        self.combo.addItems(selections)
        if preselect in selections:
            self.combo.setCurrentIndex(selections.index(preselect))
        else:
            self.combo.setCurrentIndex(0)
        layout.addWidget(self.combo)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def setSelections(self, selections, preselect):
        if selections != self.selections:
            self.selections = selections
            self.combo.clear()
            self.combo.addItems(selections)
            if preselect in selections:
                self.combo.setCurrentIndex(selections.index(preselect))
            else:
                self.combo.setCurrentIndex(0)

    def getSelection(self):
        return self.combo.currentText()


class SetupsPanel(Panel):
    """Provides a dialog to select and load the basic and optional setups."""
    panelName = 'Setup selection'

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        loadUi(self, 'panels/setup_setups.ui')

        self.errorLabel.hide()
        self.aliasGroup.hide()
        self._aliasWidgets = {}
        self._alias_config = None

        self._setupinfo = {}
        self._loaded = set()
        self._loaded_basic = None
        self._prev_aliases = {}
        self._prev_alias_config = None

        self._reload_btn = QPushButton('Reload current setup')
        if client.isconnected:
            self.on_client_connected()
        client.connected.connect(self.on_client_connected)
        client.setup.connect(self.on_client_connected)

    def on_client_connected(self):
        # fill setups
        self._setupinfo = self.client.eval('session.readSetupInfo()', {})
        all_loaded = self.client.eval('session.loaded_setups', set())
        self._prev_aliases = self.client.eval(
            '{d.name: d.alias for d in session.devices.values() '
            'if "alias" in d.parameters}', {})
        self._loaded = set()
        self._loaded_basic = None
        self.basicSetup.clear()
        self.optSetups.clear()
        self.errorLabel.hide()
        default_flags = Qt.ItemIsUserCheckable | Qt.ItemIsSelectable | \
            Qt.ItemIsEnabled
        keep = QListWidgetItem('<keep current>', self.basicSetup)
        if self._setupinfo is not None:
            for name, info in sorted(self._setupinfo.items()):
                if info is None:
                    self.errorLabel.show()
                    continue
                if info['group'] == 'basic':
                    QListWidgetItem(name, self.basicSetup)
                    if name in all_loaded:
                        self._loaded_basic = name
                        self._loaded.add(name)
                elif info['group'] == 'optional':
                    item = QListWidgetItem(name, self.optSetups)
                    item.setFlags(default_flags)
                    item.setData(Qt.UserRole, 0)
                    if name in all_loaded:
                        self._loaded.add(name)
                    item.setCheckState(Qt.Checked if name in all_loaded
                                       else Qt.Unchecked)
                elif info['group'] == 'plugplay':
                    item = QListWidgetItem(name, self.optSetups)
                    item.setFlags(default_flags)
                    item.setData(Qt.UserRole, 1)
                    if name in all_loaded:
                        self._loaded.add(name)
                    elif not self.showPnpBox.isChecked():
                        item.setHidden(True)
                    item.setCheckState(Qt.Checked if name in all_loaded
                                       else Qt.Unchecked)
        self.basicSetup.setCurrentItem(keep)
        self._prev_alias_config = self._alias_config
        if self.client.viewonly:
            self.buttonBox.setStandardButtons(QDialogButtonBox.Close)
            self.buttonBox.removeButton(self._reload_btn)
        else:
            self.buttonBox.setStandardButtons(QDialogButtonBox.Apply |
                                              QDialogButtonBox.Close)
            self.buttonBox.addButton(self._reload_btn,
                                     QDialogButtonBox.ResetRole)

    def on_basicSetup_currentItemChanged(self, item, old):
        if item and item.text() != '<keep current>':
            self.showSetupInfo(item.text())
        self.updateAliasList()

    def on_basicSetup_itemClicked(self, item):
        if item.text() != '<keep current>':
            self.showSetupInfo(item.text())
        self.updateAliasList()

    def on_optSetups_currentItemChanged(self, item, old):
        if item:
            self.showSetupInfo(item.text())

    def on_optSetups_itemClicked(self, item):
        self.showSetupInfo(item.text())
        self.updateAliasList()

    def on_showPnpBox_stateChanged(self, state):
        for i in range(self.optSetups.count()):
            item = self.optSetups.item(i)
            if item.data(Qt.UserRole) == 1:
                item.setHidden(item.checkState() == Qt.Unchecked and
                               not self.showPnpBox.isChecked())

    def on_buttonBox_clicked(self, button):
        role = self.buttonBox.buttonRole(button)
        if role == QDialogButtonBox.ApplyRole:
            self.applyChanges()
        elif role == QDialogButtonBox.RejectRole:
            self.closeWindow()
        elif role == QDialogButtonBox.ResetRole:
            if self.client.run('NewSetup()', noqueue=True) is None:
                self.showError('Could not reload setups, a script is running.')
            else:
                self.showInfo('Current setups reloaded.')
                # Close the window only in case of use in a dialog, not in a
                # tabbed window or similiar
                if isinstance(self.parent(), QDialog):
                    self.closeWindow()

    def showSetupInfo(self, setup):
        info = self._setupinfo[str(setup)]
        devs = []
        for devname, devconfig in iteritems(info['devices']):
            if not devconfig[1].get('lowlevel'):
                devs.append(devname)
        devs = ', '.join(sorted(devs))
        self.setupDescription.setText(
            '<b>%s</b><br/>%s<br/><br/>'
            'Devices: %s<br/>' % (setup, info['description'], devs))

    def _calculateSetups(self):
        cur = self.basicSetup.currentItem()
        if cur:
            basic = cur.text()
        else:
            basic = '<keep current>'
        # calculate the new setups
        setups = set()
        new_basic = False
        if basic == '<keep current>':
            if self._loaded_basic:
                setups.add(self._loaded_basic)
        else:
            setups.add(basic)
            new_basic = True
        for item in iterChecked(self.optSetups):
            setups.add(item.text())
        return setups, new_basic

    def updateAliasList(self):
        setups, _ = self._calculateSetups()
        # get includes as well
        seen = set()

        def add_includes(s):
            if s in seen or s not in self._setupinfo:
                return
            seen.add(s)
            for inc in self._setupinfo[s]['includes']:
                add_includes(inc)
                setups.add(inc)

        for setup in setups.copy():
            add_includes(setup)
        # now collect alias config
        alias_config = {}
        for setup in setups:
            if 'alias_config' in self._setupinfo[setup]:
                aliasconfig = self._setupinfo[setup]['alias_config']
                for aliasname, targets in aliasconfig.items():
                    for (target, prio) in targets.items():
                        alias_config.setdefault(aliasname, []).append((target,
                                                                       prio))
        # sort by priority
        for aliasname in alias_config:
            alias_config[aliasname].sort(key=lambda x: -x[1])
        # create/update widgets
        layout = self.aliasGroup.layout()
        # only preselect previous aliases if we have the same choices for them
        # as in the beginning
        for aliasname in sorted(alias_config):
            preselect = self._prev_alias_config is None or \
                (alias_config.get(aliasname) ==
                 self._prev_alias_config.get(aliasname))
            selections = [x[0] for x in alias_config[aliasname]]
            if aliasname in self._aliasWidgets:
                self._aliasWidgets[aliasname].setSelections(
                    selections,
                    preselect and self._prev_aliases.get(aliasname))
            else:
                wid = self._aliasWidgets[aliasname] = AliasWidget(
                    self, aliasname, selections,
                    preselect and self._prev_aliases.get(aliasname))
                layout.addWidget(wid)
        for name, wid in listitems(self._aliasWidgets):
            if name not in alias_config:
                layout.takeAt(layout.indexOf(wid)).widget().deleteLater()
                del self._aliasWidgets[name]
        if alias_config:
            self.aliasGroup.show()
        else:
            self.aliasGroup.hide()
        self._alias_config = alias_config

    def applyChanges(self):
        cmd = 'NewSetup'
        setups, new_basic = self._calculateSetups()

        to_add = setups - self._loaded
        to_remove = self._loaded - setups
        # new setups only and no basic setup change?
        if to_add and not to_remove and not new_basic:
            cmd = 'AddSetup'
            setups = to_add
        else:
            cmd = 'NewSetup'
        if setups:
            if self.client.run('%s(%s)' % (cmd, ', '.join(map(repr, setups))),
                               noqueue=True) is None:
                self.showError('Could not load setups, a script is running.')
                return
        for name, wid in self._aliasWidgets.items():
            self.client.run('%s.alias = %r' % (name, wid.getSelection()))
        if setups or self._aliasWidgets:
            self.showInfo('New setups loaded.')


class DetEnvPanel(Panel):
    """Provides a dialog to select the detector and environment devices."""
    panelName = 'Det/Env setup'

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        loadUi(self, 'panels/setup_detenv.ui')

        if client.isconnected:
            self.on_client_connected()
        client.connected.connect(self.on_client_connected)
        client.setup.connect(self.on_client_connected)

    def on_client_connected(self):
        self.detectors.clear()
        self.sampleenv.clear()

        default_flags = Qt.ItemIsUserCheckable | Qt.ItemIsSelectable | \
            Qt.ItemIsEnabled

        # fill detectors
        detectors = self.client.getDeviceList(
            'nicos.core.device.Measurable',
            exclude_class='nicos.devices.generic.detector.PassiveChannel')
        self._orig_detlist = self.client.eval('session.experiment.detlist', [])
        for detname in detectors:
            item = QListWidgetItem(detname, self.detectors)
            item.setFlags(default_flags)
            item.setCheckState(Qt.Checked if detname in self._orig_detlist
                               else Qt.Unchecked)

        # fill environment
        envdevs = self.client.getDeviceList(
            'nicos.core.device.Readable',
            exclude_class='nicos.core.device.Measurable')
        self._orig_envlist = self.client.eval('session.experiment.envlist', [])
        for devname in envdevs:
            item = QListWidgetItem(devname, self.sampleenv)
            item.setFlags(default_flags)
            item.setCheckState(Qt.Checked if devname in self._orig_envlist
                               else Qt.Unchecked)
        if self.client.viewonly:
            self.buttonBox.setStandardButtons(QDialogButtonBox.Close)
        else:
            self.buttonBox.setStandardButtons(QDialogButtonBox.Apply |
                                              QDialogButtonBox.Close)

    @pyqtSlot()
    def on_envHelpBtn_clicked(self):
        self.showInfo('''\
The devices selected as "environment" get special treatment in some places, \
depending on the instrument.

For instruments with scans, they will get their own column in scan tables.

For other instruments, they will get written to the data file where \
sample environment is placed.''')

    def on_buttonBox_clicked(self, button):
        role = self.buttonBox.buttonRole(button)
        if role == QDialogButtonBox.ApplyRole:
            self.applyChanges()
        elif role == QDialogButtonBox.RejectRole:
            self.closeWindow()

    def applyChanges(self):
        done = []

        # detectors
        new_detlist = [item.text() for item in iterChecked(self.detectors)]
        if set(new_detlist) != set(self._orig_detlist):
            self.client.run('SetDetectors(%s)' % ', '.join(new_detlist))
            done.append('New standard detectors applied.')
            self._orig_detlist = new_detlist

        # sample env
        new_envlist = [item.text() for item in iterChecked(self.sampleenv)]
        if set(new_envlist) != set(self._orig_envlist):
            self.client.run('SetEnvironment(%s)' % ', '.join(new_envlist))
            done.append('New standard environment devices applied.')
            self._orig_envlist = new_envlist

        if done:
            self.showInfo('\n'.join(done))


class GenericSamplePanel(Panel):
    """Provides a panel to input the name of the currently used sample."""

    panelName = 'Sample setup'
    uiName = 'panels/setup_sample.ui'

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        loadUi(self, self.uiName)
        for ch in self.findChildren(NicosWidget):
            ch.setClient(self.client)
        if self.client.viewonly:
            self.buttonBox.setStandardButtons(QDialogButtonBox.Close)
        else:
            self.buttonBox.setStandardButtons(QDialogButtonBox.Apply |
                                              QDialogButtonBox.Close)

    def on_buttonBox_clicked(self, button):
        role = self.buttonBox.buttonRole(button)
        if role == QDialogButtonBox.ApplyRole:
            self.applyChanges()
        elif role == QDialogButtonBox.RejectRole:
            self.closeWindow()

    def getEditBoxes(self):
        return [self.samplenameEdit]

    def applyChanges(self):
        params = []
        for edit in self.getEditBoxes():
            if edit.param == 'samplename':
                params.insert(0, '%r' % edit.getValue())
            else:
                params.append('%s=%r' % (edit.param, edit.getValue()))
        code = 'NewSample(%s)\n' % ', '.join(params)
        self.client.run(code.rstrip())
        self.showInfo('Sample parameters changed.')


class TasSamplePanel(GenericSamplePanel):
    """Provides a set of input parameters for a sample used in a TAS setup."""

    panelName = 'TAS sample setup'
    uiName = 'panels/setup_tassample.ui'

    def getEditBoxes(self):
        return [self.samplenameEdit, self.latticeEdit, self.anglesEdit,
                self.orient1Edit, self.orient2Edit, self.psi0Edit,
                self.spacegroupEdit, self.mosaicEdit]


class SXTalSamplePanel(GenericSamplePanel):
    """Provides a set of input parameters for a single crystal sample."""

    panelName = 'Single-crystal sample setup'
    uiName = 'panels/setup_sxtalsample.ui'

    def __init__(self, parent, client, options):
        GenericSamplePanel.__init__(self, parent, client, options)
        params = client.eval('session.experiment.sample.cell.cellparams()',
                             None)
        if params:
            lattice = params[:3]
            angles = params[3:6]
        else:
            lattice = [5] * 3
            angles = [90] * 3
        self.latticeEdit = typedvalue.create(self, vec3, lattice)
        self.angleEdit = typedvalue.create(self, vec3, angles)
        self.gridLayout.addWidget(self.latticeEdit, 2, 1)
        self.gridLayout.addWidget(self.angleEdit, 3, 1)

    def applyChanges(self):
        code = 'NewSample(%r, ' % self.samplenameEdit.getValue()
        code += 'cell=(%r, ' % self.cellEdit.getValue().tolist()
        code += '%r, ' % self.bravaisEdit.getValue()
        code += '%r))' % self.laueEdit.getValue()

        self.client.run(code.rstrip())
        self.showInfo('Sample parameters changed.')

    @pyqtSlot()
    def on_setLattice_clicked(self):
        lattice = self.latticeEdit.getValue()
        angles = self.angleEdit.getValue()
        newcell = SXTalCell.fromabc(*(lattice + angles))
        self.cellEdit._reinit(newcell)

    @pyqtSlot()
    def on_swapHK_clicked(self):
        self._swap(0, 1)

    @pyqtSlot()
    def on_swapHL_clicked(self):
        self._swap(0, 2)

    @pyqtSlot()
    def on_swapKL_clicked(self):
        self._swap(1, 2)

    @pyqtSlot()
    def on_invertH_clicked(self):
        self._invert(0)

    @pyqtSlot()
    def on_invertK_clicked(self):
        self._invert(1)

    @pyqtSlot()
    def on_invertL_clicked(self):
        self._invert(2)

    def _swap(self, j1, j2):
        tbl = self.cellEdit._inner
        for i in range(tbl.rowCount()):
            item1 = tbl.item(i, j1)
            item2 = tbl.item(i, j2)
            tmp = item1.text()
            item1.setText(item2.text())
            item2.setText(tmp)

    def _invert(self, j):
        tbl = self.cellEdit._inner
        for i in range(tbl.rowCount()):
            item = tbl.item(i, j)
            item.setText('%.4g' % -float(item.text()))
