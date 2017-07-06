description = 'setup for the astrium velocity selector'

group = 'lowlevel'

tango_base = 'tango://kompasshw.kompass.frm2:10000/kompass/'

devices = dict(
    selector_rpm = device('nicos.devices.tango.WindowTimeoutAO',
                          description = 'Selector speed control',
                          tangodevice = tango_base + 'selector/speed',
                          abslimits = (3100, 28300),
                          unit = 'rpm',
                          fmtstr = '%.0f',
                          timeout = 600,
                          warnlimits = (3099, 28300),
                          precision = 10,
                          comdelay = 30,
                          maxage = 35,
                         ),
    selector_lambda = device('nicos.devices.vendor.astrium.SelectorLambda',
                             description = 'Selector center wavelength control',
                             seldev = 'selector_rpm',
                             unit = 'A',
                             fmtstr = '%.2f',
                             twistangle = 23.50,
                             length = 0.25,
                             beamcenter = 0.115,
                             maxspeed = 28300,
                             maxage = 35,
                            ),
    # selector_sspeed = device('nicos.devices.tango.AnalogInput',
    #                          description = 'Selector speed read out by optical sensor',
    #                          tangodevice= tango_base + 'selector/sspeed',
    #                          unit = 'Hz',
    #                          fmtstr = '%.1d',
    #                          maxage = 35,
    #                         ),
    selector_vacuum = device('nicos.devices.tango.AnalogInput',
                             description = 'Vacuum in the selector',
                             tangodevice= tango_base + 'selector/vacuum',
                             unit = 'e-3 mbar',
                             fmtstr = '%.5f',
                             warnlimits = (0, 0.008), # selector shuts down above 0.005
                             maxage = 35,
                            ),
    selector_rtemp = device('nicos.devices.tango.AnalogInput',
                            description = 'Temperature of the selector',
                            tangodevice= tango_base + 'selector/rotortemp',
                            unit = 'C',
                            fmtstr = '%.1f',
                            warnlimits = (10, 45),
                            maxage = 35,
                           ),
    selector_wflow = device('nicos.devices.tango.AnalogInput',
                            description = 'Cooling water flow rate through selector',
                            tangodevice= tango_base + 'selector/flowrate',
                            unit = 'l/min',
                            fmtstr = '%.1f',
                            warnlimits = (2.3, 10),#without rot temp sensor; old value (2.5, 10)
                            maxage = 35,
                           ),
    selector_winlt = device('nicos.devices.tango.AnalogInput',
                            description = 'Cooling water temperature at inlet',
                            tangodevice= tango_base + 'selector/waterintemp',
                            unit = 'C',
                            fmtstr = '%.1f',
                            warnlimits = (15, 28),
                            maxage = 35,
                           ),
    selector_woutt = device('nicos.devices.tango.AnalogInput',
                            description = 'Cooling water temperature at outlet',
                            tangodevice= tango_base + 'selector/waterouttemp',
                            unit = 'C',
                            fmtstr = '%.1f',
                            warnlimits = (15, 28),
                            maxage = 35,
                           ),
    selector_vibrt = device('nicos.devices.tango.AnalogInput',
                            description = 'Selector vibration',
                            tangodevice= tango_base + 'selector/vibration',
                            unit = 'mm/s',
                            fmtstr = '%.2f',
                            warnlimits = (0, 1),
                            maxage = 35,
                           ),
)
