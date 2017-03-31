description = 'REFSANS demo setup'

group = 'basic'

excludes = ['detector', 'qmchannel']

includes = []

devices = dict(
    Sample = device('devices.sample.Sample',
                    description = 'Demo sample',
                   ),

    nok1_r = device('devices.generic.VirtualMotor',
                    lowlevel = True,
                    speed = 5,
                    abslimits = (-56.119, 1.381),
                    unit = 'mm',
                   ),

    nok1   = device('refsans.nok_support.SingleMotorNOK',
                    description = 'NOK1',
                    motor = 'nok1_r',
                    coder = 'nok1_r',
                    obs = [],
                    nok_start = 198.0,
                    nok_length = 90.0,
                    nok_end = 288.0,
                    nok_gap = 1.0,
                    backlash = -2,   # is this configured somewhere?
                    precision = 0.05,
                   ),

    nok2_r = device('devices.generic.VirtualMotor',
                     lowlevel = True,
                     abslimits = (-22.36, 10.88),
                     speed = 5,
                     unit = 'mm',
                    ),
    nok2_s = device('devices.generic.VirtualMotor',
                     lowlevel = True,
                     abslimits = (-21.61, 6.885),
                     unit = 'mm',
                    ),
    nok2   = device('refsans.nok_support.DoubleMotorNOK',
                    description = 'NOK2',
                    nok_start = 334.0,
                    nok_length = 300.0,
                    nok_end = 634.0,
                    nok_gap = 1.0,
                    inclinationlimits = (-10, 10),   # invented values, PLEASE CHECK!
                    nok_motor = [408.5, 585.0],
                    backlash = -2,   # is this configured somewhere?
                    motor_r = 'nok2_r',
                    motor_s = 'nok2_s',
                   ),

    nok3_r = device('devices.generic.VirtualMotor',
                    lowlevel = True,
                    abslimits = (-21.967, 47.782),
                    speed = 5,
                    unit = 'mm',
                   ),
    nok3_s = device('devices.generic.VirtualMotor',
                     lowlevel = True,
                     abslimits = (-20.944, 40.8055),
                     speed = 5,
                     unit = 'mm',
                    ),
    nok3   = device('refsans.nok_support.DoubleMotorNOK',
                    description = 'NOK3',
                    nok_start = 680.0,
                    nok_length = 600.0,
                    nok_end = 1280.0,
                    nok_gap = 1.0,
                    inclinationlimits = (-10, 10),   # invented values, PLEASE CHECK!
                    nok_motor = [831.0, 1131.0],
                    backlash = -2,   # is this configured somewhere?
                    motor_r = 'nok3_r',
                    motor_s = 'nok3_s',
                   ),

    nok4_r = device('devices.generic.VirtualMotor',
                    lowlevel = True,
                    abslimits = (-20.477, 48.523),
                    speed = 5,
                    unit = 'mm',
                   ),
    nok4_s = device('devices.generic.VirtualMotor',
                    lowlevel = True,
                    abslimits = (-21.3025, 41.197),
                    speed = 5,
                    unit = 'mm',
                   ),
    nok4   = device('refsans.nok_support.DoubleMotorNOK',
                    description = 'NOK4',
                    nok_start = 1326.0,
                    nok_length = 1000.0,
                    nok_end = 2326.0,
                    nok_gap = 1.0,
                    inclinationlimits = (-10, 10),   # invented values, PLEASE CHECK!
                    nok_motor = [1477.0, 2177.0],
                    backlash = -2,   # is this configured somewhere?
                    motor_r = 'nok4_r',
                    motor_s = 'nok4_s',
                   ),

    nok5a_r = device('devices.generic.VirtualMotor',
                     lowlevel = True,
                     abslimits = (-33.04875, 61.30375),
                     speed = 5,
                     unit = 'mm',
                    ),
    nok5a_s = device('devices.generic.VirtualMotor',
                     lowlevel = True,
                     abslimits = (-37.49, 66.25),
                     speed = 5,
                     unit = 'mm',
                    ),
    nok5a   = device('refsans.nok_support.DoubleMotorNOK',
                     description = 'NOK5A',
                     nok_start = 2418.5,
                     nok_length = 1720.0,
                     nok_end = 4138.5,
                     nok_gap = 1.0,
                     inclinationlimits = (-10, 10),   # invented values, PLEASE CHECK!
                     nok_motor = [3108.0, 3888.0],
                     backlash = -2,   # is this configured somewhere?
                     motor_r = 'nok5a_r',
                     motor_s = 'nok5a_s',
                    ),

    nok5b_r = device('devices.generic.VirtualMotor',
                     lowlevel = True,
                     abslimits = (-44.85, 78.8),
                     speed = 5,
                     unit = 'mm',
                    ),
    nok5b_s = device('devices.generic.VirtualMotor',
                     lowlevel = True,
                     abslimits = (-59.08, 93.41),
                     speed = 5,
                     unit = 'mm',
                    ),
    nok5b   = device('refsans.nok_support.DoubleMotorNOK',
                     description = 'NOK5B',
                     nok_start = 4153.5,
                     nok_length = 1720.0,
                     nok_end = 5873.5,
                     nok_gap = 1.0,
                     inclinationlimits = (-10, 10),   # invented values, PLEASE CHECK!
                     nok_motor = [4403.0, 5623.0],
                     backlash = -2,   # is this configured somewhere?
                     motor_r = 'nok5b_r',
                     motor_s = 'nok5b_s',
                    ),

    nok6_r  = device('devices.generic.VirtualMotor',
                     lowlevel = True,
                     abslimits = (-68.0, 96.59125),
                     speed = 5,
                     unit = 'mm',
                    ),
    nok6_s  = device('devices.generic.VirtualMotor',
                     lowlevel = True,
                     abslimits = (-81.0, 110.875),
                     speed = 5,
                     unit = 'mm',
                    ),
    nok6    = device('refsans.nok_support.DoubleMotorNOK',
                     description = 'NOK6',
                     nok_start = 5887.5,
                     nok_length = 1720.0,
                     nok_end = 7607.5,
                     nok_gap = 1.0,
                     inclinationlimits = (-10, 10),   # invented values, PLEASE CHECK!
                     nok_motor = [6137.0, 7357.0],
                     backlash = -2,   # is this configured somewhere?
                     motor_r = 'nok6_r',
                     motor_s = 'nok6_s',
                    ),

    nok7_r  = device('devices.generic.VirtualMotor',
                     lowlevel = True,
                     abslimits = (-89.475, 116.1),
                     speed = 5,
                     unit = 'mm',
                    ),
    nok7_s  = device('devices.generic.VirtualMotor',
                     lowlevel = True,
                     abslimits = (-96.94, 125.55),
                     speed = 5,
                     unit = 'mm',
                    ),
    nok7    = device('refsans.nok_support.DoubleMotorNOK',
                     description = 'NOK7',
                     nok_start = 7665.5,
                     nok_length = 1190.0,
                     nok_end = 8855.5,
                     nok_gap = 1.0,
                     inclinationlimits = (-10, 10),   # invented values, PLEASE CHECK!
                     nok_motor = [7915.0, 8605.0],
                     backlash = -2,   # is this configured somewhere?
                     motor_r = 'nok7_r',
                     motor_s = 'nok7_s',
                    ),

    nok8_r  = device('devices.generic.VirtualMotor',
                     lowlevel = True,
                     abslimits = (-102.835, 128.41),
                     speed = 5,
                     unit = 'mm',
                    ),
    nok8_s  = device('devices.generic.VirtualMotor',
                     lowlevel = True,
                     abslimits = (-104.6, 131.636),
                     speed = 5,
                     unit = 'mm',
                    ),
    nok8    = device('refsans.nok_support.DoubleMotorNOK',
                     description = 'NOK8',
                     nok_start = 8870.5,
                     nok_length = 880.0,
                     nok_end = 9750.5,
                     nok_gap = 1.0,
                     inclinationlimits = (-10, 10),   # invented values, PLEASE CHECK!
                     nok_motor = [9120.0, 9500.0],
                     backlash = -2,   # is this configured somewhere?
                     motor_r = 'nok8_r',
                     motor_s = 'nok8_s',
                    ),

    nok9_r  = device('devices.generic.VirtualMotor',
                     lowlevel = True,
                     abslimits = (-112.03425, 142.95925),
                     speed = 5,
                     unit = 'mm',
                    ),
    nok9_s  = device('devices.generic.VirtualMotor',
                     lowlevel = True,
                     abslimits = (-114.51425, 142.62775),
                     speed = 5,
                     unit = 'mm',
                    ),
    nok9    = device('refsans.nok_support.DoubleMotorNOK',
                     description = 'NOK9',
                     nok_start = 9773.5,
                     nok_length = 840.0,
                     nok_end = 10613.5,
                     nok_gap = 1.0,
                     inclinationlimits = (-10, 10),   # invented values, PLEASE CHECK!
                     nok_motor = [10023.5, 10362.7],
                     backlash = -2,   # is this configured somewhere?
                     motor_r = 'nok9_r',
                     motor_s = 'nok9_s',
                    ),

    det_time = device('devices.generic.VirtualTimer',
                      description = 'demo timer',
                     ),
    det_img  = device('devices.generic.VirtualImage',
                      description = 'demo 2D detector',
                      distance = None,
                      collimation = None,
                     ),
    det      = device('devices.generic.Detector',
                      description = 'demo 2D detector',
                      timers = ['det_timer'],
                      images = ['det_img'],
    )
)

startupcode = '''
SetDetectors(det)
printinfo("============================================================")
printinfo("Welcome to the NICOS REFSANS demo setup.")
printinfo("Run count(1) to collect an image.")
printinfo("============================================================")
'''
