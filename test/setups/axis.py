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
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

name = 'test_axis setup'

includes = ['stdsystem']

devices = dict(
    motor = device('nicos.devices.generic.VirtualMotor',
        unit = 'mm',
        curvalue = 0,
        abslimits = (-100, 100),
        userlimits = (-50, 50),
    ),
    coder = device('nicos.devices.generic.VirtualCoder',
        motor = 'motor',
        lowlevel = True,
    ),
    axis = device('nicos.devices.generic.Axis',
        motor = 'motor',
        coder = 'coder',
        obs = [],
        precision = 0,
        loopdelay = 0.02,
    ),
    aliasAxis = device('nicos.devices.generic.DeviceAlias',
        alias = 'axis',
    ),
    limit_motor = device('nicos.devices.generic.VirtualMotor',
        unit = 'mm',
        curvalue = 0,
        abslimits = (-100, 100),
    ),
    limit_coder = device('nicos.devices.generic.VirtualCoder',
        motor = 'limit_motor',
        lowlevel = True,
    ),
    limit_axis = device('nicos.devices.generic.Axis',
        motor = 'limit_motor',
        coder = 'limit_coder',
        obs = [],
        abslimits = (-1, 1),
        precision = 0,
    ),
    backlash_axis = device('nicos.devices.generic.Axis',
        motor = 'motor',
        coder = 'coder',
        obs = None,
        backlash = 0.5,
        precision = 0,
        loopdelay = 0.02,
    ),
    coder2 = device('nicos.devices.generic.VirtualCoder',
        motor = 'motor',
    ),
    obs_axis = device('nicos.devices.generic.Axis',
        motor = 'motor',
        coder = 'coder',
        obs = ['coder2'],
        backlash = 0.5,
        offset = 40,
        precision = 0,
        loopdelay = 0.02,
    ),
    slow_motor = device('nicos.devices.generic.VirtualMotor',
        unit = 'mm',
        curvalue = 0,
        abslimits = (-100, 100),
    ),
    nocoder_axis = device('nicos.devices.generic.Axis',
        motor = device('test.utils.TestReferenceMotor',
            unit = 'mm',
            curvalue = 1,
            abslimits = (-100, 100),
        ),
        precision = 0,
    ),
    nolimit_axis = device('nicos.devices.generic.Axis',
        motor = 'nolimit_motor',
        coder = None,
        obs = [],
        precision = 0,
        loopdelay = 0.02,
    ),
    nolimit_motor = device('nicos.devices.generic.VirtualMotor',
        unit = 'mm',
        curvalue = 0,
        abslimits = (-100, 100),
        userlimits = (-50, 50),
    ),
    prec_axis = device('nicos.devices.generic.Axis',
        motor = 'motor',
        coder = None,
        obs = [],
        precision = 0.2,
        loopdelay = 0.02,
    ),
)
