#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   Toni-protocol device classes
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
#   The basic NICOS methods for the NICOS daemon (http://nicos.sf.net)
#
#   Copyright (C) 2009 Jens Krüger <jens.krueger@frm2.tum.de>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# *****************************************************************************

"""Toni-protocol device classes."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import serial
import threading
from time import sleep, time

from IO import StringIO

from nicm import status
from nicm.utils import intrange, listof
from nicm.device import Device, Readable, Switchable, Param
from nicm.errors import NicmError, CommunicationError
from nicm.taco.base import TacoDevice


class ModBus(TacoDevice, Device):
    taco_class = StringIO

    parameters = {
        'maxtries': Param('Maximum tries before raising', type=int, default=5),
        'source':   Param('Source address of host', type=int, default=0),
    }

    def doReadUnit(self):
        # XXX not necessary, fix in base class?
        return ''

    def doInit(self):
        self._lock = threading.RLock()

    def _crc(self, str):
        crc = ord(str[0])
        for i in str[1:]:
            crc ^= ord(i)
        return '%02x' % crc

    def read(self, dest):
        self._lock.acquire()
        try:
            tries = self.maxtries
            while True:
                try:
                    ret = self._taco_guard(self._dev.readLine)
                except NicmError:
                    if tries == 0:
                        raise
                else:
                    break
                tries -= 1
        finally:
            self._lock.release()
        crc = self._crc(ret[1:-2])
        # check reply for validity
        if (len(ret) < 8 or ret[0] != '\x02' or ret[5] != '>' or ret[-2:] != crc
              or ret[1:3] != '%02X' % self.source or ret[3:5] != '%02X' % dest):
            raise CommunicationError(self, 'ModBus reply garbled: %r' % ret)
        return ret[6:-2]

    def communicate(self, msg, dest):
        msg = '%02X%02X%s' % (dest, self.source, msg)
        msg = '\x02' + msg + self._crc(msg)
        self._lock.acquire()
        try:
            tries = self.maxtries
            while True:
                try:
                    # the result of communicate is the echo
                    ret = self._taco_guard(self._dev.communicate, msg)
                    if ret != msg:
                        raise CommunicationError('ModBus echo garbled: %r' % ret)
                except NicmError:
                    if tries == 0:
                        raise
                    sleep(0.1)
                else:
                    break
                tries -= 1
            # wait before reading reply
            sleep(0.05)
            return self.read(dest)
        finally:
            self._lock.release()


class Valve(Switchable):

    attached_devices = {
        'bus': ModBus,
    }

    parameters = {
        'addr':     Param('Bus address of the valve control', type=int,
                          mandatory=True),
        'channel':  Param('Channel of the valve', type=intrange(0, 8),
                          mandatory=True),
        'states':   Param('Names for the closed/open states', type=listof(str),
                          default=['off', 'on']),
        'waittime': Param('Time to wait after switching', type=float, unit='s',
                          default=4),
        'unit':     Param('Unit', type=str, default=''),
    }

    def doInit(self):
        if len(self.states) != 2:
            raise ConfigurationError(self, 'Valve states must be a list of '
                                     'two strings for closed/open state')
        off, on = self.states
        self.__dict__['switchlist'] = {off: 0, on: 1}
        self._timer = 0

    def doStart(self, value):
        self.doWait()
        self._timer = time()
        msg = '%s=%02x' % (value and 'O' or 'C', 1 << self.channel)
        ret = self._adevs['bus'].communicate(msg, self.addr)
        if ret != 'OK':
            raise CommunicationError(self, 'ModBus read error: %r' % ret)

    def doRead(self):
        self.doWait()
        ret = self._adevs['bus'].communicate('R?', self.addr)
        if not ret:
            raise CommunicationError(self, 'ModBus read error: %r' % ret)
        return bool(int(ret, 16) & (1 << self.channel))

    def doStatus(self):
        self.doWait()
        ret = self._adevs['bus'].communicate('I?', self.addr)
        if not ret:
            raise CommunicationError(self, 'ModBus read error: %r' % ret)
        if int(ret) == 0:
            return status.OK, 'idle'
        else:
            return status.BUSY, 'busy'

    def doWait(self):
        if self._timer:
            # wait given time after last write action
            while time() - self._timer < self.waittime:
                sleep(0.1)
            self._timer = 0


class Leckmon(Readable):
    attached_devices = {
        'bus': ModBus,
    }

    parameters = {
        'addr':  Param('Bus address of monitor', type=int, mandatory=True),
    }

    def doRead(self):
        return self._adevs['bus'].communicate('S?', self.addr)
