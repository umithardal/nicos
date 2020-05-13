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

from os import path
from test.utils import cache_addr, runtime_root, module_root

name = 'simulation tests setup'

includes = []

sysconfig = dict(
    cache = cache_addr,
    experiment = 'Exp',
)

devices = dict(
    Sample = device('nicos.devices.tas.TASSample'),
    Exp = device('nicos.devices.experiment.Experiment',
        sample = 'Sample',
        elog = False,
        dataroot = path.join(runtime_root, 'data'),
        propprefix = 'p',
        templates = path.join(module_root, 'test', 'script_templates'),
        zipdata = True,
        serviceexp = 'service',
        lowlevel = False,
        localcontact = 'M. Aintainer <m.aintainer@frm2.tum.de>',
    ),
    motor = device('nicos.devices.generic.VirtualMotor',
        unit = 'deg',
        curvalue = 0,
        abslimits = (0, 5),
    ),
    timer = device('nicos.devices.generic.VirtualTimer',
        lowlevel = True,
    ),
    ctr1 = device('nicos.devices.generic.VirtualCounter',
        lowlevel = True,
        type = 'counter',
        countrate = 2000.,
        fmtstr = '%d',
    ),
    det = device('nicos.devices.generic.Detector',
        timers = ['timer'],
        counters = ['ctr1'],
        maxage = 3,
        pollinterval = 0.5,
    ),
    manualsim = device('nicos.devices.generic.ManualMove',
        abslimits = (0, 359),
        unit = 'deg',
        default = 45,
    ),
)
