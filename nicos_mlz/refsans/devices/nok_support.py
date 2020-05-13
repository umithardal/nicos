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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# **************************************************************************
"""Support Code for REFSANS's NOK's."""

from __future__ import absolute_import, division, print_function

from nicos.core import ConfigurationError, HasPrecision, Moveable, MoveError, \
    Readable, dictwith, status
from nicos.core.errors import HardwareError
from nicos.core.params import Attach, Override, Param, floatrange, limits, \
    none_or, nonemptylistof, oneof, tupleof
from nicos.core.utils import multiReset
from nicos.devices.abstract import CanReference, Coder
from nicos.devices.generic import Axis
from nicos.devices.generic.sequence import SeqDev, SeqMethod, SequenceItem, \
    SequencerMixin
from nicos.devices.tango import Sensor
from nicos.utils import clamp, lazy_property

from nicos_mlz.refsans.devices.mixins import PseudoNOK

MODES = ['ng', 'rc', 'vc', 'fc']


class NOKMonitoredVoltage(Sensor):
    """Return a scaled and monitored Analogue value.

    Also checks the value to be within certain limits, if not, complain.
    """

    parameters = {
        'reflimits': Param('None or Limits to check the reference: low, warn, '
                           'high',
                           type=none_or(tupleof(float, float, float)),
                           settable=False, default=None),
        'scale': Param('Scaling factor', type=float, settable=False,
                       default=1.),
    }
    parameter_overrides = {
        'unit': Override(default='V', mandatory=False),
    }

    def doInit(self, mode):
        if self.reflimits is not None:
            if not (0 <= self.reflimits[0] <= self.reflimits[1] <=
                    self.reflimits[2]):
                raise ConfigurationError(self, 'reflimits must be in ascending'
                                         ' order!')

    def doRead(self, maxage=0):
        value = self.scale * Sensor.doRead(self, maxage)
        if self.reflimits is not None:
            if abs(value) > self.reflimits[2]:
                raise HardwareError(self, 'Reference voltage (%.2f) above '
                                    'maximum (%.2f)' % (value,
                                                        self.reflimits[2]))
            if abs(value) < self.reflimits[0]:
                raise HardwareError(self, 'Reference voltage (%.2f) below '
                                    'minimum (%.2f)' % (value,
                                                        self.reflimits[0]))
            if abs(value) < self.reflimits[1]:
                self.log.warning('Reference voltage (%.2f) seems rather low, '
                                 'should be above %.2f', value,
                                 self.reflimits[1])
        return value

    def doStatus(self, maxage=0):
        try:
            self.doRead(maxage)
            return Sensor.doStatus(self, maxage)
        except HardwareError as err:
            return status.ERROR, repr(err)


class NOKPosition(Coder):
    """Device to read the current Position of a NOK.

    The Position is determined by a ratiometric measurement between two
    analogue voltages measured with i7000 modules via taco.

    As safety measure, the reference voltage obtained is checked to be in some
    configurable limits.
    """

    attached_devices = {
        'measure': Attach('Sensing Device (Poti)', Readable),
        'reference': Attach('Reference Device', Readable),
    }

    parameters = {
        'poly': Param('Polynomial coefficients in ascending order',
                      type=nonemptylistof(float), settable=True,
                      mandatory=True, default=0.),
        'length': Param('Length... ????',
                        type=float, mandatory=False),
        # fun stuff, not really needed....
        'serial': Param('Serial number',
                        type=int, mandatory=False),
    }

    parameter_overrides = {
        'fmtstr': Override(default='%.3f'),
        'unit': Override(default='mm', mandatory=False),
    }

    def doReset(self):
        multiReset(self._adevs)

    def doRead(self, maxage=0):
        """Read basically two (scaled) voltages.

         - value from the poti (times a sign correction for top mounted potis)
         - ref from a reference voltage, scaled by 2 (Why???)

        Then it calculates the ratio poti / ref.
        Then this is put into a correcting polynom of at least first order
        Result is then offset + mul * <previously calculated value>
        """
        poti = self._attached_measure.read(maxage)
        ref = self._attached_reference.read(maxage)

        self.log.debug('Poti vs. Reference value: %f / %f', poti, ref)

        # apply simple scaling
        value = poti / ref

        self.log.debug('uncorrected value: %f', value)
        result = 0.
        for i, ai in enumerate(self.poly):
            result += ai * (value ** i)
        self.log.debug('final result: %f', result)

        return result


#
# support stuff for the NOK
#

class SeqMoveOffLimitSwitch(SequenceItem):
    """Fancy SequenceItem.

    If the given device is at a limit switch, move it a little, else do nothing
    """

    def __init__(self, dev, *args, **kwargs):
        SequenceItem.__init__(self, dev=dev, args=args, kwargs=kwargs)

    def check(self):
        pass

    def run(self):
        if 'limit switch - active' in self.dev.status(0)[1]:
            # use 0.5 as fallback value
            self.dev.start(self.kwargs.get('backoffby', 0.5))

    def isCompleted(self):
        self.dev.wait()
        return True

    def __repr__(self):
        return 'MoveAwayFromLimitSwitch'


class SeqDevMin(SeqDev):
    """Fancy Sequenceitem.

    Same as SeqDev, but do not go below usermin.
    """

    def __init__(self, dev, target):
        # limit the position to allowed values
        target = clamp(target, dev.usermin, dev.usermax)
        SeqDev.__init__(self, dev, target)


#
# Nicos classes: for NOK's
#

# below code is based upon old nicm_nok.py
class SingleMotorNOK(PseudoNOK, Axis):
    """NOK using a single axis.

    Basically a generic NICOS axis with precision
    """

    parameters = {
        'nok_motor': Param('Position of the motor for this nok', type=float,
                           settable=False, unit='mm', category='general'),
    }


class DoubleMotorNOK(SequencerMixin, CanReference, PseudoNOK, HasPrecision,
                     Moveable):
    """NOK using two axes.

    If backlash is negative, approach form the negative side (default),
    else approach from the positive side.
    If backlash is zero, don't mind and just go to the target.
    """

    attached_devices = {
        'motor_r': Attach('NOK moving motor, reactor side', Moveable),
        'motor_s': Attach('NOK moving motor, sample side', Moveable),
    }

    parameters = {
        'mode': Param('Beam mode',
                      type=oneof(*MODES), settable=True, userparam=True,
                      default='ng', category='experiment'),
        'nok_motor': Param('Position of the motor for this NOK',
                           type=tupleof(float, float), settable=False,
                           unit='mm', category='general'),
        'inclinationlimits': Param('Allowed range for the positional '
                                   'difference',
                                   type=limits, mandatory=True),
        'backlash': Param('Backlash correction in phys. units',
                          type=float, default=0., unit='main'),
        'offsets': Param('Offsets of NOK-Motors (reactor side, sample side)',
                         type=tupleof(float, float), default=(0., 0.),
                         settable=False, unit='main', category='offsets'),
    }

    parameter_overrides = {
        'precision': Override(type=floatrange(0, 100)),
        'masks': Override(type=dictwith(**{name: float for name in MODES}),
                          unit='', mandatory=True),
    }

    valuetype = tupleof(float, float)
    _honor_stop = True

    @lazy_property
    def _devices(self):
        return self._attached_motor_r, self._attached_motor_s

    def doInit(self, mode):
        for dev in self._devices:
            if hasattr(dev, 'backlash') and dev.backlash != 0:
                self.log.warning('Attached Device %s should not have a '
                                 'non-zero backlash!', dev)

    def doRead(self, maxage=0):
        return [dev.read(maxage) - ofs - self.masks[self.mode]
                for dev, ofs in zip(self._devices, self.offsets)]

    def doIsAllowed(self, targets):
        target_r, target_s = targets
        target_r += self.offsets[0]
        target_s += self.offsets[1]

        incmin, incmax = self.inclinationlimits

        inclination = target_s - target_r
        if not incmin <= inclination <= incmax:
            return False, 'Inclination %.2f out of limit (%.2f, %.2f)!' % (
                inclination, incmin, incmax)

        for dev in self._devices:
            res = dev.isAllowed(target_r)
            if not res[0]:
                return res

        # no problems detected, so it should be safe to go there....
        return True, ''

    def doIsAtTarget(self, targets):
        traveldists = [target - (akt + ofs)
                       for target, akt, ofs in zip(targets, self.read(0),
                                                   self.offsets)]
        self.log.debug('doIsAtTarget', targets, 'traveldists', traveldists)
        return max(abs(v) for v in traveldists) <= self.precision

    def doStop(self):
        SequencerMixin.doStop(self)
        for dev in self._devices:
            dev.stop()
        try:
            self.wait()
        finally:
            self.reset()

    def doStart(self, targets):
        """Generate and start a sequence if none is running.

        The sequence is optimised for negative backlash.
        It will first move both motors to the lowest value of
        (target + backlash, current_position) and then
        to the final target.
        So, inbetween, the NOK should be parallel to the beam.
        """
        if self._seq_is_running():
            raise MoveError(self, 'Cannot start device, it is still moving!')

        # check precision, only move if needed!
        if self.isAtTarget(targets):
            return

        devices = self._devices

        # XXX: backlash correction and repositioning later

        # build a moving sequence
        sequence = []

        # now go to target
        sequence.append([SeqDev(d, t + ofs + self.masks[self.mode],
                                stoppable=True)
                         for d, t, ofs in zip(devices, targets, self.offsets)])

        # now go to target again
        sequence.append([SeqDev(d, t + ofs + self.masks[self.mode],
                                stoppable=True)
                         for d, t, ofs in zip(devices, targets, self.offsets)])

        self.log.debug('Seq: %r', sequence)
        self._startSequence(sequence)

    def doReset(self):
        multiReset(self._motors)


class DoubleMotorNOKIPC(DoubleMotorNOK):

    def doReference(self):
        """Reference the NOK in a sophisticated way.

        First we try to reach the lowest point ever needed for referencing,
        then we reference the lower refpoint first, and the higher later.
        After referencing is done, we go to (0, 0).
        """
        # XXX: EXTRA BIG TODO !!!
        if self._seq_is_running():
            raise MoveError(self, 'Cannot reference device, it is still '
                            'moving!')

        devices = self._devices
        refpos = [d.refpos for d in devices]

        # referencing is easier if device[0].refpos is always lower than
        #  device[1].refpos
        if refpos[1] < refpos[0]:
            # wrong order: flip oder of entries
            devices.reverse()
            refpos.reverse()

        # go below lowest interesting point
        minpos = min(self.read() + refpos + [t + self.backlash
                                             for t in refpos])

        # build a referencing sequence
        sequence = []

        # go to lowest position first
        sequence.append([SeqDevMin(d, minpos) for d in devices])

        # if one of the motors should have triggered the low-level-switch
        # move them up a little and wait until the movement has finished
        sequence.append([SeqMoveOffLimitSwitch(d, backoffby=self.backlash / 4.)
                         for d in devices])

        # ref lowest position, should finish at refpos[0]
        # The move should be first, as the referencing may block!
        sequence.append([SeqDev(devices[1], refpos[0]),
                         SeqMethod(devices[0], 'reference')])

        # ref highest position, should finish at refpos[1]
        sequence.append([SeqDev(devices[0], refpos[1]),
                         SeqMethod(devices[1], 'reference')])

        # fun: move both to 0
        sequence.append([SeqDev(d, 0) for d in devices])

        # GO
        self._startSequence(sequence)


class DoubleMotorNOKBeckhoff(DoubleMotorNOK):

    def doReference(self):
        """Reference the NOK.

        Just set the do_reference bit and wait for completion
        """
        if self._seq_is_running():
            raise MoveError(self, 'Cannot reference device, it is still '
                            'moving!')

        # according to docu it is sufficient to set the ref bit of one of the
        # coupled motors
        for dev in self._devices:
            dev._HW_reference()

        for dev in self._devices:
            dev.wait()

    def doStart(self, targets):
        """Generate and start a sequence if none is running.

        The sequence is optimised for negative backlash.
        It will first move both motors to the lowest value of
        (target + backlash, current_position) and then
        to the final target.
        So, inbetween, the NOK should be parallel to the beam.
        MP 12.12.2017 09:16:05
        """
        if self._seq_is_running():
            raise MoveError(self, 'Cannot start device, it is still moving!')

        # check precision, only move if needed!
        traveldists = [target - dev.read(0) - ofs
                       for target, dev, ofs in zip(targets, self._devices,
                                                   self.offsets)]
        if max(abs(v) for v in traveldists) <= self.precision:
            return

        devices = self._devices

        # XXX: backlash correction and repositioning later

        # build a moving sequence
        sequence = []

        # now go to target
        sequence.append([SeqDev(d, t + ofs, stoppable=True)
                         for d, t, ofs in zip(devices, targets, self.offsets)])

        # now go to target again
        sequence.append([SeqDev(d, t + ofs, stoppable=True)
                         for d, t, ofs in zip(devices, targets, self.offsets)])

        self.log.debug('Seq: %r', sequence)
        self._startSequence(sequence)


class MotorEncoderDifference(Readable):

    attached_devices = {
        'motor': Attach('moving motor', Moveable),
        'analog': Attach('analog encoder maybe poti', Readable),
    }

    def doRead(self, maxage=0):
        return abs(self._attached_analog.read(maxage) -
                   self._attached_motor.read(maxage))

    def doStatus(self, maxage=0):
        return status.OK, ''
