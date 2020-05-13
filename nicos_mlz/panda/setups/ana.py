#  -*- coding: utf-8 -*-

description = 'Analyser'

# sampletable.py contains all buses
includes = ['system','sampletable']
excludes = ['bambus']

group = 'lowlevel'

tango_base = 'tango://phys.panda.frm2:10000/panda/'

# channel 1   2   3   4   5   6    7       8
#        ath att agx --- --- aty afh_pg afh_heu

# eases address settings: 0x5.. = stepper, 0x6.. = poti, 0x7.. = coder ; .. = channel
MOTOR = lambda x: 0x50 + x
POTI = lambda x: 0x60 + x
CODER = lambda x: 0x70 + x

# eases confbyte settings for IPC-coder cards:
ENDAT = 0x80
SSI = 0

GRAY = 0x40
BINARY = 0

P_NONE = 0x20
P_EVEN = 0

TOTALBITS = lambda x: x & 0x1f

devices = dict(

    # ATT is first device and has 1 stepper, 0 poti, 1 coder
    att_step = device('nicos.devices.vendor.ipc.Motor',
        bus = 'bus1',
        addr = MOTOR(1),
        slope = -200,
        unit = 'deg',
        abslimits = (-140, 140),
        zerosteps = 500000,
        confbyte = 8+128,   # 128 = ten times slower (no gear at att!!!)
        speed = 100,
        accel = 50,
        microstep = 2,
        startdelay = 0,
        stopdelay = 0,
        ramptype = 1,
        # current = 2.0,
        lowlevel = True,
    ),
    att_enc = device('nicos.devices.vendor.ipc.Coder',
        bus = 'bus1',
        addr = CODER(1),
        slope = -2**20 / 360.0,
        zerosteps = 854914,
        confbyte = 148,
        unit = 'deg',
        circular = -360,  # map values to -180..0..180 degree
        lowlevel = True,
    ),
    anablocks = device('nicos_mlz.panda.devices.ana.AnaBlocks',
        description = 'Control for ana shielding blocks',
        tangodevice = tango_base + 'analyzer/plc_blockcontrol',
        lowlevel = False,
    ),
    att = device('nicos_mlz.panda.devices.ana.ATT_Axis',
        description = 'Analyser two theta',
        anablocks = 'anablocks',
        motor = 'att_step',
        coder = 'att_enc',
        precision = 0.05,
        jitter = 0.5,
        maxtries = 10,
        offset = 0.54568,
    ),
    # temporary disable of the ATT axis to allow movement
    # att = device('nicos.devices.generic.Axis',
    #     description = 'Analyser two theta',
    #     motor = 'att_step',
    #     coder = 'att_enc',
    #     precision = 0.05,
    #     jitter = 0.5,
    #     maxtries = 10,
    #     offset = 0.54568,
    # ),

    # ath is second device and has 1 stepper, 0 poti, 1 coder
    ath_step = device('nicos.devices.vendor.ipc.Motor',
        bus = 'bus1',
        addr = MOTOR(2),
        slope = 1600,
        unit = 'deg',
        abslimits = (-120, 5),
        zerosteps = 500000,
        speed = 250,
        accel = 24,
        microstep = 16,
        startdelay = 0,
        stopdelay = 0,
        ramptype = 1,
        lowlevel = True,
        # current = 2.0,
    ),
    ath_enc = device('nicos.devices.vendor.ipc.Coder',
        bus = 'bus1',
        addr = CODER(2),
        slope = 2**18 / 360.0,
        zerosteps = 235467,
        confbyte = 50,
        unit = 'deg',
        circular = -360,  # map values to -180..0..180 degree
        lowlevel = True,
    ),
    ath = device('nicos.devices.generic.Axis',
        description = 'analyser rocking angle',
        motor = 'ath_step',
        coder = 'ath_enc',
        precision = 0.03,
        maxtries = 50,
        offset = -2.209,
        # rotary = True,
    ),

    # agx is third device and has 1 stepper, 0 poti, 1 coder
    agx_step = device('nicos.devices.vendor.ipc.Motor',
        bus = 'bus1',
        addr = MOTOR(3),
        slope = 3200,
        unit = 'deg',
        abslimits = (-5, 5),
        zerosteps = 500000,
        speed = 100,
        accel = 8,
        microstep = 16,
        startdelay = 0,
        stopdelay = 0,
        ramptype = 1,
        lowlevel = True,
        # current = 2.0,
    ),
    agx_enc = device('nicos.devices.vendor.ipc.Coder',
        bus = 'bus1',
        addr = CODER(3),
        slope = -2**13,
        zerosteps = 16121227,
        confbyte = 153,
        unit = 'deg',
        circular = -4096,  # 12 bit (4096) for turns, times 2 deg per turn divided by 2 (+/-)
        lowlevel = True,
    ),
    agx = device('nicos.devices.generic.Axis',
        description = 'analyser tilt (up/down)',
        motor = 'agx_step',
        coder = 'agx_enc',
        precision = 0.01,
        # rotary = True,
    ),

    # fourth device is unused

    # fith device is unused

    # aty is sixth device and has 1 stepper, 0 poti, 1 coder
    aty_step = device('nicos.devices.vendor.ipc.Motor',
        bus = 'bus1',
        addr = MOTOR(6),
        slope = 400,
        unit = 'mm',
        abslimits = (-10, 10),
        zerosteps = 500000,
        speed = 100,
        accel = 8,
        microstep = 16,
        lowlevel = True,
        # divider = 4,
        # current = 1.5,
    ),
    aty_enc = device('nicos.devices.vendor.ipc.Coder',
        bus = 'bus1',
        addr = CODER(6),
        slope = -2**13,
        zerosteps = 15348276,
        confbyte = 153,
        unit = 'mm',
        circular = -4096,    # 12 bit (4096) for turns, times 2 deg per turn divided by 2 (+/-)
        lowlevel = True,
    ),
    aty = device('nicos.devices.generic.Axis',
        description = 'analyser translation along Y (thickness correction)',
        motor = 'aty_step',
        coder = 'aty_enc',
        precision = 0.05,
        fmtstr = '%.1f',
    ),

    # eigth device is unused

    # afh is seventh device and has 1 stepper, 0 poti, 0 coder
    afh_step = device('nicos.devices.vendor.ipc.Motor',
        bus = 'bus1',
        addr = MOTOR(7),
        slope = 8 * 400 / 360.0,
        unit = 'deg',
        abslimits = (-179, 179),
        zerosteps = 500000,
        speed = 20,
        accel = 15,
        microstep = 2 * 8,
        startdelay = 0,
        stopdelay = 0,
        ramptype = 1,
        lowlevel = True,
        # current = 2.0,
    ),
    afh_enc = device('nicos.devices.vendor.ipc.Coder',
        bus = 'bus1',
        addr = CODER(7),
        slope = 2**13 / 360.0,
        zerosteps = 5870,
        confbyte = SSI | GRAY | P_NONE | TOTALBITS(13),
        unit = 'deg',
        circular = -360,
        lowlevel = True,
    ),

    # afh = device('nicos.devices.generic.Axis',
    #     motor = 'afh_step',
    #     coder = 'afh_enc',
    #     precision = 1,
    #     fmtstr='%.1f',
    # ),

    afh_pg = device('nicos_mlz.panda.devices.rot_axis.RotAxis',
        description = 'horizontal focus of PG analyser',
        motor = 'afh_step',
        dragerror = 5,
        coder = 'afh_enc',
        abslimits = (-179, 179),
        precision = 1,
        fmtstr = '%.1f',
        autoref = None,  # disable autoref since there is no refswitch
    ),
    afh = device('nicos.devices.generic.DeviceAlias',
        alias = 'afh_pg',
    ),
)
