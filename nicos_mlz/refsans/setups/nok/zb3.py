description = "DoubleSlit [slit k1] between nok6 and nok7"

group = 'lowlevel'

includes = ['nok_ref', 'nokbus3']
showcase_values = configdata('cf_showcase.showcase_values')

tango_base = 'tango://refsanshw.refsans.frm2.tum.de:10000/test/'

devices = dict(
    zb3 = device('nicos_mlz.refsans.devices.slits.DoubleSlit',
        description = 'ZB3 slit',
        slit_r = 'zb3r',
        slit_s = 'zb3s',
        fmtstr = 'open: %.3f, zpos: %.3f',
        unit = 'mm',
    ),
    zb3r = device('nicos_mlz.refsans.devices.slits.SingleSlit',
        description = 'ZB3 slit, reactor side',
        motor = 'zb3r_m',
        nok_start = 8837.5,
        nok_length = 13.0,
        nok_end = 8850.5,
        nok_gap = 1.0,
        masks = {
            'slit': -0.3,
            'point': 0,
            'gisans': -110,
        },
        unit = 'mm',
        lowlevel = True,
    ),
    zb3s = device('nicos_mlz.refsans.devices.slits.SingleSlit',
        description = 'ZB3 slit, sample side',
        motor = 'zb3s_m',
        nok_start = 8837.5,
        nok_length = 13.0,
        nok_end = 8850.5,
        nok_gap = 1.0,
        masks = {
            'slit': 1.7,
            'point': 0,
            'gisans': 0,
        },
        unit = 'mm',
        lowlevel = True,
    ),
    zb3r_m = device('nicos_mlz.refsans.devices.nok_support.NOKMotorIPC',
        description = 'IPC controlled Motor of ZB3, reactor side',
        abslimits = (-221.0, 95.0),
        bus = 'nokbus3',
        addr = 0x57,
        slope = 800.0,
        speed = 50,
        accel = 50,
        confbyte = 32,
        ramptype = 2,
        microstep = 1,
        refpos = 72.774,
        zerosteps = int(677.125 * 800),
        lowlevel = showcase_values['hide_poti'] and showcase_values['NOreference'],
    ),
    zb3s_m = device('nicos_mlz.refsans.devices.nok_support.NOKMotorIPC',
        description = 'IPC controlled Motor of ZB3, sample side',
        abslimits = (-106.0, 113.562),
        bus = 'nokbus3',
        addr = 0x58,
        slope = 800.0,
        speed = 50,
        accel = 50,
        confbyte = 32,
        ramptype = 2,
        microstep = 1,
        refpos = 105.837,
        zerosteps = int(644.562 * 800),
        lowlevel = showcase_values['hide_poti'] and showcase_values['NOreference'],
    ),
    zb3r_acc = device('nicos_mlz.refsans.devices.nok_support.MotorEncoderDifference',
         description = 'calc error Motor and poti',
         motor = 'zb3r_m',
         analog = 'zb3r_obs',
         lowlevel = showcase_values['hide_acc'],
         unit = 'mm'
    ),
    zb3r_obs = device('nicos_mlz.refsans.devices.nok_support.NOKPosition',
        description = 'Position sensing for ZB3, reactor side',
        reference = 'nok_refc1',
        measure = 'zb3r_poti',
        poly = [-140.539293, 1004.824 / 1.92],
        serial = 7778,
        length = 500.0,
        lowlevel = showcase_values['hide_poti'] and showcase_values['NOreference'],
    ),
    zb3r_poti = device('nicos_mlz.refsans.devices.nok_support.NOKMonitoredVoltage',
        description = 'Poti for ZB3, reactor side',
        tangodevice = tango_base + 'wb_c/1_2',
        scale = -1,  # mounted from top
        lowlevel = True,
    ),
    zb3s_acc = device('nicos_mlz.refsans.devices.nok_support.MotorEncoderDifference',
         description = 'calc error Motor and poti',
         motor = 'zb3s_m',
         analog = 'zb3s_obs',
         lowlevel = showcase_values['hide_acc'],
         unit = 'mm'
    ),
    zb3s_obs = device('nicos_mlz.refsans.devices.nok_support.NOKPosition',
        description = 'Position sensing for ZB3, sample side',
        reference = 'nok_refc1',
        measure = 'zb3s_poti',
        poly = [118.68, 1000. / 1.921],
        serial = 7781,
        length = 500.0,
        lowlevel = showcase_values['hide_poti'] and showcase_values['NOreference'],
    ),
    zb3s_poti = device('nicos_mlz.refsans.devices.nok_support.NOKMonitoredVoltage',
        description = 'Poti for ZB3, sample side',
        tangodevice = tango_base + 'wb_c/1_3',
        scale = 1,   # mounted from bottom
        lowlevel = True,
    ),
)

alias_config = {
    'primary_aperture': {'zb3': 100},
}
