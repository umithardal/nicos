description = 'IPC slit after mono shielding'

includes = ['system']

devices = dict(
    # gs1bus    = device('nicos.ipc.IPCModBusTCP',
    #                    host = 'mirars7.mira.frm2',
    #                    port = 4001,
    #                    lowlevel = True),

    # gs1_l_mot = device('nicos.ipc.SlitMotor',
    #                    lowlevel = True,
    #                    bus = 'gs1bus',
    #                    addr = 0x48,
    #                    side = 2,
    #                    slope = -78.0,
    #                    zerosteps = 1070,
    #                    resetpos = -30,
    #                    abslimits = (-32, 13)),
    # gs1_r_mot = device('nicos.ipc.SlitMotor',
    #                    lowlevel = True,
    #                    bus = 'gs1bus',
    #                    addr = 0x48,
    #                    side = 3,
    #                    slope = 80.0,
    #                    zerosteps = 1200,
    #                    resetpos = 30,
    #                    abslimits = (-13, 32)),
    # gs1_b_mot = device('nicos.ipc.SlitMotor',
    #                    lowlevel = True,
    #                    bus = 'gs1bus',
    #                    addr = 0x48,
    #                    side = 0,
    #                    slope = -40.0,
    #                    zerosteps = 770,
    #                    resetpos = -45,
    #                    abslimits = (-60, 18)),
    # gs1_t_mot = device('nicos.ipc.SlitMotor',
    #                    lowlevel = True,
    #                    bus = 'gs1bus',
    #                    addr = 0x48,
    #                    side = 1,
    #                    slope = 40.0,
    #                    zerosteps = 730,
    #                    resetpos = 45,
    #                    abslimits = (-17, 60)),

    # gs1_l     = device('nicos.generic.Axis',
    #                    lowlevel = True,
    #                    precision = 0.1,
    #                    backlash = -2.,
    #                    motor = 'gs1_l_mot',
    #                    coder = 'gs1_l_mot',
    #                    obs = None),
    # gs1_r     = device('nicos.generic.Axis',
    #                    lowlevel = True,
    #                    precision = 0.1,
    #                    backlash = 2.,
    #                    motor = 'gs1_r_mot',
    #                    coder = 'gs1_r_mot',
    #                    obs = None),
    # gs1_b     = device('nicos.generic.Axis',
    #                    lowlevel = True,
    #                    precision = 0.1,
    #                    backlash = -3.,
    #                    motor = 'gs1_b_mot',
    #                    coder = 'gs1_b_mot',
    #                    obs = None),
    # gs1_t     = device('nicos.generic.Axis',
    #                    lowlevel = True,
    #                    precision = 0.1,
    #                    backlash = 3.,
    #                    motor = 'gs1_t_mot',
    #                    coder = 'gs1_t_mot',
    #                    obs = None),

    # gs1       = device('nicos.generic.Slit',
    #                    description = 'sample slit 1',
    #                    left = 'gs1_l',
    #                    right = 'gs1_r',
    #                    bottom = 'gs1_b',
    #                    top = 'gs1_t',
    #                    opmode = '4blades',
    #                    pollinterval = 5,
    #                    maxage = 10),

    gs2bus    = device('nicos.ipc.IPCModBusTCP',
                       host = 'mirars7.mira.frm2',
                       port = 4001,
                       lowlevel = True),

    gs2_l_mot = device('nicos.ipc.SlitMotor',
                       lowlevel = True,
                       bus = 'gs2bus',
                       addr = 0x49,
                       side = 2,
                       slope = -80,
                       zerosteps = 1170,
                       resetpos = -20,
                       abslimits = (-32, 13)),
    gs2_r_mot = device('nicos.ipc.SlitMotor',
                       lowlevel = True,
                       bus = 'gs2bus',
                       addr = 0x49,
                       side = 3,
                       slope = 80.,
                       zerosteps = 1800,
                       resetpos = 20,
                       abslimits = (-13, 32)),
    gs2_b_mot = device('nicos.ipc.SlitMotor',
                       lowlevel = True,
                       bus = 'gs2bus',
                       addr = 0x49,
                       side = 0,
                       slope = -40.,
                       zerosteps = 720,
                       resetpos = -45,
                       abslimits = (-70, 17)),
    gs2_t_mot = device('nicos.ipc.SlitMotor',
                       lowlevel = True,
                       bus = 'gs2bus',
                       addr = 0x49,
                       side = 1,
                       slope = 40.,
                       zerosteps = 790,
                       resetpos = 45,
                       abslimits = (-19, 70)),

    gs2_l     = device('nicos.generic.Axis',
                       lowlevel = True,
                       precision = 0.1,
                       backlash = -2.,
                       motor = 'gs2_l_mot',
                       coder = 'gs2_l_mot',
                       obs = None),
    gs2_r     = device('nicos.generic.Axis',
                       lowlevel = True,
                       precision = 0.1,
                       backlash = 2.,
                       motor = 'gs2_r_mot',
                       coder = 'gs2_r_mot',
                       obs = None),
    gs2_b     = device('nicos.generic.Axis',
                       lowlevel = True,
                       precision = 0.1,
                       backlash = -2.,
                       motor = 'gs2_b_mot',
                       coder = 'gs2_b_mot',
                       obs = None),
    gs2_t     = device('nicos.generic.Axis',
                       lowlevel = True,
                       precision = 0.1,
                       backlash = 2.,
                       motor = 'gs2_t_mot',
                       coder = 'gs2_t_mot',
                       obs = None),

    gs2       = device('nicos.generic.Slit',
                       description = 'sample slit 2',
                       left = 'gs2_l',
                       right = 'gs2_r',
                       bottom = 'gs2_b',
                       top = 'gs2_t',
                       opmode = '4blades',
                       pollinterval = 5,
                       maxage = 10),
)
