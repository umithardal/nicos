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

description = 'detector related devices including beamstop'

includes = []

# included by sans1
group = 'lowlevel'

nethost = 'sans1srv.sans1.frm2'

devices = dict(
    det1_t_ist = device('devices.taco.FRMTimerChannel',
                        description = 'measured time of detector 1',
                        tacodevice = '//%s/sans1/qmesydaq/timer' % (nethost, ),
                        fmtstr = '%.0f',
                        lowlevel = True,
                        maxage = 120,
                        pollinterval = 15,
                       ),

#   det1_t_ist = device('devices.taco.FRMTimerChannel',
#                       tacodevice = '//%s/sans1/qmesydaq/det' % (nethost, ),
#                       fmtstr = '%.1f',
#                       pollinterval = 1,
#                       maxage = 3,
#                       # lowlevel = True,
#                      ),

#   det1_t_soll = device('devices.taco.FRMTimerChannel',
#                        tacodevice = '//%s/sans1/qmesydaq/timer' % (nethost, ),
#                        fmtstr = '%.1f',
#                        pollinterval = 5,
#                        maxage = 13,
#                        # lowlevel = True,
#                       ),

    det1_hv_interlock = device('devices.taco.DigitalInput',
                          description = 'interlock for detector 1 high voltage',
                          tacodevice = '//%s/sans1/interlock/hv' % (nethost, ),
                          lowlevel = True,
                          ),
    det1_hv_discharge_mode = device('devices.taco.DigitalInput',
                               description = 'set discharge mode of detector 1',
                               tacodevice = '//%s/sans1/interlock/mode' % (nethost, ),
                               lowlevel = True,
                              ),
    det1_hv_discharge = device('devices.taco.DigitalOutput',
                          description = 'enable and disable discharge of detector 1',
                          tacodevice = '//%s/sans1/interlock/discharge' % (nethost, ),
                          lowlevel = True,
                         ),
    #~ det1_hv_supply = device('devices.taco.VoltageSupply',
    det1_hv_supply = device('sans1.hv.VoltageSupply',
                description = 'high voltage power supply of detector 1',
                tacodevice = '//%s/sans1/iseg/hv' % (nethost, ),
                abslimits = [0, 1501],
                maxage = 120,
                pollinterval = 15,
                fmtstr = '%d',
                lowlevel = True,
                precision = 1,
               ),
    det1_hv_ax    = device('sans1.hv.Sans1HV',
                      description = 'high voltage of detector 1',
                      unit = 'V',
                      supply = 'det1_hv_supply',
                      discharger = 'det1_hv_discharge',
                      interlock = 'det1_hv_interlock',
                      maxage = 120,
                      pollinterval = 15,
                      lowlevel = True,
                     ),
    det1_hv_offtime = device('sans1.hv.Sans1HVOffDuration',
                      description = 'Duration below operating voltage',
                      hv_supply = 'det1_hv_ax',
                      maxage = 120,
                      pollinterval = 15,
                     ),
    det1_hv    = device('devices.generic.Switcher',
                        description = 'high voltage of detector 1 switcher',
                        moveable = 'det1_hv_ax',
                        mapping = {'ON': 1500, 'OFF': 0},
                        precision = 1,
                        unit = '',
                        fallback = 'unknown',
                       ),
    hv_current = device('devices.taco.AnalogInput',
                        description = 'high voltage current of detector 1',
                        tacodevice = '//%s/sans1/iseg/hv-current' % (nethost, ),
                        maxage = 120,
                        pollinterval = 15,
                        lowlevel = True,
                       ),

    #~ det1_x = device('devices.taco.axis.Axis',
                      #~ description = 'detector 1 x axis',
                      #~ tacodevice = '//%s/sans1/detector1/x' % (nethost, ),
                      #~ fmtstr = '%.1f',
                      #~ abslimits = (4, 570),
                      #~ maxage = 120,
                      #~ pollinterval = 5,
                      #~ requires = dict(level='admin'),
                      #~ precision = 0.3,
                     #~ ),
    det1_x = device('devices.generic.Axis',
                      description = 'detector 1 x axis',
                      fmtstr = '%.1f',
                      abslimits = (4, 570),
                      maxage = 120,
                      pollinterval = 5,
                      requires = dict(level='admin'),
                      precision = 0.3,
                      motor = 'det1_xmot',
                      coder = 'det1_xenc',
                      obs=[],
                     ),
    #~ det1_xmot = device('devices.taco.motor.Motor',
    det1_xmot = device('sans1.misc.Motor',
                         description = 'detector 1 x motor',
                         tacodevice = '//%s/sans1/detector1/xmot' % (nethost, ),
                         fmtstr = '%.1f',
                         abslimits = (4, 570),
                         lowlevel = True,
                       ),
    #~ det1_xenc = device('devices.taco.coder.Coder',
    det1_xenc = device('sans1.misc.Coder',
                         description = 'detector 1 x motor',
                         tacodevice = '//%s/sans1/detector1/xenc' % (nethost, ),
                         fmtstr = '%.1f',
                         lowlevel = True,
                        ),

    det1_z = device('devices.generic.sequence.LockedDevice',
                      description = 'detector 1 z position interlocked with high voltage supply',
                      device = 'det1_z_ax',
                      lock = 'det1_hv_ax',
                      # lockvalue = None,     # go back to previous value
                      unlockvalue = 0.0,
                      # keepfixed = False,	# do not fix supply voltage after movement
                      fmtstr = '%.1f',
                      maxage = 120,
                      pollinterval = 15,
                     ),

    #~ det1_z_ax = device('devices.taco.axis.Axis',
                      #~ description = 'detector 1 z axis',
                      #~ tacodevice = '//%s/sans1/detector1/z' % (nethost, ),
                      #~ fmtstr = '%.1f',
                      #~ abslimits = (1100, 20000),
                      #~ maxage = 120,
                      #~ pollinterval = 5,
                      #~ lowlevel = True,
                      #~ precision = 1,
                      #~ userlimits = (1111, 20000),
                     #~ ),
    det1_z_ax = device('devices.generic.Axis',
                      description = 'detector 1 z axis',
                      fmtstr = '%.1f',
                      abslimits = (1100, 20000),
                      maxage = 120,
                      pollinterval = 5,
                      lowlevel = True,
                      precision = 1,
                      userlimits = (1111, 20000),
                      motor = 'det1_zmot',
                      coder = 'det1_zenc',
                      obs=[],
                     ),
    #~ det1_zmot = device('devices.taco.motor.Motor',
    det1_zmot = device('sans1.misc.Motor',
                         description = 'detector 1 z motor',
                         tacodevice = '//%s/sans1/detector1/zmot' % (nethost, ),
                         fmtstr = '%.1f',
                         abslimits = (1100, 20000),
                         lowlevel = True,
                        ),
    #~ det1_zenc = device('devices.taco.coder.Coder',
    det1_zenc = device('sans1.misc.Coder',
                         description = 'detector 1 z encoder',
                         tacodevice = '//%s/sans1/detector1/zenc' % (nethost, ),
                         fmtstr = '%.1f',
                         lowlevel = True,
                        ),

    #~ det1_omg = device('devices.taco.axis.Axis',
                          #~ description = 'detector 1 omega axis',
                          #~ tacodevice = '//%s/sans1/detector1/omega' % (nethost, ),
                          #~ fmtstr = '%.1f',
                          #~ abslimits = (-0.2, 21),
                          #~ maxage = 120,
                          #~ pollinterval = 5,
                          #~ requires = dict(level='admin'),
                          #~ userlimits = (0, 20),
                          #~ precision = 0.2,
                         #~ ),
    det1_omg = device('devices.generic.Axis',
                          description = 'detector 1 omega axis',
                          fmtstr = '%.1f',
                          abslimits = (-0.2, 21),
                          maxage = 120,
                          pollinterval = 5,
                          requires = dict(level='admin'),
                          userlimits = (0, 20),
                          precision = 0.2,
                          motor = 'det1_omegamot',
                          coder = 'det1_omegaenc',
                          obs=[],
                         ),
    det1_omegamot = device('sans1.misc.Motor',
                             description = 'detector 1 omega motor',
                             tacodevice = '//%s/sans1/detector1/omegamot' % (nethost, ),
                             fmtstr = '%.1f',
                             abslimits = (-0.2, 21),
                             lowlevel = True,
                            ),
    det1_omegaenc = device('sans1.misc.Coder',
                             description = 'detector 1 omega encoder',
                             tacodevice = '//%s/sans1/detector1/omegaenc' % (nethost, ),
                             fmtstr = '%.1f',
                             lowlevel = True,
                            ),

    bs1_x    = device('nicos.devices.generic.Axis',
                        description = 'beamstop 1 x axis',
                        motor = 'bs1_xmot',
                        coder = 'bs1_xmot',
                        obs = [],
                        precision = 0.1,
                        fmtstr = '%.2f',
                        abslimits = (480, 868),
                       ),
    bs1_xmot = device('devices.taco.motor.Motor',
                        description = 'beamstop 1 x motor',
                        tacodevice = '//%s/sans1/beamstop1/xmot' % (nethost, ),
                        fmtstr = '%.2f',
                        abslimits = (480, 868),
                        lowlevel = True,
                       ),
    bs1_y    = device('nicos.devices.generic.Axis',
                        description = 'beamstop 1 y axis',
                        motor = 'bs1_ymot',
                        coder = 'bs1_ymot',
                        obs = [],
                        precision = 0.1,
                        fmtstr = '%.2f',
                        abslimits = (-90, 500),
                        userlimits = (100, 500),
                       ),
    bs1_ymot = device('devices.taco.motor.Motor',
                        description = 'beamstop 1 y motor',
                        tacodevice = '//%s/sans1/beamstop1/ymot' % (nethost, ),
                        fmtstr = '%.1f',
                        abslimits = (-90, 500),
                        lowlevel = True,
                       ),

)
