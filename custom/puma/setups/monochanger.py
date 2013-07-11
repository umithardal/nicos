#  -*- coding: utf-8 -*-

description = 'Monochanger'

group = 'optional'

includes = ['system', 'motorbus1', 'motorbus4', 'motorbus7', 'monochromator', 'puma']

monostates  = ['Dummy',      'PG002',      'CU220',      'CU111',      'None']
monodevices = ['mono_dummy', 'mono_pg002', 'mono_cu220', 'mono_cu111', 'mono_dummy']
depotpos    = [(315.4, 8),   (45.46, 1),  (135.4, 2),   (225.7, 4),]


devices = dict(
    st_lift = device('devices.vendor.ipc.Motor',
                     description = 'Motor of the monochromator lift',
                     bus = 'motorbus4',
                     addr = 51,
                     slope = -160,
                     unit = 'mm',
                     abslimits = (-144, 360),
                     zerosteps = 500000,
                     lowlevel = True,
                    ),

    co_lift = device('devices.vendor.ipc.Coder',
                     description = 'Potentiometer coder of the monochromator' \
                                   ' lift',
                     bus = 'motorbus1',
                     addr = 162,
                     slope = -7.256,
                     zerosteps = 2935.18,
                     unit = 'mm',
                     lowlevel = True,
                     readings = 50,
                    ),

    mli    = device('devices.generic.axis.Axis',
                    description = 'Axis for the monochromater changer lift',
                    motor = 'st_lift',
                    coder = 'co_lift',
                    obs = ['co_lift',],
                    dragerror = 20,
                    obsreadings = 100,
                    precision = 0.25,
                    offset = 0,
                    maxtries = 10,
                    loopdelay = 1,
                   ),

    sw_lift = device('devices.vendor.ipc.IPCSwitches',
                     description = 'Switches of the lift axis card',
                     bus = 'motorbus4',
                     addr = 51,
                     fmtstr = '%d',
                     lowlevel = True,
                    ),

    lift   = device('puma.senseswitch.SenseSwitch',
                    description = 'Monochromator lift',
                    moveable = 'mli',
                    readable = 'sw_lift',
                    mapping = dict( top2   = (357.9, 1),
                                    top1   = (356.1, 0),
                                    ref    = (0, 4),
                                    bottom = (-142.8, 2),
                                  ),
                    precision = [0.25, 0],
                    blockingmove = True,
                    timeout = 300,
                   ),


# Depot
    st_mag = device('devices.vendor.ipc.Motor',
                    bus = 'motorbus7',
                    addr = 76,
                    slope = 200,
                    unit = 'deg',
                    abslimits = (20, 340),
                    zerosteps = 500000,
                    lowlevel = True,
                    ),

    co_mag = device('devices.vendor.ipc.Coder',
                    bus = 'motorbus1',
                    addr = 123,
                    slope = 181.97,
                    zerosteps = 2681.64,
                    unit = 'deg',
                    lowlevel = True,
                    ),

    mag    = device('devices.generic.Axis',
                    motor = 'st_mag',
                    coder = 'co_mag',
                    obs = [],
                    precision = 0.05,
                    offset = 0,
                    maxtries = 10,
                    dragerror = 90,
                    loopdelay = 2,
                    lowlevel = True,
                    ),

    io_mag = device('devices.vendor.ipc.Input',
                   bus = 'motorbus8',
                   addr = 106,
                   first = 3,
                   last = 6,
                   unit = '',
                   lowlevel = True,
                   ),

    depot = device('puma.senseswitch.SenseSwitch',
                   description = 'Monochromator depot',
                   moveable = 'mag',
                   readable = 'io_mag',
                   mapping = dict(zip(monostates[:4], depotpos)),
                   precision = [0.2, 0],
                   unit = '',
                   blockingmove = True,
                   timeout = 300,
                  ),

# Magnetic Lock
    mlock_op = device('devices.vendor.ipc.Input',
                   bus = 'motorbus8',
                   addr = 101,
                   first = 0,
                   last = 3,
                   unit = '',
                   lowlevel = True,
                   ),

    mlock_cl = device('devices.vendor.ipc.Input',
                   bus = 'motorbus8',
                   addr = 101,
                   first = 5,
                   last = 8,
                   unit = '',
                   lowlevel = True,
                   ),

    mlock_set = device('devices.vendor.ipc.Output',
                   bus = 'motorbus8',
                   addr = 110,
                   first = 0,
                   last = 3,
                   unit = '',
                   lowlevel = True,
                   ),

    mlock   = device('puma.maglock.MagLock',
                   description = 'Magnetic lock at depot',
                   states = monostates[:4],
                   depot = 'depot',
                   io_open = 'mlock_op',
                   io_closed = 'mlock_cl',
                   io_set = 'mlock_set',
                   unit = '',
                   ),
# Greifer (grip)
    gr_stat = device('devices.vendor.ipc.Input',
                   bus = 'motorbus8',
                   addr = 101,
                   first = 14,
                   last = 15,
                   unit = '',
                   lowlevel = True,
                   ),

    gr_set = device('devices.vendor.ipc.Output',
                   bus = 'motorbus8',
                   addr = 110,
                   first = 5,
                   last = 5,
                   unit = '',
                   lowlevel = True,
                   ),

    grip = device('puma.senseswitch.SenseSwitch',
                   description = 'monochromator grip',
                   moveable = 'gr_set',
                   readable = 'gr_stat',
                   mapping = dict(open=(1, 2), closed=(0, 1)),
                   precision = None,  # literal compare!
                   blockingmove = True,
                   unit = '',
                   ),

# 3R coupling
    r3_set = device('devices.vendor.ipc.Output',
                   bus = 'motorbus8',
                   addr = 110,
                   first = 4,
                   last = 4,
                   unit = '',
                   lowlevel = True,
                   ),


    r3   =  device('nicos.devices.generic.Switcher',
                   description = 'R3 coupling holding monochromators',
                   moveable = 'r3_set',
                   mapping = dict(closed=0, open=1),
                   precision = 0.0,
                   blockingmove = True,
                   unit = '',
                   ),

# holdstat
    holdstat_io = device('devices.vendor.ipc.Input',
                   bus = 'motorbus8',
                   addr = 101,
                   first = 9,
                   last = 12,
                   unit = '',
                   lowlevel = True,
                   ),

    holdstat = device('devices.generic.switcher.ReadonlySwitcher',
                      description = 'What is in the holder position',
                      # monostates has five elements ! (last one is for 'none')
                      mapping = dict(zip(monostates, [14, 13, 11, 7, 15])),
                      readable = 'holdstat_io',
                     ),
# Mchanger
    mchanger = device('puma.mchanger.Mchanger',
                   description = 'The actual monochromator changer',
                   monochromator = 'mono',
                   mapping = dict(zip(monostates, monodevices)),
                   depot = 'depot',
                   r3 = 'r3',
                   lift = 'lift',
                   grip = 'grip',
                   mlock = 'mlock',
                   holdstat = 'holdstat',
                   foch = 'mfhpg',
                   focv = 'mfvpg',
                   changing_positions = dict(
                                              mth = 90.0,
                                              mtt = -36.5027,
                                              mty = 16.14,
                                              mgx = 0,
                                              mgy = 0,
                                            ),
                   unit = '',
                   ),

    mono_dummy_mth = device('devices.generic.VirtualMotor',
                      description = 'Virtual mth, DONT USE FOR EXPERIMENTS!',
                      abslimits = (-360, 360),
                      unit = 'deg',
                      lowlevel = True,
                   ),
    mono_dummy_mtt = device('devices.generic.VirtualMotor',
                      description = 'Virtual mtt, DONT USE FOR EXPERIMENTS!',
                      abslimits = (-360, 360),
                      unit = 'deg',
                      lowlevel = True,
                   ),
    mono_dummy     = device('devices.tas.Monochromator',
                      description = 'Dummy monochromator, DONT USE FOR EXPERIMENTS!',
                      order = 1,
                      unit = 'A-1',
                      theta = 'mono_dummy_mth',
                      twotheta = 'mono_dummy_mtt',
                      reltheta = True,
                      focush = None,
                      focusv = None,
                      hfocuspars = [1],
                      vfocuspars = [1],
                      abslimits = (1, 60),
                      dvalue = 3.1415,
                      ),


)
