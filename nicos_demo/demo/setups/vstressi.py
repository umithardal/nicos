description = 'Virtual STRESS-SPEC instrument'

group = 'basic'

sysconfig = dict(
    instrument = 'VSTRESSI',
    datasinks = ['caresssink', 'yamlsink'],
)

includes = ['source']

devices = dict(
    VSTRESSI = device('nicos.devices.instrument.Instrument',
        description = 'Virtual STRESSI instrument',
        responsible = 'R. Esponsible <r.esponsible@frm2.tum.de>',
        instrument = 'V-Stress-Spec',
        website = 'http://www.nicos-controls.org',
        operators = ['NICOS developer team'],
        facility = 'NICOS demo instruments',
        doi = 'http://dx.doi.org/10.17815/jlsrf-1-25',
    ),
    tths = device('nicos.devices.generic.VirtualMotor',
        description = 'Simulated TTHS',
        fmtstr = '%.2f',
        unit = 'deg',
        abslimits = (20, 130),
    ),
    chism = device('nicos.devices.generic.VirtualMotor',
        description = 'Simulated CHIS motor',
        fmtstr = '%.2f',
        unit = 'deg',
        abslimits = (-180, 180),
        lowlevel = True,
    ),
    chis = device('nicos.devices.generic.Axis',
        description = 'Simulated CHIS axis',
        motor = 'chism',
        coder = 'chism',
        precision = 0.001,
    ),
    phism = device('nicos.devices.generic.VirtualMotor',
        description = 'Simulated PHIS motor',
        fmtstr = '%.2f',
        unit = 'deg',
        abslimits = (-720, 720),
        lowlevel = True,
    ),
    phis = device('nicos.devices.generic.Axis',
        description = 'Simulated PHIS axis',
        motor = 'phism',
        coder = 'phism',
        precision = 0.001,
    ),
    omgs = device('nicos.devices.generic.VirtualMotor',
        description = 'Simulated OMGS',
        fmtstr = '%.2f',
        unit = 'deg',
        abslimits = (-200, 200),
    ),
    omgm = device('nicos.devices.generic.VirtualMotor',
        description = 'Simulated OMGM',
        fmtstr = '%.2f',
        unit = 'deg',
        abslimits = (-200, 200),
    ),
    tthm_r = device('nicos_mlz.stressi.devices.wavelength.TransformedMoveable',
        description = 'Base hardware device',
        dev = 'tthm',
        informula = '1./0.956 * x - 11.5 / 0.956',
        outformula = '0.956 * x + 11.5',
        precision = 0.001,
        lowlevel = True,
    ),
    tthm = device('nicos.devices.generic.VirtualMotor',
        description = 'virtual TTHM',
        fmtstr = '%.2f',
        unit = 'deg',
        abslimits = (50, 100),
    ),
    transm_m = device('nicos.devices.generic.VirtualMotor',
        description = 'Simulated TRANSM',
        fmtstr = '%.2f',
        unit = 'mm',
        abslimits = (-200, 200),
        lowlevel = True,
    ),
    transm = device('nicos.devices.generic.Switcher',
        description = 'Monochromator changer',
        moveable = 'transm_m',
        mapping = {'Si': 0.292, 'PG': 30.292, 'Ge': 60.292,},
        # requires = {'level': 'admin'},
        precision = 0.01,
        unit = '',
    ),
    xt = device('nicos.devices.generic.VirtualMotor',
        description = 'Simulated XT',
        fmtstr = '%.2f',
        unit = 'mm',
        abslimits = (-120, 120),
    ),
    yt = device('nicos.devices.generic.VirtualMotor',
        description = 'Simulated YT',
        fmtstr = '%.2f',
        unit = 'mm',
        abslimits = (-120, 120),
    ),
    zt = device('nicos.devices.generic.VirtualMotor',
        description = 'Simulated ZT',
        fmtstr = '%.2f',
        unit = 'mm',
        abslimits = (-0, 300),
    ),
    mon = device('nicos.devices.generic.VirtualCounter',
        description = 'Simulated MON',
        fmtstr = '%d',
        type = 'monitor',
        lowlevel = True,
    ),
    tim1 = device('nicos.devices.generic.VirtualTimer',
        description = 'Simulated TIM1',
        fmtstr = '%.2f',
        unit = 's',
        lowlevel = True,
    ),
    image = device('nicos.devices.generic.VirtualImage',
        description = 'Image data device',
        fmtstr = '%d',
        pollinterval = 86400,
        lowlevel = True,
        sizes = (256, 256),
    ),
    adet = device('nicos.devices.generic.Detector',
        description = 'Classical detector with single channels',
        timers = ['tim1'],
        monitors = ['mon'],
        counters = [],
        images = ['image'],
        pollinterval = None,
        liveinterval = 0.5,
    ),
    slits_u = device('nicos.devices.generic.VirtualMotor',
        description = 'SLITS_U',
        fmtstr = '%.2f',
        unit = 'mm',
        abslimits = (-10, 43),
        lowlevel = True,
    ),
    slits_d = device('nicos.devices.generic.VirtualMotor',
        description = 'SLITS_D',
        fmtstr = '%.2f',
        unit = 'mm',
        abslimits = (-43, 10),
        lowlevel = True,
    ),
    slits_l = device('nicos.devices.generic.VirtualMotor',
        description = 'SLITS_L',
        fmtstr = '%.2f',
        unit = 'mm',
        abslimits = (-26, 10),
        lowlevel = True,
    ),
    slits_r = device('nicos.devices.generic.VirtualMotor',
        description = 'SLITS_R',
        fmtstr = '%.2f',
        unit = 'mm',
        abslimits = (-10, 26),
        lowlevel = True,
    ),
    slits = device('nicos_mlz.stressi.devices.slit.Slit',
        description = 'sample slit 4 blades',
        left = 'slits_l',
        right = 'slits_r',
        bottom = 'slits_d',
        top = 'slits_u',
        opmode = 'centered',
        pollinterval = 5,
        maxage = 10,
    ),
    slitm_w = device('nicos.devices.generic.VirtualMotor',
        description = 'SLITM_W',
        fmtstr = '%.2f',
        unit = 'mm',
        abslimits = (0, 100),
        lowlevel = True,
    ),
    slitm_h = device('nicos.devices.generic.VirtualMotor',
        description = 'SLITM_H',
        fmtstr = '%.2f',
        unit = 'mm',
        abslimits = (0, 155),
        lowlevel = True,
    ),
    slitm = device('nicos_mlz.stressi.devices.slit.TwoAxisSlit',
        description = 'Monochromator entry slit',
        horizontal = 'slitm_w',
        vertical = 'slitm_h',
    ),

    slite = device('nicos.devices.generic.VirtualMotor',
        description = 'SLITE',
        fmtstr = '%.2f',
        unit = 'mm',
        abslimits = (0, 70),
    ),
    wav = device('nicos_mlz.stressi.devices.wavelength.Wavelength',
        description = 'The incoming wavelength',
        omgm = 'omgm',
        crystal = 'transm',
        plane = '',  # '100',
        base = 'tthm_r',
        unit = 'AA',
        fmtstr = '%.2f',
        abslimits = (0.9, 2.5),
    ),
    ysd = device('nicos.devices.generic.ManualMove',
        description = 'distance sample detector',
        default = 100.,
        fmtstr = '%.2f',
        unit = 'mm',
        abslimits = (0, 1100.),
    ),
    psz = device('nicos.devices.generic.VirtualMotor',
        description = 'PSZ',
        fmtstr = '%.2f',
        unit = 'mm',
        abslimits = (-100., 100),
    ),
    psh = device('nicos.devices.generic.VirtualMotor',
        description = 'PSH',
        fmtstr = '%.2f',
        unit = 'mm',
        abslimits = (-100., 100),
    ),
    pst = device('nicos.devices.generic.VirtualMotor',
        description = 'PST',
        fmtstr = '%.2f',
        unit = 'mm',
        abslimits = (-100., 100),
    ),
    psw = device('nicos.devices.generic.VirtualMotor',
        description = 'PSw',
        fmtstr = '%.2f',
        unit = 'mm',
        abslimits = (-100., 100),
    ),
    mot1 = device('nicos.devices.generic.VirtualMotor',
        description = 'MOT1',
        fmtstr = '%.2f',
        unit = 'mm',
        abslimits = (-200., 200),
    ),
    m1_foc = device('nicos.devices.generic.VirtualMotor',
        description = 'M1_FOC',
        fmtstr = '%.2f',
        unit = 'steps',
        abslimits = (0, 4096),
    ),
    m3_foc = device('nicos.devices.generic.VirtualMotor',
        description = 'M3_FOC',
        fmtstr = '%.2f',
        unit = 'steps',
        abslimits = (0, 4096),
    ),
    caresssink = device('nicos_mlz.stressi.devices.datasinks.CaressScanfileSink',
        lowlevel = True,
        filenametemplate = ['m2%(scancounter)08d.dat'],
    ),
    yamlsink = device('nicos_mlz.stressi.devices.datasinks.YamlDatafileSink',
        lowlevel = True,
        filenametemplate = ['m2%(scancounter)08d.yaml'],
    ),
    hv1 = device('nicos.devices.generic.VirtualMotor',
        description = 'HV power supply 1',
        requires = {'level': 'admin'},
        abslimits = (0, 3200),
        speed = 2,
        fmtstr = '%.1f',
        unit = 'V',
    ),
    hv2 = device('nicos.devices.generic.VirtualMotor',
        description = 'HV power supply 2',
        requires = {'level': 'admin'},
        abslimits = (-2500, 0),
        speed = 2,
        fmtstr = '%.1f',
        unit = 'V',
    ),
    omgs_osc = device('nicos.devices.generic.Oscillator',
        description = 'Oscillation of OMGS',
        moveable = 'omgs',
        unit = '',
    ),
    # histogram = device('nicos_mlz.frm2.devices.qmesydaqsinks.HistogramFileFormat',
    #     description = 'Histogram data written via QMesyDAQ',
    #     image = 'image',
    # ),
    # listmode = device('nicos_mlz.frm2.devices.qmesydaqsinks.ListmodeFileFormat',
    #     description = 'Listmode data written via QMesyDAQ',
    #     image = 'image',
    # ),
)

startupcode = '''
SetDetectors(adet)
'''
