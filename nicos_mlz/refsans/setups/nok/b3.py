description = 'B3 aperture devices'

group = 'optional'

lprecision = 0.01


# b3 not in full function, therefore copy of b1
if False:
    uribase = 'tango://refsansctrl01.refsans.frm2:10000/refsans/b3/'
    devices = dict(
        b3_m1 = device('nicos.devices.tango.Actuator',
            tangodevice = uribase + '_blende_b3_m1',
            lowlevel = True,
        ),
        b3_m2 = device('nicos.devices.tango.Actuator',
            tangodevice = uribase + '_blende_b3_m2',
            lowlevel = True,
        ),
        b3_m3 = device('nicos.devices.tango.Actuator',
            tangodevice = uribase + '_blende_b3_m3',
            lowlevel = True,
        ),
        b3_m4 = device('nicos.devices.tango.Actuator',
            tangodevice = uribase + '_blende_b3_m4',
            lowlevel = True,
        ),
        b3 = device('nicos.devices.generic.Slit',
            description = 'B3 aperture',
            top = 'b3_m4',
            bottom = 'b3_m3',
            left = 'b3_m1',
            right = 'b3_m2',
            coordinates = 'opposite',
            opmode = '4blades',
        ),
    )
else:
    nethost = 'refsanssrv.refsans.frm2'
    devices = dict(
        b3 = device('nicos_mlz.refsans.devices.nok_support.DoubleSlitSequence',
            description = 'b3 and h3 inside Samplechamber',
            fmtstr = '%.3f mm, %.3f mm',
            unit = '',
            nok_start = -1,
            nok_length = -1,
            nok_end = -1,
            nok_gap = -1,
            inclinationlimits = (-1000, 1000),
            masks = dict(
                slit = [84.044, 50.4169, 0.10, 16.565],
                pinhole = [84.044, 50.4169, 0.00, 45.22],
                gisans = [84.044, 50.4169, 0.00, 45.22],
            ),
            slit_r = 'b3r',
            slit_s = 'b3s',
            # nok_motor = [-1, -1],
        ),
        b3_mode = device('nicos.devices.generic.ReadonlyParamDevice',
            description = 'b3 mode',
            device = 'b3',
            parameter = 'mode',
        ),
        b3r = device('nicos_mlz.refsans.devices.slits.SingleSlit',
           description = 'b3 slit, reactor side',
           lowlevel = True,
           motor = 'b3_rm',
           nok_start = -1,
           nok_length =-1,
           nok_end = -1,
           nok_gap = -1,
           masks = {
               'slit': 36.32,
               'point': 36.32,
               'gisans': 36.32,
           },
           unit = 'mm',
        ),
        b3s = device('nicos_mlz.refsans.devices.slits.SingleSlit',
           description = 'b3 slit, sample side',
           lowlevel = True,
           motor = 'b3_sm',
           nok_start = -1,
           nok_length =-1,
           nok_end = -1,
           nok_gap = -1,
           masks = {
               'slit': 36.404,
               'point': 36.404,
               'gisans': 36.404,
           },
           unit = 'mm',
        ),
        b3_rm = device('nicos_mlz.refsans.devices.beckhoff.nok.BeckhoffMotorCab1M0x',
            description = 'tbd',
            tacodevice = '//%s/test/modbus/probenort'% (nethost,),
            address = 0x3214+3*10, # decimal 12820
            slope = -10000,
            unit = 'mm',
            abslimits = (-393.0, 330.0),
            ruler = -200.0,
            lowlevel = True,
        ),
        b3_r = device('nicos.devices.generic.Axis',
            description = 'b3, reactorside',
            motor = 'b3_rm',
            coder = 'b3_rm',
            offset = 0.0,
            precision = lprecision,
            lowlevel = True,
        ),
        b3_sm = device('nicos_mlz.refsans.devices.beckhoff.nok.BeckhoffMotorCab1M0x',
            description = 'tbd',
            tacodevice = '//%s/test/modbus/probenort'% (nethost,),
            address = 0x3214+2*10, # decimal 12820
            slope = 10000,
            unit = 'mm',
            abslimits = (-102.0, 170.0),
            ruler = 0.0,
            lowlevel = True,
        ),
        b3_s = device('nicos.devices.generic.Axis',
            description = 'b3, sampleside',
            motor = 'b3_sm',
            coder = 'b3_sm',
            offset = 0.0,
            precision = lprecision,
            lowlevel = True,
        ),
    )
