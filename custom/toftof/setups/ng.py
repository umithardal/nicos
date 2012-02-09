description = 'elliptical neutron guide nose'
includes = ['system']

nethost= '//toftofsrv.toftof.frm2/'

devices = dict(
    ng_left    = device('nicos.taco.motor.Motor',
                   tacodevice = nethost + 'toftof/pm/motleft',
                   fmtstr = "%7.3f",
                   abslimits = (-20000.0, 20000.)),
    ng_right    = device('nicos.taco.motor.Motor',
                   tacodevice = nethost + 'toftof/pm/motright',
                   fmtstr = "%7.3f",
                   abslimits = (-20000.0, 20000.)),
    ng_bottom    = device('nicos.taco.motor.Motor',
                   tacodevice = nethost + 'toftof/pm/motbottom',
                   fmtstr = "%7.3f",
                   abslimits = (-20000.0, 20000.)),
    ng_top   = device('nicos.taco.motor.Motor',
                   tacodevice = nethost + 'toftof/pm/mottop',
                   fmtstr = "%7.3f",
                   abslimits = (-20000.0, 20000.)),
)
