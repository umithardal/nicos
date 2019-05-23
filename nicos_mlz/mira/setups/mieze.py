description = 'MIEZE measurement setup'
group = 'optional'

includes = ['cascade', 'guidehall', 'nl6', 'cbox1', 'cbox2',
    # 'heinzinger',  # temporarily removed, since it is absend
    'tuning']

tango_base = 'tango://miractrl.mira.frm2:10000/mira/'

devices = dict(
    hsf1 = device('nicos.devices.tango.PowerSupply',
        description = 'first coupling coil - Helmholtz coil',
        tangodevice = tango_base + 'tti1/out1',
        abslimits = (0, 2),
        timeout = 2,
        precision = 0.005,
    ),
    sf1 = device('nicos.devices.tango.PowerSupply',
        description = 'first coupling coil - pi/2 flipper',
        tangodevice = tango_base + 'tti1/out2',
        abslimits = (0, 2),
        timeout = 2,
        precision = 0.005,
    ),
    hsf2 = device('nicos.devices.tango.PowerSupply',
        description = 'second coupling coil - Helmholtz coil',
        tangodevice = tango_base + 'tti2/out1',
        abslimits = (0, 2),
        timeout = 2,
        precision = 0.005,
    ),
    sf2 = device('nicos.devices.tango.PowerSupply',
        description = 'second coupling coil - pi/2 flipper',
        tangodevice = tango_base + 'tti2/out2',
        abslimits = (0, 2),
        timeout = 2,
        precision = 0.005,
    ),
)
