description = 'PUMA multi detector device'

group = 'optional'

import math

includes = ['multianalyzer']

excludes = [
    'detector', 'refsans', 'qmchannel', 'pgaa'
]

modules = ['nicos_mlz.puma.commands']

level = False

devices = dict(
    med = device('nicos_mlz.puma.devices.multidetector.PumaMultiDetectorLayout',
        description = 'PUMA multi detector',
        rotdetector = ['rd1', 'rd2', 'rd3', 'rd4', 'rd5', 'rd6', 'rd7', 'rd8',
                       'rd9', 'rd10', 'rd11'],
        rotguide = ['rg1', 'rg2', 'rg3', 'rg4', 'rg5', 'rg6', 'rg7', 'rg8',
                    'rg9', 'rg10', 'rg11'],
        att = device('nicos.devices.generic.Axis',
            motor = device('nicos_mlz.puma.devices.virtual.VirtualReferenceMotor',
                abslimits = (-90, 15),
                unit = 'deg',
                refpos = -1,
                fmtstr = '%.3f',
            ),
            precision = 0.01,
        ),
    ),
    mfvpg  = device('nicos_mlz.puma.devices.focus.FocusAxis',
        description = 'Vertical focus of PG-Monochromator',
        motor = device('nicos.devices.generic.VirtualMotor',
            unit = 'deg',
            abslimits = (-20, 55),
        ),
        uplimit = 38,
        lowlimit = 16.0,
        flatpos = 37,
        startpos = 38,
        precision = 0.1,
    ),
    mfhpg  = device('nicos_mlz.puma.devices.focus.FocusAxis',
        description = 'Horizontal focus of PG-Monochromator',
        motor = device('nicos.devices.generic.VirtualMotor',
            unit = 'deg',
            abslimits = (-20, 55),
        ),
        uplimit = 70,
        lowlimit = -12.0,
        flatpos = 4.668,
        startpos = -7.874,
        precision = 0.1,
    ),
    mono_pg002 = device('nicos.devices.tas.Monochromator',
        description = 'PG-002 monochromator',
        order = 1,
        unit = 'A-1',
        theta = 'mth',
        twotheta = 'mtt',
        reltheta = True,
        focush = None,  # 'mfhpg',
        focusv = None,  # 'mfvpg',
        # focus value should equal mth (for arcane reasons...)
        hfocuspars = [0.59065,7.33506,0.86068,-0.22745,0.02901],
        vfocuspars = [0.59065,7.33506,0.86068,-0.22745,0.02901],
        abslimits = (1, 7.5),
        dvalue = 3.355,
        scatteringsense = -1,
        crystalside = -1,
    ),
    monitor = device('nicos.devices.generic.VirtualCounter',
        description = 'Monitor',
        fmtstr = '%d',
        type = 'monitor',
        lowlevel = True,
    ),
    timer = device('nicos.devices.generic.VirtualTimer',
        description = 'timer',
        fmtstr = '%.2f',
        unit = 's',
        lowlevel = True,
    ),
    image = device('nicos.devices.generic.VirtualImage',
        description = 'Image data device',
        fmtstr = '%d',
        pollinterval = 86400,
        lowlevel = True,
        sizes = (1, 11),
    ),
    det = device('nicos.devices.generic.Detector',
        description = 'Multidetector with single channels',
        timers = ['timer'],
        monitors = ['monitor'],
        images = ['image'],
        # counters = ['ctr1', 'ctr2', 'ctr3', 'ctr4', 'ctr5',
        #             'ctr6', 'ctr7', 'ctr8', 'ctr9', 'ctr10',
        #             'ctr11'],
        maxage = 86400,
        pollinterval = None,
    ),
)

for i in range(11):
    devices['rd%d' % (i + 1)] = device('nicos.devices.generic.Axis',
        description = 'Rotation detector %d multidetector' % (i + 1),
        motor = device('nicos_mlz.puma.devices.virtual.VirtualReferenceMotor',
            abslimits = (-39 + (11 - (i + 1)) * 2.5, 11 - i * 2.5),
            unit = 'deg',
            refpos = -13.5 - i * 2.5,
            fmtstr = '%.3f',
            speed = 3,
        ),
        precision = 0.01,
        lowlevel = level,
    )
    devices['rg%d' % (i + 1)] = device('nicos.devices.generic.Axis',
        description = 'Rotation guide %d multidetector' % (i + 1),
        motor = device('nicos_mlz.puma.devices.virtual.VirtualReferenceMotor',
            abslimits = (-8, 25),
            unit = 'deg',
            refpos = -7.7,
            fmtstr = '%.3f',
            speed = 1,
        ),
        precision = 0.01,
        lowlevel = level,
    )
    devices['ctr%d' % (i + 1)] = device('nicos.devices.generic.VirtualCounter',
        lowlevel = True,
        type = 'counter',
        countrate = 1 + int(2000 * math.exp(-((i + 1) - 6) ** 2 / 2.)),
        fmtstr = '%d',
    )

startupcode = '''
SetDetectors(det)
'''