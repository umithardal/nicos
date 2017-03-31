# -*- coding: utf-8 -*-

description = 'GALAXI motors'

group = 'optional'

tango_base = 'tango://localhost:10000/galaxi/'

devices = dict(
    ro_y     = device('devices.tango.Motor',
                      description = 'ROY axis',
                      tangodevice = tango_base + 'fzjs7/ROY',
                      lowlevel = True,
                     ),
    roy      = device('devices.generic.Axis',
                      description = 'ROY axis',
                      motor = 'ro_y',
                      coder = 'ro_y',
                      offset = 0,
                      precision = 0.01,
                      maxtries = 1,
                      userlimits = (-5000, 5000),
                     ),
    ro_z     = device('devices.tango.Motor',
                      description = 'ROZ axis',
                      tangodevice = tango_base + 'fzjs7/ROZ',
                      lowlevel = True,
                     ),
    roz      = device('devices.generic.Axis',
                      description = 'ROZ axis',
                      motor = 'ro_z',
                      coder = 'ro_z',
                      offset = 0,
                      precision = 0.01,
                      maxtries = 1,
                      userlimits = (-5000, 5000),
                     ),
    dof_chi  = device('devices.tango.Motor',
                      description = 'DOFChi axis',
                      tangodevice = tango_base + 'fzjs7/DOFChi',
                      lowlevel = True,
                     ),
    dofchi   = device('devices.generic.Axis',
                      description = 'DOFChi axis',
                      motor = 'dof_chi',
                      coder = 'dof_chi',
                      offset = 0,
                      precision = 0.01,
                      maxtries = 1,
                      userlimits = (-50, 50),
                     ),
    dof_om   = device('devices.tango.Motor',
                      description = 'DOFOm axis',
                      tangodevice = tango_base + 'fzjs7/DOFOm',
                      lowlevel = True,
                     ),
    dofom    = device('devices.generic.Axis',
                      description = 'DOFOm axis',
                      motor = 'dof_om',
                      coder = 'dof_om',
                      offset = 0,
                      precision = 0.01,
                      maxtries = 1,
                      userlimits = (-50, 50),
                     ),
    rob_y    = device('devices.tango.Motor',
                      description = 'ROBY axis',
                      tangodevice = tango_base + 'fzjs7/ROBY',
                      lowlevel = True,
                     ),
    roby     = device('devices.generic.Axis',
                      description = 'ROBY axis',
                      motor = 'rob_y',
                      coder = 'rob_y',
                      offset = 0,
                      precision = 0.01,
                      maxtries = 1,
                     ),
    rob_z    = device('devices.tango.Motor',
                      description = 'ROBZ axis',
                      tangodevice = tango_base + 'fzjs7/ROBZ',
                      lowlevel = True,
                     ),
    robz     = device('devices.generic.Axis',
                      description = 'ROBZ axis',
                      motor = 'rob_z',
                      coder = 'rob_z',
                      offset = 0,
                      precision = 0.01,
                      maxtries = 1,
                     ),
)
