description = '3He insert from FRM II Sample environment group'

group = 'plugplay'

includes = ['alias_T']

nethost = setupname

devices = {
    'T_%s' % setupname: device('nicos.devices.taco.TemperatureController',
                               description = 'The control device to the 3He pot',
                               tacodevice = '//%s/box/ls370/control' % nethost,
                               abslimits = (0, 300),
                               unit = 'K',
                               fmtstr = '%.3f',
                               pollinterval = 5,
                               maxage = 6,
                              ),

    'T_%s_A' % setupname: device('nicos.devices.taco.TemperatureSensor',
                                 description = 'The mixing chamber temperature',
                                 tacodevice = '//%s/box/ls370/sensora' % nethost,
                                 unit = 'K',
                                 fmtstr = '%.3f',
                                 pollinterval = 5,
                                 maxage = 6,
                                ),

    'T_%s_B' % setupname: device('nicos.devices.taco.TemperatureSensor',
                                 description = 'The sample temperature (if installed)',
                                 tacodevice = '//%s/box/ls370/sensorb' % nethost,
                                 unit = 'K',
                                 fmtstr = '%.3f',
                                 pollinterval = 5,
                                 maxage = 6,
                                ),

    '%s_p1' % setupname: device('nicos.devices.taco.AnalogInput',
                                description = 'Pressure turbo pump inlet',
                                tacodevice = '//%s/box/inficon/gauge1' % nethost,
                                fmtstr = '%.4g',
                                pollinterval = 15,
                                maxage = 20,
                               ),

    '%s_p2' % setupname: device('nicos.devices.taco.AnalogInput',
                                description = 'Pressure turbo pump outlet',
                                tacodevice = '//%s/box/module/gauge2' % nethost,
                                fmtstr = '%.4g',
                                pollinterval = 15,
                                maxage = 20,
                               ),

    '%s_p3' % setupname: device('nicos.devices.taco.AnalogInput',
                                description = 'Pressure compressor inlet',
                                tacodevice = '//%s/box/module/gauge3' % nethost,
                                fmtstr = '%.4g',
                                pollinterval = 15,
                                maxage = 20,
                               ),

    '%s_p4' % setupname: device('nicos.devices.taco.AnalogInput',
                                description = 'Pressure compressor outlet',
                                tacodevice = '//%s/box/module/gauge4' % nethost,
                                fmtstr = '%.4g',
                                pollinterval = 15,
                                maxage = 20,
                               ),

    '%s_p5' % setupname: device('nicos.devices.taco.AnalogInput',
                                description = 'Pressure dump/tank',
                                tacodevice = '//%s/box/module/gauge5' % nethost,
                                fmtstr = '%.4g',
                                pollinterval = 15,
                                maxage = 20,
                               ),

    '%s_p6' % setupname: device('nicos.devices.taco.AnalogInput',
                                description = 'Pressure vacuum dewar',
                                tacodevice = '//%s/box/inficon/gauge6' % nethost,
                                fmtstr = '%.4g',
                                pollinterval = 15,
                                maxage = 20,
                               ),

    '%s_flow' % setupname: device('nicos.devices.taco.AnalogInput',
                                  description = 'Gas flow',
                                  tacodevice = '//%s/box/module/flow' % nethost,
                                  fmtstr = '%.4g',
                                  unit = 'mln/min',
                                  pollinterval = 15,
                                  maxage = 20,
                                 ),

}

alias_config = {
    'T':  {'T_%s' % setupname: 300},
    'Ts': {'T_%s_A' % setupname: 300, 'T_%s_B' % setupname: 280},
}