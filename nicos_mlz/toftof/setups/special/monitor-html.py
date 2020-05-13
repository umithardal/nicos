description = 'setup for the status monitor'

group = 'special'

_reactorblock = Block('Reactor', [
    BlockRow(Field(name='Power', dev='ReactorPower'),
            ),
    ],
)

_expcolumn = Row(
    Block('Experiment', [
        BlockRow(
#                Field(name='Proposal', key='exp/proposal', width=7),
#                Field(name='Title', key='exp/title', width=30, istext=True,
#                      maxlen=40),
#                Field(name='Sample', key='sample/samplename', width=30,
#                      istext=True, maxlen=40),
                 Field(name='Last Image file', key='exp/lastpoint'),
                ),
        ],
    ),
)

_chopperblock = Block('Chopper system', [
    BlockRow(Field(name='Wavelength', dev='chWL', format='%.1f'),
            ),
    BlockRow(
             Field(name='Nom. Speed', dev='chSpeed', format='%.0f'),
             Field(name='Act. Speed', dev='ch', format='%.0f'),
            ),
#   BlockRow(Field(name='Ratio', dev='chRatio'),
#            Field(name='CRC', dev='chCRC'),
#            Field(name='Slit type', dev='chST'),
#           ),
#   '---',
#   BlockRow(Field(name='Disk 1', dev='chDS[0]', format='%.1f'),
#            Field(name='Disk 2', dev='chDS[1]', format='%.1f'),
#           ),
#   BlockRow(
#            Field(name='Disk 3', dev='chDS[2]', format='%.1f'),
#            Field(name='Disk 4', dev='chDS[3]', format='%.1f'),
#           ),
#   BlockRow(
#            Field(name='Disk 5', dev='chDS[4]', format='%.1f'),
#           ),
#   BlockRow(
#            Field(name='Disk 6', dev='chDS[5]', format='%.1f'),
#            Field(name='Disk 7', dev='chDS[6]', format='%.1f'),
#           ),
#   '---',
#   BlockRow(Field(name='Flow in (FAK40)', dev='flow_in_ch_cooling',),),
#   '---',
#   BlockRow(Field(name='Gauge 1', dev='vac0', format='%.2g'),
#            Field(name='Gauge 2', dev='vac1', format='%.2g'),
#           ),
#   BlockRow(Field(name='Gauge 3', dev='vac2', format='%.2g'),
#            Field(name='Gauge 4', dev='vac3', format='%.2g'),
#           ),
    ],
    setups='toftof',
)

_choppercoolingblock = Block('Cooling system (Chopper)', [
    BlockRow(Field(name='T in', dev='t_in_ch_cooling',),
             Field(name='T out', dev='t_out_ch_cooling',),
             Field(name='Flow in', dev='flow_in_ch_cooling',),
             Field(name='P in', dev='p_in_ch_cooling',),
             Field(name='Leakage', dev='leak_ch_cooling',),
             Field(name='Cool power', dev='power_ch_cooling',),
            )
    ],
    setups='toftof',
)

_collimationblock = Block('Radial Collimator/Collimation', [
    BlockRow(Field(name='Radial', dev='rc_motor',),
             Field(name='Collimator', dev='ngc',),
            ),
    ],
    setups='toftof',
)

_samplecoolingblock = Block('Cooling system (Sample)', [
    BlockRow(Field(name='Flow in', dev='flow_in_sa_cooling',),
            ),
    ],
    setups='biofurnace or ccmhts01 or ccr* or htf* or ccm*',
)

_ccrblock = Block('Sample environment', [
    BlockRow(Field(name='Stick', dev='T_ccr17_stick',),
             Field(name='Tube', dev='T_ccr17_tube',),
            ),
    BlockRow(
             Field(name='Vacuum/Gas', dev='ccr17_p2',)
            ),
    ],
    setups='ccr17',
)

_julabo01block = Block('Sample environment', [
    BlockRow(Field(name='Julabo', dev='T_julabo01'),)
    ],
    setups='julabo01',
)

_htfblock = Block('Sample environment', [
    BlockRow(Field(name='Sample', dev='T_htf01'),
             Field(name='Vacuum', dev='htf01_p'),
            ),
    ],
    setups='htf01',
)

_biofurnaceblock = Block('Sample environment', [
    BlockRow(Field(name='Sample', dev='T_bio',),)
    ],
    setups='biofurnace',
)

_temperatureblock = Block('Sample environment', [
    BlockRow(Field(name='Sample Temperatur', dev='T',)),
    ],
    setups='ccr* or cci* or htf* or biofurnace',
)

_pressureblock = Block('Sample environment', [
    BlockRow(Field(name='Pressure', dev='pressure',)),
    ],
    setups='pressure',
)

_magnetblock = Block('Sample environment', [
    BlockRow(Field(name='Magnetic field', dev='B',)),
    ],
    setups='ccm*',
)

_ngblock = Block('Neutron Guide', [
    BlockRow(Field(name='Focus', dev='ng_focus')),
    ],
    setups='ng',
)

_vacuumblock = Block('Vacuum', [
    BlockRow(Field(name='Gauge 1', dev='vac0', format='%.2g'),
             Field(name='Gauge 2', dev='vac1', format='%.2g'),
             Field(name='Gauge 3', dev='vac2', format='%.2g'),
             Field(name='Gauge 4', dev='vac3', format='%.2g'),
            ),
    ],
)

_tableblock = Block('Sample table', [
    BlockRow(Field(dev='gx'),
             Field(dev='gy'),
             Field(dev='gz'),
            ),
    BlockRow(Field(dev='gcx'),
             Field(dev='gcy'),
             Field(dev='gphi'),
            ),
    ]
)

_samplerotationblock = Block('Sample rotation', [
    BlockRow(Field(dev='sth')),
    ],
    setups='newport1*',
)

_slitblock = Block('Sample slit', [
    BlockRow(Field(dev='slit', istext=True, width=24, name='Slit'))
    ],
)

_measblock = Block('Measurement', [
    BlockRow(Field(key='det/timechannels', name='Time channels'),),
    BlockRow(Field(name='Time', dev='timer', format='%.1f'),
             Field(name='Monitor', key='det/rates[1][1]', format='%.1f'),
             Field(name='Counts', key='det/rates[1][0]', format='%.1f'),
            ),
    ],
)

_rateblock = Block('Detector rates', [
#     BlockRow(Field(gui='nicos_mlz/toftof/gui/ratespanel.ui')),
      ],
      setups='toftof',
)

_col1 = Column(
    _measblock,
    _chopperblock,
)

_col2 = Column(
    _reactorblock,
#   _samplecoolingblock,
#   _collimationblock,
    _ngblock,
    _temperatureblock,
    _ccrblock,
    _julabo01block,
    _htfblock,
    _biofurnaceblock,
    _pressureblock,
    _magnetblock,
    _samplerotationblock,
)

_col3 = Column(
    _rateblock,
)

devices = dict(
    Monitor = device('nicos.services.monitor.html.Monitor',
        title = 'TOFTOF status monitor',
        loglevel = 'info',
        interval = 10,
        filename = '/toftofcontrol/status.html',
        cache = 'tofhw.toftof.frm2:14869',
        prefix = 'nicos/',
        font = 'Luxi Sans',
        valuefont = 'Consolas',
        # padding = 2,
        fontsize = 17,
        layout = [[_expcolumn], [_col1, _col2]],
    ),
)
