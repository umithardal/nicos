#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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
#
# *****************************************************************************

import numpy as np
import PyTango

from nicos.core import status, Moveable, Measurable, Value, Param, Attach, \
    oneof, listof, intrange, ConfigurationError, SIMULATION, MASTER
from nicos.core.constants import FINAL, INTERRUPTED
from nicos.core.params import ArrayDesc
from nicos.devices.generic.detector import ImageChannelMixin, ActiveChannel, \
    Detector
from nicos.devices.generic.virtual import VirtualImage
from nicos.devices.tango import PyTangoDevice
from nicos_mlz.jcns.devices.fpga import FPGAChannelBase


RTMODES = ('standard', 'tof', 'realtime', 'realtime_external')


class KWSImageChannel(ImageChannelMixin, PyTangoDevice, ActiveChannel):

    attached_devices = {
        'timer':       Attach('The timer channel', Measurable),
        'highvoltage': Attach('The high voltage switch', Moveable, optional=True),
    }

    parameters = {
        'mode':        Param('Measurement mode switch', type=oneof(*RTMODES),
                             settable=True, category='general'),
        'slices':      Param('Calculated TOF slices', userparam=False,
                             unit='us', settable=True, type=listof(int),
                             category='general'),
    }

    def doInit(self, mode):
        if mode != SIMULATION:
            self._resolution = tuple(self._dev.detectorSize)
        else:
            self._resolution = (128, 128, 1)

    def _configure(self, tofsettings):
        value = self.mode
        if value == 'standard':
            self._setup_standard()
        elif value == 'tof':
            self._setup_tof(False, tofsettings)
        elif value == 'realtime':
            self._setup_tof(False, tofsettings)
        elif value == 'realtime_external':
            self._setup_tof(True, tofsettings)

    def _setup_standard(self):
        if self._mode != SIMULATION:
            self._dev.measureMode = 0
        self.slices = []
        dimensions = (self._resolution[0], self._resolution[1])
        # (x, y)
        self.arraydesc = ArrayDesc('data', dimensions, np.uint32)

    def _setup_tof(self, ext_trigger, tofsettings):
        # set timing of TOF slices
        channels, interval, q = tofsettings
        times = [0]
        for i in range(channels):
            times.append(times[-1] + int(interval * q**i))
        self.slices = times
        dimensions = (self._resolution[0], self._resolution[1], channels)
        # (x, y, t)
        self.arraydesc = ArrayDesc('data', dimensions, np.uint32)
        if self._mode == SIMULATION:
            return
        if ext_trigger:
            # RT measurement
            self._dev.measureMode = 2
            # number of external signals, != 1 not tested yet
            self._dev.rtParameter = 1
        else:
            # TOF measurement -- since the detector starts a TOF sweep
            # when the inhibit signal is taken away, this also works for
            # realtime without external signal
            self._dev.measureMode = 1
        self._dev.tofRange = times

    def doPrepare(self):
        if self._attached_highvoltage:
            self._attached_highvoltage.maw('on')
        self._dev.Prepare()

    def doStart(self):
        self.readresult = [0, 0.0]
        self._dev.Start()

    def doPause(self):
        # no stop necessary, gate will be cleared by counter card
        return True

    def doResume(self):
        pass

    def doFinish(self):
        self._dev.Stop()

    def doStop(self):
        self.doFinish()

    def doStatus(self, maxage=0):
        if self._dev.State() == PyTango.DevState.MOVING:
            return status.BUSY, 'counting'
        return status.OK, 'idle'

    def valueInfo(self):
        return (Value(name='total', type='counter', fmtstr='%d',
                      errors='sqrt', unit='cts'),
                Value(name='rate', type='monitor', fmtstr='%.1f', unit='cps'))

    _last = None

    def doReadArray(self, quality):
        shape = self.arraydesc.shape[::-1]
        arr = self._dev.GetBlock([0, int(np.product(shape))])
        cur = arr.sum(), self._attached_timer.read(0)[0]

        # for final images, calculate overall rate on detector
        if quality in (FINAL, INTERRUPTED):
            self.readresult = [cur[0], cur[0] / cur[1] if cur[1] else 0]
            return np.asarray(arr, np.uint32).reshape(shape)

        # for live measurements, calculate live rate on detector
        if cur[1] == 0:
            rate = 0.0
        elif self._last is None or self._last[1] > cur[1]:
            rate = cur[0] / cur[1]
        elif self._last[1] == cur[1]:
            rate = 0.0
        else:
            rate = (cur[0] - self._last[0]) / (cur[1] - self._last[1])

        self._last = cur
        self.readresult = [cur[0], rate]

        # live image handled in separate application - KWSLive
        return None


class VirtualKWSImageChannel(VirtualImage):

    parameters = {
        'mode':        Param('Measurement mode switch', type=oneof(*RTMODES),
                             settable=True, category='general'),
        'slices':      Param('Calculated TOF slices', userparam=False,
                             unit='us', settable=True, type=listof(int),
                             category='general'),
    }

    def _configure(self, tofsettings):
        if self.mode == 'standard':
            self.slices = []
            self.arraydesc = ArrayDesc('data', self.sizes, np.uint32)
        else:
            # set timing of TOF slices
            channels, interval, q = tofsettings
            times = [0]
            for i in range(channels):
                times.append(times[-1] + int(interval * q**i))
            self.slices = times
            self.arraydesc = ArrayDesc('data', self.sizes + (channels,),
                                       np.uint32)

    def doReadArray(self, quality):
        res = VirtualImage.doReadArray(self, quality)
        if self.mode != 'standard':
            return np.repeat(np.expand_dims(res, 2), len(self.slices) - 1, 2)
        return res


class KWSDetector(Detector):

    attached_devices = {
        'shutter':     Attach('Shutter for opening and closing', Moveable),
    }

    parameters = {
        'mode':        Param('Measurement mode switch', type=oneof(*RTMODES),
                             settable=True, volatile=True),
        'tofchannels': Param('Number of TOF channels',
                             type=intrange(1, 1023), settable=True,
                             category='general'),
        'tofinterval': Param('Interval dt between TOF channels', type=int,
                             unit='us', settable=True, category='general'),
        'tofprogression':
                       Param('Progression q of TOF intervals (t_i = dt * q^i)',
                             type=float, default=1.0, settable=True,
                             category='general'),
        'kwscounting': Param('True when taking data with kwscount()',
                             type=bool, default=False, settable=True,
                             userparam=False),
        'openshutter': Param('True to open/close shutter while counting',
                             type=bool, default=True, settable=True),
    }

    _img = None

    def doInit(self, session_mode):
        Detector.doInit(self, session_mode)
        self._img = self._attached_images[0]
        if session_mode == MASTER:
            if not self._attached_images or \
               not isinstance(self._attached_images[0], (KWSImageChannel,
                                                         VirtualKWSImageChannel)):
                raise ConfigurationError(self, 'KWSDetector needs a KWSChannel '
                                         'as attached image')
            self.kwscounting = False

    def _configure(self):
        for ch in self._channels:
            if isinstance(ch, FPGAChannelBase):
                ch.extmode = self.mode == 'realtime_external'
        # TODO: ensure that total meas. time < 2**31 usec
        self._img._configure((self.tofchannels, self.tofinterval,
                              self.tofprogression))

    def doReadMode(self):
        if self._img is None:
            return 'standard'  # bootstrap
        return self._img.mode

    def doWriteMode(self, mode):
        self._img.mode = mode

    def doSetPreset(self, **preset):
        # override time preset in realtime mode
        if self.mode in ('realtime', 'realtime_external'):
            # set counter card preset to last RT slice
            preset = {'t': self._img.slices[-1] / 1000000.0}
        Detector.doSetPreset(self, **preset)

    def doPrepare(self):
        self._configure()
        Detector.doPrepare(self)

    def doStart(self):
        if self.openshutter:
            self._attached_shutter.maw('open')
        self.kwscounting = True
        Detector.doStart(self)

    def doFinish(self):
        Detector.doFinish(self)
        self.kwscounting = False
        if self.openshutter:
            self._attached_shutter.maw('closed')

    def doStop(self):
        Detector.doStop(self)
        self.kwscounting = False
        if self.openshutter:
            self._attached_shutter.maw('closed')