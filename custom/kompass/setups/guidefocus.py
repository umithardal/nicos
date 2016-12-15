description = 'Neutron guide focussing devices'

group = 'lowlevel'

nethost = 'kompasshw.kompass.frm2'

devices = dict(
    lguide_m = device('devices.taco.Motor',
                      description = 'Long table motor',
                      tacodevice = '//%s/kompass/ltable/motor' % nethost,
                      abslimits = (-1000, 1000),
                      fmtstr = '%.4f',
                      lowlevel = True,
                     ),
    lguide_c = device('devices.taco.Coder',
                      description = 'Long table coder',
                      tacodevice = '//%s/kompass/ltable/coder' % nethost,
                      fmtstr = '%.4f',
                      lowlevel = True,
                     ),
    lguide = device('devices.generic.Axis',
                    description = 'Long table position',
                    motor = 'lguide_m',
                    coder = 'lguide_c',
                    fmtstr = '%.4f',
                    precision = 0.001,
                   ),
    sguide_m = device('devices.taco.Motor',
                      description = 'Short table motor',
                      tacodevice = '//%s/kompass/stable/motor' % nethost,
                      abslimits = (-1000, 1000),
                      fmtstr = '%.4f',
                      lowlevel = True,
                     ),
    sguide_c = device('devices.taco.Coder',
                      description = 'Short table coder',
                      tacodevice = '//%s/kompass/stable/coder' % nethost,
                      fmtstr = '%.4f',
                      lowlevel = True,
                     ),
    sguide = device('devices.generic.Axis',
                    description = 'Short table position',
                    motor = 'sguide_m',
                    coder = 'sguide_c',
                    fmtstr = '%.4f',
                    precision = 0.001,
                   ),
    guide = device('devices.generic.MultiSwitcher',
                   description = 'Neutron guide selector',
                   moveables = ['sguide', 'lguide'],
                   mapping = {'straight': [0., 0.],
                              'focussing': [1., 1.],
                              },
                   fallback = 'undefined',
                   fmtstr = '%s',
                   precision = [0.05, 0.05],
                   blockingmove = False,
                   lowlevel = False,
                   unit = '',
                  ),
)
