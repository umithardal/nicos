description = 'setup for the HTML status monitor'
group = 'special'

_expcolumn = Column(
    Block('Experiment', [
        BlockRow(
                 Field(name='Current status', key='exp/action', width=90,
                       istext=True, maxlen=90),
                 Field(name='Last file', key='exp/lastpoint'),
                 Field(name='Current Sample', key='sample/samplename', width=26),
                ),
        ],
    ),
)

_selcolumn = Column(
    Block('Selector', [
        BlockRow(
                 Field(name='selector_rpm', dev='selector_rpm', width=16),
                 Field(name='selector_lambda', dev='selector_lambda', width=16),
                 ),
        BlockRow(
                 Field(name='selector_ng', dev='selector_ng', width=16),
                 Field(name='selector_tilt', dev='selector_tilt', width=16),
                ),
        BlockRow(
                 Field(name='water flow', dev='selector_wflow', width=16),
                 Field(name='rotor temp.', dev='selector_rtemp', width=16),
                ),
        ],
    ),
)

_ubahncolumn = Column(
    Block('U-Bahn', [
        BlockRow(
                 Field(name='Train', dev='Ubahn'),
                ),
        ],
    ),
)

_meteocolumn = Column(
    Block('Outside Temp', [
        BlockRow(
                 Field(name='Temp', dev='meteo', width=12),
                ),
        ],
    ),
)

_pressurecolumn = Column(
    Block('Pressure', [
        BlockRow(
                 # Field(name='Col Pump', dev='coll_pump'),
                 Field(name='Col Tube', dev='coll_tube'),
                 Field(name='Col Nose', dev='coll_nose'),
                 Field(name='Det Nose', dev='det_nose'),
                 Field(name='Det Tube', dev='det_tube'),
                 ),
        ],
    ),
)

_table2 = Column(
    Block('Sample Table 2', [
        BlockRow(
                 Field(name='st2_z', dev='st2_z', width=13),
                 ),
        BlockRow(
                 Field(name='st2_y', dev='st2_y', width=13),
                 ),
        BlockRow(
                 Field(name='st2_x', dev='st2_x', width=13),
                 ),
        ],
        setups='sample_table_2',
    ),
)

_table1 = Column(
    Block('Sample Table 1', [
        BlockRow(
                 Field(name='st1_phi', dev='st1_phi', width=13),
                 Field(name='st1_y', dev='st1_y', width=13),
                 ),
        BlockRow(
                 Field(name='st1_chi', dev='st1_chi', width=13),
                  Field(name='st1_z', dev='st1_z', width=13),
                ),
        BlockRow(
                 Field(name='st1_omg', dev='st1_omg', width=13),
                 Field(name='st1_x', dev='st1_x', width=13),
                ),
        ],
        setups='sample_table_1',
    ),
)

_sans1general = Column(
    Block('General', [
        BlockRow(
                 Field(name='Reactor', dev='ReactorPower', width=12),
                 Field(name='6 Fold Shutter', dev='Sixfold', width=12),
                 Field(name='NL4a', dev='NL4a', width=12),
                ),
        BlockRow(
                 Field(name='T in', dev='t_in_memograph', width=12, unit='C'),
                 Field(name='T out', dev='t_out_memograph', width=12, unit='C'),
                 Field(name='Cooling', dev='cooling_memograph', width=12,
                       unit='kW'),
                ),
        BlockRow(
                 Field(name='Flow in', dev='flow_in_memograph', width=12,
                       unit='l/min'),
                 Field(name='Flow out', dev='flow_out_memograph', width=12,
                       unit='l/min'),
                 Field(name='Leakage', dev='leak_memograph', width=12,
                       unit='l/min'),
                ),
        BlockRow(
                 Field(name='P in', dev='p_in_memograph', width=12, unit='bar'),
                 Field(name='P out', dev='p_out_memograph', width=12,
                       unit='bar'),
                 Field(name='Crane Pos', dev='Crane', width=12),
                ),
        ],
    ),
)

_sans1det = Column(
    Block('Detector', [
        BlockRow(
                 Field(name='t', dev='det1_t_ist', width=13),
                 Field(name='t preset', key='det1_timer.preselection', width=13),
                ),
        BlockRow(
                 Field(name='det1_hv', dev='det1_hv_ax', width=13),
                 Field(name='det1_z', dev='det1_z', width=13),
                ),
        BlockRow(
                 Field(name='det1_omg', dev='det1_omg', width=13),
                 Field(name='det1_x', dev='det1_x', width=13),
                ),
        BlockRow(
                 Field(name='bs1', dev='bs1', width=13),
                 Field(name='bs1_shape', dev='bs1_shape', width=13),
                ),
        BlockRow(
                 Field(name='events', dev='det1_ev', width=13),
                ),
        BlockRow(
                 Field(name='mon 1', dev='det1_mon1', width=13),
                 Field(name='mon 2', dev='det1_mon2', width=13),
                ),
        ],
    ),
)

_atpolcolumn = Column(
    Block('Attenuator / Polarizer',[
        BlockRow(
                 Field(dev='att', name='att', width=12),
                 ),
        BlockRow(
                 Field(dev='ng_pol', name='ng_pol', width=12),
                ),
        ],
    ),
)

_sanscolumn = Column(
    Block('Collimation',[
        BlockRow(
                 Field(dev='bg1', name='bg1', width=12),
                 Field(dev='bg2', name='bg2', width=12),
                 Field(dev='sa1', name='sa1', width=12),
                 Field(dev='sa2', name='sa2', width=12),
                ),
        BlockRow(
                 Field(dev='col', name='col', unit='m', format = '%.1f',
                       width=12),
                ),
        ],
    ),
)

# _birmag = Column(
#     Block('17T Magnet', [
#         BlockRow(
#                  Field(name='helium level', dev='helevel_birmag', width=13),
#                  Field(name='field birmag', dev='field_birmag', width=13),
#                 ),
#         BlockRow(
#                  Field(name='Setpoint 1 birmag', dev='sp1_birmag', width=13),
#                  Field(name='Setpoint 2 birmag', dev='sp2_birmag', width=13),
#                 ),
#         BlockRow(
#                  Field(name='Temp a birmag', dev='ta_birmag', width=13),
#                  Field(name='Temp b birmag', dev='tb_birmag', width=13),
#                 ),
#         ],
#         setups='birmag',
#     ),
# )

_miramagnet = Column(
    Block('MIRA Magnet', [
        BlockRow(
                 Field(name='Field', dev='B_miramagnet'),
                 Field(name='Target', key='B_miramagnet/target', width=12),
                ),
        BlockRow(
                 Field(name='Current', dev='I_miramagnet', width=12),
                ),
        ],
        setups='miramagnet',
    ),
)

_miramagnet_plot = Column(
    Block('Miramagnet plot', [
        BlockRow(
                 Field(plot='30 min miramagnet', name='30 min',
                       dev='B_miramagnet', width=60, height=40, plotwindow=1800),
                 Field(plot='30 min miramagnet', name='Target',
                       key='B_miramagnet/target'),
                 Field(plot='6 h', name='6 h',
                       dev='B_miramagnet', width=60, height=40, plotwindow=6*3600),
                 Field(plot='6 h', name='Target',
                       key='B_miramagnet/target'),
        ),
        ],
        setups='miramagnet',
    ),
)

_amagnet = Column(
    Block('Antares Magnet', [
        BlockRow(
                 Field(name='Field', dev='B_amagnet'),
                 Field(name='Target', key='B_amagnet/target', width=12),
                ),
        ],
        setups='amagnet',
    ),
)

_sc1 = Column(
    Block('Sample Changer 1', [
         BlockRow(
            Field(name='Position', dev='sc1_y'),
            Field(name='SampleChanger', dev='sc1'),
        ),
        ],
        setups='sc1',
    ),
)

_sc2 = Column(
    Block('Sample Changer 2', [
         BlockRow(
            Field(name='Position', dev='sc2_y'),
            Field(name='SampleChanger', dev='sc2'),
        ),
        ],
        setups='sc2',
    ),
)

_sc_t = Column(
    Block('Temperature Sample Changer', [
         BlockRow(
            Field(name='Position', dev='sc_t_y'),
            Field(name='SampleChanger', dev='sc_t'),
        ),
        ],
        setups='sc_t',
    ),
)

_ccmsanssc = Column(
    Block('Magnet Sample Changer', [
         BlockRow(
            Field(name='Position', dev='ccmsanssc_axis'),
        ),
         BlockRow(
            Field(name='SampleChanger', dev='ccmsanssc_position', format='%i'),
        ),
         BlockRow(
            Field(name='Switch', dev='ccmsanssc_switch'),
        ),
        ],
        setups='ccmsanssc',
    ),
)

_htf03 = Column(
    Block('HTF03', [
        BlockRow(
            Field(name='Temperature', dev='T_htf03', format='%.2f'),
            Field(name='Target', key='t_htf03/target', format='%.2f'),
        ),
        BlockRow(
            Field(name='Setpoint', key='t_htf03/setpoint', format='%.1f'),
            Field(name='Heater Power', key='t_htf03/heaterpower', format='%.1f'),
        ),
        ],
        setups='htf03',
    ),
)

_htf03_plot = Column(
    Block('HTF03 plot', [
        BlockRow(
                 Field(plot='30 min htf03', name='30 min', dev='T_htf03',
                       width=60, height=40, plotwindow=1800),
                 Field(plot='30 min htf03', name='Setpoint',
                       dev='T_htf03/setpoint'),
                 Field(plot='30 min htf03', name='Target', dev='T_htf03/target'),
                 Field(plot='12 h htf03', name='12 h', dev='T_htf03', width=60,
                       height=40, plotwindow=12*3600),
                 Field(plot='12 h htf03', name='Setpoint',
                       dev='T_htf03/setpoint'),
                 Field(plot='12 h htf03', name='Target', dev='T_htf03/target'),
        ),
        ],
        setups='htf03',
    ),
)

_irf01 = Column(
    Block('IRF01', [
        BlockRow(
            Field(name='Temperature', dev='T_irf01', format='%.2f'),
            Field(name='Target', key='t_irf01/target', format='%.2f'),
        ),
        BlockRow(
            Field(name='Setpoint', key='t_irf01/setpoint', format='%.1f'),
            Field(name='Heater Power', key='t_irf01/heaterpower', format='%.1f'),
        ),
        ],
        setups='irf01',
    ),
)

_irf01_plot = Column(
    Block('IRF01 plot', [
        BlockRow(
                 Field(plot='30 min irf01', name='30 min', dev='T_irf01',
                       width=60, height=40, plotwindow=1800),
                 Field(plot='30 min irf01', name='Setpoint',
                       dev='T_irf01/setpoint'),
                 Field(plot='30 min irf01', name='Target', dev='T_irf01/target'),
                 Field(plot='12 h irf01', name='12 h', dev='T_irf01', width=60,
                       height=40, plotwindow=12*3600),
                 Field(plot='12 h irf01', name='Setpoint',
                       dev='T_irf01/setpoint'),
                 Field(plot='12 h irf01', name='Target', dev='T_irf01/target'),
        ),
        ],
        setups='irf01',
    ),
)

_irf10 = Column(
    Block('IRF10', [
        BlockRow(
            Field(name='Temperature', dev='T_irf10', format='%.2f'),
            Field(name='Target', key='t_irf10/target', format='%.2f'),
        ),
        BlockRow(
            Field(name='Setpoint', key='t_irf10/setpoint', format='%.1f'),
            Field(name='Heater Output', key='t_irf10/heateroutput', format='%.1f'),
        ),
        ],
        setups='irf10',
    ),
)

_irf10_plot = Column(
    Block('IRF10 plot', [
        BlockRow(
                 Field(plot='30 min irf10', name='30 min', dev='T_irf10',
                       width=60, height=40, plotwindow=1800),
                 Field(plot='30 min irf10', name='Setpoint',
                       dev='T_irf10/setpoint'),
                 Field(plot='30 min irf10', name='Target', dev='T_irf10/target'),
                 Field(plot='12 h irf10', name='12 h', dev='T_irf10', width=60,
                       height=40, plotwindow=12*3600),
                 Field(plot='12 h irf10', name='Setpoint',
                       dev='T_irf10/setpoint'),
                 Field(plot='12 h irf10', name='Target', dev='T_irf10/target'),
        ),
        ],
        setups='irf10',
    ),
)

_htf01 = Column(
    Block('HTF01', [
        BlockRow(
            Field(name='Temperature', dev='T_htf01', format='%.2f'),
            Field(name='Target', key='t_htf01/target', format='%.2f'),
        ),
        BlockRow(
            Field(name='Setpoint', key='t_htf01/setpoint', format='%.1f'),
            Field(name='Heater Power', key='t_htf01/heaterpower', format='%.1f'),
        ),
        ],
        setups='htf01',
    ),
)

_htf01_plot = Column(
    Block('HTF01 plot', [
        BlockRow(
                 Field(plot='30 min htf01', name='30 min', dev='T_htf01',
                       width=60, height=40, plotwindow=1800),
                 Field(plot='30 min htf01', name='Setpoint',
                       dev='T_htf01/setpoint'),
                 Field(plot='30 min htf01', name='Target', dev='T_htf01/target'),
                 Field(plot='12 h htf01', name='12 h', dev='T_htf01', width=60,
                       height=40, plotwindow=12*3600),
                 Field(plot='12 h htf01', name='Setpoint',
                       dev='T_htf01/setpoint'),
                 Field(plot='12 h htf01', name='Target', dev='T_htf01/target'),
        ),
        ],
        setups='htf01',
    ),
)

_p_filter = Column(
    Block('Pressure Water Filter FAK40', [
        BlockRow(
                 Field(name='P in', dev='p_in_filter', width=12, unit='bar'),
                 Field(name='P out', dev='p_out_filter', width=12, unit='bar'),
                 Field(name='P diff', dev='p_diff_filter', width=12, unit='bar'),
                ),
        ],
    ),
)

_ccmsans = Column(
    Block('SANS-1 5T Magnet', [
        BlockRow(Field(name='Field', dev='b_ccmsans', width=14),
                ),
        BlockRow(
                 Field(name='Target', key='b_ccmsans/target', width=14),
                 Field(name='Asymmetry', key='b_ccmsans/asymmetry', width=14),
                ),
        BlockRow(
                 Field(name='Power Supply 1', dev='a_ccmsans_left', width=14),
                 Field(name='Power Supply 2', dev='a_ccmsans_right', width=14),
                ),
        ],
        setups='ccmsans',
    ),
)

_ccmsans_temperature = Column(
    Block('SANS-1 5T Magnet Temperatures', [
        BlockRow(
                 Field(name='CH Stage 1', dev='ccmsans_T1', width=14),
                 Field(name='CH Stage 2', dev='ccmsans_T2', width=14),
                ),
        BlockRow(
                 Field(name='Shield Top', dev='ccmsans_T3', width=14),
                 Field(name='Shield Bottom', dev='ccmsans_T4', width=14),
                ),
        BlockRow(
                 Field(name='Magnet TL', dev='ccmsans_T5', width=14),
                 Field(name='Magnet TR', dev='ccmsans_T6', width=14),
                ),
        BlockRow(
                 Field(name='Magnet BL', dev='ccmsans_T8', width=14),
                 Field(name='Magnet BR', dev='ccmsans_T7', width=14),
                ),
        ],
        setups='ccmsans',
    ),
)

_ccmsans_plot = Column(
    Block('SANS-1 5T Magnet plot', [
        BlockRow(
                 Field(plot='30 min ccmsans', name='30 min', dev='B_ccmsans',
                       width=60, height=40, plotwindow=1800),
                 Field(plot='30 min ccmsans', name='Target',
                       key='B_ccmsans/target'),
                 Field(plot='12 h ccmsans', name='12 h', dev='B_ccmsans',
                       width=60, height=40, plotwindow=12*3600),
                 Field(plot='12 h ccmsans', name='Target',
                       key='B_ccmsans/target'),
        ),
        ],
        setups='ccmsans',
    ),
)

_ccm2a = Column(
    Block('CCM2a Magnet', [
        BlockRow(
             Field(name='Field', dev='B_ccm2a', width=12),
            ),
        BlockRow(
             Field(name='Target', key='B_ccm2a/target', width=12),
             Field(name='Readback', dev='B_ccm2a_readback', width=12),
            ),
        ],
    setups='ccm2a',
    ),
)

_ccm2a_temperature = Column(
    Block('CCM2a Magnet Temperature', [
        BlockRow(
             Field(name='T1', dev='ccm2a_T1', width=12),
             Field(name='T2', dev='ccm2a_T2', width=12),
            ),
        BlockRow(
             Field(name='TA', dev='ccm2a_TA', width=12),
             Field(name='TB', dev='ccm2a_TB', width=12),
            ),
        ],
    setups='ccm2a',
    ),
)

_ccm2a_plot = Column(
    Block('CCM2a Magnet plot', [
        BlockRow(
                 Field(plot='30 min ccm2a', name='30 min', dev='B_ccm2a',
                       width=60, height=40, plotwindow=1800),
                 Field(plot='30 min ccm2a', name='Target', key='B_ccm2a/target'),
                 Field(plot='12 h ccm2a', name='12 h', dev='B_ccm2a', width=60,
                       height=40, plotwindow=12*3600),
                 Field(plot='12 h ccm2a', name='Target', key='B_ccm2a/target'),
        ),
        ],
        setups='ccm2a',
    ),
)

_ccr19_plot = Column(
    Block('30min T and Ts plot', [
        BlockRow(
                 Field(plot='30 min ccr19', name='T', dev='T', width=60,
                       height=40, plotwindow=1800),
                 Field(plot='30 min ccr19', name='Ts', dev='Ts'),
                 Field(plot='30 min ccr19', name='Setpoint', key='T/setpoint'),
                 Field(plot='30 min ccr19', name='Target', key='T/target'),
        ),
        ],
        setups='ccr19',
    ),
)

_spinflipper = Column(
    Block('Spin Flipper', [
        BlockRow(
             Field(name='P', dev='P_spinflipper'),
        ),
        BlockRow(
             Field(name='Forward', key='P_spinflipper/forward', unitkey='W'),
             Field(name='Reverse', key='P_spinflipper/reverse', unitkey='W'),
        ),
        BlockRow(
             Field(name='Temperature', dev='T_spinflipper'),
             Field(name='Voltage', dev='U_spinflipper'),
        ),
        BlockRow(
             Field(name='A_spinflipper_hp', dev='A_spinflipper_hp'),
             Field(name='F_spinflipper_hp', dev='F_spinflipper_hp'),
        ),
        ],
        setups='spinflip',
    ),
)

newports = []
for k in [1,2,3,4,5,10,11,12]:
    newports.append(Block('NewPort%02d' % k, [
        BlockRow(
            Field(name='Position', dev='sth_newport%02d' % k,
                   unitkey='t/unit', width=12),
        ),
        ],
        setups='newport%02d' % k,
    ))
_newports = Column(*tuple(newports))

ccrs = []
for i in range(10, 22 + 1):
    ccrs.append(Block('CCR%d' % i, [
        BlockRow(
                 Field(name='Setpoint', key='t_ccr%d_tube/setpoint' % i,
                       unitkey='t/unit', width=12),
                 Field(name='Target', key='t_ccr%d/target' % i,
                   unitkey='t/unit', width=12),
        ),
        BlockRow(
            Field(name='Manual Heater Power Stick',
                  key='t_ccr%d_stick/heaterpower' % i, format='%.3f'),
        ),
        BlockRow(
            Field(name='Manual Heater Power Tube',
                  key='t_ccr%d_tube/heaterpower' % i, format='%.3f'),
        ),
        BlockRow(
                 Field(name='A', dev='T_ccr%d_A' % i, width=12),
                 Field(name='B', dev='T_ccr%d_B' % i, width=12),
                ),
        BlockRow(
             Field(name='C', dev='T_ccr%d_C' % i, width=12),
             Field(name='D', dev='T_ccr%d_D' % i, width=12),
        ),
        ],
        setups='ccr%d' % i,
    ))
_ccrs = Column(*tuple(ccrs))

cryos = []
for cryo in ['cci3he1', 'cci3he2', 'cci3he3', 'cci3he10', 'ccidu1', 'ccidu2']:
    cryos.append(Block(cryo.title(), [
        BlockRow(
            Field(name='Setpoint', key='t_%s/setpoint' % cryo,
                   unitkey='t/unit'),
            Field(name='Target', key='t_%s/target' % cryo,
                   unitkey='t/unit'),
        ),
        BlockRow(
            Field(name='Manual Heater Power', key='t_%s/heaterpower' % cryo,
                   unitkey='t/unit'),
        ),
        BlockRow(
             Field(name='A', dev='T_%s_A' % cryo),
             Field(name='B', dev='T_%s_B' % cryo),
        ),
        BlockRow(
             Field(name='C', dev='T_%s_C' % cryo),
             Field(name='D', dev='T_%s_D' % cryo),
        ),
        ],
        setups=cryo,
    ))
_cryos = Column(*tuple(cryos))

_julabo = Column(
    Block('Julabo', [
        BlockRow(
            Field(name='T Intern', dev='T_julabo_intern',
                   format='%.2f', unit='C', width=14),
        Field(name='Target Intern', key='T_julabo_intern/target',
                   format='%.2f', unit='C', width=14),
            Field(name='Setpoint Intern', key='T_julabo_intern/setpoint',
                   format='%.2f', unit='C', width=14),
        ),
        BlockRow(
            Field(name='T Extern', dev='T_julabo_extern',
                   format='%.2f', unit='C', width=14),
            Field(name='Target Extern', key='T_julabo_extern/target',
                   format='%.2f', unit='C', width=14),
            Field(name='Setpoint Extern', key='T_julabo_extern/setpoint',
                   format='%.2f', unit='C', width=14),
        ),
        ],
        setups='julabo',
    ),
)

_julabo_plot = Column(
    Block('Julabo plot', [
        BlockRow(
                 Field(plot='julabo 30min', name='T Julabo intern',
                       dev='T_julabo_intern', width=60, height=40,
                       plotwindow=1800),
                 Field(plot='julabo 30min', name='T Julabo extern',
                       dev='T_julabo_extern'),
                 Field(plot='julabo 12h', name='T Julabo intern',
                       dev='T_julabo_intern', width=60, height=40,
                       plotwindow=12*3600),
                 Field(plot='julabo 12h', name='T Julabo extern',
                       dev='T_julabo_extern'),
        ),
        ],
        setups='julabo',
    ),
)

_pressure_box = Column(
    Block('Pressure', [
        BlockRow(
            Field(name='Pressure', dev='pressure_box'),
        ),
        ],
        setups='pressure_box',
    ),
)

_pressure_box_plot = Column(
    Block('Pressure plot', [
        BlockRow(
                 Field(plot='pressure box 30min', name='Pressure 30min',
                       dev='pressure_box', width=60, height=40,
                       plotwindow=1800),
                 Field(plot='pressure box 12h', name='Pressure 12h',
                       dev='pressure_box', width=60, height=40,
                       plotwindow=12*3600),
        ),
        ],
        setups='pressure_box',
    ),
)

_dilato = Column(
    Block('Dilatometer', [
        BlockRow(
             Field(name='Temperature', dev='Ts_dil',
                   format='%.2f', unit='C', width=14),
             Field(name='Set Temp', dev='dil_set_temp',
                   format='%.2f', unit='C', width=14),
             ),
        BlockRow(
             Field(name='Length change', dev='dil_dl',
                   format='%.2f', unit='um', width=14),
             Field(name='Force', dev='dil_force',
                   format='%.2f', unit='N', width=14),
             ),
        BlockRow(
             Field(name='Power', dev='dil_power',
                   format='%.2f', unit='%', width=14),
             Field(name='Time', dev='dil_time',
                   format='%.2f', unit='s', width=14),
        ),
        ],
    setups='dilato',
    ),
)

_dilato_plot = Column(
    Block('Dilatometer plot temperature', [
        BlockRow(
                 Field(plot='30 min dil', name='30 min', dev='Ts_dil',
                       width=60, height=40, plotwindow=1800),
                 Field(plot='30 min dil', name='setpoint', dev='dil_set_temp',
                       width=60, height=40, plotwindow=1800),
                 Field(plot='12 h dil', name='12 h', dev='Ts_dil',
                       width=60, height=40, plotwindow=12*3600),
                 Field(plot='12 h dil', name='setpoint', dev='dil_set_temp',
                       width=60, height=40, plotwindow=12*3600),
        ),
        ],
        setups='dilato',
    ),
)

_dilato_plot2 = Column(
    Block('Dilatometer plot length change', [
        BlockRow(
                 Field(plot='30 min dil2', name='30 min', dev='dil_dl',
                       width=60, height=40, plotwindow=1800),
                 Field(plot='12 h dil2', name='12 h', dev='dil_dl',
                       width=60, height=40, plotwindow=12*3600),
        ),
        ],
        setups='dilato',
    ),
)

_dilato_plot3 = Column(
    Block('Dilatometer plot force', [
        BlockRow(
                 Field(plot='30 min dil3', name='30 min', dev='dil_force',
                       width=60, height=40, plotwindow=1800),
                 Field(plot='12 h dil3', name='12 h', dev='dil_force',
                       width=60, height=40, plotwindow=12*3600),
        ),
        ],
        setups='dilato',
    ),
)

_tisane_fc = Column(
    Block('TISANE Frequency Counter', [
        BlockRow(
                Field(name='Frequency', dev='tisane_fc', format='%.2e', width=12),
                ),
        ],
        setups='tisane',
    ),
)

_tisane_counts = Column(
    Block('TISANE Counts', [
        BlockRow(
                Field(name='Counts', dev='TISANE_det_pulses', width=12),
                ),
        ],
        setups='tisane',
    ),
)

_chop_phase = Column(
    Block('Phase Positions', [
        BlockRow(
                 Field(name='1', dev='chopper_ch1_phase', unit='deg', format='%.2f'),
                 Field(name='2', dev='chopper_ch2_phase', unit='deg', format='%.2f'),
                 Field(name='water', dev='chopper_waterflow', width=8, format = '%.2'),
                ),
        ],
        setups='chopper_phase',
    ),
)

_live = Column(
    Block('Live image of Detector', [
        BlockRow(
            Field(name='Data (lin)', picture='sans1-online/live_lin.png',
                  width=64, height=64),
            Field(name='Data (log)', picture='sans1-online/live_log.png',
                  width=64, height=64),
        ),
        ],
    ),
)

_col_slit = Column(
    Block('Slit Positions', [
        BlockRow(
                 Field(name='Top', dev='slit_top', unit='mm', format='%.2f',
                       width=12),
                ),
        BlockRow(
                 Field(name='Left', dev='slit_left', unit='mm', format='%.2f',
                       width=12),
                 Field(name='Right', dev='slit_right', unit='mm', format='%.2f',
                       width=12),
                ),
        BlockRow(
                 Field(name='Bottom', dev='slit_bottom', unit='mm',
                       format='%.2f', width=12),
                ),
        BlockRow(
                 Field(name='Slit [width x height]', dev='slit', unit='mm'),
                ),
        ],
    ),
)

_helios01 = Column(
    Block('Helios', [
        BlockRow(
                Field(name='spin', dev='flipper_helios01', width=12),
                ),
        ],
        setups='helios01',
    ),
)

wuts = []
for wut in ['wut-0-10-01', 'wut-0-10-02', 'wut-4-20-01', 'wut-4-20-02']:
    _wd = wut.replace('-', '_')
    wuts.append(Block(wut, [
        BlockRow(
            Field(name='input 1', dev=_wd +'_1'),
            Field(name='input 2', dev=_wd+'_2'),
        ),
        ],
        setups=wut,
    ))
_wuts = Column(*tuple(wuts))

devices = dict(
    Monitor = device('nicos.services.monitor.html.Monitor',
        title = 'SANS-1 Status monitor',
        filename = '/sans1control/webroot/index.html',
        interval = 10,
        loglevel = 'info',
        cache = 'sans1ctrl.sans1.frm2',
        prefix = 'nicos/',
        font = 'Luxi Sans',
        valuefont = 'Consolas',
        fontsize = 17,
        layout = [
            Row(_expcolumn),
            Row(_sans1general, _table2, _table1, _sans1det),
            Row(_ubahncolumn, _meteocolumn, _pressurecolumn, _p_filter),
            Row(_selcolumn, _chop_phase, _col_slit, _atpolcolumn, _sanscolumn),
            Row(_ccmsans, _ccmsans_temperature,
                _ccm2a, _ccm2a_temperature,
                _spinflipper, _ccrs, _cryos, _sc1, _sc2,
                _sc_t, _ccmsanssc, _miramagnet, _amagnet,
                _htf03, _htf01, _irf01, _irf10, _newports, _julabo,
                _tisane_counts, _tisane_fc, _helios01, _wuts, _dilato,
                _pressure_box),
            Row(_ccmsans_plot, _ccm2a_plot, _ccr19_plot,
                _htf03_plot, _irf01_plot, _irf10_plot, _htf01_plot, _julabo_plot,
                _miramagnet_plot, _dilato_plot, _pressure_box_plot),
            Row(_dilato_plot2),
            Row(_dilato_plot3),
            Row(_live),
        ],
    ),
)
