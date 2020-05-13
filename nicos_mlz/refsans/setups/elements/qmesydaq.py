description = 'qmesydaq devices for REFSANS'

# to be included by refsans ?
group = 'lowlevel'

instrument_values = configdata('instrument.values')

nethost = instrument_values['nethost']
tacodev = '//%s/test/qmesydaq' % nethost

sysconfig = dict(
    datasinks = ['Listmode'],
)

devices = dict(
    # BerSANSFileSaver = device('nicos_mlz.sans1.devices.bersans.BerSANSImageSink',
    #     description = 'Saves image data in BerSANS format',
    #     filenametemplate = [
    #         'D%(pointcounter)07d.001', '/data_user/D%(pointcounter)07d.001'
    #     ],
    #     subdir = 'bersans',
    # ),
    Listmode = device('nicos_mlz.devices.qmesydaqsinks.ListmodeSink',
        description = 'Listmode data written via QMesyDAQ',
        image = 'image',
        subdir = 'list',
        filenametemplate = ['%(proposal)s_%(pointcounter)08d.mdat'],
    ),
    LiveViewSink = device('nicos.devices.datasinks.LiveViewSink',
        description = 'Sends image data to LiveViewWidget',
    ),
    mon1 = device('nicos.devices.vendor.qmesydaq.taco.Counter',
        description = 'QMesyDAQ Counter0',
        tacodevice = '%s/counter0' % tacodev,
        type = 'monitor',
    ),
    mon2 = device('nicos.devices.vendor.qmesydaq.taco.Counter',
        description = 'QMesyDAQ Counter1',
        tacodevice = '%s/counter0' % tacodev,
        type = 'monitor',
    ),
    # qm_ctr2 = device('nicos.devices.vendor.qmesydaq.taco.Counter',
    #     description = 'QMesyDAQ Counter2',
    #     tacodevice = '%s/counter2' % tacodev,
    #     type = 'monitor',
    # ),
    # qm_ctr3 = device('nicos.devices.vendor.qmesydaq.taco.Counter',
    #     description = 'QMesyDAQ Counter3',
    #     tacodevice = '%s/counter3' % tacodev,
    #     type = 'monitor',
    # ),
    # qm_ev = device('nicos.devices.vendor.qmesydaq.taco.Counter',
    #     description = 'QMesyDAQ Events channel',
    #     tacodevice = '%s/events' % tacodev,
    #     type = 'counter',
    # ),
    timer = device('nicos.devices.vendor.qmesydaq.taco.Timer',
        description = 'QMesyDAQ Timer',
        tacodevice = '%s/timer' % tacodev,
    ),
    image = device('nicos.devices.vendor.qmesydaq.taco.Image',
        description = 'QMesyDAQ Image',
        tacodevice = '%s/det' % tacodev,
    ),
    det = device('nicos.devices.generic.Detector',
        description = 'QMesyDAQ Image type Detector1',
        timers = ['timer'],
        monitors = ['mon1', 'mon2'],
        images = ['image'],
    ),
)

startupcode = '''
SetDetectors(det)
'''
