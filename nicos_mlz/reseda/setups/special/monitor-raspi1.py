description = 'setup for the right status monitor'
group = 'special'

_expcolumn = Column(
    Block('Experiment', [
        BlockRow(Field(name='Proposal', key='exp/proposal', width=7),
                 Field(name='Title',    key='exp/title',    width=30,
                       istext=True, maxlen=15),
                 Field(name='Sample',   key='sample/samplename', width=20,
                       istext=True, maxlen=15),
                 #Field(name='Current status', key='exp/action', width=30,
                 #      istext=True),
                 Field(name='Last file', key='exp/lastscan'),
                 Field(name='EchoTime', key='echotime', unit='ns'),
                 Field(name='Wavelength', dev='selector_lambda', unit='A')),
        ],
        setups='selector',
    ),
)

_column1 = Column(
    Block('Attenuators', [
        BlockRow(Field(name='att0', dev='att0'),
                 Field(name='att1', dev='att1'),
                 Field(name='att2', dev='att2')),
        ],
        setups='attenuators',
    ),
    Block('Slits', [
        BlockRow(Field(name='Pinhole 5', dev='pinhole5', unit='mm'),
                 Field(name='Pinhole 10', dev='pinhole10', unit='mm'),
                 Field(name='Slit 10x40', dev='slit', unit='mm')),
        ],
        setups='slits',
    ),
    Block('Environment', [
        BlockRow(Field(name='Power', dev='ReactorPower', format='%.1f', width=6),
                 Field(name='6-fold', dev='Sixfold', min='open', width=6)),
                 #Field(dev='NL5S', min='open', width=6),
                 #Field(dev='UBahn', width=5, istext=True, unit=' '),
                 #Field(dev='OutsideTemp', name='Temp', width=4, unit=' '),
        BlockRow(#Field(dev='DoseRate', name='Rate', width=6),
                 #Field(dev='Cooling', width=6),
                 #Field(dev='CoolTemp', name='CoolT', width=6, format='%.1f', unit=' '),
                 #Field(dev='PSDGas', width=6),
                 #Field(dev='ar', name='PSD Ar', width=4, format='%.1f', unit=' '),
                 #Field(dev='co2', name='PSD CO2', width=4, format='%.1f', unit=' '),
                 #Field(dev='t_in_fak40', name='FAK40', width=6, format='%.1f', unit=' '),
                 Field(dev='Crane', width=7)),
        ],
        setups='reactor and guidehall',
    ),
)

_column2 = Column(
    Block('Sample slits', [
        #BlockRow(Field(dev='slit1', name='Entrance slit', width=24, istext=True)),
        BlockRow(Field(dev='slit2', name='Sample slit', width=24, istext=True)),
        ],
        setups='slitsng',
    ),
    Block('Sample table', [
        BlockRow(Field(name='Rotation', dev='srz', unit='deg')),
        BlockRow('stx', 'sty'),
        BlockRow('sgx', 'sgy'),
        ],
        setups='sampletable',
    ),
    Block('arms', [
        BlockRow(Field(name='arm1', dev='arm1_rot', unit='deg'),
                 Field(name='arm2', dev='arm2_rot', unit='deg')),
        ],
     ),
)

_column3 = Column(
    Block('Cascade detector', [
        BlockRow(Field(name='ROI',   key='psd_channel[0]', format='%.0f', width=9),
                 Field(name='Total', key='psd_channel[1]', format='%.0f', width=9),
                 Field(name='MIEZE', key='psd_channel[2]', format='%.3f', width=6),
                 Field(name='Last image', key='exp/lastpoint')),
        BlockRow('timer', 'monitor1' ),
        BlockRow(Field(dev='mon_hv', width=6)),
                 #Field(dev='PSDHV', width=5),
                 #Field(dev='dtx')),
        ],
        setups='det_cascade and det_base',
    ),
    Block('Cryostat', [
        #BlockRow(
        #    Field(widget='nicos.guisupport.plots.TrendPlot', devices='T', names='T',  plotwindow=7200)),
        BlockRow(
            Field(name='T' ,key='T', unit='K'),
            Field(name='Ts', key='Ts', unit='K'),
            Field(name='Pressure', key='P_ccr', unit='mbar')),
        ],
        setups='alias_T and ccr'
        ),
)

devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        title = 'RESEDA MIEZE',
        loglevel = 'info',
        cache = 'resedahw2.reseda.frm2',
        prefix = 'nicos/',
        font = 'Droid Sans',
        valuefont = 'Consolas',
        fontsize = '14',
        padding = 2,
        layout = [[_expcolumn], [_column1, _column2, _column3]]
    ),
)
