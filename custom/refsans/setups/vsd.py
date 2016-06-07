description = 'vsd readout devices'

group = 'optional'

nethost = 'refsanssrv.refsans.frm2'

# according to docu: 'anhang_a_refsans_vsd.pdf'

devices = dict(
    _vsdio = device('refsans.beckhoff.vsd.VSDIO',
                    description = 'TACO Modbus Device for communication with VSD',
                    tacodevice = '//%s/test/modbus/vsd'% (nethost,),
                    address = 0x3000,
                    lowlevel = True,
                   ),

    Air1Pressure = device('refsans.beckhoff.vsd.AnalogValue',
            description='VSD: Analog value of Air1Pressure',
            iodev='_vsdio',
            channel='Air1Pressure',
            unit='bar',
    ),

    Air2Pressure = device('refsans.beckhoff.vsd.AnalogValue',
            description='VSD: Analog value of Air2Pressure',
            iodev='_vsdio',
            channel='Air2Pressure',
            unit='bar',
    ),

    Media1Current = device('refsans.beckhoff.vsd.AnalogValue',
            description='VSD: Analog value of Media1Current',
            iodev='_vsdio',
            channel='Media1Current',
            unit='mA',
    ),

    Media1Voltage = device('refsans.beckhoff.vsd.AnalogValue',
            description='VSD: Analog value of Media1Voltage',
            iodev='_vsdio',
            channel='Media1Voltage',
            unit='V',
    ),

    Media2Current = device('refsans.beckhoff.vsd.AnalogValue',
            description='VSD: Analog value of Media2Current',
            iodev='_vsdio',
            channel='Media2Current',
            unit='mA',
    ),

    Media2Voltage = device('refsans.beckhoff.vsd.AnalogValue',
            description='VSD: Analog value of Media2Voltage',
            iodev='_vsdio',
            channel='Media2Voltage',
            unit='V',
    ),

    Media3Current = device('refsans.beckhoff.vsd.AnalogValue',
            description='VSD: Analog value of Media3Current',
            iodev='_vsdio',
            channel='Media3Current',
            unit='mA',
    ),

    Media3Voltage = device('refsans.beckhoff.vsd.AnalogValue',
            description='VSD: Analog value of Media3Voltage',
            iodev='_vsdio',
            channel='Media3Voltage',
            unit='V',
    ),

    Media4Current = device('refsans.beckhoff.vsd.AnalogValue',
            description='VSD: Analog value of Media4Current',
            iodev='_vsdio',
            channel='Media4Current',
            unit='mA',
    ),

    Media4Voltage = device('refsans.beckhoff.vsd.AnalogValue',
            description='VSD: Analog value of Media4Voltage',
            iodev='_vsdio',
            channel='Media4Voltage',
            unit='V',
    ),

    Temperature1 = device('refsans.beckhoff.vsd.AnalogValue',
            description='VSD: Analog value of Temperature1',
            iodev='_vsdio',
            channel='Temperature1',
            unit='degC',
    ),

    Temperature2 = device('refsans.beckhoff.vsd.AnalogValue',
            description='VSD: Analog value of Temperature2',
            iodev='_vsdio',
            channel='Temperature2',
            unit='degC',
    ),

    Temperature3 = device('refsans.beckhoff.vsd.AnalogValue',
            description='VSD: Analog value of Temperature3',
            iodev='_vsdio',
            channel='Temperature3',
            unit='degC',
    ),

    Temperature4 = device('refsans.beckhoff.vsd.AnalogValue',
            description='VSD: Analog value of Temperature4',
            iodev='_vsdio',
            channel='Temperature4',
            unit='degC',
    ),

    Temperature5 = device('refsans.beckhoff.vsd.AnalogValue',
            description='VSD: Analog value of Temperature5',
            iodev='_vsdio',
            channel='Temperature5',
            unit='degC',
    ),

    Temperature6 = device('refsans.beckhoff.vsd.AnalogValue',
            description='VSD: Analog value of Temperature6',
            iodev='_vsdio',
            channel='Temperature6',
            unit='degC',
    ),

    Temperature7 = device('refsans.beckhoff.vsd.AnalogValue',
            description='VSD: Analog value of Temperature7',
            iodev='_vsdio',
            channel='Temperature7',
            unit='degC',
    ),

    Temperature8 = device('refsans.beckhoff.vsd.AnalogValue',
            description='VSD: Analog value of Temperature8',
            iodev='_vsdio',
            channel='Temperature8',
            unit='degC',
    ),

    User1Current = device('refsans.beckhoff.vsd.AnalogValue',
            description='VSD: Analog value of User1Current',
            iodev='_vsdio',
            channel='User1Current',
            unit='mA',
    ),

    User1Voltage = device('refsans.beckhoff.vsd.AnalogValue',
            description='VSD: Analog value of User1Voltage',
            iodev='_vsdio',
            channel='User1Voltage',
            unit='V',
    ),

    User2Current = device('refsans.beckhoff.vsd.AnalogValue',
            description='VSD: Analog value of User2Current',
            iodev='_vsdio',
            channel='User2Current',
            unit='mA',
    ),

    User2Voltage = device('refsans.beckhoff.vsd.AnalogValue',
            description='VSD: Analog value of User2Voltage',
            iodev='_vsdio',
            channel='User2Voltage',
            unit='V',
    ),

    Water1Flow = device('refsans.beckhoff.vsd.AnalogValue',
            description='VSD: Analog value of Water1Flow',
            iodev='_vsdio',
            channel='Water1Flow',
            unit='l/min',
    ),

    Water1Pressure = device('refsans.beckhoff.vsd.AnalogValue',
            description='VSD: Analog value of Water1Pressure',
            iodev='_vsdio',
            channel='Water1Pressure',
            unit='bar',
    ),

    Water1Temp = device('refsans.beckhoff.vsd.AnalogValue',
            description='VSD: Analog value of Water1Temp',
            iodev='_vsdio',
            channel='Water1Temp',
            unit='degC',
    ),

    Water2Flow = device('refsans.beckhoff.vsd.AnalogValue',
            description='VSD: Analog value of Water2Flow',
            iodev='_vsdio',
            channel='Water2Flow',
            unit='l/min',
    ),

    Water2Pressure = device('refsans.beckhoff.vsd.AnalogValue',
            description='VSD: Analog value of Water2Pressure',
            iodev='_vsdio',
            channel='Water2Pressure',
            unit='bar',
    ),

    Water2Temp = device('refsans.beckhoff.vsd.AnalogValue',
            description='VSD: Analog value of Water2Temp',
            iodev='_vsdio',
            channel='Water2Temp',
            unit='degC',
    ),

    Water3Flow = device('refsans.beckhoff.vsd.AnalogValue',
            description='VSD: Analog value of Water3Flow',
            iodev='_vsdio',
            channel='Water3Flow',
            unit='l/min',
    ),

    Water3Temp = device('refsans.beckhoff.vsd.AnalogValue',
            description='VSD: Analog value of Water3Temp',
            iodev='_vsdio',
            channel='Water3Temp',
            unit='degC',
    ),

    Water4Flow = device('refsans.beckhoff.vsd.AnalogValue',
            description='VSD: Analog value of Water4Flow',
            iodev='_vsdio',
            channel='Water4Flow',
            unit='l/min',
    ),

    Water4Temp = device('refsans.beckhoff.vsd.AnalogValue',
            description='VSD: Analog value of Water4Temp',
            iodev='_vsdio',
            channel='Water4Temp',
            unit='degC',
    ),

    Water5Flow = device('refsans.beckhoff.vsd.AnalogValue',
            description='VSD: Analog value of Water5Flow',
            iodev='_vsdio',
            channel='Water5Flow',
            unit='l/min',
    ),

    Water5Temp = device('refsans.beckhoff.vsd.AnalogValue',
            description='VSD: Analog value of Water5Temp',
            iodev='_vsdio',
            channel='Water5Temp',
            unit='degC',
    ),

    AkkuPower = device('refsans.beckhoff.vsd.DigitalValue',
            description='VSD: Digital value of AkkuPower',
            iodev='_vsdio',
            channel='AkkuPower',
            mapping=dict(On=1,Off=0),
    ),

    ChopperEnable1 = device('refsans.beckhoff.vsd.DigitalValue',
            description='VSD: Digital value of ChopperEnable1',
            iodev='_vsdio',
            channel='ChopperEnable1',
            mapping=dict(On=1,Off=0),
    ),

    ChopperEnable2 = device('refsans.beckhoff.vsd.DigitalValue',
            description='VSD: Digital value of ChopperEnable2',
            iodev='_vsdio',
            channel='ChopperEnable2',
            mapping=dict(On=1,Off=0),
    ),

    ControllerStatus = device('refsans.beckhoff.vsd.DigitalValue',
            description='VSD: Digital value of ControllerStatus',
            iodev='_vsdio',
            channel='ControllerStatus',
            mapping=dict(On=1,Off=0),
    ),

    Media_DigitalOutput1 = device('refsans.beckhoff.vsd.DigitalValue',
            description='VSD: Digital value of Media_DigitalOutput1',
            iodev='_vsdio',
            channel='Media_DigitalOutput1',
            mapping=dict(On=1,Off=0),
    ),

    Media_DigitalOutput2 = device('refsans.beckhoff.vsd.DigitalValue',
            description='VSD: Digital value of Media_DigitalOutput2',
            iodev='_vsdio',
            channel='Media_DigitalOutput2',
            mapping=dict(On=1,Off=0),
    ),

    Media_DigitalOutput3 = device('refsans.beckhoff.vsd.DigitalValue',
            description='VSD: Digital value of Media_DigitalOutput3',
            iodev='_vsdio',
            channel='Media_DigitalOutput3',
            mapping=dict(On=1,Off=0),
    ),

    Media_DigitalOutput4 = device('refsans.beckhoff.vsd.DigitalValue',
            description='VSD: Digital value of Media_DigitalOutput4',
            iodev='_vsdio',
            channel='Media_DigitalOutput4',
            mapping=dict(On=1,Off=0),
    ),

    Merker128 = device('refsans.beckhoff.vsd.DigitalValue',
            description='VSD: Digital value of Merker128',
            iodev='_vsdio',
            channel='Merker128',
            mapping=dict(On=1,Off=0),
    ),

    Merker129 = device('refsans.beckhoff.vsd.DigitalValue',
            description='VSD: Digital value of Merker129',
            iodev='_vsdio',
            channel='Merker129',
            mapping=dict(On=1,Off=0),
    ),

    Merker253 = device('refsans.beckhoff.vsd.DigitalValue',
            description='VSD: Digital value of Merker253',
            iodev='_vsdio',
            channel='Merker253',
            mapping=dict(On=1,Off=0),
    ),

    Merker254 = device('refsans.beckhoff.vsd.DigitalValue',
            description='VSD: Digital value of Merker254',
            iodev='_vsdio',
            channel='Merker254',
            mapping=dict(On=1,Off=0),
    ),

    PowerBreakdown = device('refsans.beckhoff.vsd.DigitalValue',
            description='VSD: Digital value of PowerBreakdown',
            iodev='_vsdio',
            channel='PowerBreakdown',
            mapping=dict(On=1,Off=0),
    ),

    PowerSupplyNormal = device('refsans.beckhoff.vsd.DigitalValue',
            description='VSD: Digital value of PowerSupplyNormal',
            iodev='_vsdio',
            channel='PowerSupplyNormal',
            mapping=dict(On=1,Off=0),
    ),

    PowerSupplyUSV = device('refsans.beckhoff.vsd.DigitalValue',
            description='VSD: Digital value of PowerSupplyUSV',
            iodev='_vsdio',
            channel='PowerSupplyUSV',
            mapping=dict(On=1,Off=0),
    ),

    SolenoidValve = device('refsans.beckhoff.vsd.DigitalValue',
            description='VSD: Digital value of SolenoidValve',
            iodev='_vsdio',
            channel='SolenoidValve',
            mapping=dict(On=1,Off=0),
    ),

    TempVibration = device('refsans.beckhoff.vsd.DigitalValue',
            description='VSD: Digital value of TempVibration',
            iodev='_vsdio',
            channel='TempVibration',
            mapping=dict(On=1,Off=0),
    ),

    VSD_User1DigitalInput = device('refsans.beckhoff.vsd.DigitalValue',
            description='VSD: Digital value of VSD_User1DigitalInput',
            iodev='_vsdio',
            channel='VSD_User1DigitalInput',
            mapping=dict(On=1,Off=0),
    ),

    VSD_User1DigitalOutput1 = device('refsans.beckhoff.vsd.DigitalValue',
            description='VSD: Digital value of VSD_User1DigitalOutput1',
            iodev='_vsdio',
            channel='VSD_User1DigitalOutput1',
            mapping=dict(On=1,Off=0),
    ),

    VSD_User1DigitalOutput2 = device('refsans.beckhoff.vsd.DigitalValue',
            description='VSD: Digital value of VSD_User1DigitalOutput2',
            iodev='_vsdio',
            channel='VSD_User1DigitalOutput2',
            mapping=dict(On=1,Off=0),
    ),

    VSD_User2DigitalInput = device('refsans.beckhoff.vsd.DigitalValue',
            description='VSD: Digital value of VSD_User2DigitalInput',
            iodev='_vsdio',
            channel='VSD_User2DigitalInput',
            mapping=dict(On=1,Off=0),
    ),

    VSD_User2DigitalOutput1 = device('refsans.beckhoff.vsd.DigitalValue',
            description='VSD: Digital value of VSD_User2DigitalOutput1',
            iodev='_vsdio',
            channel='VSD_User2DigitalOutput1',
            mapping=dict(On=1,Off=0),
    ),

    VSD_User2DigitalOutput2 = device('refsans.beckhoff.vsd.DigitalValue',
            description='VSD: Digital value of VSD_User2DigitalOutput2',
            iodev='_vsdio',
            channel='VSD_User2DigitalOutput2',
            mapping=dict(On=1,Off=0),
    ),

    VSD_User3DigitalInput1 = device('refsans.beckhoff.vsd.DigitalValue',
            description='VSD: Digital value of VSD_User3DigitalInput1',
            iodev='_vsdio',
            channel='VSD_User3DigitalInput1',
            mapping=dict(On=1,Off=0),
    ),

    VSD_User3DigitalInput2 = device('refsans.beckhoff.vsd.DigitalValue',
            description='VSD: Digital value of VSD_User3DigitalInput2',
            iodev='_vsdio',
            channel='VSD_User3DigitalInput2',
            mapping=dict(On=1,Off=0),
    ),

    VSD_User3DigitalInput3 = device('refsans.beckhoff.vsd.DigitalValue',
            description='VSD: Digital value of VSD_User3DigitalInput3',
            iodev='_vsdio',
            channel='VSD_User3DigitalInput3',
            mapping=dict(On=1,Off=0),
    ),

    VSD_User3DigitalOutput1 = device('refsans.beckhoff.vsd.DigitalValue',
            description='VSD: Digital value of VSD_User3DigitalOutput1',
            iodev='_vsdio',
            channel='VSD_User3DigitalOutput1',
            mapping=dict(On=1,Off=0),
    ),

    VSD_User3DigitalOutput2 = device('refsans.beckhoff.vsd.DigitalValue',
            description='VSD: Digital value of VSD_User3DigitalOutput2',
            iodev='_vsdio',
            channel='VSD_User3DigitalOutput2',
            mapping=dict(On=1,Off=0),
    ),

    VSD_User3DigitalOutput3 = device('refsans.beckhoff.vsd.DigitalValue',
            description='VSD: Digital value of VSD_User3DigitalOutput3',
            iodev='_vsdio',
            channel='VSD_User3DigitalOutput3',
            mapping=dict(On=1,Off=0),
    ),

    VSD_User4DigitalInput1 = device('refsans.beckhoff.vsd.DigitalValue',
            description='VSD: Digital value of VSD_User4DigitalInput1',
            iodev='_vsdio',
            channel='VSD_User4DigitalInput1',
            mapping=dict(On=1,Off=0),
    ),

    VSD_User4DigitalInput2 = device('refsans.beckhoff.vsd.DigitalValue',
            description='VSD: Digital value of VSD_User4DigitalInput2',
            iodev='_vsdio',
            channel='VSD_User4DigitalInput2',
            mapping=dict(On=1,Off=0),
    ),

    VSD_User4DigitalInput3 = device('refsans.beckhoff.vsd.DigitalValue',
            description='VSD: Digital value of VSD_User4DigitalInput3',
            iodev='_vsdio',
            channel='VSD_User4DigitalInput3',
            mapping=dict(On=1,Off=0),
    ),

    VSD_User4DigitalOutput1 = device('refsans.beckhoff.vsd.DigitalValue',
            description='VSD: Digital value of VSD_User4DigitalOutput1',
            iodev='_vsdio',
            channel='VSD_User4DigitalOutput1',
            mapping=dict(On=1,Off=0),
    ),

    VSD_User4DigitalOutput2 = device('refsans.beckhoff.vsd.DigitalValue',
            description='VSD: Digital value of VSD_User4DigitalOutput2',
            iodev='_vsdio',
            channel='VSD_User4DigitalOutput2',
            mapping=dict(On=1,Off=0),
    ),

    VSD_User4DigitalOutput3 = device('refsans.beckhoff.vsd.DigitalValue',
            description='VSD: Digital value of VSD_User4DigitalOutput3',
            iodev='_vsdio',
            channel='VSD_User4DigitalOutput3',
            mapping=dict(On=1,Off=0),
    ),


)
