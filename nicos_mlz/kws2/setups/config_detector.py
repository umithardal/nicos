description = 'presets for the detector position'
group = 'configdata'

# Assigns presets for the detector z position and x/y displacement of the
# beamstop for each selector preset.
#
# When you add a new detector z position, make sure to add a real offset as
# well in the DETECTOR_OFFSETS table below.

DETECTOR_PRESETS = {
#    '2.9A tilt': {
#        '1.5m':    dict(z=1.5,  x=15.0,  y=620.0),
#        '1.5m DB': dict(z=1.5,  x=18.8,  y=500.0, attenuator='in'),
#        '2m':      dict(z=2,    x=18.8,  y=596.8),
#        '2m DB':   dict(z=2,    x=13.0,  y=500.0, attenuator='in'),
#        '4m':      dict(z=4,    x=14.0,  y=621.0),
#        '8m':      dict(z=8,    x=22.5,  y=593.8),
#        '8m DB':   dict(z=8,    x=13.0,  y=500.0, attenuator='in'),
#        '20m DB':  dict(z=19.9, x=13.0,  y=500.0, attenuator='in'),
#        '20m':     dict(z=19.9, x=21.0,  y=586.0),
#        'Small':   dict(det='small', x=0.0, y=711.4),
#    },
#    '3.95A tilt': {
#        '1.5m':    dict(z=1.5,  x=18.8,  y=596.8),
#        '1.5m DB': dict(z=1.5,  x=18.8,  y=500.0, attenuator='in'),
#        '2m':      dict(z=2,    x=18.8,  y=597.8),
#        '4m':      dict(z=4,    x=19.5,  y=597.5),
#       '6m':      dict(z=6,    x=16.0,  y=603.6),
#        '8m':      dict(z=8,    x=21.5,  y=594.0),
#        '8m DB':   dict(z=8,    x=13.0,  y=500.0, attenuator='in'),
#       '8m att':  dict(z=8,    x=13.0,  y=500.0),
#        '20m':     dict(z=19.9, x=20.0,  y=586.0),
#        'Small':   dict(det='small', x=0.0, y=711.4),
#    },
    '4.66A': {
        '1.5m':    dict(z=1.5,  x=1.0,  y=520),
        '1.5m DB': dict(z=1.5,  x=2.0,  y=500.0, attenuator='in'),
        '2m':      dict(z=2,    x=1,    y=521.5),
        '4m':      dict(z=4,    x=3,    y=521.5),
        '8m DB':   dict(z=8,    x=13.0, y=500.0, attenuator='in'),
        '8m':      dict(z=8,    x=2.5,  y=520.5),
        '20m':     dict(z=19.9, x=3.0,  y=514),
        'Small':   dict(det='small', x=0.0, y=711.4),
##########################################################################
############################# ACHTUNG ####################################
# New beamstop values measured on 03.05.2017 for 2, 4, 8, and 20m at 5 A
# wavelength
##########################################################################
##########################################################################
    },
#    '4.66A tilt': {
#        '1.5m':    dict(z=1.5,  x=18.8,  y=596.8),
#	 '1.5m DB': dict(z=1.5,  x=18.8,  y=500.0, attenuator='in'),
#        '2m':      dict(z=2,    x=18.8,  y=597.8),
#        '4m':      dict(z=4,    x=19.5,  y=597.5),
#        '8m DB':   dict(z=8,    x=13.0,  y=500.0, attenuator='in'),
#        '8m':      dict(z=8,    x=17.0,  y=621),
#        '20m':     dict(z=19.9, x=20.0,  y=586.0),
#        'Small':   dict(det='small', x=0.0, y=711.4),
#    },
    '5A': {
        '1.5m':    dict(z=1.5,  x=1.0,  y=520),
        '1.5m DB': dict(z=1.5,  x=2.0,  y=620.0, attenuator='in'),
        '2m':      dict(z=2,    x=1.0,  y=521.5),
        '4m':      dict(z=4,    x=3,    y=521.5),
#       '6m':      dict(z=6,    x=16.0, y=603.6),
        '8m':      dict(z=8,    x=1.5,  y=520.5),
#x=21.5,  y=594.0),
        '8m DB':   dict(z=8,    x=2.0,  y=620.0, attenuator='in'),
#       '8m att':  dict(z=8,    x=13.0, y=500.0),
        '20m':     dict(z=19.9, x=3.0,  y=512.0),
#       '20ms':    dict(z=19.9, x=21.0, y=400.0),
        '20m DB':  dict(z=19.9, x=2.0,  y=620.0, attenuator='in'),
        'Small':   dict(det='small', x=0.0, y=711.4),
    },
#    '5A tilt': {
#        '1.5m':    dict(z=1.5,  x=19.0,  y=596.5),
#        '2m':      dict(z=2,    x=15.6,  y=617.0),
#        '2m DB':   dict(z=2,    x=13.0,  y=500.0, attenuator='in'),
#        '4m':      dict(z=4,    x=13.7,  y=617.0),
#        '6m':      dict(z=6,    x=16.0,  y=603.6),
#        '8m':      dict(z=8,    x=16.0,  y=617.0),
#        '8m DB':   dict(z=8,    x=13.0,  y=500.0, attenuator='in'),
#        '8m att':  dict(z=8,    x=13.0,  y=500.0),
#        '20m':     dict(z=19.9, x=14.6,  y=592.4),
#        'Small':   dict(det='small', x=0.0, y=711.4),
#    },
#    '6A tilt': {
#        '1.5m':    dict(z=1.5,  x=19.0,  y=596.5),
#        '1.5m DB': dict(z=1.5,  x=18.8,  y=500.0, attenuator='in'),
#        '2m':      dict(z=2,    x=18.8,  y=597.8),
#        '4m':      dict(z=4,    x=19.5,  y=597.5),
#        '6m':      dict(z=6,    x=16.0,  y=603.6),
#        '8m':      dict(z=8,    x=21.5,  y=594.0),
#        '8m DB':   dict(z=8,    x=13.0,  y=500.0, attenuator='in'),
#        '8m att':  dict(z=8,    x=13.0,  y=500.0),
#        '20m':     dict(z=19.9, x=20.0,  y=586.5),
#        'Small':   dict(det='small', x=0.0, y=711.4),
#    },
#    '6A': {
#        '1.5m DB': dict(z=1.5,  x=18.8,  y=500.0, attenuator='in'),
#        '2m':      dict(z=2,    x=13.0,  y=597.8),
#        '8m DB':   dict(z=8,    x=13.0,  y=500.0, attenuator='in'),
#        'Small':   dict(det='small', x=0.0, y=711.4),
#    },
    '7A': {
        '1.5m':    dict(z=1.5,  x=1.0,   y=520.5),
        '1.5m DB': dict(z=1.5,  x=18.8,  y=500.0, attenuator='in'),
        '2m':      dict(z=2,    x=1.0,   y=521.5),
#       '2m DB':   dict(z=2,    x=16.9,  y=500.0, attenuator='in'),
        '4m':      dict(z=4,    x=2.5,   y=521.0),
        '8m':      dict(z=8,    x=5.0,   y=522),
        '8m DB':   dict(z=8,    x=13.0,  y=500.0, attenuator='in'),
        '20m DB':  dict(z=19.9, x=13.0,  y=500.0, attenuator='in'),
        '20m':     dict(z=19.9, x=15.5,  y=606.0),
        'Small':   dict(det='small', x=-40.0, y=785.0),
    },
#    '7A tilt': {
#        '1.5m':    dict(z=1.5,  x=18.8,  y=596.8),
#        '1.5m DB': dict(z=1.5,  x=18.8,  y=500.0, attenuator='in'),
#        '2m':      dict(z=2,    x=18.8,  y=597.9),
#        '2m DB':   dict(z=2,    x=16.9,  y=500.0, attenuator='in'),
#        '4m':      dict(z=4,    x=20.3,  y=597.5),
#        '8m':      dict(z=8,    x=20.9,  y=592.5),
#        '8m DB':   dict(z=8,    x=20.9,  y=500.0, attenuator='in'),
#        '20m':     dict(z=19.9, x=15.0,  y=581.2),
#        'Small':   dict(det='small', x=-40.0, y=785),
#    },
#    '8A': {
#        '1.5m':    dict(z=1.5,  x=18.8,  y=500.0),
#        '1.5m DB': dict(z=1.5,  x=18.8,  y=500.0, attenuator='in'),
#        '2m':      dict(z=2,    x=18.8,  y=597.8),
#        '8m DB':   dict(z=8,    x=13.0,  y=500.0, attenuator='in'),
#        '8m':      dict(z=8,    x=2.5,   y=610.0),
#        '20m':     dict(z=19.9, x=1.0,   y=610.0),
#        'Small':   dict(det='small', x=0.0, y=711.4),
#    },
#    '9A': {
#        '1.5m':    dict(z=1.5,  x=18.8,  y=500.0),
#        '1.5m DB': dict(z=1.5,  x=18.8,  y=500.0, attenuator='in'),
#        '2m':      dict(z=2,    x=18.8,  y=597.8),
#        '4m':      dict(z=4,    x=16.3,  y=604.0),
#        '8m DB':   dict(z=8  ,  x=13.0,  y=500.0, attenuator='in'),
#        'Small':   dict(det='small', x=0.0, y=711.4),
# only 8m and 20 m have been updated at lambda = 10 A
#    },
    '10A': {
        '1.5m':    dict(z=1.5,  x=18.8,  y=500.0),
        '1.5m DB': dict(z=1.5,  x=18.8,  y=500.0, attenuator='in'),
        '2m':      dict(z=2,    x=16.0,  y=600.0),
        '4m':      dict(z=4,    x=1.5,   y=519.0),
        '8m':      dict(z=8,    x=3.0,   y=516.0),
        '8m DB':   dict(z=8,    x=4.0,   y=620.0, attenuator='in'),
        '20m':     dict(z=19.9, x=4.0,   y=494.0),
        '20m DB':  dict(z=19.9, x=4.0,   y=300.0),
        'Small':   dict(det='small', x=0.0, y=711.4),
    },
#    '11.3A': {
#        '2m':      dict(z=2,    x=18.8,  y=597.8),
#        '8m DB':   dict(z=8,    x=13.0,  y=500.0, attenuator='in'),
#        '4m':      dict(z=4,    x=16.3,  y=604.0),
#        '8m':      dict(z=8,    x=16.3,  y=600.0),
#        '8m DB':   dict(z=8,    x=13.0,  y=500.0, attenuator='in'),
#        '20m':     dict(z=19.9, x=21.5,  y=567.2),
#        'Small':   dict(det='small', x=0.0, y=711.4),
#    },
#    '19A': {
#        '2m':      dict(z=2,    x=18.8,  y=597.8),
#        '20m':     dict(z=19.9, x=16.0,  y=620.0),
#        '8m':      dict(z=8,    x=13.0,  y=500.0),
#        'Small':   dict(det='small', x=0.0, y=711.4),
#    },
}

SMALL_DET_POSITION = 17.0

# This offset is added to 20m + det_z to get the chopper-detector length
# for time-of-flight mode calculation.
#
# It varies with detector distance because the det_z value is not actually
# particularly accurate.

DETECTOR_OFFSETS = {
    1.5:  0.7,
    2:    0.7,
    2.1:  0.7,
    4:    0.7,
    4.1:  0.7,
    6:    0.7,
    8:    0.7,
    8.1:  0.7,
    17.0: 0.7,     # for small detector
    19.9: 0.7,
}
