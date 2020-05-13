description = 'Heater for ZEBRA Battery'

group = 'optional'

nethost = '172.25.20.210'

devices = dict(
    T1 = device('nicos.devices.taco.TemperatureController',
        description = 'The control device to the sample',
        tacodevice = '//%s/mpfc/ls340/control1' % nethost,
        abslimits = (0, 800),
        unit = 'C',
        fmtstr = '%.3f',
        pollinterval = 5,
        maxage = 6,
    ),
    T2 = device('nicos.devices.taco.TemperatureController',
        description = 'The control device to the sample',
        tacodevice = '//%s/mpfc/ls340/control2' % nethost,
        abslimits = (0, 800),
        unit = 'C',
        fmtstr = '%.3f',
        pollinterval = 5,
        maxage = 6,
    ),
)

startupcode = '''
AddEnvironment(T1, T2)
'''
