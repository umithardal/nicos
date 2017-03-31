#  -*- coding: utf-8 -*-

description = 'Monochanger'

group = 'optional'

includes = ['system', 'motorbus1', 'motorbus4', 'motorbus7', 'monochromator', 'puma']

monostates  = ['GE311',      'PG002',      'CU220',      'CU111',      'None']
monodevices = ['mono_ge311', 'mono_pg002', 'mono_cu220', 'mono_cu111', 'mono_dummy']
magazinpos  = [(315.4, 8),   (45.46, 1),  (135.4, 2),   (225.4, 4),]


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
                     confbyte = 52,
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

    mli    = device('devices.generic.Axis',
                    description = 'Axis for the monochromater changer lift',
                    motor = 'st_lift',
                    coder = 'co_lift',
                    obs = ['co_lift',],
                    dragerror = 20,
                    obsreadings = 100,
                    precision = 0.15,
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
                    moveables = 'mli',
                    readables = 'sw_lift',
                    mapping = dict( top2   = (358.1, 1),
                                    top1   = (355.3, 0),
                                    ref    = (0, 4),
                                    bottom = (-142.5, 2),
                                  ),
                    precision = [0.5, 0],
                    blockingmove = True,
                    fallback ='<unknown>',
                    timeout = 300,
                   ),


# Magazin
    st_mag = device('devices.vendor.ipc.Motor',
                    bus = 'motorbus7',
                    addr = 76,
                    slope = 200,
                    unit = 'deg',
                    abslimits = (20, 340),
                    zerosteps = 500000,
                    lowlevel = True,
                    confbyte = 44,
                   ),

#    co_mag = device('devices.vendor.ipc.Coder',
#                    bus = 'motorbus1',
#                    addr = 123,
#                    slope = 181.97,
#                    zerosteps = 2681.64,
#                    unit = 'deg',
#                    lowlevel = True,
#                   ),

    mag    = device('devices.generic.Axis',
                    description = 'monochromator magazin moving axis',
                    motor = 'st_mag',
                    coder = 'st_mag',
                    obs = [],
                    precision = 0.05,
                    offset = 0,
                    maxtries = 10,
                    dragerror = 90,
                    loopdelay = 2,
                    lowlevel = False,
                   ),

    io_mag = device('devices.vendor.ipc.Input',
                    bus = 'motorbus9',
                    addr = 106,
                    first = 3,
                    last = 6,
                    unit = '',
                    lowlevel = True,
                   ),

    magazin = device('puma.senseswitch.SenseSwitch',
                     description = 'Monochromatormagazin',
                     moveables = 'mag',
                     readables = 'io_mag',
                     mapping = dict(zip(monostates[:4], magazinpos)),
                     precision = [0.2, 0],
                     unit = '',
                     blockingmove = True,
                     fallback ='<unknown>',
                     timeout = 300,
                    ),

# Magnetic Lock
    mlock_op = device('devices.vendor.ipc.Input',
                      bus = 'motorbus9',
                      addr = 101,
                      first = 0,
                      last = 3,
                      unit = '',
                      lowlevel = True,
                     ),

    mlock_cl = device('devices.vendor.ipc.Input',
                      bus = 'motorbus9',
                      addr = 101,
                      first = 5,
                      last = 8,
                      unit = '',
                      lowlevel = True,
                     ),

    mlock_set = device('devices.vendor.ipc.Output',
                       bus = 'motorbus9',
                       addr = 110,
                       first = 0,
                       last = 3,
                       unit = '',
                       lowlevel = True,
                      ),

    mlock   = device('puma.maglock.MagLock',
                     description = 'Magnetic lock at magazin',
                     states = monostates[:4],
                     magazin = 'magazin',
                     io_open = 'mlock_op',
                     io_closed = 'mlock_cl',
                     io_set = 'mlock_set',
                     unit = '',
                    ),
# Greifer (grip)
    gr_stat = device('devices.vendor.ipc.Input',
                     bus = 'motorbus9',
                     addr = 101,
                     first = 14,
                     last = 15,
                     unit = '',
                     lowlevel = True,
                    ),

    gr_set = device('devices.vendor.ipc.Output',
                    bus = 'motorbus9',
                    addr = 110,
                    first = 5,
                    last = 5,
                    unit = '',
                    lowlevel = True,
                   ),

    grip = device('puma.senseswitch.SenseSwitch',
                  description = 'monochromator grip',
                  moveables = 'gr_set',
                  readables = 'gr_stat',
                  mapping = dict(open=(1, 2), closed=(0, 1)),
                  precision = None,  # literal compare!
                  blockingmove = True,
                  unit = '',
                  timeout = 13,
                  fallback ='<unknown>',
                 ),

# 3R coupling
    r3_set = device('devices.vendor.ipc.Output',
                    bus = 'motorbus9',
                    addr = 110,
                    first = 4,
                    last = 4,
                    unit = '',
                    lowlevel = True,
                   ),


    r3   =  device('devices.generic.Switcher',
                   description = 'R3 coupling holding monochromators',
                   moveable = 'r3_set',
                   mapping = dict(closed=0, open=1),
                   precision = 0.0,
                   blockingmove = True,
                   unit = '',
                  ),

# holdstat
    holdstat_io = device('devices.vendor.ipc.Input',
                         bus = 'motorbus9',
                         addr = 101,
                         first = 9,
                         last = 12,
                         unit = '',
                         lowlevel = True,
                        ),

    holdstat = device('devices.generic.ReadonlySwitcher',
                      description = 'What is in the holder position',
                      # monostates has five elements ! (last one is for 'none')
                      mapping = dict(zip(monostates, [14, 13, 11, 7, 15])),
                      readable = 'holdstat_io',
                     ),
# holdstat
    monostat_io = device('devices.vendor.ipc.Input',
                         bus = 'motorbus9',
                         addr = 106,
                         first = 0,
                         last = 2,
                         unit = '',
                         lowlevel = True,
                        ),

    mono_stat = device('devices.generic.ReadonlySwitcher',
                       description = 'What is at the monotable',
                       # monostates has five elements ! (last one is for 'none'). Unfortunately, Dummy (like 'none') returns 0
                       mapping = dict(zip(monostates, [4, 1, 2, 3, 0])),
                       readable = 'monostat_io',
                      ),
# Mchanger
    mchanger = device('puma.mchanger.Mchanger',
                      description = 'The actual monochromator changer',
                      monochromator = 'mono',
                      mapping = dict(zip(monostates, monodevices)),
                      magazin = 'magazin',
                      r3 = 'r3',
                      lift = 'lift',
                      grip = 'grip',
                      mlock = 'mlock',
                      holdstat = 'holdstat',
                      mono_stat = 'mono_stat',
#                      foch = 'mfhpg',
#                      focv = 'mfvpg',
                      changing_positions = dict(
                                                mth = 90.0,
                                                mtt = -36.5027,
                                                mty = 16.14,
                                                mgx = 0,
                                                mgy = 0,
                                               ),
                      init_positions = dict(
                                            mty = 70,
                                            mgx = 0,
                                            mgy = 0.1,
                                           ),
                      unit = '',
                     ),

    mono_dummy = device('devices.tas.Monochromator',
                        description = 'Dummy monochromator, DONT USE FOR EXPERIMENTS!',
                        order = 1,
                        unit = 'A-1',
                        theta = 'mth',
                        twotheta = 'mtt',
                        reltheta = True,
                        focush = None,
                        focusv = None,
                        hfocuspars = [1],
                        vfocuspars = [1],
                        abslimits = (1, 60),
                        dvalue = 3.1415,
                        scatteringsense = -1,
                        crystalside = -1,
                        fixed = 'Dummy monochromator, DONT USE FOR EXPERIMENTS!',
                        fixedby = ('brain', 30),
                       ),


)
