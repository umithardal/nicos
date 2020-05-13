#  -*- coding: utf-8 -*-

description = '3He detector'
group = 'optional'
includes = ['det_base']
excludes = ['det_cascade']

taco_base = '//resedasrv/reseda'
tango_base = 'tango://resedahw2.reseda.frm2:10000/reseda'

devices = dict(
    scandet = device('nicos_mlz.reseda.devices.scandet.ScanningDetector',
        description = 'Scanning detector for scans per echotime',
        scandev = 'nse1',
        detector = 'det',
        maxage = 2,
        pollinterval = 0.5,
    ),
    det = device('nicos.devices.generic.Detector',
        description = 'FRM II multichannel counter card',
        timers = ['timer'],
        monitors = ['monitor1', ],
        counters = ['counter'],
        fmtstr = 'timer %s, monitor1 %s, ctr %s',
        maxage = 2,
        pollinterval = 0.5,
    ),
    det_hv = device('nicos.devices.tango.PowerSupply',
        description = 'High voltage power supply of the 3he detector',
        tangodevice = '%s/3he_det/hv' % tango_base,
        abslimits = (0, 1350),
        unit = 'V',
    ),
    det_rot_mot = device('nicos.devices.tango.Motor',
        description = 'Detector rotation (motor)',
        tangodevice = '%s/3he_det/rot' % tango_base,
        fmtstr = '%.3f',
        lowlevel = True,
        unit = 'deg',
    ),
    det_rot_enc = device('nicos.devices.taco.Coder',
        description = 'Detector rotation (encoder)',
        tacodevice = '%s/enc/det2_1' % taco_base,
        fmtstr = '%.3f',
        lowlevel = True,
        unit = 'deg',
    ),
    det_rot = device('nicos.devices.generic.Axis',
        description = 'Detector rotation',
        motor = 'det_rot_mot',
        coder = 'det_rot_enc',
        fmtstr = '%.3f',
        precision = 0.1,
        unit = 'deg',
    ),
    det_x = device('nicos.devices.tango.Motor',
        description = 'Detector x translation (motor)',
        tangodevice = '%s/3he_det/x' % tango_base,
        fmtstr = '%.1f',
        unit = 'mm',
    ),
    det_y = device('nicos.devices.tango.Motor',
        description = 'Detector y translation (motor)',
        tangodevice = '%s/3he_det/y' % tango_base,
        fmtstr = '%.1f',
        unit = 'mm'
    ),
)

startupcode = '''
SetDetectors(det)
'''
