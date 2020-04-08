description = 'IPC slits serial #7 and #6'
group = 'lowlevel'

includes = ['system']

devices = dict(
    # gs1bus    = device('nicos.devices.vendor.ipc.IPCModBusTCP',
    #                    host = 'mirars7.mira.frm2',
    #                    port = 4001,
    #                    lowlevel = True,
    #                   ),

    # gs1_l_mot = device('nicos.devices.vendor.ipc.SlitMotor',
    #                    lowlevel = True,
    #                    bus = 'gs1bus',
    #                    addr = 0x77,
    #                    side = 2,
    #                    slope = -78.0,
    #                    zerosteps = 1070,
    #                    resetpos = -30,
    #                    abslimits = (-32, 13),
    #                   ),
    # gs1_r_mot = device('nicos.devices.vendor.ipc.SlitMotor',
    #                    lowlevel = True,
    #                    bus = 'gs1bus',
    #                    addr = 0x77,
    #                    side = 3,
    #                    slope = 80.0,
    #                    zerosteps = 1200,
    #                    resetpos = 30,
    #                    abslimits = (-13, 32),
    #                   ),
    # gs1_b_mot = device('nicos.devices.vendor.ipc.SlitMotor',
    #                    lowlevel = True,
    #                    bus = 'gs1bus',
    #                    addr = 0x77,
    #                    side = 0,
    #                    slope = -40.0,
    #                    zerosteps = 770,
    #                    resetpos = -45,
    #                    abslimits = (-60, 18),
    #                   ),
    # gs1_t_mot = device('nicos.devices.vendor.ipc.SlitMotor',
    #                    lowlevel = True,
    #                    bus = 'gs1bus',
    #                    addr = 0x77,
    #                    side = 1,
    #                    slope = 40.0,
    #                    zerosteps = 730,
    #                    resetpos = 45,
    #                    abslimits = (-17, 60),
    #                   ),

    # gs1_l     = device('nicos.devices.generic.Axis',
    #                    lowlevel = True,
    #                    precision = 0.1,
    #                    backlash = -2.,
    #                    motor = 'gs1_l_mot',
    #                    coder = 'gs1_l_mot',
    #                   ),
    # gs1_r     = device('nicos.devices.generic.Axis',
    #                    lowlevel = True,
    #                    precision = 0.1,
    #                    backlash = 2.,
    #                    motor = 'gs1_r_mot',
    #                    coder = 'gs1_r_mot',
    #                   ),
    # gs1_b     = device('nicos.devices.generic.Axis',
    #                    lowlevel = True,
    #                    precision = 0.1,
    #                    backlash = -3.,
    #                    motor = 'gs1_b_mot',
    #                    coder = 'gs1_b_mot',
    #                   ),
    # gs1_t     = device('nicos.devices.generic.Axis',
    #                    lowlevel = True,
    #                    precision = 0.1,
    #                    backlash = 3.,
    #                    motor = 'gs1_t_mot',
    #                    coder = 'gs1_t_mot',
    #                   ),

    # gs1       = device('nicos.devices.generic.Slit',
    #                    description = 'sample slit 1',
    #                    left = 'gs1_l',
    #                    right = 'gs1_r',
    #                    bottom = 'gs1_b',
    #                    top = 'gs1_t',
    #                    opmode = '4blades',
    #                    pollinterval = 5,
    #                    maxage = 10,
    #                   ),
    gs2bus = device('nicos.devices.vendor.ipc.IPCModBusTacoSerial',
        tacodevice = '//mirasrv/mira/network/rs13_1',
        lowlevel = True,
    ),
    gs2_l_mot = device('nicos.devices.vendor.ipc.SlitMotor',
        lowlevel = True,
        bus = 'gs2bus',
        addr = 0x66,
        side = 2,
        slope = -78.,
        zerosteps = 1170,
        resetpos = -20,
        abslimits = (-32, 13),
    ),
    gs2_r_mot = device('nicos.devices.vendor.ipc.SlitMotor',
        lowlevel = True,
        bus = 'gs2bus',
        addr = 0x66,
        side = 3,
        slope = 78.,
        zerosteps = 1200,
        resetpos = 20,
        abslimits = (-13, 32),
    ),
    gs2_b_mot = device('nicos.devices.vendor.ipc.SlitMotor',
        lowlevel = True,
        bus = 'gs2bus',
        addr = 0x66,
        side = 0,
        slope = -40.,
        zerosteps = 720,
        resetpos = -45,
        abslimits = (-70, 17),
    ),
    gs2_t_mot = device('nicos.devices.vendor.ipc.SlitMotor',
        lowlevel = True,
        bus = 'gs2bus',
        addr = 0x66,
        side = 1,
        slope = 39.5,
        zerosteps = 790,
        resetpos = 45,
        abslimits = (-19, 70),
    ),
    gs2_l = device('nicos.devices.generic.Axis',
        lowlevel = True,
        precision = 0.1,
        backlash = -2.,
        motor = 'gs2_l_mot',
        coder = 'gs2_l_mot',
    ),
    gs2_r = device('nicos.devices.generic.Axis',
        lowlevel = True,
        precision = 0.1,
        backlash = 2.,
        motor = 'gs2_r_mot',
        coder = 'gs2_r_mot',
    ),
    gs2_b = device('nicos.devices.generic.Axis',
        lowlevel = True,
        precision = 0.1,
        backlash = -2.,
        motor = 'gs2_b_mot',
        coder = 'gs2_b_mot',
    ),
    gs2_t = device('nicos.devices.generic.Axis',
        lowlevel = True,
        precision = 0.1,
        backlash = 2.,
        motor = 'gs2_t_mot',
        coder = 'gs2_t_mot',
    ),
    gs2 = device('nicos.devices.generic.Slit',
        description = 'sample slit 2',
        left = 'gs2_l',
        right = 'gs2_r',
        bottom = 'gs2_b',
        top = 'gs2_t',
        opmode = '4blades',
        pollinterval = 5,
        maxage = 10,
    ),
)
