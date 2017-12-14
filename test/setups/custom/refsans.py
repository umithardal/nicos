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
#
# *****************************************************************************

name = 'test_refsans setup'

includes = ['detector']

sysconfig = dict(
    datasinks = ['configsink'],
)

devices = dict(
    nok1 = device('nicos_mlz.refsans.devices.nok_support.SingleMotorNOK',
        motor = device('nicos.devices.generic.VirtualMotor',
            unit = 'mm',
            abslimits = (-56.119, 1.381),
        ),
        nok_start = 198.0,
        nok_length = 90.0,
        nok_end = 288.0,
        nok_gap = 1.0,
        backlash = -2,
        precision = 0.05,
    ),
    nok2 = device('nicos_mlz.refsans.devices.nok_support.DoubleMotorNOK',
        nok_start = 334.0,
        nok_length = 300.0,
        nok_end = 634.0,
        nok_gap = 1.0,
        inclinationlimits = (-10, 10),
        motor_r = device('nicos.devices.generic.Axis',
            motor = device('nicos.devices.generic.VirtualMotor',
                unit = 'mm',
                abslimits = (-25., 25.),
            ),
            precision = 0.05,
        ),
        motor_s = device('nicos.devices.generic.Axis',
            motor = device('nicos.devices.generic.VirtualMotor',
                unit = 'mm',
                abslimits = (-25., 25.),
            ),
            precision = 0.05,
        ),
        nok_motor = [408.5, 585.0],
        backlash = -2,
        precision = 0.05,
    ),
    nok_inc_failed = device('nicos_mlz.refsans.devices.nok_support.DoubleMotorNOK',
        nok_start = 334.0,
        nok_length = 300.0,
        nok_end = 634.0,
        nok_gap = 1.0,
        inclinationlimits = (10, -10),
        motor_r = device('nicos.devices.generic.Axis',
            motor = device('nicos.devices.generic.VirtualMotor',
                unit = 'mm',
                abslimits = (-25., 25.),
            ),
            precision = 0.05,
        ),
        motor_s = device('nicos.devices.generic.Axis',
            motor = device('nicos.devices.generic.VirtualMotor',
                unit = 'mm',
                abslimits = (-25., 25.),
            ),
            precision = 0.05,
        ),
        nok_motor = [408.5, 585.0],
        backlash = -2,
        precision = 0.05,
    ),
    obs = device('nicos_mlz.refsans.devices.nok_support.NOKPosition',
        reference = device('nicos.devices.generic.VirtualCoder',
            motor = device('nicos.devices.generic.VirtualMotor',
                abslimits = (0, 10),
                unit = 'V',
                curvalue = 10.,
            ),
            unit = 'V',
        ),
        measure = device('nicos.devices.generic.VirtualCoder',
            motor = device('nicos.devices.generic.VirtualMotor',
                abslimits = (0, 10),
                unit = 'V',
                curvalue = 5.,
            ),
            unit = 'V',
        ),
        # off, mul * 1000 / sensitivity, higher orders...
        poly = [9., 900.],
        serial = 6510,
        length = 250.0,
    ),
    zb1 = device('nicos_mlz.refsans.devices.slits.SingleSlit',
        motor = device('nicos.devices.generic.virtual.VirtualMotor',
            abslimits = (-184, 0.0),
            userlimits = (-184, 0.0),
            unit = 'mm',
            speed = 0.,
        ),
        nok_start = 5856.5,
        nok_length = 13,
        nok_end = 5862.5,
        nok_gap = 1,
        masks = {
            'slit': 0,
            'point': 0,
            'gisans': -100,
        },
        unit = 'mm',
    ),
    zb3r = device('nicos_mlz.refsans.devices.slits.SingleSlit',
        motor = device('nicos.devices.generic.Axis',
            motor = device('nicos.devices.generic.virtual.VirtualMotor',
                abslimits = (-677.125, 99.125),
                userlimits = (-221.0, 95.0),
                unit = 'mm',
            ),
            precision = 0.5,
            unit = 'mm',
        ),
        nok_start = 8837.5,
        nok_length = 13.0,
        nok_end = 8850.5,
        nok_gap = 1.0,
        masks = {
            'slit': -0,
            'point': -0,
            'gisans': -110,
        },
        unit = 'mm',
    ),
    zb3s = device('nicos_mlz.refsans.devices.slits.SingleSlit',
        description = 'ZB3 slit, sample side',
        motor = device('nicos.devices.generic.Axis',
            motor = device('nicos.devices.generic.virtual.VirtualMotor',
                abslimits = (-150.8125, 113.5625),
                userlimits = (-150.0, 113.562),
                unit = 'mm',
            ),
            precision = 0.5,
            unit = 'mm',
        ),
        nok_start = 8837.5,
        nok_length = 13.0,
        nok_end = 8850.5,
        nok_gap = 1.0,
        masks = {
            'slit': -0,
            'point': -0,
            'gisans': -110,
        },
        unit = 'mm',
    ),
    zb3 = device('nicos_mlz.refsans.devices.slits.DoubleSlit',
        description = 'ZB3 slit',
        slit_r = 'zb3r',
        slit_s = 'zb3s',
        unit = 'mm x mm',
    ),
    configsink = device('nicos_mlz.refsans.devices.datasinks.ConfigObjDatafileSink',
        lowlevel = True,
    ),
    vacuum_CB = device('nicos.devices.generic.ManualMove',
        default = 3.5e-6,
        abslimits = (0, 1000),
        unit = 'mbar',
    ),
    shutter = device('nicos.devices.generic.ManualSwitch',
        states = ['closed', 'open'],
    ),
    zb0 = device('nicos_mlz.refsans.devices.nok_support.SingleMotorNOK',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-180.815, 69.185),
            speed = 5,
            unit = 'mm',
        ),
        obs = [],
        nok_start = 4121.5,
        nok_length = 13.0,
        nok_end = 4134.5,
        nok_gap = 1.0,
        masks = dict(
            k1 = [-110.0, 0.0],
            slit = [0.0, 0.0],
        ),
        nok_motor = 4128.5,
        backlash = -2,
        precision = 0.05,
    ),
    table = device('nicos.devices.generic.Axis',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (620, 11025),
            unit = 'mm',
        ),
        precision = 0.05,
    ),
    tube = device('nicos.devices.generic.VirtualMotor',
        description = 'tube Motor',
        abslimits = (-120, 1000),
        unit = 'mm',
    ),
    h2_width = device('nicos.devices.generic.VirtualMotor',
        unit = 'mm',
        abslimits = (-69.5, 69.5),
    ),
    h2_center = device('nicos.devices.generic.VirtualMotor',
        unit = 'mm',
        abslimits = (0.05, 69.5),
    ),
    top_phi = device('nicos.devices.generic.VirtualMotor',
        abslimits = (-10.5, 10.5),
        unit = 'deg',
    ),
    pivot = device('nicos.devices.generic.ManualSwitch',
        states = list(range(1, 14)),
    ),
)
