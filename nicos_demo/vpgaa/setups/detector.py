description = 'PGAA detectors'

group = 'lowlevel'

devices = dict(
    truetim = device('nicos.devices.generic.VirtualTimer',
        description = 'True time timer',
        fmtstr = '%.2f',
        unit = 's',
        lowlevel = True,
    ),
    livetim = device('nicos.devices.generic.VirtualTimer',
        description = 'Live time timer',
        fmtstr = '%.2f',
        unit = 's',
        lowlevel = True,
    ),
    image = device('nicos_demo.vpgaa.devices.Spectrum',
        description = 'Image data device',
        fmtstr = '%d',
        pollinterval = 86400,
        sizes = (1, 16384),
        lowlevel = True,
    ),
    _60p = device('nicos_demo.vpgaa.devices.DSPec',
        description = 'DSpec detector for high energy gamma x-rays ',
        timers = ['truetim', 'livetim'],
        monitors = [],
        counters = [],
        images = ['image'],
        gates = ['shutter'],
        enablevalues = ['open'],
        disablevalues = ['closed'],
        pollinterval = None,
        liveinterval = 0.5,
        prefix = 'P'
    ),
    LEGe = device('nicos_demo.vpgaa.devices.DSPec',
        description = 'DSpec detector for low energy gamma x-rays',
        timers = ['truetim', 'livetim'],
        monitors = [],
        counters = [],
        images = ['image'],
        gates = ['shutter'],
        enablevalues = ['open'],
        disablevalues = ['closed'],
        pollinterval = None,
        liveinterval = 0.5,
        prefix = 'L'
    ),
)
