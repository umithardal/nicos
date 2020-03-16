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
#   Georg Brandl <g.brandl@fz-juelich.de>
#   Michael Wedel <michael.wedel@esss.se>
#
# *****************************************************************************

"""
This module contains some classes for NICOS - EPICS integration. The underlying module
for handling EPICS communication is pvaPy.
"""

from __future__ import absolute_import, division, print_function

from time import time as currenttime
import numpy as np

from nicos import session
from nicos.commands import helparglist, hiddenusercommand
from nicos.core import POLLER, SIMULATION, CommunicationError, \
    ConfigurationError, DeviceMixinBase, HasLimits, Moveable, Override, \
    Param, Readable, anytype, floatrange, none_or, pvname, status
from nicos.core.mixins import HasWindowTimeout
from nicos.devices.epics import SEVERITY_TO_STATUS, STAT_TO_STATUS
from nicos.utils import HardwareStub

try:
    import pvaccess

    FTYPE_TO_VALUETYPE = {
        pvaccess.ScalarType.DOUBLE: float,
        pvaccess.ScalarType.INT: int,
        pvaccess.ScalarType.STRING: str,
    }
except ImportError:
    pvaccess = None

    FTYPE_TO_VALUETYPE = {}

__all__ = [
    'EpicsDevice', 'EpicsReadable', 'EpicsStringReadable',
    'EpicsMoveable','EpicsAnalogMoveable', 'EpicsDigitalMoveable',
    'EpicsWindowTimeoutDevice',
]


@hiddenusercommand
@helparglist('name[, as_string, use_ca]')
def pvget(name, as_string=False, use_ca=True):
    channel = pvaccess.Channel(name, pvaccess.CA if use_ca else pvaccess.PVA)
    return _pvget(channel, as_string=as_string)


@hiddenusercommand
@helparglist('name, value[, use_ca]')
def pvput(name, value, use_ca=True):
    pvaccess.Channel(name, pvaccess.CA if use_ca else pvaccess.PVA).put(value)


def _convert_chars_to_str(char_array):
    firstnull = char_array.index(0) if 0 in char_array else len(char_array)
    try:
        cval = ''.join([chr(i) for i in char_array[:firstnull]]).rstrip()
    except ValueError:
        cval = ''
    return cval


def _pvget(channel, field='value', as_string=False):
    try:
        result = channel.get(field).getPyObject()
    except pvaccess.PvaException:
        return None

    if as_string:
        if (isinstance(result, dict) and
                {'index', 'choices'}.issubset(set(result))):
            # convert (most probably) enum to string
            return result.get('choices')[result.get('index')]
        elif isinstance(result, list):
            return _convert_chars_to_str(result)
        elif isinstance(result, np.ndarray):
            return _convert_chars_to_str(result.tolist())
    # For ENUMs do not return the dict but just the index
    if isinstance(result, dict) and 'index' in result:
        return result['index']
    return result


class EpicsDevice(DeviceMixinBase):
    """
    Basic EPICS device.
    """

    hardware_access = True
    valuetype = anytype

    parameters = {
        'epicstimeout': Param('Timeout for getting EPICS PVs',
                              type=none_or(floatrange(0.1, 60)),
                              default=1.0),
        'usepva': Param('If true, PVAcess is used instead of ChannelAccess',
                        type=bool, default=False, preinit=True)
    }

    # A set of all parameters that indicate PV names.  Since PVs are very
    # limited, an EpicsDevice is expected to use many different PVs a lot
    # of times.
    pv_parameters = set()

    pv_cache_relations = {}

    # This will store PV objects for each PV param.
    _pvs = {}
    _pvctrls = {}

    def doPreinit(self, mode):
        # Don't create PVs in simulation mode
        self._pvs = {}
        self._pvctrls = {}

        if mode != SIMULATION:
            # When there are standard names for PVs (see motor record), the PV names
            # may be derived from some prefix. To make this more flexible, the pv_parameters
            # are obtained via a method that can be overridden in subclasses.
            pv_parameters = self._get_pv_parameters()

            # For cases where for example readpv and writepv are the same, this dict makes
            # sure that only one Channel object is created per PV.
            pv_names = {}

            for pvparam in pv_parameters:
                # Retrieve the actual PV-name from (potentially overridden) method
                pv_name = self._get_pv_name(pvparam)

                try:
                    pv = pv_names.setdefault(pv_name, self._create_pv(pv_name))
                    self._pvs[pvparam] = pv

                    pv.setTimeout(self.epicstimeout)

                    self._pvctrls[pvparam] = pv.get('display').toDict().get('display')
                    if self._pvctrls[pvparam] is None:
                        self._pvctrls[pvparam] = pv.get('control').toDict().get('control', {})

                except pvaccess.PvaException:
                    raise CommunicationError(self, 'could not connect to PV %r'
                                             % pv_name)
        else:
            for pvparam in self._get_pv_parameters():
                self._pvs[pvparam] = HardwareStub(self)
                self._pvctrls[pvparam] = {}

    def doInit(self, mode):
        if mode != SIMULATION:
            self._register_pv_callbacks()

    def _create_pv(self, pv_name):
        return pvaccess.Channel(pv_name, pvaccess.PVA if self.usepva else pvaccess.CA)

    def _get_pv_parameters(self):
        # The default implementation of this method simply returns the pv_parameters set
        return self.pv_parameters

    def _get_pv_name(self, pvparam):
        # In the default case, the name of a PV-parameter is stored in a parameter.
        # This method can be overridden in subclasses in case the name can be derived
        # using some other information.
        return getattr(self, pvparam)

    def doStatus(self, maxage=0):
        return status.OK, ''

    def _setMode(self, mode):
        super(EpicsDevice, self)._setMode(mode)
        # remove the PVs on entering simulation mode, to prevent
        # accidental access to the hardware
        if mode == SIMULATION:
            for key in self._pvs:
                self._pvs[key] = HardwareStub(self)

    def _get_pv(self, pvparam, field='value', as_string=False):
        """
        Uses pvaccess to obtain a field from a PV. The default field is value,
        so that

            val = self._get_pv('readpv')

        retrieves the value of the PV. To obtain alarm or other status information,
        the field parameter can be specified:

            alarm = self._get_pv('readpv', field='alarm')

        Args:
            pvparam: The PV parameter to be queried. Is translated to a PV name internally.
            field: Field of the PV to obtain, default is value.

        Returns: Value of the queried PV field.
        """
        # result = self._pvs[pvparam].get(field).toDict().get(field)
        result = _pvget(self._pvs[pvparam], field, as_string)

        if result is None:  # timeout or channel not connected
            raise CommunicationError(self, 'timed out getting PV %r from EPICS'
                                     % self._get_pv_name(pvparam))

        return result

    def _get_pvctrl(self, pvparam, ctrl, default=None, update=False):
        if update:
            self._pvctrls[pvparam] = self._pvs[pvparam].get('display').toDict().get('display')
            if self._pvctrls[pvparam] is None:
                self._pvctrls[pvparam] = self._pvs[pvparam].get('control').toDict().get(
                    'control', {})
        return self._pvctrls[pvparam].get(ctrl, default)

    def _get_pv_datatype(self, pvparam):
        pv_data = self._pvs[pvparam].get().getStructureDict()['value']
        if not isinstance(pv_data, list):
            return FTYPE_TO_VALUETYPE.get(pv_data, anytype)
        else:
            return [FTYPE_TO_VALUETYPE.get(dt, anytype) for dt in pv_data]

    def _put_pv(self, pvparam, value, wait=True):
        self._pvs[pvparam].put(value)

    def _put_pv_blocking(self, pvparam, value, update_rate=0.1):
        # TODO: figure out why putGet segfaults
        self._put_pv(pvparam, value)

    def _register_pv_callbacks(self):
        """
        If this is a poller session, monitor the PVs specified in the
        ``pv_cache_relations`` member for updates and put the values
        into the cache. This happens in addition to polling, but makes sure that
        values get inserted into the cache immediately when they are available.

        This example would map the value of readpv to the ``value`` of the device:

            pv_cache_relations = {
                'readpv': 'value',
            }

        This method has to be called explicitly in ``doInit``, should it be re-implemented.
        """
        if session.sessiontype == POLLER:
            for pvparam in self._get_pv_parameters():
                corresponding_cache_key = self.pv_cache_relations.get(pvparam)
                if corresponding_cache_key is not None:
                    self._register_pv_update_callback(pvparam, corresponding_cache_key)

    def _register_pv_update_callback(self, pvparam, cache_key, pv_field='value'):
        """
        Subscribes to a PV monitor that updates the cache whenever the PV is updated
        via ChannelAccess.

        Args:
            pvparam: The pvparam to subscribe to, for example readpv or writepv
            cache_key: The cache key that corresponds to the PV's value
            pv_field: Field of the PV to obtain, default is value.

        """
        self.log.info('Registering callback for %s (PV: %s)', pvparam,
                      self._get_pv_name(pvparam))

        def update_callback(pv_object, obj=self, key=cache_key):
            if isinstance(obj, Readable):
                if key == 'value' or key == 'status':
                    ret = obj.poll()
                    ct = currenttime()
                    obj._cache.put(self, 'status', ret[0], ct, self.maxage)
                    obj._cache.put(self, 'value', ret[1], ct, self.maxage)
                else:
                    obj._pollParam(key)

        pv = self._pvs[pvparam]
        pv.setMonitorMaxQueueLength(10)
        pv.subscribe('_'.join((self.name, pvparam, cache_key, 'poller')), update_callback)

        #if not pv.isMonitorActive():
        pv.startMonitor('')

    def _get_mapped_epics_status(self):
        # Checks the status and severity of all the associated PVs.
        # Returns the worst status (error prone first) and
        # a list of all associated pvs having that error
        status_map = {}
        for name in self._pvs:
            epics_status = self._get_pvctrl(name, 'status', update=True)
            epics_severity = self._get_pvctrl(name, 'severity')

            mapped_status = STAT_TO_STATUS.get(epics_status, None)

            if mapped_status is None:
                mapped_status = SEVERITY_TO_STATUS.get(
                    epics_severity, status.UNKNOWN)

            status_map.setdefault(mapped_status, []).append(
                self._get_pv_name(name))

        return max(status_map.items())


class EpicsReadable(EpicsDevice, Readable):
    """
    Handles EPICS devices that can only read a value.
    """

    parameters = {
        'readpv': Param('PV for reading device value',
                        type=pvname, mandatory=True, preinit=True),
    }

    pv_parameters = {'readpv'}

    pv_cache_relations = {
        'readpv': 'value',
    }

    parameter_overrides = {
        'unit': Override(mandatory=False),
    }

    def doInit(self, mode):
        if mode != SIMULATION:
            self.valuetype = self._get_pv_datatype('readpv')
            self._register_pv_callbacks()

    def doReadUnit(self):
        pvunit = self._get_pvctrl('readpv', 'units', '')
        if not pvunit and 'unit' in self._config:
            return self._config['unit']
        return pvunit

    def doRead(self, maxage=0):
        return self._get_pv('readpv')


class EpicsStringReadable(EpicsReadable):
    """
    This device handles string PVs, also when they are implemented as
    character waveforms.
    """
    valuetype = str

    def doRead(self, maxage=0):
        return self._get_pv('readpv', as_string=True)


class EpicsMoveable(EpicsDevice, Moveable):
    """
    Handles EPICS devices which can set and read a value.
    """

    parameters = {
        'readpv': Param('PV for reading device value',
                        type=pvname, mandatory=True, preinit=True),
        'writepv': Param('PV for writing device target',
                         type=pvname, mandatory=True, preinit=True),
        'targetpv': Param('Optional target readback PV.',
                          type=none_or(pvname), mandatory=False, preinit=True)
    }

    parameter_overrides = {
        'unit': Override(mandatory=False),
        'target': Override(volatile=True),
    }

    pv_parameters = {'readpv', 'writepv'}

    pv_cache_relations = {
        'readpv': 'value',
        'targetpv': 'target',
    }

    def _get_pv_parameters(self):
        """
        Overriden from EpicsDevice. If the targetpv parameter is specified,
        the PV-object should be created accordingly. Otherwise, just return
        the mandatory pv_parameters.
        """
        if self.targetpv:
            return self.pv_parameters | {'targetpv'}

        return self.pv_parameters

    def doInit(self, mode):
        if mode == SIMULATION:
            return
        intype = self._get_pv_datatype('readpv')
        outtype = self._get_pv_datatype('writepv')
        if intype != self.valuetype:
            raise ConfigurationError(self, 'Input PV %r does not have the '
                                           'correct data type' % self.readpv)
        if outtype != self.valuetype:
            raise ConfigurationError(self, 'Output PV %r does not have the '
                                           'correct data type' % self.writepv)

        if self.targetpv:
            target_type = self._get_pv_datatype('targetpv')

            if target_type != self.valuetype:
                raise ConfigurationError(
                    self, 'Target PV %r does not have the '
                          'correct data type' % self.targetpv)

        self._register_pv_callbacks()

    def doReadUnit(self):
        return self._get_pvctrl('readpv', 'units', '')

    def doReadTarget(self):
        """
        In many cases IOCs provide a readback of the setpoint, here represented
        as targetpv. Since this is not provided everywhere, it should still be
        possible to get the target.
        """
        if self.targetpv:
            return self._get_pv('targetpv')

        value = self._params.get('target')
        return value if value is not None else self._config.get('target')

    def doRead(self, maxage=0):
        return self._get_pv('readpv')

    def doStart(self, value):
        self._put_pv('writepv', value)

    def doStop(self):
        self.doStart(self.doRead())


class EpicsStringMoveable(EpicsMoveable):
    """
    This device handles string PVs, also when they are implemented as
    character waveforms.
    """
    valuetype = str

    def doRead(self, maxage=0):
        return self._get_pv('readpv', as_string=True)


class EpicsAnalogMoveable(HasLimits, EpicsMoveable):
    """
    Handles EPICS devices which can set and read a floating value.
    """

    valuetype = float

    parameter_overrides = {
        'abslimits': Override(mandatory=False),
    }

    def doReadAbslimits(self):
        absmin = self._get_pvctrl('writepv', 'limitLow', -1e308)
        absmax = self._get_pvctrl('writepv', 'limitHigh', 1e308)
        return (absmin, absmax)


class EpicsWindowTimeoutDevice(HasWindowTimeout, EpicsAnalogMoveable):
    """
    Analog moveable with window timeout.
    """
    pass


class EpicsDigitalMoveable(EpicsMoveable):
    """
    Handles EPICS devices which can set and read an integer value.
    """
    valuetype = int
