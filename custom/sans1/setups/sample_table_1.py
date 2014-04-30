#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2014 by the NICOS contributors (see AUTHORS)
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
#   Andreas Wilhelm <andreas.wilhelm@frm2.tum.de>
#
# *****************************************************************************

description = 'bottom sample table devices'

group = 'lowlevel'

nethost = 'sans1srv.sans1.frm2'

devices = dict(
    st1_omg    = device('devices.taco.axis.Axis',
                         description = 'table 1 omega axis',
                         tacodevice = '//%s/sans1/table/omega-2b' % (nethost, ),
                         pollinterval = 15,
                         maxage = 60,
                         fmtstr = '%.2f',
                         abslimits = (-180, 180),
                        ),
    st1_omgmot = device('devices.taco.motor.Motor',
                         description = 'table 1 omega motor',
                         tacodevice = '//%s/sans1/table/omega-2bmot' % (nethost, ),
                         fmtstr = '%.2f',
                         abslimits = (-180, 180),
                         lowlevel = True,
                        ),
    st1_omgenc = device('devices.taco.coder.Coder',
                         description = 'table 1 omega encoder',
                         tacodevice = '//%s/sans1/table/omega-2benc' % (nethost, ),
                         fmtstr = '%.2f',
                         lowlevel = True,
                        ),

    st1_chi    = device('devices.taco.axis.Axis',
                       description = 'table 1 chi axis',
                       tacodevice = '//%s/sans1/table/chi-2b' % (nethost, ),
                       pollinterval = 15,
                       maxage = 60,
                       fmtstr = '%.2f',
                       abslimits = (-5, 5),
                      ),
    st1_chimot = device('devices.taco.motor.Motor',
                       description = 'table 1 chi motor',
                       tacodevice = '//%s/sans1/table/chi-2bmot' % (nethost, ),
                       fmtstr = '%.2f',
                       abslimits = (-5, 5),
                       lowlevel = True,
                      ),
    st1_chienc = device('devices.taco.coder.Coder',
                       description = 'table 1 chi encoder',
                       tacodevice = '//%s/sans1/table/chi-2benc' % (nethost, ),
                       fmtstr = '%.2f',
                       lowlevel = True,
                      ),

    st1_phi    = device('devices.taco.axis.Axis',
                       description = 'table 1 phi axis',
                       tacodevice = '//%s/sans1/table/phi-2b' % (nethost, ),
                       pollinterval = 15,
                       maxage = 60,
                       fmtstr = '%.2f',
                       abslimits = (-5, 5),
                      ),
    st1_phimot = device('devices.taco.motor.Motor',
                       description = 'table 1 phi motor',
                       tacodevice = '//%s/sans1/table/phi-2bmot' % (nethost, ),
                       fmtstr = '%.2f',
                       abslimits = (-5, 5),
                       lowlevel = True,
                      ),
    st1_phienc = device('devices.taco.coder.Coder',
                       description = 'table 1 phi encoder',
                       tacodevice = '//%s/sans1/table/phi-2benc' % (nethost, ),
                       fmtstr = '%.2f',
                       lowlevel = True,
                      ),

    st1_y    = device('devices.taco.axis.Axis',
                     description = 'table 1 y axis',
                     tacodevice = '//%s/sans1/table/y-2b' % (nethost, ),
                     pollinterval = 15,
                     maxage = 60,
                     fmtstr = '%.2f',
                     abslimits = (-100, 100),
                    ),
    st1_ymot = device('devices.taco.motor.Motor',
                     description = 'table 1 y motor',
                     tacodevice = '//%s/sans1/table/y-2bmot' % (nethost, ),
                     fmtstr = '%.2f',
                     abslimits = (-100, 100),
                     lowlevel = True,
                    ),
    st1_yenc = device('devices.taco.coder.Coder',
                     description = 'table 1 y encoder',
                     tacodevice = '//%s/sans1/table/y-2benc' % (nethost, ),
                     fmtstr = '%.2f',
                     lowlevel = True,
                    ),

    st1_z    = device('devices.taco.axis.Axis',
                     description = 'table 1 z axis',
                     tacodevice = '//%s/sans1/table/z-2b' % (nethost, ),
                     pollinterval = 15,
                     maxage = 60,
                     fmtstr = '%.2f',
                     abslimits = (-100, 100),
                    ),
    st1_zmot = device('devices.taco.motor.Motor',
                     description = 'table 1 z motor',
                     tacodevice = '//%s/sans1/table/z-2bmot' % (nethost, ),
                     fmtstr = '%.2f',
                     abslimits = (-100, 100),
                     lowlevel = True,
                    ),
    st1_zenc = device('devices.taco.coder.Coder',
                     description = 'table 1 z encoder',
                     tacodevice = '//%s/sans1/table/z-2benc' % (nethost, ),
                     fmtstr = '%.2f',
                     lowlevel = True,
                    ),

    st1_x    = device('devices.taco.axis.Axis',
                     description = 'table 1 x axis',
                     tacodevice = '//%s/sans1/table/x-2b' % (nethost, ),
                     pollinterval = 15,
                     maxage = 60,
                     fmtstr = '%.2f',
                     abslimits = (-750, 150),
                    ),
    st1_xmot = device('devices.taco.motor.Motor',
                     description = 'table 1 x motor',
                     tacodevice = '//%s/sans1/table/x-2bmot' % (nethost, ),
                     fmtstr = '%.2f',
                     abslimits = (-750, 150),
                     lowlevel = True,
                    ),
    st1_xenc = device('devices.taco.coder.Coder',
                     description = 'table 1 x encoder',
                     tacodevice = '//%s/sans1/table/x-2benc' % (nethost, ),
                     fmtstr = '%.2f',
                     lowlevel = True,
                    ),
)
