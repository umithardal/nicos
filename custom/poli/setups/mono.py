description = 'POLI monochromator devices'

group = 'lowlevel'

tango_base = 'tango://phys.poli.frm2:10000/poli/'

devices = dict(
    chi_m     = device('devices.tango.Motor',
                       description = 'monochromator tilt (chi axis)',
                       tangodevice = tango_base + 'fzjs7/chi_m',
                       fmtstr = '%.2f',
                       abslimits = (0, 12.8),
                       precision = 0.01,
                      ),
    theta_m   = device('devices.tango.Motor',
                       description = 'monochromator rotation (theta axis)',
                       tangodevice = tango_base + 'fzjs7/theta_m',
                       fmtstr = '%.2f',
                       abslimits = (0, 1300),
                       precision = 0.1,
                      ),
    x_m       = device('devices.tango.Motor',
                       description = 'monochromator translation (x axis)',
                       tangodevice = tango_base + 'fzjs7/x_m',
                       fmtstr = '%.2f',
                       abslimits = (0, 90),
                       precision = 0.01,
                      ),
    changer_m = device('devices.tango.Motor',
                       description = 'monochromator changer axis',
                       tangodevice = tango_base + 'fzjs7/change_m',
                       fmtstr = '%.2f',
                       abslimits = (0, 4000),
                       precision = 0.1,
                      ),
    wavelength = device('devices.generic.ManualMove',
                        description = 'wavelength',
                        fmtstr = '%.3f',
                        unit = 'AA',
                        abslimits = (0.01, 10),
                        default = 1.8,
                       ),

    #h_m       = device('devices.generic.DeviceAlias',
    #                  ),
    #v_m       = device('devices.generic.DeviceAlias',
    #                  ),
    #h_m_alias = device('devices.generic.ParamDevice',
    #                   lowlevel = True,
    #                   device = 'h_m',
    #                   parameter = 'alias',
    #                  ),
    #v_m_alias = device('devices.generic.ParamDevice',
    #                   lowlevel = True,
    #                   device = 'v_m',
    #                   parameter = 'alias',
    #                  ),
    #mono      = device('poli.mono.MultiSwitcher',
    #                   description = 'monochromator wavelength switcher',
    #                   # note: precision of chi and theta is so large because they are expected
    #                   # to be changed slightly depending on setup
    #                   moveables = ['x_m', 'changer_m', 'chi_m', 'theta_m', 'h_m_alias', 'v_m_alias'],
    #                   precision = [0.01,  0.01,        5,       10,        None,        None],
    #                   mapping = {
    #                       0.9:  [38, 190,  6.3, 236, 'cuh', 'cuv'],
    #                       1.14: [45, 3.79, 8.6, 236, 'sih', 'siv'],
    #                   },
    #                   changepos = 0,
    #                  ),
)
