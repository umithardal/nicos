description = 'collimation slit'

group = 'lowlevel'

tango_base = 'tango://sans1hw.sans1.frm2:10000/sans1/'

devices = dict(
    slit_top = device('nicos.devices.tango.Motor',
        description = 'collimation slit top axis',
        lowlevel = False,
        tangodevice = tango_base + 'slit_col/top',
        abslimits = (0, 25),
        precision = 0.05,
    ),
    slit_bottom = device('nicos.devices.tango.Motor',
        description = 'collimation slit bottom axis',
        lowlevel = False,
        tangodevice = tango_base + 'slit_col/bottom',
        abslimits = (0, 25),
        precision = 0.05,
    ),
    slit_left = device('nicos.devices.tango.Motor',
        description = 'collimation slit left axis',
        lowlevel = False,
        tangodevice = tango_base + 'slit_col/left',
        abslimits = (0, 25),
        precision = 0.05,
    ),
    slit_right = device('nicos.devices.tango.Motor',
        description = 'collimation slit right axis',
        lowlevel = False,
        tangodevice = tango_base + 'slit_col/right',
        abslimits = (0, 25),
        precision = 0.05,
    ),
    slit = device('nicos.devices.generic.Slit',
        description = 'Collimation slit',
        top = 'slit_top',
        bottom = 'slit_bottom',
        left = 'slit_left',
        right = 'slit_right',
        opmode = 'centered',
        coordinates = 'opposite',
        pollinterval = 5,
        maxage = 12,
    ),
)
