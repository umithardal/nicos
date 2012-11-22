description = 'miscellaneous devices'
group = 'basic'

includes = ['system']
excludes = ['excluded']

devices = dict(
    m1       = device('devices.generic.VirtualMotor',
                      lowlevel = True,
                      #loglevel = 'debug',
                      abslimits = (-100, 100),
                      speed = 0.5,
                      unit = 'deg'),

    m2       = device('devices.generic.VirtualMotor',
                      lowlevel = True,
                      loglevel = 'debug',
                      abslimits = (-100, 100),
                      speed = 1,
                      unit = 'deg'),

    c1       = device('devices.generic.VirtualCoder',
                      lowlevel = True,
                      motor = 'm1',
                      unit = 'deg'),

    a1       = device('devices.generic.Axis',
                      motor = 'm1',
                      coder = 'c1',
                      obs = ['c1'],
                      abslimits = (0, 100),
                      userlimits = (0, 50),
                      precision = 0,
                      pollinterval = 0.5),

    a2       = device('devices.generic.Axis',
                      motor = 'm2',
                      coder = 'm2',
                      obs = [],
                      precision = 0,
                      abslimits = (0, 100)),

    sw       = device('devices.generic.Switcher',
                      moveable = 'a2',
                      states = ['in', 'out'],
                      values = [1, 0],
                      precision = 0),

    ap       = device('devices.generic.DeviceAlias',
                      alias = 'a1',
                      devclass = 'nicos.core.Moveable'),

    a1speed  = device('devices.generic.ParamDevice',
                      device = 'a1',
                      parameter = 'speed'),

    sxl      = device('devices.generic.VirtualMotor',
                      abslimits = (-20, 40),
                      unit = 'mm'),
    sxr      = device('devices.generic.VirtualMotor',
                      abslimits = (-40, 20),
                      unit = 'mm'),
    sxb      = device('devices.generic.VirtualMotor',
                      abslimits = (-50, 30),
                      unit = 'mm'),
    sxt      = device('devices.generic.VirtualMotor',
                      abslimits = (-30, 50),
                      unit = 'mm'),
    slit     = device('devices.generic.Slit',
                      left = 'sxl',
                      right = 'sxr',
                      bottom = 'sxb',
                      top = 'sxt'),

    mm       = device('devices.generic.ManualMove',
                      abslimits = (0, 100),
                      unit = 'mm'),
    msw      = device('devices.generic.ManualSwitch',
                      states = ['unknown', 'on', 'off']),
)
