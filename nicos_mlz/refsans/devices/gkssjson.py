#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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
#   Matthias Pomm <matthias.pomm@hzg.de>
#
# *****************************************************************************
"""REFSANS SDS (safe detector system) devices."""

import requests

from nicos.core import Override, Param, Readable, intrange, oneof, status
from nicos.core.mixins import HasOffset
from nicos.core.errors import CommunicationError, ConfigurationError, \
    NicosError


class JsonBase(Readable):
    """Base class for webinterface

    """

    parameters = {
        'url': Param('URL reading the values',
                     type=str,
                     ),
        'timeout': Param('timeout to get an answers from URL',
                         default=0.1),
        'valuekey': Param('Key inside the json dict, only to proof comm',
                          type=str,),
    }

    def _read_controller(self, keys):
        self.log.debug(keys)
        try:
            data = requests.get(self.url, timeout=self.timeout).json()
            self.log.debug(data)
        except requests.Timeout as e:
            raise CommunicationError(self, 'HTTP request failed: %s' % e)
        except Exception as e:
            raise ConfigurationError(self, 'HTTP request failed: %s' % e)
        res = {}
        for key in keys:
            res[key] = data[key]
        return res

    def doStatus(self, maxage=0):
        try:
            self._read_controller([self.valuekey])
            return status.OK, ''
        except NicosError:
            return status.ERROR, 'Could not talk to hardware.'


class CPTMaster(JsonBase):

    def _read_ctrl(self, channel):
        data = self._read_controller([self.valuekey, 'start_act'])
        self.log.debug('res: %r', data)
        self.log.debug('channel %d', channel)
        if channel == 0:
            self.log.debug('calc speed')
            res = 3e9 / data['start_act']  # speed
            res -= self.offset  # should be Zero
        else:
            self.log.debug('calc phase in respect to Disk 1')
            res = -360.0 * data[self.valuekey][channel] / data['start_act']
            res -= self.offset
            res = self._kreis(res)
        return res

    def _kreis(self, phase, kreis=360.0):
        line = 'phase %.2f' % phase
        if phase > kreis / 2:
            phase -= kreis
        if phase < -kreis / 2:
            phase += kreis
        self.log.debug(line + ' %.2f' % phase)
        return phase


class CPTReadout(HasOffset, CPTMaster):

    parameters = {
        'index': Param('Index of value',
                       type=intrange(0, 99),),
    }

    def doRead(self, maxage=0):
        return self._read_ctrl(self.index)
        # res = self._kreis(self._read_ctrl(self.index) - self.offset)
        # return res


class SdsRatemeter(JsonBase):
    """Read the count rates for the different input channels of the SDS."""

    parameters = {
        'channel': Param('Channel to be rated',
                         type=oneof('a', 'x', 'y'), default='a',
                         settable=False)
    }

    parameter_overrides = {
        'fmtstr': Override(default='%d'),
        'unit': Override(default='cps'),
    }

    def doRead(self, maxage=0):
        res = self._read_controller(['mon_counts_cps_%s' % self.channel])
        return int(res.values()[0])
