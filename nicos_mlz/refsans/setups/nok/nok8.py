description = "neutronguide sideMirror noMirror"

group = 'lowlevel'

includes = ['nok_ref', 'nokbus3']
showcase_values = configdata('cf_showcase.showcase_values')
optic_values = configdata('cf_optic.optic_values')

tango_host = 'tango://refsanshw:10000/test/'

devices = dict(
    nok8 = device('nicos_mlz.refsans.devices.nok_support.DoubleMotorNOK',
        description = 'NOK8',
        fmtstr = '%.2f, %.2f',
        nok_start = 8870.5,
        nok_length = 880.0,
        nok_end = 9750.5,
        nok_gap = 1.0,
        inclinationlimits = (-100, 100),
        motor_r = 'nok8r_axis',
        motor_s = 'nok8s_axis',
        nok_motor = [9120.0, 9500.0],
        backlash = -2,
        precision = 0.5,
        masks = {
            'ng': optic_values['ng'],
            'rc': optic_values['ng'],
            'vc': optic_values['vc'],
            'fc': optic_values['fc'],
        },
    ),
    nok8r_axis = device('nicos.devices.generic.Axis',
        description = 'Axis of NOK8, reactor side',
        motor = 'nok8r_motor',
        coder = 'nok8r_motor',
        # obs = ['nok8r_obs'],
        backlash = 0,
        precision = 0.5,
        unit = 'mm',
        lowlevel = True,
    ),
    nok8r_motor = device('nicos_mlz.refsans.devices.nok_support.NOKMotorIPC',
        description = 'IPC controlled Motor of NOK8, reactor side',
        abslimits = (-102.835, 128.415),
        bus = 'nokbus3',
        addr = 0x54,
        slope = 800.0,
        speed = 10,
        accel = 10,
        confbyte = 48,
        ramptype = 2,
        microstep = 1,
        refpos = 80.915,
        zerosteps = int(669.085 * 800),
        lowlevel = showcase_values['hide_poti'],
    ),

    nok8r_acc = device('nicos_mlz.refsans.devices.nok_support.MotorEncoderDifference',
         description = 'calc error Motor and poti',
         motor = 'nok8r_motor',
         analog = 'nok8r_obs',
         lowlevel = showcase_values['hide_acc'],
         unit = 'mm'
    ),

    nok8r_obs = device('nicos_mlz.refsans.devices.nok_support.NOKPosition',
        description = 'Position sensing for NOK8, reactor side',
        reference = 'nok_refc1',
        measure = 'nok8r_poti',
        poly = [10.518174, 1001.53 / 3.85],
        serial = 6508,
        length = 250.0,
        lowlevel = showcase_values['hide_poti'],
    ),

    nok8r_poti = device('nicos_mlz.refsans.devices.nok_support.NOKMonitoredVoltage',
        description = 'Poti for NOK8, reactor side',
        tangodevice = tango_host + 'wb_c/1_4',
        scale = -1,
        lowlevel = True,
    ),

    nok8s_axis = device('nicos.devices.generic.Axis',
        description = 'Axis of NOK8, sample side',
        motor = 'nok8s_motor',
        coder = 'nok8s_motor',
        # obs = ['nok8s_obs'],
        backlash = 0,
        precision = 0.5,
        unit = 'mm',
        lowlevel = True,
    ),
    nok8s_motor = device('nicos_mlz.refsans.devices.nok_support.NOKMotorIPC',
        description = 'IPC controlled Motor of NOK8, sample side',
        abslimits = (-104.6, 131.65),
        bus = 'nokbus3',
        addr = 0x55,
        slope = 800.0,
        speed = 10,
        accel = 10,
        confbyte = 48,
        ramptype = 2,
        microstep = 1,
        refpos = 85.499,
        zerosteps = int(664.6 * 800),
        lowlevel = showcase_values['hide_poti'],
    ),

    nok8s_acc = device('nicos_mlz.refsans.devices.nok_support.MotorEncoderDifference',
         description = 'calc error Motor and poti',
         motor = 'nok8s_motor',
         analog = 'nok8s_obs',
         lowlevel = showcase_values['hide_acc'],
         unit = 'mm'
    ),

    nok8s_obs = device('nicos_mlz.refsans.devices.nok_support.NOKPosition',
        description = 'Position sensing for NOK8, sample side',
        reference = 'nok_refc2',
        measure = 'nok8s_poti',
        poly = [8.752627, 998.722 / 3.85],
        serial = 6511,
        length = 250.0,
        lowlevel = showcase_values['hide_poti'],
    ),

    nok8s_poti = device('nicos_mlz.refsans.devices.nok_support.NOKMonitoredVoltage',
        description = 'Poti for NOK8, sample side',
        tangodevice = tango_host + 'wb_c/2_0',
        scale = -1,  # mounted from top
        lowlevel = True,
    ),
)
