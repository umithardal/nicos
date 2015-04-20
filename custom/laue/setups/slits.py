description = 'Manual slits'
group = 'lowlevel'

devices = dict(
   sampleslit =  device('devices.generic.manual.ManualSwitch',
                        description = 'samples slit',
                        states = [1, 2, 3, 4, 5, 6, 7, 8],
                        unit = "mm",
                        fmtstr = '%.0f'),
)
