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
# *****************************************************************************

"""Devices for the Refsans VSD."""

from __future__ import absolute_import, division, print_function

import struct

from nicos.core import SIMULATION, Attach, Override, Param, Readable, dictof, \
    oneof, requires, status, usermethod
from nicos.devices.tango import PyTangoDevice


class VSDIO(PyTangoDevice, Readable):
    """
    Basic IO Device object for devices in refsans' vsd rack
    contains common things for all devices.
    """

    hardware_access = True

    parameters = {
        'address': Param('Starting offset (words) of IO area',
                         type=oneof(12288),
                         mandatory=True, settable=False,
                         userparam=False, default=12288),
        'firmware': Param('Firmware Version', settable=False,
                          type=str, mandatory=False, volatile=True),
    }

    def doInit(self, mode):
        # switch off watchdog, important before doing any write access
        if mode != SIMULATION:
            self._dev.WriteOutputWord((0x1120, 0))

    #
    # access-helpers for accessing the fields inside the IO area
    #

    def _readU16(self, addr):
        # reads a uint16 from self.address + addr
        value = self._dev.ReadOutputWords((self.address + addr, 1))[0]
        self.log.debug('_readU16(%d): -> %d', addr, value)
        return value

    def _readI16(self, addr):
        # reads a int16 from self.address + addr
        value = self._dev.ReadOutputWords((self.address + addr, 1))[0]
        if value > 32767:
            value = value - 65536
        self.log.info('_readI16(%d): -> %d', addr, value)
        return value

    def _writeU16(self, addr, value):
        # writes a uint16 to self.address+addr
        value = int(value)
        self.log.debug('_writeU16(%d, %d)', addr, value)
        self._dev.WriteOutputWord((self.address + addr, value))

    def _readU32(self, addr):
        # reads a uint32 from self.address + addr .. self.address + addr + 1
        value = self._dev.ReadOutputWords((self.address + addr, 2))
        value = struct.unpack('=I', struct.pack('<2H', *value))[0]
        self.log.debug('_readU32(%d): -> %d', addr, value)
        return value

    def _writeU32(self, addr, value):
        # writes a uint32 to self.address + addr
        value = int(value)
        self.log.debug('_writeU32(%d, %d)', addr, value)
        value = struct.unpack('<2H', struct.pack('=I', value))
        self._dev.WriteOutputWords(tuple([self.address + addr]) + value)

    @requires(level='admin')
    def _load_factory(self):
        #QAD should be
        # pwd([0xFFFF,2])
        # write('kommando',[0xFFFF,2])
        #see Nicos old
        self._dev.WriteOutputWords((12338,25759,245))
        self._dev.WriteOutputWords((12340,65535,2))
        ACK = self._dev.ReadOutputWord(12363)
        NAK = self._dev.ReadOutputWord(12364)
        self.log.info('_load_factory %d %d', ACK, NAK)

    # mapping of user selectable channel name to BYTE_OFFSET, scaling and unit
    _HW_AnalogChannels = dict(
        User1Voltage=(200, 0.01, 'V-foo'),
        User1Current=(202, 0.01, 'mA-foo'),
        User2Voltage=(204, 0.01, 'V-foo'),
        User2Current=(206, 0.01, 'mA-foo'),
        Temperature1=(208, 0.01, 'degC'),
        Temperature2=(210, 0.01, 'degC'),
        Temperature3=(212, 0.01, 'degC'),
        Temperature4=(214, 0.01, 'degC'),
        Temperature5=(344, 0.01, 'degC'),
        Temperature6=(346, 0.01, 'degC'),
        Temperature7=(348, 0.01, 'degC'),
        Temperature8=(350, 0.01, 'degC'),
        Media1Voltage=(300, 0.01, 'V'),
        Media1Current=(302, 0.01, 'mA'),
        Media2Voltage=(304, 0.01, 'V'),
        Media2Current=(306, 0.01, 'mA'),
        Media3Voltage=(308, 0.01, 'V'),
        Media3Current=(310, 0.01, 'mA'),
        Media4Voltage=(312, 0.01, 'V'),
        Media4Current=(314, 0.01, 'mA'),
        Air1Pressure=(316, 0.01, 'bar'),
        Air2Pressure=(318, 0.01, 'bar'),
        Water1Temp=(320, 0.01, 'degC'),
        Water1Flow=(322, 0.01, 'l/min'),
        Water2Temp=(324, 0.01, 'degC'),
        Water2Flow=(326, 0.01, 'l/min'),
        Water3Temp=(328, 0.01, 'degC'),
        Water3Flow=(330, 0.01, 'l/min'),
        Water4Temp=(332, 0.01, 'degC'),
        Water4Flow=(334, 0.01, 'l/min'),
        Water5Temp=(336, 0.01, 'degC'),
        Water5Flow=(338, 0.01, 'l/min'),
        Water1Pressure=(340, 0.01, 'bar'),
        Water2Pressure=(342, 0.01, 'bar'),
        X16Voltage1=(352, 0.01, 'V'),
        X16Voltage2=(354, 0.01, 'V'),
        X16Voltage3=(356, 0.01, 'V'),
        X16Voltage4=(358, 0.01, 'V'),
    )

    # mapping of user selectable channel name to BYTE_OFFSET, bit number
    _HW_DigitalChannels = dict(
        (('Merker%d' % i, (160 + 2 * (i // 16), i % 16))
         for i in range(128, 255)),
        ControllerStatus=(148, 0),
        TempVibration=(148, 1),
        ChopperEnable1=(148, 2),
        ChopperEnable2=(148, 3),
        AkkuPower=(148, 4),
        PowerBreakdown=(148, 5),
        SolenoidValve=(148, 6),
        PowerSupplyUSV=(148, 7),
        PowerSupplyNormal=(148, 8),
        VSD_User1DigitalInput=(154, 0),
        VSD_User2DigitalInput=(154, 1),
        VSD_User3DigitalInput1=(154, 2),
        VSD_User3DigitalInput2=(154, 3),
        VSD_User3DigitalInput3=(154, 4),
        VSD_User4DigitalInput1=(154, 5),
        VSD_User4DigitalInput2=(154, 6),
        VSD_User4DigitalInput3=(156, 7),
        VSD_User1DigitalOutput1=(156, 0),
        VSD_User1DigitalOutput2=(156, 1),
        VSD_User2DigitalOutput1=(156, 2),
        VSD_User2DigitalOutput2=(156, 3),
        VSD_User3DigitalOutput1=(156, 4),
        VSD_User3DigitalOutput2=(156, 5),
        VSD_User3DigitalOutput3=(156, 6),
        VSD_User4DigitalOutput1=(156, 7),
        VSD_User4DigitalOutput2=(156, 8),
        VSD_User4DigitalOutput3=(156, 9),
        Media_DigitalOutput1=(158, 0),
        Media_DigitalOutput2=(158, 1),
        Media_DigitalOutput3=(158, 2),
        Media_DigitalOutput4=(158, 3),
    )
    #
    # Hardware abstraction: which actions do we want to do...
    #

    def _HW_readVersion(self):
        return 'V%.1f' % (self._readU32(120 // 2) * 0.1)

    def _HW_parallel_pumping_pressure(self):
        return 0

    #
    # Nicos Methods
    #

    def doRead(self, maxage=0):
        return self._HW_parallel_pumping_pressure()

    def doReadFirmware(self):
        return self._HW_readVersion()

    def doStatus(self, maxage=0):
        return status.OK, ''

    @usermethod
    def diag(self):
        """Display all available diagnostic values."""
        self.log.info("Analog Values:")
        for k, v in sorted(self._HW_AnalogChannels.items()):
            self.log.info("%s: %.2f %s", k, v[1] * self._readI16(v[0] // 2),
                          v[2])
        self.log.info("Digital Values:")
        for k, v in sorted(self._HW_DigitalChannels.items()):
            if k.startswith('Merker'):
                continue
            self.log.info("%s: %s", k,
                          'SET' if self._readU16(v[0] // 2) & (1 << v[1])
                          else 'clear')
        self.log.info("Merkerwords:")
        for i in range(16):
            self.log.info("Merker%d..%d : 0x%04x", 128 + 15 + 16 * i,
                          128 + 16 * i, self._readU16(160 // 2 + i))


class AnalogValue(Readable):
    attached_devices = {
        'iodev': Attach('IO Device', VSDIO),
    }
    parameters = {
        'channel': Param('Channel for readout',
                         type=oneof(*VSDIO._HW_AnalogChannels),
                         settable=True, preinit=True),
    }

    parameter_overrides = {
        'unit': Override(mandatory=False, volatile=True, settable=False),
    }

    def doReadUnit(self):
        _ofs, _scale, unit = \
            self._attached_iodev._HW_AnalogChannels[self.channel]
        if unit == 'mA-foo':
            unit = 'mA'
        elif unit == 'V-foo':
            unit = 'V'
        return unit

    def doRead(self, maxage=0):
        ofs, scale, _unit = \
            self._attached_iodev._HW_AnalogChannels[self.channel]
        # ofs is in Bytes, we need it in words! => /2
        if _unit == 'mA-foo':
            raw = scale * self._attached_iodev._readU16(ofs // 2)
            self.log.debug('mA-foo %.2f', raw)
            # Work around bug in firmware
            if raw > 20.0:
                raw -= 615.37
            self.log.debug('mA-foo %.2f', raw)
            # Tested against Multimeter (2018-08-07)
            raw /= 2.0
            self.log.debug('mA-foo %.2f', raw)
        elif _unit == 'V-foo':
            raw = self._attached_iodev._readU16(ofs // 2)
            self.log.debug('V-foo %d', raw)
            # Work around bug in firmware
            if raw > 0x8000:
                raw -= 63536
                self.log.debug('V-foo %d sign1', raw)
            self.log.debug('V-foo %d sign', raw)
            # Tested against Multimeter (2018-08-07)
            raw /= 2.0
            self.log.debug('v-foo %.2f /2.0', raw)
            raw *= scale
            self.log.debug('v-foo %.2f scale', raw)
        else:
            raw = scale * self._attached_iodev._readU16(ofs // 2)
        return raw

    def doStatus(self, maxage=0):
        return status.OK, ''


class DigitalValue(Readable):
    attached_devices = {
        'iodev': Attach('IO Device', VSDIO),
    }
    parameters = {
        'channel': Param('Channel for readout',
                         type=oneof(*VSDIO._HW_DigitalChannels),
                         settable=True, preinit=True),
        'mapping': Param('Mapping of 0/1 to sensible strings',
                         type=dictof(str, oneof(0, 1)), mandatory=True),
    }

    parameter_overrides = {
        'unit': Override(mandatory=False, settable=False, default=''),
    }

    def doInit(self, mode):
        self._revmapping = {v: k for k, v in self.mapping.items()}

    def doRead(self, maxage=0):
        ofs, bit = self._attached_iodev._HW_DigitalChannels[self.channel]
        # ofs is in Bytes, we need it in words! => /2
        if self._attached_iodev._readU16(ofs // 2) & (1 << bit):
            return self._revmapping[1]
        return self._revmapping[0]

    def doStatus(self, maxage=0):
        return status.OK, ''
