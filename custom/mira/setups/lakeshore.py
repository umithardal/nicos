description = 'LakeShore 340 cryo controller for CCR-5 cryostat'
group = 'optional'

modules = ['nicos.mira.commands']

devices = dict(
    T        = device('devices.taco.TemperatureController',
                      tacodevice = 'mira/ls340/control',
                      sensor_A = 'TA',
                      sensor_B = 'TB',
                      sensor_C = 'TC',
                      sensor_D = None,
                      pollinterval = 0.7,
                      maxage = 2,
                      abslimits = (0, 300)),
    TA       = device('devices.taco.TemperatureSensor',
                      tacodevice = 'mira/ls340/a',
                      pollinterval = 0.7,
                      maxage = 2),
    TB       = device('devices.taco.TemperatureSensor',
                      tacodevice = 'mira/ls340/b',
                      pollinterval = 0.7,
                      maxage = 2),
    TC       = device('devices.taco.TemperatureSensor',
                      tacodevice = 'mira/ls340/c',
                      pollinterval = 0.7,
                      maxage = 2),
    Pcryo    = device('devices.taco.AnalogInput',
                      description = 'Cryo sample tube pressure',
                      tacodevice = 'mira/ccr0/p1',
                      fmtstr = '%.3f'),
    Cryo     = device('devices.taco.NamedDigitalOutput',
                      mapping = {0: 'off', 1: 'on'},
                      tacodevice = 'mira/ccr0/pump',),
    CryoGas  = device('mira.ccr.GasValve',
                      mapping = {0: 'off', 1: 'on'},
                      tacodevice = 'mira/ccr0/gas',
                      timeout = 600),
    CryoVac  = device('devices.taco.NamedDigitalOutput',
                      mapping = {0: 'off', 1: 'on'},
                      tacodevice = 'mira/ccr0/vacuum'),
)
