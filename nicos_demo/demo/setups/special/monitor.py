description = 'setup for the status monitor'
group = 'special'

_expcolumn = Column(
    Block('Experiment', [
        BlockRow(
            Field(name='Proposal', key='exp/proposal', width=7),
            Field(name='Title',    key='exp/title',    width=20, istext=True,
                  maxlen=20),
            Field(name='Current status', key='exp/action', width=40,
                  istext=True, maxlen=40),
            Field(name='Last scan file', key='exp/lastscan',
                  setups='tas'),
            Field(name='Last image file', key='exp/lastpoint',
                  setups='sans'),
        )
    ],
    ),
)

_axisblock = Block('Axes', [
    BlockRow(Field(gui='nicos/clients/gui/panels/tasaxes.ui')),
    # BlockRow('mth', 'mtt'),
    # BlockRow('psi', 'phi'),
    # BlockRow('ath', 'att'),
    ],
    setups='tas',  # this is the name of a setup that must be loaded in the
                   # NICOS master instance for this block to be displayed
)

_tempblock = SetupBlock('cryo')  # this block is loaded from the "cryo" setup

_detectorblock = Block('Detector', [
    BlockRow(Field(name='timer', dev='timer'),
             Field(name='ctr1',  dev='ctr1'),
             Field(name='ctr2',  dev='ctr2')),
    ],
    setups='detector',
)

_tasblock = Block('Triple-axis', [
    BlockRow(Field(dev='tas[0]', name='H', format='%.3f', unit=' '),
             Field(dev='tas[1]', name='K', format='%.3f', unit=' '),
             Field(dev='tas[2]', name='L', format='%.3f', unit=' '),
             Field(dev='tas[3]', name='E', format='%.3f', unit=' ')),
    BlockRow(Field(key='tas/scanmode', name='Mode'),
             Field(dev='mono', name='ki', min=1.55, max=1.6),
             Field(dev='ana', name='kf'),
             Field(key='tas/energytransferunit', name='Unit')),
    BlockRow(Field(widget='nicos.guisupport.tas.TasWidget',
                   width=40, height=30,
                   mthdev='mth',
                   mttdev='mtt',
                   sthdev='psi',
                   sttdev='phi',
                   athdev='ath',
                   attdev='att',
                   Lmsdev='Lms',
                   Laddev='Lad',
                   Lsadev='Lsa',)),
    ],
    setups='tas',
)

_slitblock = Block('Sample Slit', [
    BlockRow(Field(dev='ss', name='Sample slit')),
    BlockRow(Field(dev='ss.height', name='Height'),
             Field(dev='ss.width', name='Width')),
    ],
    setups='tas',
)

_sansblock = Block('SANS', [
    BlockRow(
        Field(dev='guide1', name='G1',
              widget='nicos_mlz.sans1.gui.monitorwidgets.CollimatorTable',
              options=['off', 'ng', 'P3', 'P4'],
              # options=['off', 'ng'],#'P3', 'P4'],
              width=4, height=5),
        Field(dev='guide2', name='G2',
              widget='nicos_mlz.sans1.gui.monitorwidgets.CollimatorTable',
              options=['off', 'ng', 'P3', 'P4'],
              # options=['off', 'ng'],#'P3','P4'],
              width=4, height=5),
        Field(dev='guide3', name='G3',
              widget='nicos_mlz.sans1.gui.monitorwidgets.CollimatorTable',
              options=['off', 'ng', 'P3', 'P4'],
              # options=['off', 'ng'],#'P3','P4'],
              width=4, height=5),
        Field(dev='guide4', name='G4',
              widget='nicos_mlz.sans1.gui.monitorwidgets.CollimatorTable',
              options=['off', 'ng', 'P3', 'P4'],
              # options=['off', 'ng'],#'P3', 'P4'],
              width=4, height=5),
        # Field(dev='det_pos', name='Detector position',
        #       widget='nicos_mlz.sans1.gui.monitorwidgets.Tube', width=30,
        #       height=10)),
        Field(devices=['det_pos1', 'det_pos1_x', 'det_pos1_tilt', 'det_pos2'],
              name='Detector position',
              widget='nicos_mlz.sans1.gui.monitorwidgets.Tube2', width=30, height=10,
              posscale=21)
    ),
    BlockRow(
        Field(dev='guide', name='Guide',
              widget='nicos_mlz.sans1.gui.monitorwidgets.BeamOption',
              width=10, height=4),
        Field(dev='det_HV', name='Detector HV', format='%d'),
        Field(key='det/lastcounts', name='Counts on det', format='%d', setups='sans and misc')
    ),
    '---',
    BlockRow(
        Field(name='Data (linear)', picture='data/live_lin.png', refresh=1,
              width=12, height=12),
        Field(name='Data (log)', picture='data/live_log.png', refresh=1,
              width=12, height=12),
    )
    ],
    setups='sans',
)

_rightcolumn = Column(_axisblock, _tempblock)

_leftcolumn = Column(_tasblock, _slitblock, _sansblock)

devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        title = 'NICOS status monitor',
        loglevel = 'info',
        cache = 'localhost:14869',
        font = 'Luxi Sans',
        valuefont = 'Consolas',
        padding = 0,
        colors = 'light',
        layout = [
            Row(_expcolumn),
            Row(_leftcolumn, _rightcolumn),
        ],
    ),
)
