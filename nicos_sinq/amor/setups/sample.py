description = 'Sample devices in the SINQ AMOR.'

pvprefix = 'SQ:AMOR:mota:'

includes = ['distances']

devices = dict(
    som=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='Sample omega motor',
               motorpv=pvprefix + 'som',
               errormsgpv=pvprefix + 'som-MsgTxt',
               ),
    soz=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='Sample z lift of base motor',
               motorpv=pvprefix + 'soz',
               errormsgpv=pvprefix + 'soz-MsgTxt',
               ),
    stz=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='Sample z translation on sample table motor',
               motorpv=pvprefix + 'stz',
               errormsgpv=pvprefix + 'stz-MsgTxt',
               ),
    sch=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='Sample chi motor',
               motorpv=pvprefix + 'sch',
               errormsgpv=pvprefix + 'sch-MsgTxt',
               ),
    fma=device('nicos_sinq.amor.devices.epics_amor_magnet.EpicsAmorMagnet',
               epicstimeout=3.0,
               description='Sample magnet',
               basepv='SQ:AMOR:FMA',
               pvdelim=':',
               switchpvs={'read': 'SQ:AMOR:FMA:PowerStatusRBV',
                          'write': 'SQ:AMOR:FMA:PowerStatus'},
               switchstates={'on': 1, 'off': 0},
               precision=0.1,
               timeout=None,
               window=5.0,
               ),
    hsy=device('nicos_sinq.amor.devices.magnet_field.MagneticFieldDevice',
               description='Sample magnet read in magnetic field',
               magnet='fma'
               ),
    dist_chopper_sample=device(
        'nicos_sinq.amor.devices.component_handler.ComponentReferenceDistance',
        description='Distance of sample to chopper',
        distcomponent='dsample',
        distreference='dchopper'
    ),
)
