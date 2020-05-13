# -*- coding: utf-8 -*-
description = 'ANTARES Pilz security system states'

group = 'optional'

tango_base = 'tango://antareshw.antares.frm2:10000/antares/'

devices = dict(
    emergency = device('nicos.devices.tango.NamedDigitalInput',
        description = 'Emergency readout',
        tangodevice = tango_base + 'fzjdp_digital/PilzEmergencyStop',
        mapping = dict(
            zip([
                ', '.join([
                    'Emergency stop %d pressed' % k for k in range(1, 6)
                    if v & (2 ** (k - 1))
                ]) or 'ok' for v in range(32)
            ], range(32))
        ),
        unit = '',
    ),

    # searchbuttons
    tourbutton1 = device('nicos.devices.tango.NamedDigitalInput',
        description = 'Tourbutton1',
        tangodevice = tango_base + 'fzjdp_digital/PilzSecTourButton1',
        mapping = dict(unpressed = 1, pressed = 0),
        unit = '',
    ),
    tourbutton2 = device('nicos.devices.tango.NamedDigitalInput',
        description = 'Tourbutton2',
        tangodevice = tango_base + 'fzjdp_digital/PilzSecTourButton2',
        mapping = dict(unpressed = 1, pressed = 0),
        unit = '',
    ),
    tourbutton3 = device('nicos.devices.tango.NamedDigitalInput',
        description = 'Tourbutton3',
        tangodevice = tango_base + 'fzjdp_digital/PilzSecTourButton3',
        mapping = dict(unpressed = 1, pressed = 0),
        unit = '',
    ),

    # door state
    door_rot = device('nicos.devices.tango.NamedDigitalInput',
        description = 'Rotating door',
        tangodevice = tango_base + 'fzjdp_digital/PilzDoorRot',
        mapping = dict(closed = 1, open = 0),
        unit = '',
    ),
    door_slide = device('nicos.devices.tango.NamedDigitalInput',
        description = 'Sliding door',
        tangodevice = tango_base + 'fzjdp_digital/PilzDoorSlide',
        mapping = dict(closed = 1, open = 0),
        unit = '',
    ),
    pilz_state = device('nicos.devices.tango.NamedDigitalInput',
        description = 'Pilz state',
        tangodevice = tango_base + 'fzjdp_digital/PilzFailure',
        mapping = dict(ok = 0, failure = 1),
        unit = '',
    ),
)
