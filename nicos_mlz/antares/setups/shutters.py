# -*- coding: utf-8 -*-
description = 'ANTARES shutter devices'

group = 'optional'

tango_base = 'tango://antareshw.antares.frm2:10000/antares/'

devices = dict(
    # Pilz shutter control
    shutter1_io = device('nicos.devices.tango.DigitalOutput',
        description = 'Tango device for Shutter 1',
        tangodevice = tango_base + 'fzjdp_digital/PilzShutter1',
        lowlevel = True,
    ),
    shutter1 = device('nicos.devices.generic.Switcher',
        description = 'Shutter 1',
        moveable = 'shutter1_io',
        mapping = dict(open = 1, closed = 2),
        fallback = '<undefined>',
        precision = 0,
        unit = '',
    ),
    shutter2_io = device('nicos.devices.tango.DigitalOutput',
        description = 'Tango device for Shutter 2',
        tangodevice = tango_base + 'fzjdp_digital/PilzShutter2',
        lowlevel = True,
    ),
    shutter2 = device('nicos.devices.generic.Switcher',
        description = 'Shutter 2',
        moveable = 'shutter2_io',
        mapping = dict(open = 1, closed = 2),
        fallback = '<undefined>',
        precision = 0,
        unit = '',
    ),
    fastshutter_io = device('nicos.devices.tango.DigitalOutput',
        description = 'Tango device for Fast shutter',
        tangodevice = tango_base + 'fzjdp_digital/FastShutter',
        comdelay = 0.1,
        comtries = 10,
        lowlevel = True,
    ),
    fastshutter = device('nicos.devices.generic.Switcher',
        description = 'Fast shutter',
        moveable = 'fastshutter_io',
        mapping = dict(open = 1, closed = 2),
        fallback = '<undefined>',
        precision = 0,
        unit = '',
    ),
)
