description = 'sample table devices'

includes = []

nethost = 'pgaasrv.pgaa.frm2'

devices = dict(
    sample_motor = device('devices.taco.motor.Motor',
                          description = 'Motor to change the sample position',
                          tacodevice = '//%s/pgaa/pgaa/sample' % (nethost,),
                          fmtstr = '%.1f',
                          abslimits = (-5, 356),
                          lowlevel = False,
                         ),
    samplepos = device('devices.generic.Switcher',
                       description = 'Sample switcher',
                       moveable = 'sample_motor',
                       mapping  = {'1' : 4.00,
                                   '2' : 74.00,
                                   '3' : 144.00,
                                   '4' : 214.00,
                                   '5' : 284.00,
                                   '6' : 354.00,
                                  },
                       precision = 0.1,
                       blockingmove = False,
                       unit = '',
                      ),
#   e1    = device('devices.taco.Coder',
#                  description = '',
#                  tacodevice = '//%s/pgaa/phytronixe/e1' % (nethost,),
#                  fmtstr = '%7.3f',
#                 ),
#   ellip = device('devices.taco.DigitalInput',
#                  description = '',
#                  tacodevice = '//%s/pgaa/pgai/ellip' % (nethost,),
#                 ),
#   ftube = device('devices.taco.DigitalInput',
#                  description = '',
#                  tacodevice = '//%s/pgaa/pgai/ftube' % (nethost,),
#                 ),
#   press1 = device('devices.taco.DigitalInput',
#                   description = '',
#                   tacodevice = '//%s/pgaa/pgai/press1' % (nethost,),
#                  ),
#   press2 = device('devices.taco.DigitalInput',
#                   description = '',
#                   tacodevice = '//%s/pgaa/pgai/press2' % (nethost,),
#                  ),
)
