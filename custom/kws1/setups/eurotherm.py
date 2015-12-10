# -*- coding: utf-8 -*-

description = 'setup for Eurotherm sample heater'
group = 'optional'

includes = ['alias_T']

devices = dict(
    T_et = device('devices.tango.TemperatureController',
                  description = 'Eurotherm temperature controller',
                  tangodevice = 'tango://phys.kws1.frm2:10000/kws1/eurotherm/control',
                  abslimits = (0, 200),
                  precision = 0.1,
                 ),
)

alias_config = dict(T={'T_et': 100})
