description = 'analyzer table'

devices = dict(
#    ath      = device('nicos.taco.Axis',
#                      description = 'analyzer theta',
#                      tacodevice = 'mira/axis/ath',
#                      abslimits = (90 - 90, 90 + 90),
#                      fmtstr = '%.3f',
#                      offset = 90.0),

    ath_co   = device('nicos.taco.Coder', tacodevice='mira/encoder/ath', lowlevel = True),
    ath_mo   = device('nicos.taco.Motor', tacodevice='mira/motor/ath', abslimits = (0, 180), lowlevel = True),
    ath      = device('nicos.generic.Axis', coder = 'ath_co', motor = 'ath_mo', obs = [], precision = 0.005,
                      ),


    att      = device('nicos.taco.HoveringAxis',
                      description = 'analyzer two-theta',
                      tacodevice = 'mira/axis/att',
                      abslimits = (-90 - 135, -90 + 135),
                      startdelay = 1,
                      stopdelay = 2,
                      switch = 'air_ana',
                      switchvalues = (0, 1),
                      fmtstr = '%.3f'),

#    att      = device('nicos.taco.Axis',
#                      description = 'analyzer two-theta',
#                      tacodevice = 'mira/axis/att',
#                      abslimits = (-90 - 135, -90 + 135),
#                      fmtstr = '%.2f',
#                      offset = -90.0),
    vatt     = device('nicos.generic.VirtualMotor',
                      abslimits = (-180, 180),
                      unit = 'deg'),

    ana      = device('nicos.tas.Monochromator',
                      unit = 'A-1',
                      theta = 'ath',
                      twotheta = 'att',
                      focush = None,
                      focusv = None,
                      abslimits = (0, 10),
                      dvalue = 3.355,
                      scatteringsense = -1),

#    adr      = device('nicos.taco.Axis',
#                      description = 'analyzer detector rotation',
#                      tacodevice = 'mira/axis/adr',
#                      abslimits = (-180, 180),
#                      fmtstr = '%.3f'),
)
