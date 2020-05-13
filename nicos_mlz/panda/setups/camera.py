description = 'Neutron camera'
group = 'optional'

tango_base = 'tango://phys.panda.frm2:10000/panda/'

sysconfig = dict(
    datasinks = ['tifformat'],
)

devices = dict(
    camtimer = device('nicos.devices.tango.TimerChannel',
        description = 'Timer for the neutron camera',
        tangodevice = tango_base + 'atikccd/timer',
    ),
    camimage = device('nicos_mlz.devices.camera.CameraImage',
        description = 'Image for the neutron camera',
        tangodevice = tango_base + 'atikccd/image',
    ),
    ctr1 = device('nicos.devices.generic.RectROIChannel',
        description = 'Virtual tube 1',
    ),
    ctr2 = device('nicos.devices.generic.RectROIChannel',
        description = 'Virtual tube 2',
    ),
    ctr3 = device('nicos.devices.generic.RectROIChannel',
        description = 'Virtual tube 3',
    ),
    ctr4 = device('nicos.devices.generic.RectROIChannel',
        description = 'Virtual tube 4',
    ),
    ctr5 = device('nicos.devices.generic.RectROIChannel',
        description = 'Virtual tube 5',
    ),
    ctr6 = device('nicos.devices.generic.RectROIChannel',
        description = 'Virtual tube 6',
    ),
    ctr7 = device('nicos.devices.generic.RectROIChannel',
        description = 'Virtual tube 7',
    ),
    ctr8 = device('nicos.devices.generic.RectROIChannel',
        description = 'Virtual tube 8',
    ),
    cam = device('nicos.devices.generic.Detector',
        description = 'NeutronOptics camera',
        timers = ['camtimer'],
        counters = [
            'ctr1', 'ctr2', 'ctr3', 'ctr4', 'ctr5', 'ctr6', 'ctr7', 'ctr8'
        ],
        images = ['camimage'],
        postprocess = [
            ('ctr1', 'camimage'), ('ctr2', 'camimage'), ('ctr3', 'camimage'),
            ('ctr4', 'camimage'), ('ctr5', 'camimage'), ('ctr6', 'camimage'),
            ('ctr7', 'camimage'), ('ctr8', 'camimage')
        ],
    ),
    cam_temp = device('nicos.devices.tango.AnalogOutput',
        description = 'Temperature of neutron camera',
        tangodevice = tango_base + 'atikccd/cooling',
    ),
    tifformat = device('nicos.devices.datasinks.TIFFImageSink',
        description = 'saves image data in TIFF format',
        filenametemplate = ['%(proposal)s_%(pointcounter)08d.tiff'],
        mode = 'I',
    ),
)
