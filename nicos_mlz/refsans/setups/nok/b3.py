description = 'B3 aperture devices'

# group = 'lowlevel'
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
            description = 'tbd',
            nok_start = -1,
            nok_length =-1,
            nok_end = -1,
            nok_gap = -1,
            inclinationlimits = (-1000, 1000),
            masks = dict(
                # slit = [84.044, 50.4169, 0.00, 4.06],
                slit = [84.044, 50.4169, 0.10, 16.565],
                # MP 27.03.18 bend
                # slit = [84.044, 50.4169, 0.00, 45.22],
                # MP 22.02.2018 12:47:22 Schwanenhals
                # MP height scan 22.02.2018 12:46:29
                # slit = [84.044, 50.4169, 0.00, 4.06],
                # MP hight scann 30.01.2018 13:24:04 open=todo
                pinhole = [84.044, 50.4169, 0.00, 45.22],
                gisans = [84.044, 50.4169, 0.00, 45.22],
            ),
            motor_r = 'b3_r',
            motor_s = 'b3_s',
            nok_motor = [-1, -1],
            backlash = 0,
            precision = lprecision,
        ),
        b3_mode = device('nicos.devices.generic.ReadonlyParamDevice',
            description = 'b3 mode',
            device = 'b3',
            parameter = 'mode',
        ),
        b3_rm = device('nicos_mlz.refsans.devices.beckhoff.nok.BeckhoffMotorCab1M0x',
            description = 'tbd',
            tacodevice = '//%s/test/modbus/probenort'% (nethost,),
            address = 0x3214+3*10, # dez12820
            slope = -10000,
            unit = 'mm',
            abslimits = (-193.0, 130.0),
            userlimits = (-193.0, 130.0),
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
            address = 0x3214+2*10, # dez12820
            slope = 10000,
            unit = 'mm',
            abslimits = (-102.0, 170.0),
            userlimits = (-102.0, 170.0),
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
