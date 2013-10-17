#  -*- coding: utf-8 -*-

description = 'Monochromator'

group = 'lowlevel'

includes = ['system', 'motorbus1','motorbus4', 'motorbus7', 'motorbus8']


devices = dict(
    st_mtt = device('devices.vendor.ipc.Motor',
                    bus = 'motorbus4',
                    addr = 52,
                    slope = -1200,
                    unit = 'deg',
                    abslimits = (-110.1, -14.1),
                    zerosteps = 500000,
                    lowlevel = True,
                    ),
#     st_mtt = device('nicos.generic.VirtualMotor',
#                    unit = 'deg',
#                    abslimits = (-355, 355),
#                    ),
#
#     st_mth = device('nicos.generic.VirtualMotor',
#                    unit = 'deg',
#                    abslimits = (-355, 355),
#                    ),

    st_mth = device('devices.vendor.ipc.Motor',
                    bus = 'motorbus7',
                    addr = 70,
                    slope = -400,
                    unit = 'deg',
                    abslimits = (5, 175),
                    zerosteps = 500000,
                    lowlevel = True,
                    ),

#    co_mtt = device('devices.vendor.ipc.Coder',
    co_mtt = device('puma.mtt_coder.SpecialCoder',
                    bus = 'motorbus8',
                    addr = 120,
                    slope = -182.044,
                    zerosteps = 61180,
                    unit = 'deg',
                    circular = -360,
                    confbyte = 32,
                    lowlevel = True,
                    ),

#    co_mth = device('devices.vendor.ipc.Coder',
    co_mth = device('puma.mtt_coder.SpecialCoder',
                    bus = 'motorbus8',
                    addr = 121,
                    slope = -181.638,
                    zerosteps = 32823,
                    unit = 'deg',
                    lowlevel = True,
                    ),

#     co_mtt = device('nicos.generic.VirtualCoder',
#                    motor = 'st_mtt',
#                    unit = 'deg',
#                    lowlevel = True,
#                    ),

#     co_mth = device('nicos.generic.VirtualCoder',
#                    motor = 'st_mth',
#                    unit = 'deg',
#                    lowlevel = True,
#                    ),


    io_flag = device('devices.vendor.ipc.Input',
                    bus = 'motorbus8',
                    addr = 102,
                    first = 9,
                    last = 9,
                    unit = '',
                    lowlevel = True,
                    ),

    polyswitch = device('devices.vendor.ipc.Output',
                    bus = 'motorbus8',
                    addr = 115,
                    first = 0,
                    last = 0,
                    unit = '',
                    lowlevel = True,
                    ),


    mtt    = device('puma.mtt.MTT_Axis',
                    description  = 'Monochromator Two Theta',
                    motor = 'st_mtt',
                    coder = 'co_mtt',
                    io_flag = 'io_flag',
                    polyswitch = 'polyswitch',
                    obs = [],
                    precision = 0.01,
                    offset = -0.151,
                    maxtries = 10,
                    ),
    mth    = device('devices.generic.Axis',
                    description = 'Monochromator Theta',
                    motor = 'st_mth',
                    coder = 'co_mth',
                    obs = [],
                    precision = 0.012,
                    offset = -0.056,
                    maxtries = 8,
                    ),

   st_mfhpg = device('devices.vendor.ipc.Motor',
                    bus = 'motorbus7',
                    addr = 74,
                    slope = -40,
                    unit = 'deg',
                    abslimits = (-20, 55),
                    zerosteps = 27499.95,
                    lowlevel = True,
                    ),

   co_mfhpg = device('devices.vendor.ipc.Coder',
                    bus = 'motorbus1',
                    addr = 152,
                    slope = -26.79,
                    zerosteps = 2789.045,
                    unit = 'deg',
                    lowlevel = True,
                    ),
   mfhpg   = device('puma.focus.focus_Axis',
                   description = 'Horizontal focus of PG-Monochromator',
                   motor = 'st_mfhpg',
                   coder = 'co_mfhpg',
                   obs = [],
                   uplimit = 70,
                   lowlimit = 4.668,
                   flatpos = 4.668,
                   startpos = -7.874,
                   precision = 0.8,
                   maxtries = 15,
                   loopdelay = 2,
                   ),

  st_mfvpg = device('devices.vendor.ipc.Motor',
                    bus = 'motorbus7',
                    addr = 75,
                    slope = 168.0,
                    unit = 'deg',
                    abslimits = (-20, 55),
                    zerosteps = 10875.53,
                    lowlevel = True,
                    ),
   co_mfvpg = device('devices.vendor.ipc.Coder',
                    bus = 'motorbus1',
                    addr = 153,
                    slope = 146.043,
                    zerosteps = -2150.938,
                    unit = 'deg',
                    lowlevel = True,
                    ),
   mfvpg   = device('puma.focus.focus_Axis',
                   description = 'Vertical focus of PG-Monochromator',
                   motor = 'st_mfvpg',
                   coder = 'co_mfvpg',
                   obs = [],
                   uplimit = 38,
                   lowlimit = 16.5,
                   flatpos = 37,
                   startpos = 38,
                   precision = 0.8,
                   maxtries = 15,
                   loopdelay = 2,
                   ),
# CU220 FOcusing
   st_mfhcu = device('devices.vendor.ipc.Motor',
                    bus = 'motorbus7',
                    addr = 74,
                    slope = -130,
                    unit = 'deg',
                    abslimits = (-30, 100),
                    zerosteps = 498537,
                    lowlevel = True,
                    ),

   co_mfhcu = device('devices.vendor.ipc.Coder',
                    bus = 'motorbus1',
                    addr = 152,
                    slope = -19.595,
                    zerosteps = 2632,
                    unit = 'deg',
                    lowlevel = True,
                    ),
   mfhcu   = device('puma.focus.focus_Axis',
                   description = 'Horizontal focus of Cu220-Monochromator',
                   motor = 'st_mfhcu',
                   coder = 'co_mfhcu',
                   obs = [],
                   uplimit = 90,
                   lowlimit = -13.5,
                   flatpos = -13.5,
                   startpos = -15.,
                   precision = 0.8,
                   maxtries = 25,
                   loopdelay = 2,
                   ),

  st_mfvcu = device('devices.vendor.ipc.Motor',
                    bus = 'motorbus7',
                    addr = 75,
                    slope = 226.,
                    unit = 'deg',
                    abslimits = (-25, 60),
                    zerosteps = 488702,
                    lowlevel = True,
                    ),

   co_mfvcu = device('devices.vendor.ipc.Coder',
                    bus = 'motorbus1',
                    addr = 153,
                    slope = 51.429,
                    zerosteps = -79.082,
                    unit = 'deg',
                    lowlevel = True,
                    ),
   mfvcu   = device('puma.focus.focus_Axis',
                   description = 'Vertical focus of Cu220-Monochromator',
                   motor = 'st_mfvcu',
                   coder = 'co_mfvcu',
                   obs = [],
                   uplimit = 54,
                   lowlimit = 7,
                   flatpos = 54,
                   startpos = 56,
                   precision = 0.8,
                   maxtries = 25,
                   loopdelay = 2,
                   ),
# Tilt and Translation

   st_mty = device('devices.vendor.ipc.Motor',
                   bus = 'motorbus7',
                   addr = 71,
                   slope = 200,
                   unit = 'mm',
                   abslimits = (0, 90),
                   zerosteps = 500000,
                   lowlevel = True,
                   ),


   co_mty = device('devices.vendor.ipc.Coder',
                    bus = 'motorbus1',
                    addr = 151,
                    slope = 36.37,
                    zerosteps = 17,
                    unit = 'mm',
                    lowlevel = True,
                    ),

    mty    = device('devices.generic.Axis',
                    description = 'Translation of Monochromator (corrects depth of crystals',
                    motor = 'st_mty',
                    coder = 'co_mty',
                    obs = [],
                    precision = 0.3,
                    offset = 0,
                    maxtries = 10,
                    loopdelay = 1,
                    ),

   st_mgx = device('devices.vendor.ipc.Motor',
                   bus = 'motorbus7',
                   addr = 73,
                   slope = 400,
                   unit = 'mm',
                   abslimits = (-3.6, 3.6),
                   zerosteps = 500000,
                   lowlevel = True,
                   ),

    mgx   = device('devices.generic.Axis',
                    description = 'tilt of monochromator (up/down)',
                    motor = 'st_mgx',
                    coder = 'st_mgx',
                    obs = [],
                    precision = 0.1,
                    offset = 0,
                    maxtries = 10,
                    backlash = 0.25,
                    ),

    st_mgy = device('devices.vendor.ipc.Motor',
                   bus = 'motorbus7',
                   addr = 72,
                   slope = -400,
                   unit = 'mm',
                   abslimits = (-3.6, 3.6),
                   zerosteps = 500000,
                   lowlevel = True,
                   ),

    mgy   = device('devices.generic.Axis',
                    description = 'tilt of monochromator',
                    motor = 'st_mgy',
                    coder = 'st_mgy',
                    obs = [],
                    precision = 0.1,
                    offset = 0,
                    maxtries = 10,
                    backlash = 0.25,
                    ),
)
