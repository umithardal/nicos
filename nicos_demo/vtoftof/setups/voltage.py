description = 'low and high voltage power supplies for detector'

group = 'lowlevel'

devices = dict(
    hv0 = device('nicos.devices.generic.VirtualMotor',
        description = 'ISEG HV power supply 1',
        requires = {'level': 'admin'},
        abslimits = (0, 1600),
        ramp = 120,
        curvalue = 1500,
        fmtstr = '%.1f',
        unit = 'V',
    ),
    hv1 = device('nicos.devices.generic.VirtualMotor',
        description = 'ISEG HV power supply 2',
        requires = {'level': 'admin'},
        abslimits = (0, 1600),
        ramp = 120,
        curvalue = 1500,
        fmtstr = '%.1f',
        unit = 'V',
    ),
    hv2 = device('nicos.devices.generic.VirtualMotor',
        description = 'ISEG HV power supply 3',
        requires = {'level': 'admin'},
        abslimits = (0, 1600),
        ramp = 120,
        curvalue = 1500,
        fmtstr = '%.1f',
        unit = 'V',
    ),
    lv0 = device('nicos.devices.generic.ManualSwitch',
        description = 'LV power supply 1',
        requires = {'level': 'admin'},
        pollinterval = 10,
        maxage = 12,
        states = ['on', 'off']
    ),
    lv1 = device('nicos.devices.generic.ManualSwitch',
        description = 'LV power supply 2',
        requires = {'level': 'admin'},
        pollinterval = 10,
        maxage = 12,
        states = ['on', 'off']
    ),
    lv2 = device('nicos.devices.generic.ManualSwitch',
        description = 'LV power supply 3',
        requires = {'level': 'admin'},
        pollinterval = 10,
        maxage = 12,
        states = ['on', 'off']
    ),
    lv3 = device('nicos.devices.generic.ManualSwitch',
        description = 'LV power supply 4',
        requires = {'level': 'admin'},
        pollinterval = 10,
        maxage = 12,
        states = ['on', 'off']
    ),
    lv4 = device('nicos.devices.generic.ManualSwitch',
        description = 'LV power supply 5',
        requires = {'level': 'admin'},
        pollinterval = 10,
        maxage = 12,
        states = ['on', 'off']
    ),
    lv5 = device('nicos.devices.generic.ManualSwitch',
        description = 'LV power supply 6',
        requires = {'level': 'admin'},
        pollinterval = 10,
        maxage = 12,
        states = ['on', 'off']
    ),
    lv6 = device('nicos.devices.generic.ManualSwitch',
        description = 'LV power supply 7',
        requires = {'level': 'admin'},
        pollinterval = 10,
        maxage = 12,
        states = ['on', 'off']
    ),
    lv7 = device('nicos.devices.generic.ManualSwitch',
        description = 'LV power supply 8',
        requires = {'level': 'admin'},
        pollinterval = 10,
        maxage = 12,
        states = ['on', 'off']
    ),
)