description = 'Simulated CARESS HWB Devices'

group = 'basic'

sysconfig = dict(
    instrument = 'VSTRESSI',
    datasinks = ['caresssink', 'yamlsink'],
)

includes = ['source',]

devices = dict(
    VSTRESSI = device('devices.instrument.Instrument',
                      description = 'Virtual STRESSI instrument',
                      responsible = 'R. Esponsible <r.esponsible@frm2.tum.de>',
                      instrument = 'V-Stress-Spec',
                      website = 'http://www.nicos-controls.org',
                      operators = ['NICOS developer team', ],
                      facility = 'NICOS demo instruments',
                      doi = 'http://dx.doi.org/10.17815/jlsrf-1-25',
                     ),
    tths = device('devices.generic.VirtualMotor',
                  description = 'Simulated HWB TTHS',
                  fmtstr = '%.2f',
                  unit = 'deg',
                  abslimits = (20, 130),
                 ),
    chism = device('devices.generic.VirtualMotor',
                   description = 'Simulated HWB CHIS Motor',
                   fmtstr = '%.2f',
                   unit = 'deg',
                   abslimits = (-180, 180),
                   lowlevel = True,
                  ),
    chis = device('devices.generic.axis.Axis',
                  description = 'Simulated HWB CHIS axis',
                  motor = 'chism',
                  coder = 'chism',
                  precision = 0.001,
                 ),
    phism = device('devices.generic.VirtualMotor',
                   description = 'Simulated HWB PHIS motor',
                   fmtstr = '%.2f',
                   unit = 'deg',
                   abslimits = (-720, 720),
                   lowlevel = True,
                  ),
    phis = device('devices.generic.axis.Axis',
                  description = 'Simulated HWB PHIS axis',
                  motor = 'phism',
                  coder = 'phism',
                  precision = 0.001,
                 ),
    omgs = device('devices.generic.VirtualMotor',
                  description = 'Simulated HWB OMGS',
                  fmtstr = '%.2f',
                  unit = 'deg',
                  abslimits = (-200, 200),
                 ),
    omgm = device('devices.generic.VirtualMotor',
                  description = 'Simulated HWB OMGM',
                  fmtstr = '%.2f',
                  unit = 'deg',
                  abslimits = (-200, 200),
                 ),
    tthm_r = device('stressi.wavelength.TransformedMoveable',
                    description = 'Base hardware device',
                    dev = 'tthm',
                    informula = '1./0.956 * x - 11.5 / 0.956',
                    outformula = '0.956 * x + 11.5',
                    precision = 0.001,
                    lowlevel = True,
                   ),
    tthm = device('devices.generic.VirtualMotor',
                  description = 'virtual HWB TTHM',
                  fmtstr = '%.2f',
                  unit = 'deg',
                  abslimits = (50, 100),
                 ),
    transm_m = device('devices.generic.VirtualMotor',
                      description = 'Simulated HWB TRANSM',
                      fmtstr = '%.2f',
                      unit = 'mm',
                      abslimits = (-200, 200),
                      lowlevel = True,
                     ),
    transm = device('devices.generic.Switcher',
                    description = 'Monochromator changer',
                    moveable = 'transm_m',
                    mapping = {'Si': 0.292, 'PG': 30.292, 'Ge': 60.292,},
                    # requires = {'level': 'admin'},
                    precision = 0.01,
                    unit = '',
                   ),
    xt = device('devices.generic.VirtualMotor',
                description = 'Simulated HWB XT',
                fmtstr = '%.2f',
                unit = 'mm',
                abslimits = (-120, 120),
               ),
    yt = device('devices.generic.VirtualMotor',
                description = 'Simulated HWB YT',
                fmtstr = '%.2f',
                unit = 'mm',
                abslimits = (-120, 120),
               ),
    zt = device('devices.generic.VirtualMotor',
                description = 'Simulated HWB ZT',
                fmtstr = '%.2f',
                unit = 'mm',
                abslimits = (-0, 300),
               ),
    mon = device('devices.generic.VirtualCounter',
                 description = 'Simulated HWB MON',
                 fmtstr = '%d',
                 type = 'monitor',
                 lowlevel = True,
                ),
    tim1 = device('devices.generic.VirtualTimer',
                  description = 'Simulated HWB TIM1',
                  fmtstr = '%.2f',
                  unit = 's',
                  lowlevel = True,
                 ),
    image = device('devices.generic.VirtualImage',
                   description = 'Image data device',
                   fmtstr = '%d',
                   pollinterval = 86400,
                   lowlevel = True,
                   sizes = (256, 256),
                  ),
    adet = device('devices.generic.Detector',
                  description = 'Classical detector with single channels',
                  timers = ['tim1'],
                  monitors = ['mon'],
                  counters = [],
                  images = ['image'],
                  pollinterval = None,
                  liveinterval = 0.5,
                 ),
    slits_u = device('devices.generic.VirtualMotor',
                 description = 'HWB SLITS_U',
                 fmtstr = '%.2f',
                 unit = 'mm',
                 abslimits = (-10, 43),
                 lowlevel = True,
                 ),
    slits_d = device('devices.generic.VirtualMotor',
                 description = 'HWB SLITS_D',
                 fmtstr = '%.2f',
                 unit = 'mm',
                 abslimits = (-43, 10),
                 lowlevel = True,
                 ),
    slits_l = device('devices.generic.VirtualMotor',
                 description = 'HWB SLITS_L',
                 fmtstr = '%.2f',
                 unit = 'mm',
                 abslimits = (-26, 10),
                 lowlevel = True,
                 ),
    slits_r = device('devices.generic.VirtualMotor',
                 description = 'HWB SLITS_R',
                 fmtstr = '%.2f',
                 unit = 'mm',
                 abslimits = (-10, 26),
                 lowlevel = True,
                 ),
    slits = device('stressi.slit.Slit',
                   description = 'sample slit 4 blades',
                   left = 'slits_l',
                   right = 'slits_r',
                   bottom = 'slits_d',
                   top = 'slits_u',
                   opmode = 'centered',
                   pollinterval = 5,
                   maxage = 10,
                  ),
    slitm_w = device('devices.generic.VirtualMotor',
                     description = 'HWB SLITM_W',
                     fmtstr = '%.2f',
                     unit = 'mm',
                     abslimits = (0, 100),
                     lowlevel = True,
                    ),
    slitm_h = device('devices.generic.VirtualMotor',
                     description = 'HWB SLITM_H',
                     fmtstr = '%.2f',
                     unit = 'mm',
                     abslimits = (0, 155),
                     lowlevel = True,
                    ),
    slitm = device('stressi.slit.TwoAxisSlit',
                   description = 'Monochromator entry slit',
                   horizontal = 'slitm_w',
                   vertical = 'slitm_h',
                  ),

    slite = device('devices.generic.VirtualMotor',
                   description = 'HWB SLITE',
                   fmtstr = '%.2f',
                   unit = 'mm',
                   abslimits = (0, 70),
                  ),
    wav = device('stressi.wavelength.Wavelength',
                 description = 'The incoming wavelength',
                 omgm = 'omgm',
                 crystal = 'transm',
                 plane = '',  # '100',
                 base = 'tthm_r',
                 unit = 'AA',
                 fmtstr = '%.2f',
                 abslimits = (0.9, 2.5),
                ),
    ysd = device('devices.generic.ManualMove',
                 description = 'distance sample detector',
                 default = 100.,
                 fmtstr = '%.2f',
                 unit = 'mm',
                 abslimits = (0, 1100.),
                ),
    psz = device('devices.generic.VirtualMotor',
                 description = 'HWB PSZ',
                 fmtstr = '%.2f',
                 unit = 'mm',
                 abslimits = (-100., 100),
                ),
    psh = device('devices.generic.VirtualMotor',
                 description = 'HWB PSH',
                 fmtstr = '%.2f',
                 unit = 'mm',
                 abslimits = (-100., 100),
                ),
    pst = device('devices.generic.VirtualMotor',
                 description = 'HWB PST',
                 fmtstr = '%.2f',
                 unit = 'mm',
                 abslimits = (-100., 100),
                ),
    psw = device('devices.generic.VirtualMotor',
                 description = 'HWB PSw',
                 fmtstr = '%.2f',
                 unit = 'mm',
                 abslimits = (-100., 100),
                ),
    mot1 = device('devices.generic.VirtualMotor',
                  description = 'HWB MOT1',
                  fmtstr = '%.2f',
                  unit = 'mm',
                  abslimits = (-200., 200),
                 ),
    m1_foc = device('devices.generic.VirtualMotor',
                    description = 'HWB M1_FOC',
                    fmtstr = '%.2f',
                    unit = 'steps',
                    abslimits = (0, 4096),
                   ),
    m3_foc = device('devices.generic.VirtualMotor',
                    description = 'HWB M3_FOC',
                    fmtstr = '%.2f',
                    unit = 'steps',
                    abslimits = (0, 4096),
                   ),
    caresssink = device('stressi.datasinks.CaressScanfileSink',
                        lowlevel = True,
                        filenametemplate = ['m2%(scancounter)08d.dat'],
                       ),
    yamlsink = device('stressi.datasinks.YamlDatafileSink',
                      lowlevel = True,
                      filenametemplate = ['m2%(scancounter)08d.yaml'],
                     ),
    hv1   = device('devices.generic.VirtualMotor',
                   description = 'ISEG HV power supply 1',
                   requires = {'level': 'admin'},
                   abslimits = (0, 3200),
                   speed = 2,
                   fmtstr = '%.1f',
                   unit = 'V',
                  ),
    hv2   = device('devices.generic.VirtualMotor',
                   description = 'ISEG HV power supply 2',
                   requires = {'level': 'admin'},
                   abslimits = (-2500, 0),
                   speed = 2,
                   fmtstr = '%.1f',
                   unit = 'V',
                  ),
    omgs_osc = device('devices.generic.oscillator.Oscillator',
                      description = 'Oscillation of OMGS',
                      moveable = 'omgs',
                     ),
#   histogram = device('frm2.qmesydaqsinks.HistogramFileFormat',
#                      description = 'Histogram data written via QMesyDAQ',
#                      image = 'image',
#                     ),
#   listmode = device('frm2.qmesydaqsinks.ListmodeFileFormat',
#                     description = 'Listmode data written via QMesyDAQ',
#                     image = 'image',
#                    ),
)

startupcode = '''
SetDetectors(adet)
'''
