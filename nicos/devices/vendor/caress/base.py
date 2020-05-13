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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""Devices via the CARESS device service."""

from __future__ import absolute_import, division, print_function

from nicos import session
from nicos.core import POLLER, SIMULATION, HasLimits, HasPrecision, Moveable, \
    Param
from nicos.core.errors import ConfigurationError, NicosError
from nicos.devices.vendor.caress.core import ACTIVE, ACTIVE1, CARESS, \
    CHTYPE_INT32, CORBA, CORBA_DEVICE, DEVICE_DRIVABLE, DEVICE_READABLE, \
    KEEP_ACTION, READBLOCK_NORMAL, CARESSDevice


class Driveable(HasLimits, HasPrecision, CARESSDevice, Moveable):
    """Base class to all CARESS driveable devices."""

    hardware_access = True

    parameters = {
        '_started': Param('Indicator to signal device is started',
                          type=bool, default=False, settable=False,
                          ),
    }

    def doInit(self, mode):
        CARESSDevice.doInit(self, mode)
        if session.sessiontype == POLLER or mode == SIMULATION:
            return

        self._setROParam('_started', False)
        is_readable = True
        if hasattr(self._caressObject, 'is_readable_module'):
            is_readable = self._caress_guard(
                self._caressObject.is_readable_module, self.cid)

        if hasattr(self._caressObject, 'is_drivable_module'):
            is_drivable = self._caress_guard(
                self._caressObject.is_drivable_module, self.cid)
        elif self._device_kind() in [CORBA_DEVICE, 501]:
            # 500, 501 devices may be any combination of readable or drivable
            # Query capabilities from server
            (ret, _, _, chtype) = self._caress_guard(
                self._caressObject.readblock_params_orb, -0x80000000,
                self.cid, 1, 0, 0)
            if ret != READBLOCK_NORMAL or chtype != CHTYPE_INT32:
                # Something went wrong, assume no capabilities
                is_readable = False
                is_drivable = False
            else:
                (ret, _, dataseq) = self._caress_guard(
                    self._caressObject.int_readblock_module_orb, -0x80000000,
                    self.cid, 1, 1, ())
                if ret != READBLOCK_NORMAL or len(dataseq) != 1:
                    # Something went wrong, assume no capabilities
                    is_readable = False
                    is_drivable = False
                else:
                    is_readable = bool(dataseq[0] & DEVICE_READABLE)
                    is_drivable = bool(dataseq[0] & DEVICE_DRIVABLE)
                    # readable, drivable, counting, status, needs_reference,
                    # new_interface
        else:
            is_drivable = self._device_kind() in [3, 7, 13, 14, 15, 23, 24, 25,
                                                  28, 29, 30, 31, 32, 33, 37,
                                                  39, 40, 41, 43, 44, 45, 49,
                                                  50, 51, 53, 54, 56, 62, 67,
                                                  68, 70, 71, 72, 73, 76, 100,
                                                  103, 105, 106, 107, 108, 110,
                                                  111, 112, 114, 115, 123, 124,
                                                  125, 126]

        self.log.debug('readable module: %r', is_readable)
        self.log.debug('driveable module: %r', is_drivable)
        if not (is_drivable or is_readable):
            raise ConfigurationError(self, 'Object is not a moveable module')

    def doStart(self, target):
        self.log.debug('target: %r', target)
        timeout = 0
        if hasattr(self._caressObject, 'drive_module'):
            val = CARESS.Value(f=target)
            self.log.debug('%r', val.f)
            result = self._caress_guard(self._caressObject.drive_module, 0,
                                        self.cid, val, timeout)
            if result[0] != CARESS.OK:
                raise NicosError(self, 'Could not start the device')
        else:
            params = []
            params.append(CORBA.Any(CORBA._tc_long, self.cid))
            params.append(CORBA.Any(CORBA._tc_long, 0))  # status placeholder
            params.append(CORBA.Any(CORBA._tc_long, 2))  # 2 values
            params.append(CORBA.Any(CORBA._tc_long, 5))  # type 32 bit float
            params.append(CORBA.Any(CORBA._tc_float, target))
            params.append(CORBA.Any(CORBA._tc_float, self.precision))
            params.append(CORBA.Any(CORBA._tc_long, 0))  # no next module
            result = self._caress_guard(self._caressObject.drive_module_orb, 0,
                                        params, 0, timeout)
            if result[0] != 0:
                raise NicosError(self, 'Could not start the device')
        self._setROParam('_started', True)

    def doStatus(self, maxage=0):
        return CARESSDevice.doStatus(self, maxage)

    def _stop(self, stopmode=KEEP_ACTION):
        self.log.debug('stop: StopMode : %d', stopmode)
        if hasattr(self._caressObject, 'stop_module'):
            result = self._caress_guard(self._caressObject.stop_module, stopmode,
                                        self.cid)
            if result in [(CARESS.OK, ACTIVE), (CARESS.OK, ACTIVE1)]:
                raise NicosError(self, 'Could not stop the module')
        else:
            result = self._caress_guard(self._caressObject.stop_module_orb,
                                        stopmode, self.cid)
            if result in [(0, ACTIVE), (0, ACTIVE1)]:
                raise NicosError(self, 'Could not stop the module')

    def doStop(self):
        self._stop()
