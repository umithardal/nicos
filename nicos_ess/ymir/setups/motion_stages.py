description = 'Stray motion stage(s) at Utgård/YMIR.'

devices = dict(
    m1=device('nicos_ess.devices.epics.motor.EpicsMotor',
              epicstimeout=3.0,
              precision=0.1,
              description='Single axis positioner',
              motorpv='LabS-ESSIIP:MC-MCU-01:m1',
              errormsgpv='LabS-ESSIIP:MC-MCU-01:m1-MsgTxt',
              errorbitpv='LabS-ESSIIP:MC-MCU-01:m1-Err',
              reseterrorpv='LabS-ESSIIP:MC-MCU-01:m1-ErrRst'
              ),
)
