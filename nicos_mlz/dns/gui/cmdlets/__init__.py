#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2019 by the NICOS contributors (see AUTHORS)
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
#   Thomas Mueller <t.mueller@fz-juelich.de>
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""NICOS GUI cmdlets for DNS."""

from __future__ import absolute_import, division, print_function

from nicos.clients.gui.cmdlets import Cmdlet, register
from nicos.utils import findResource


class DNSScan(Cmdlet):
    name = ''
    category = ''
    uiName = ''

    def __init__(self, parent, client):
        Cmdlet.__init__(self, parent, client, self.uiName)
        for spin in [self.bankpositions, self.lowest_2theta, self.MonpMin,
                     self.SF, self.NSF]:
            spin.valueChanged.connect(self.changed)
        for box in [self.RB_time, self.RB_monitor, self.RB_min_per_mon,
                    self.open_before, self.close_after]:
            box.toggled.connect(self.changed)

        self.off.stateChanged.connect(self.disablexyz)
        self.RB_min_per_mon.toggled.connect(self.disable_mpm)
        self.XYZ.clicked.connect(self.checkXYZ)
        self.deselect.clicked.connect(self.uncheckfields)
        self._allfields = [
            self.XSF, self.XNSF, self.YSF, self.YNSF, self.ZSF,
            self.ZNSF, self.Zero_SF, self.Zero_SF, self.off,
        ]
        for field in self._allfields:
            field.stateChanged.connect(self.check_which_times)
        self.MonpMin.setDisabled(True)
        self.SF.setDisabled(True)
        lowest_2theta = self.client.getDeviceValue('det_rot')
        omega_start = self.client.getDeviceValue('sample_rot')
        if lowest_2theta is not None:  # just if you are not connected
            self.lowest_2theta.setValue(lowest_2theta)
        else:
            self.lowest_2theta.setValue(-5)
        if omega_start is not None:
            self.omega_start.setValue(omega_start)
        else:
            self.omega_start.setValue(100)
        # this should probably be read somehow from the configuration of
        # abslimits but I have no idea how to get them directly
        self.lowest_2theta.setMinimum(-20)
        self.lowest_2theta.setMaximum(-4)
        self.omega_start.setMinimum(2.5)
        self.omega_start.setMaximum(352)

    def disable_mpm(self):
        self.MonpMin.setEnabled(self.RB_min_per_mon.isChecked())

    def check_which_times(self):
        sf_state = self.XSF.isChecked() or \
            self.YSF.isChecked() or \
            self.ZSF.isChecked() or \
            self.Zero_SF.isChecked() or \
            self.Zero_SF.isChecked()

        if (self.off.isChecked() or
                self.XNSF.isChecked() or
                self.YNSF.isChecked() or
                self.ZNSF.isChecked() or
                self.Zero_NSF.isChecked()):
            nsf_state = True
        elif (not self.XSF.isChecked() and
              not self.YSF.isChecked() and
              not self.ZSF.isChecked() and
              not self.Zero_SF.isChecked() and
              not self.Zero_SF.isChecked()):
            nsf_state = True   # nothing checked
        else:
            nsf_state = False  # only SF
        self.SF.setEnabled(sf_state)
        self.NSF.setEnabled(nsf_state)
        self.changed()

    def uncheckfields(self):
        for fieldbox in self._allfields:
            fieldbox.setChecked(False)

    def checkXYZ(self):
        self.uncheckfields()
        for fieldbox in [self.XSF, self.XNSF, self.YSF, self.YNSF, self.ZSF,
                         self.ZNSF]:
            fieldbox.setChecked(True)

    def disablexyz(self, state):
        for fieldbox in self._allfields:
            if fieldbox == self.off:
                continue
            fieldbox.setChecked(False)
            fieldbox.setDisabled(state)

    def getValues(self):
        if self.RB_time.isChecked():
            norm = 't'
        else:
            norm = 'mon1'
        return {
            'off': self.off.isChecked(),
            'zero_sf': self.Zero_SF.isChecked(),
            'zero_nsf': self.Zero_NSF.isChecked(),
            'x_sf': self.XSF.isChecked(),
            'x_nsf': self.XNSF.isChecked(),
            'y_sf': self.YSF.isChecked(),
            'y_nsf': self.YNSF.isChecked(),
            'z_sf': self.ZSF.isChecked(),
            'z_nsf': self.ZNSF.isChecked(),
            'time': self.RB_time.isChecked(),
            'monitor': self.RB_monitor.isChecked(),
            'min_per_mon': self.RB_min_per_mon.isChecked(),
            'bankpositions': self.bankpositions.value(),
            'lowest_2theta': self.lowest_2theta.value(),
            'omega_start': self.omega_start.value(),
            'MonpMin': self.MonpMin.value(),
            'SF': self.SF.value(),
            'NSF': self.NSF.value(),
            'norm': norm,
            'open_before': self.open_before.isChecked(),
            'close_after': self.close_after.isChecked(),
        }

    def isValid(self):
        limit_det_rot = self.client.getDeviceParam('det_rot', 'userlimits')
        limit_sample_rot = self.client.getDeviceParam('sample_rot',
                                                      'userlimits')
        if limit_det_rot is None:  # not connected
            limit_det_rot = [-20, -4]
            limit_sample_rot = [2.5, 352]
        if self.RB_min_per_mon.isChecked():
            MonpMin_valid = self.markValid(self.MonpMin,
                                           self.MonpMin.value() > 0)
        else:
            MonpMin_valid = True
        # tta is the deviation of 2theta for the last bank position
        tta = 5 - 5 / self.bankpositions.value()
        theta_valid = self.markValid(
            self.lowest_2theta,
            limit_det_rot[0] + tta <= self.lowest_2theta.value()
            <= limit_det_rot[1])
        omega_valid = self.markValid(
            self.omega_start,
            limit_sample_rot[0] + tta <= self.omega_start.value()
            <= limit_sample_rot[1])
        if self.SF.isEnabled():
            sf_valid = self.markValid(self.SF, self.SF.value() > 0)
        else:
            sf_valid = 1
        if self.NSF.isEnabled():
            nsf_valid = self.markValid(self.NSF, self.NSF.value() > 0)
        else:
            nsf_valid = 1
        valid = [
            theta_valid,
            omega_valid,
            sf_valid,
            nsf_valid,
            MonpMin_valid,
        ]
        return all(valid)

    def pregenerate(self, mode):
        values = self.getValues()
        active_fields = []
        command = ''
        mpm_string = ''
        if values['open_before']:
            command += "maw(expshutter, 'open')\n"
        if values['min_per_mon']:
            mpm_string = '*mpm'
            command += 'mpm={}\n'.format(values['MonpMin'])
        # check the theta angle and choose corresponding field values
        if values['lowest_2theta'] <= -15:
            ang = '20'
        else:
            ang = '7'
        # this must be list since order is important for dnsplot
        for field in ['x_sf', 'x_nsf', 'y_sf', 'y_nsf', 'z_sf',
                      'z_nsf', 'zero_sf', 'zero_nsf', 'off']:
            if values[field]:
                active_fields.append(field)
        if not active_fields:
            fieldstring = ''
        else:
            fieldstring = ("field=['{}'], ".format("', '".join(active_fields)))
            fieldstring = fieldstring.replace('x_', 'x{}_'.format(ang))
            fieldstring = fieldstring.replace('y_', 'y{}_'.format(ang))
            fieldstring = fieldstring.replace('z_', 'z{}_'.format(ang))
        # calculate increments from number of bank positions
        if (values['bankpositions']) == 1:
            increment = 0
        else:
            increment = -5.0 / values['bankpositions']

        # if only SF or only NSF or empty list, use t= instead of both
        sf_state = '_sf' in fieldstring
        nsf_state = '_nsf' in fieldstring
        timestring = '{}sf={}{}, {}nsf={}{}'.format(values['norm'],
                                                    values['SF'],
                                                    mpm_string,
                                                    values['norm'],
                                                    values['NSF'],
                                                    mpm_string)
        if ("'off'" in active_fields or
                not active_fields or
                (nsf_state and not sf_state)):
            timestring = '{}={}{}'.format(values['norm'], values['NSF'],
                                          mpm_string)
        if (sf_state and not nsf_state):
            timestring = '{}={}{}'.format(values['norm'], values['SF'],
                                          mpm_string)
        return command, values, increment, fieldstring, timestring


class PowderScan(DNSScan):
    name = 'Powder Scan'
    category = 'DNS'
    uiName = findResource('nicos_mlz/dns/gui/cmdlets/powder_scan.ui')

    def __init__(self, parent, client):
        DNSScan.__init__(self, parent, client)
        self.omega_start.valueChanged.connect(self.changed)

    def isValid(self):
        common_valid = DNSScan.isValid(self)
        limit_det_rot = self.client.getDeviceParam('det_rot', 'userlimits')
        limit_sample_rot = self.client.getDeviceParam('sample_rot',
                                                      'userlimits')
        if limit_det_rot is None:
            limit_det_rot = [-20, -4]
            limit_sample_rot = [2.5, 352]
        tta = 5 - 5 / self.bankpositions.value()
        omega_valid = self.markValid(
            self.omega_start,
            limit_sample_rot[0] + tta <= self.omega_start.value()
            <= limit_sample_rot[1])
        valid = [
            common_valid,
            omega_valid,
        ]
        return all(valid)

    def generate(self, mode):
        command, values, increment, fieldstring, timestring = \
            self.pregenerate(mode)
        command += ('scan([det_rot, sample_rot], '
                    '[{}, {}], [{}, {}], {}, {}{})').format(
                        values['lowest_2theta'],
                        values['omega_start'],
                        increment,
                        increment,
                        values['bankpositions'],
                        fieldstring,
                        timestring)
        if values['close_after']:
            command += "\nmaw(expshutter, 'closed')"
        return command


class SingleCrystalScan(DNSScan):
    name = 'Single Crystal'
    category = 'DNS'
    uiName = findResource('nicos_mlz/dns/gui/cmdlets/sc_scan.ui')

    def __init__(self, parent, client):
        DNSScan. __init__(self, parent, client)
        self.update_omega_end()
        self.omega_step.valueChanged.connect(self.update_omega_end)
        self.omega_start.valueChanged.connect(self.update_omega_end)
        self.omega_nos.valueChanged.connect(self.update_omega_end)

    def update_omega_end(self):
        self.omega_end.setText('{:.3f}'.format(self.omega_start.value()
                                               + self.omega_step.value()
                                               * self.omega_nos.value()))
        self.changed()

    def getValues(self):
        dic_all = DNSScan.getValues(self)
        dic_all.update({
            'omega_step': self.omega_step.value(),
            'omega_nos': self.omega_nos.value(),
        })
        return dic_all

    def isValid(self):
        common_valid = DNSScan.isValid(self)
        limit_det_rot = self.client.getDeviceParam('det_rot', 'userlimits')
        limit_sample_rot = self.client.getDeviceParam('sample_rot',
                                                      'userlimits')
        if limit_det_rot is None:
            limit_det_rot = [-20, -4]
            limit_sample_rot = [2.5, 352]
        tta = 5. - 5. / self.bankpositions.value()
        omega_end_valid = (limit_sample_rot[0] + tta <= float(self.omega_end.text())
                           <= limit_sample_rot[1])
        self.markValid(self.omega_end, omega_end_valid)
        valid = [
            common_valid,
            omega_end_valid,
        ]
        return all(valid)

    def generate(self, mode):
        command, values, increment, fieldstring, timestring = \
            self.pregenerate(mode)
        values = self.getValues()

        for i in range(values['bankpositions']):
            if (values['bankpositions'] > 1 and
                    i != values['bankpositions'] - 1):
                linebreak = '\n'
            else:
                linebreak = ''
            command += (
                'scan([det_rot, sample_rot], '
                '[{:8.3f}, {:8.3f}], [0, {}], {}, {}{}){}').format(
                    values['lowest_2theta'] + increment*i,
                    values['omega_start'] + increment*i,
                    values['omega_step'],
                    values['omega_nos'],
                    fieldstring,
                    timestring,
                    linebreak)
        if values['close_after']:
            command += "\nmaw(expshutter, 'closed')"
        return command


class Shutter(Cmdlet):
    name = 'Shutter'
    category = 'DNS'

    def __init__(self, parent, client):
        Cmdlet.__init__(self, parent, client,
                        findResource('nicos_mlz/dns/gui/cmdlets/shutter.ui'))
        self.shutter.currentIndexChanged.connect(self.changed)

    def getValues(self):
        return {'shutter': self.shutter.currentText()}

    def generate(self, mode):
        if mode == 'simple':
            return "maw expshutter '{}'".format(self.getValues()['shutter'])
        return "maw(expshutter, '{}')".format(self.getValues()['shutter'])


class SetTemperature(Cmdlet):
    name = 'Set Temperature'
    category = 'DNS'

    def __init__(self, parent, client):
        Cmdlet.__init__(self, parent, client,
                        findResource('nicos_mlz/dns/gui/cmdlets/temperature.ui'))
        self.temperature.valueChanged.connect(self.changed)
        self.waitfor.toggled.connect(self.changed)

    def getValues(self):
        if self.waitfor.isChecked():
            command = 'maw'
        else:
            command = 'move'
        return {
            'temperature': self.temperature.value(),
            'command': command,
        }

    def generate(self, mode):
        values = self.getValues()
        if mode == 'simple':
            return '{} T {}'.format(values['command'], values['temperature'])
        return '{}(T, {})'.format(values['command'], values['temperature'])


register(Shutter)
register(SetTemperature)
register(PowderScan)
register(SingleCrystalScan)
