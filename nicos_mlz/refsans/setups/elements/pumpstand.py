description = 'Pumpstand devices using Beckhoff controllers'

group = 'lowlevel'

instrument_values = configdata('instrument.values')

tango_host = instrument_values['tango_base'] + 'pumpstand/io/modbus'
code_base = instrument_values['code_base'] + 'beckhoff.pumpstation.'

# according to docu: 'Anhang_A_REFSANS_Cab1 ver25.06.2014 0.1.3 mit nok5b.pdf'
# according to docu: '_2013-04-08 Anhang_A_REFSANS_Schlitten V0.7.pdf'
# according to docu: '_2013-04-05 Anhang A V0.6.pdf'
# according to docu: '_Anhang_A_REFSANS_Pumpstand.pdf'
devices = dict(
    # according to '_Anhang_A_REFSANS_Pumpstand.pdf'
    pumpstand = device(code_base + 'PumpstandIO',
        description = 'io device for pumpstand',
        tangodevice = tango_host,
        address = 0x4026,  # 16422
        parallel_pumping = 10,  # below 10mbar, parallel pumping is allowed
        lowlevel = True,
    ),
    pressure_CB = device(code_base + 'PumpstandPressure',
        description = 'Pressure in CB (provided by Pumpstand)',
        iodev = 'pumpstand',
        chamber = 'CB',
        # limits = (turn_pump_off_below_this_pressure, turn_pump_on_above_this_pressure),
    ),
    pressure_SR = device(code_base + 'PumpstandPressure',
        description = 'Pressure in SR (provided by Pumpstand)',
        iodev = 'pumpstand',
        chamber = 'SR',
        # limits = (turn_pump_off_below_this_pressure, turn_pump_on_above_this_pressure),
    ),
    pressure_SFK = device(code_base + 'PumpstandPressure',
        description = 'Pressure in SFK (provided by Pumpstand)',
        iodev = 'pumpstand',
        chamber = 'SFK',
        # limits = (turn_pump_off_below_this_pressure, turn_pump_on_above_this_pressure),
    ),
    pump_CB = device('nicos.devices.generic.Switcher',
        description = 'Pumping state & control device for CB',
        moveable = device(code_base + 'PumpstandPump',
            description = 'pump CB (provided by Pumpstand)',
            iodev = 'pumpstand',
            chamber = 'CB',
        ),
        precision = 0.01,
        lowlevel = True,
        mapping = dict(vent = 1, off = 0, pump = -1),
    ),
    pump_SR = device('nicos.devices.generic.Switcher',
        description = 'Pumping state & control device for SR',
        moveable = device(code_base + 'PumpstandPump',
            description = 'pump SR (provided by Pumpstand)',
            iodev = 'pumpstand',
            chamber = 'SR',
        ),
        precision = 0.01,
        lowlevel = True,
        mapping = dict(vent = 1, off = 0, pump = -1),
    ),
    pump_SFK = device('nicos.devices.generic.Switcher',
        description = 'Pumping state & control device for SFK',
        moveable = device(code_base + 'PumpstandPump',
            description = 'pump SFK (provided by Pumpstand)',
            iodev = 'pumpstand',
            chamber = 'SFK',
        ),
        precision = 0.01,
        lowlevel = True,
        mapping = dict(vent = 1, off = 0, pump = -1),
    ),
)
