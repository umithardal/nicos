description = 'x-z detector table at beam TREFF with long x axis'

group = 'lowlevel'

excludes = ['short_table_treff', 'table_lab']

nethost = 'localhost'

devices = dict(
    mo_x = device('nicos.devices.taco.Motor',
        lowlevel = True,
        tacodevice = '//%s/del/table/xmot' % nethost,
        unit = 'mm',
        abslimits = (0, 972),
        userlimits = (0, 972),
    ),
    x = device('nicos.devices.generic.Axis',
        description = 'Detector table x axis',
        motor = 'mo_x',
        fmtstr = '%.3f',
        precision = 0.01,
    ),
    mo_y = device('nicos.devices.taco.Motor',
        lowlevel = True,
        tacodevice = '//%s/del/table/ymot' % nethost,
        unit = 'mm',
        abslimits = (0, 264.5),
        userlimits = (0, 264.5),
    ),
    y = device('nicos.devices.generic.Axis',
        description = 'Detector table y axis',
        motor = 'mo_y',
        fmtstr = '%.3f',
        precision = 0.01,
    ),
)
