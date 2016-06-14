#  -*- coding: utf-8 -*-

description = 'Virtual setup for the choppers'
group = 'lowlevel'
display_order = 65

devices = dict(
    chopper         = device('kws1.chopper.Chopper',
                             description = 'high-level chopper/TOF presets',
                             resolutions = [1, 2.5, 5, 10],
                             selector = 'selector',
                             det_pos = 'detector',
                             params = 'chopper_params',
                             daq = 'det',
                            ),

    chopper_params  = device('kws1.chopper.ChopperParams',
                             description = 'Chopper frequency and opening',
                             motor1 = 'chopper1_motor',
                             motor2 = 'chopper2_motor',
                             freq1 = 'chopper1_freq',
                             freq2 = 'chopper2_freq',
                             phase1 = 'chopper1_phase',
                             phase2 = 'chopper2_phase',
                            ),

    chopper1_phase  = device('devices.generic.VirtualMotor',
                             description = 'Phase of the first chopper',
                             unit = 'deg',
                             fmtstr = '%.1f',
                             abslimits = (0, 360),
                             precision = 1.0,
                             lowlevel = True,
                            ),
    chopper1_freq   = device('devices.generic.VirtualMotor',
                             description = 'Frequency of the first chopper',
                             unit = 'Hz',
                             fmtstr = '%.1f',
                             abslimits = (0, 100),
                             precision = 0.1,
                             lowlevel = True,
                            ),
    chopper2_phase  = device('devices.generic.VirtualMotor',
                             description = 'Phase of the second chopper',
                             unit = 'deg',
                             fmtstr = '%.1f',
                             abslimits = (0, 360),
                             precision = 1.0,
                             lowlevel = True,
                            ),
    chopper2_freq   = device('devices.generic.VirtualMotor',
                             description = 'Frequency of the second chopper',
                             unit = 'Hz',
                             fmtstr = '%.1f',
                             abslimits = (0, 100),
                             precision = 0.1,
                             lowlevel = True,
                            ),
    chopper1_motor  = device('devices.generic.VirtualMotor',
                             description = 'Motor switch of the first chopper',
                             lowlevel = True,
                             abslimits = (0, 1),
                             unit = '',
                            ),
    chopper2_motor  = device('devices.generic.VirtualMotor',
                             description = 'Motor switch of the second chopper',
                             lowlevel = True,
                             abslimits = (0, 1),
                             unit = '',
                            ),
)

extended = dict(
    poller_cache_reader = ['detector', 'selector', 'det'],
)
