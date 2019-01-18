description = "sc2 height after nok9"

group = 'lowlevel'

nethost = 'refsanssrv.refsans.frm2'
tacodev = '//%s/test' % nethost

devices = dict(
    sc2 = device('nicos.devices.taco.Axis',
        description = 'sc2 Motor',
        tacodevice = '%s/sc2/motor' % tacodev,
        abslimits = (-150, 150),
        refpos = -7.2946,
    ),
)
