#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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

name = 'test scanning setup'

includes = ['axis', 'detector']

devices = dict(
    motor2 = device('nicos.devices.generic.VirtualMotor',
                    unit = 'deg',
                    initval = 0,
                    abslimits = (0, 5),
                   ),

    manual = device('nicos.devices.generic.ManualMove',
                    unit = 'mm',
                    abslimits = (-5, 5),
                   ),

    tdev   = device('test.utils.TestDevice',
                    unit = 'mm',
                    abslimits = (-5, 5),
                    maxage = 0.0,  # no caching!
                   ),

    sry    = device('nicos.devices.generic.VirtualMotor',
                    unit = 'deg',
                    initval = 0,
                    abslimits = (-360, 360),
                   ),

)
