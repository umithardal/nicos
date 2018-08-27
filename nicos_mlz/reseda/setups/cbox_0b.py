#  -*- coding: utf-8 -*-

description = 'Capacity box %s' % setupname
group = 'optional'

tango_base = 'tango://resedahw2.reseda.frm2:10000/reseda'

includes = ['rte1104']

devices = {
    '%s_fg_freq' % setupname:
        device('nicos_mlz.reseda.devices.rte1104.RTE1104TimescaleSetting',
            description = 'Frequency setting chain of subdevices: setting timescale',
            io = 'rte1104_io',
            freqgen = device('nicos.devices.tango.AnalogOutput',
                description = 'Frequency generator frequency',
                tangodevice = '%s/%s/fg_frequency' % (tango_base, setupname),
                pollinterval = 30,
                fmtstr = '%.4g',
                unit = 'Hz',
               ),
        ),
     '%s_reg_amp' % setupname:
        device('nicos_mlz.reseda.devices.rte1104.RTE1104YScaleSetting',
            description = 'amplitude setting chain of subdevices: setting channel 2',
            io = 'rte1104_io',
            channel = 2,
            regulator = device('nicos_mlz.reseda.devices.regulator.Regulator',
                description = 'Auto regulating amplitude',
                sensor = '%s_coil_rms' % setupname,
                moveable = '%s_fg_amp' % setupname,
                loopdelay = 1.0,
                maxstep = 0.1,
                minstep = 0.005,
                maxage = 11.0,
                pollinterval = 5.0,
                stepfactor = 0.3,
                unit = 'V',
               ),
        ),
    '%s_fg_amp' % setupname:
        device('nicos.devices.tango.AnalogOutput',
            description = 'Frequency generator amplitude',
            tangodevice = '%s/%s/fg_amplitude' % (tango_base, setupname),
            # abslimits have to be set in res file!
            pollinterval = 5,
            unit = 'V',
        ),
    '%s_fwdp' % setupname:
        device('nicos.devices.tango.AnalogInput',
            description = 'Power amplifier forward power',
            tangodevice = '%s/%s/pa_fwdp' % (tango_base, setupname),
            pollinterval = 10,
            unit = 'W',
        ),
    '%s_revp' % setupname:
        device('nicos.devices.tango.AnalogInput',
            description = 'Power amplifier reverse power',
            tangodevice = '%s/%s/pa_revp' % (tango_base, setupname),
            pollinterval = 10,
            unit = 'W',
        ),
    '%s' % setupname:
        device('nicos_mlz.reseda.devices.cbox.CBoxResonanceFrequency',
            pollinterval = 30,
            description = 'CBox',
            unit = 'Hz',
            power_divider = device('nicos.devices.tango.DigitalOutput',
                description = 'Power divider to split the power for both coils',
                tangodevice = '%s/%s/plc_power_divider' %
                (tango_base, setupname),
                lowlevel = False,  # temporary due to inaccurate auto tune
                unit = '',
                fmtstr = '%.0f',
            ),
            highpass = device('nicos.devices.tango.DigitalOutput',
                description = 'Highpass filter to smooth the signal',
                tangodevice = '%s/%s/plc_highpass' % (tango_base, setupname),
                lowlevel = False,  # temporary due to inaccurate auto tune
                unit = '',
                fmtstr = '%.0f',
            ),
            pa_fwdp = '%s_fwdp' % setupname,
            pa_revp = '%s_revp' % setupname,
            fg = '%s_fg_freq' % setupname,
            coil_amp = '%s_coil_rms' % setupname,
            diplexer = device('nicos.devices.tango.DigitalOutput',
                description =
                'Lowpass filter to smooth the signal (enable for low frequency, disable for high frequency)',
                tangodevice = '%s/%s/plc_diplexer' % (tango_base, setupname),
                lowlevel = False,  # temporary due to inaccurate auto tune
                unit = '',
                fmtstr = '%.0f',
            ),
            coil1_c1 = device('nicos.devices.tango.DigitalOutput',
                description = 'Coil 1: Capacitor bank 1',
                tangodevice = '%s/%s/plc_a_c1' % (tango_base, setupname),
                lowlevel = False,  # temporary due to inaccurate auto tune
                unit = '',
                fmtstr = '%.0f',
            ),
            coil1_c2 = device('nicos.devices.tango.DigitalOutput',
                description = 'Coil 1: Capacitor bank 2',
                tangodevice = '%s/%s/plc_a_c2' % (tango_base, setupname),
                lowlevel = False,  # temporary due to inaccurate auto tune
                unit = '',
                fmtstr = '%.0f',
            ),
            coil1_c3 = device('nicos.devices.tango.DigitalOutput',
                description = 'Coil 1: Capacitor bank 3',
                tangodevice = '%s/%s/plc_a_c3' % (tango_base, setupname),
                lowlevel = False,  # temporary due to inaccurate auto tune
                unit = '',
                fmtstr = '%.0f',
            ),
            coil1_c1c2serial = device('nicos.devices.tango.DigitalOutput',
                description =
                'Coil 1: Use c1 and c2 in serial instead of parallel',
                tangodevice = '%s/%s/plc_a_c1c2serial' %
                (tango_base, setupname),
                lowlevel = False,  # temporary due to inaccurate auto tune
                unit = '',
                fmtstr = '%.0f',
            ),
            coil1_transformer = device('nicos.devices.tango.DigitalOutput',
                description =
                'Coil 1: Used to manipulate the coil resistance to match the power amplifier resistance',
                tangodevice = '%s/%s/plc_a_transformer' %
                (tango_base, setupname),
                lowlevel = False,  # temporary due to inaccurate auto tune
                unit = '',
                fmtstr = '%.0f',
            ),
            coil2_c1 = device('nicos.devices.tango.DigitalOutput',
                description = 'Coil 2: Capacitor bank 1',
                tangodevice = '%s/%s/plc_b_c1' % (tango_base, setupname),
                lowlevel = False,  # temporary due to inaccurate auto tune
                unit = '',
                fmtstr = '%.0f',
            ),
            coil2_c2 = device('nicos.devices.tango.DigitalOutput',
                description = 'Coil 2: Capacitor bank 2',
                tangodevice = '%s/%s/plc_b_c2' % (tango_base, setupname),
                lowlevel = False,  # temporary due to inaccurate auto tune
                unit = '',
                fmtstr = '%.0f',
            ),
            coil2_c3 = device('nicos.devices.tango.DigitalOutput',
                description = 'Coil 2: Capacitor bank 3',
                tangodevice = '%s/%s/plc_b_c3' % (tango_base, setupname),
                lowlevel = False,  # temporary due to inaccurate auto tune
                unit = '',
                fmtstr = '%.0f',
            ),
            coil2_c1c2serial = device('nicos.devices.tango.DigitalOutput',
                description =
                'Coil 2: Use c1 and c2 in serial instead of parallel',
                tangodevice = '%s/%s/plc_b_c1c2serial' %
                (tango_base, setupname),
                lowlevel = False,  # temporary due to inaccurate auto tune
                unit = '',
                fmtstr = '%.0f',
            ),
            coil2_transformer = device('nicos.devices.tango.DigitalOutput',
                description =
                'Coil 2: Used to manipulate the coil resistance to match the power amplifier resistance',
                tangodevice = '%s/%s/plc_b_transformer' %
                (tango_base, setupname),
                lowlevel = False,  # temporary due to inaccurate auto tune
                unit = '',
                fmtstr = '%.0f',
            ),
        ),
    '%s_coil_rms' % setupname:  device('nicos_mlz.reseda.devices.rte1104.RTE1104',
       description = 'rms Coil voltage (Input Channel 2)',
       io = 'rte1104_io',
       channel = 2,
       unit = 'V',
    ),
}
