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
#   Jens Krüger <jens.kruege@frm2.tum.de>
#
# *****************************************************************************

name = 'test_spodi setup'

includes = ['stdsystem']

sysconfig = dict(
    datasinks = ['spodisink', 'spodilivesink'],
)

devices = dict(
    tths = device('nicos.devices.generic.VirtualMotor',
        unit = 'deg',
        abslimits = (-3.1, 170),
    ),
    omgs = device('nicos.devices.generic.VirtualMotor',
        unit = 'deg',
        abslimits = (-360, 360),
    ),
    mon1 = device('nicos.devices.generic.VirtualCounter',
        fmtstr = '%d',
        type = 'monitor',
    ),
    tim1 = device('nicos.devices.generic.VirtualTimer',
        unit = 's',
    ),
    spodi_image = device('nicos_mlz.spodi.devices.virtual.VirtualImage',
        pollinterval = None,
        sizes = (80, 256),
        background = 0,
    ),
    basedet = device('nicos.devices.generic.Detector',
        description = 'Classical detector with single channels',
        timers = ['tim1'],
        monitors = ['mon1'],
        images = ['spodi_image'],
        maxage = 86400,
        pollinterval = None,
    ),
    adet = device('nicos_mlz.spodi.devices.detector.Detector',
        motor = 'tths',
        detector = 'basedet',
        pollinterval = None,
        maxage = 86400,
        liveinterval = 5,
    ),
    spodisink = device('nicos_mlz.spodi.devices.datasinks.CaressHistogram',
        filenametemplate = ['m1%(pointcounter)08d.ctxt'],
        detectors = ['adet'],
    ),
    spodilivesink = device('nicos_mlz.spodi.devices.datasinks.LiveViewSink'),
)
