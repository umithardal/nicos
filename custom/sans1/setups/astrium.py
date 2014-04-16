description = 'setup for the velocity selector'

group = 'lowlevel'

tacodevice = '//sans1srv/sans1/network/selector'

devices = dict(
    selector_state = device('devices.vendor.astrium.SelectorState',
                      tacodevice = tacodevice,
                      lowlevel = True,
                      pollinterval = 10,
                      maxage = 12,
                     ),
    selector_rpm = device('devices.vendor.astrium.SelectorSpeed',
                      description = 'Selector speed control',
                      tacodevice = tacodevice,
                      abslimits = (3000, 28300),
                      statedev = 'selector_state',
                      unit = 'rpm',
                      fmtstr = '%.0f',
                      precision = 50,
                      timeout = 600,
                      warnlimits = (0, 3000),
                      blockedspeeds = [(3500, 4200), (9500, 10000)],
                     ),
    selector_lambda = device('devices.vendor.astrium.SelectorLambda',
                      description = 'Selector center wavelength control',
                      seldev = 'selector_rpm',
                      unit = 'A',
                      fmtstr = '%.2f',
                      twistangle = 48.27,
                      length = 0.25,
                      beamcenter = 0.115, # antares value!, sans1 value unknown
                      maxspeed = 28300,
                     ),
    selector_sspeed = device('devices.vendor.astrium.SelectorValue',
                      description = 'Selector speed read out by optical sensor',
                      statedev = 'selector_state',
                      valuename = 'SSPEED',
                      unit = 'Hz',
                      fmtstr = '%.1d',
                     ),
    selector_vacuum = device('devices.vendor.astrium.SelectorValue',
                      description = 'Vacuum in the selector',
                      statedev = 'selector_state',
                      valuename = 'VACUM',
                      unit = 'x1e-3 mbar',
                      fmtstr = '%.5f',
                      warnlimits = (0, 0.001), # selector shuts down above 0.005
                     ),
    selector_rtemp = device('devices.vendor.astrium.SelectorValue',
                      description = 'Temperature of the selector',
                      statedev = 'selector_state',
                      valuename = 'RTEMP',
                      unit = 'C',
                      fmtstr = '%.1f',
                      warnlimits = (10, 45),
                     ),
    selector_wflow = device('devices.vendor.astrium.SelectorValue',
                      description = 'Cooling water flow rate through selector',
                      statedev = 'selector_state',
                      valuename = 'WFLOW',
                      unit = 'l/min',
                      fmtstr = '%.1f',
                      warnlimits = (1.5, 10),
                     ),
    selector_winlt = device('devices.vendor.astrium.SelectorValue',
                      description = 'Cooling water temperature at inlet',
                      statedev = 'selector_state',
                      valuename = 'WINLT',
                      unit = 'C',
                      fmtstr = '%.1f',
                      warnlimits = (15, 20),
                     ),
    selector_woutt = device('devices.vendor.astrium.SelectorValue',
                      description = 'Cooling water temperature at outlet',
                      statedev = 'selector_state',
                      valuename = 'WOUTT',
                      unit = 'C',
                      fmtstr = '%.1f',
                      warnlimits = (15, 20),
                     ),
    selector_vibrt = device('devices.vendor.astrium.SelectorValue',
                      description = 'Selector vibration',
                      statedev = 'selector_state',
                      valuename = 'VIBRT',
                      unit = 'mm/s',
                      fmtstr = '%.2f',
                      warnlimits = (0, 1),
                     ),
)
