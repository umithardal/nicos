#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Module authors:
#   Andreas Wilhelm <andreas.wilhelm@frm2.tum.de>
#
# *****************************************************************************

description = 'setup for the status monitor for SANS1'

group = 'special'


_sc1 = Block('Sample Changer 1', [
    BlockRow(Field(name='sc1_y', dev='sc1_y'),),
    BlockRow(Field(name='SampleChanger', dev='sc1'),),
    ],
    setups='sc1',
)

_sc2 = Block('Sample Changer 2', [
    BlockRow(Field(name='sc2_y', dev='sc2_y'),),
    BlockRow(Field(name='SampleChanger 2', dev='sc2'),),
    ],
    setups='sc2',
)

_st2 = Block('Sample Table 2', [
    BlockRow(Field(name='st2_z', dev='st2_z'),),
    BlockRow(Field(name='st2_y', dev='st2_y'),),
    BlockRow(Field(name='st2_x', dev='st2_x'),),
    ],
    setups='sample_table_2',
)

_st1 = Block('Sample Table 1', [
    BlockRow(Field(name='st1_phi', dev='st1_phi'),),
    BlockRow(Field(name='st1_chi', dev='st1_chi'),),
    BlockRow(Field(name='st1_omg', dev='st1_omg'),),
    BlockRow(Field(name='st1_y', dev='st1_y'),),
    BlockRow(Field(name='st1_z', dev='st1_z'),),
    BlockRow(Field(name='st1_x', dev='st1_x'),),
    ],
    setups='sample_table_1',
)

_htf03 = Block('HTF03', [
    BlockRow(
             Field(name='Temperature', dev='T_htf03', format='%.2f', unit='C', width=12),
             Field(name='Target', key='t_htf03/target', format='%.2f', unit='C', width=12),
             ),
    BlockRow(
             Field(name='Setpoint', key='t_htf03/setpoint', format='%.1f', unit='C', width=12),
             Field(name='Heater Power', key='t_htf03/heaterpower', format='%.1f', unit='%', width=12),
             #Field(name='Vacuum', key='htf03_p'),
            ),
    BlockRow(
             Field(name='P', key='t_htf03/p', format='%i'),
             Field(name='I', key='t_htf03/i', format='%i'),
             Field(name='D', key='t_htf03/d', format='%i'),
            ),
    ],
    setups='htf03',
)

_htf03_plot = Block('HTF03 plot', [
    BlockRow(
        Field(widget='nicos.guisupport.plots.TrendPlot',
              width=70, height=35, plotwindow=1800,
              devices=['T_htf03', 'T_htf03/setpoint', 'T_htf03/target'],
              names=['30min', 'Setpoint', 'Target'],
              ),
    ),
    BlockRow(
        Field(widget='nicos.guisupport.plots.TrendPlot',
              width=70, height=35, plotwindow=12*3600,
              devices=['T_htf03', 'T_htf03/setpoint', 'T_htf03/target'],
              names=['12h', 'Setpoint', 'Target'],
              ),
    ),
    ],
    setups='htf03',
)

_htf01 = Block('HTF01', [
    BlockRow(
             Field(name='Temperature', dev='T_htf01', format='%.2f', unit='C', width=12),
             Field(name='Target', key='t_htf01/target', format='%.2f', unit='C', width=12),
             ),
    BlockRow(
             Field(name='Setpoint', key='t_htf01/setpoint', format='%.1f', unit='C', width=12),
             Field(name='Heater Power', key='t_htf01/heaterpower', format='%.1f', unit='%', width=12),
             #Field(name='Vacuum', key='htf01_p'),
            ),
    BlockRow(
             Field(name='P', key='t_htf01/p', format='%i'),
             Field(name='I', key='t_htf01/i', format='%i'),
             Field(name='D', key='t_htf01/d', format='%i'),
            ),
    ],
    setups='htf01',
)

_htf01_plot = Block('HTF01 plot', [
    BlockRow(
        Field(widget='nicos.guisupport.plots.TrendPlot',
              width=70, height=35, plotwindow=1800,
              devices=['T_htf01', 'T_htf01/setpoint', 'T_htf01/target'],
              names=['30min', 'Setpoint', 'Target'],
              ),
    ),
    BlockRow(
        Field(widget='nicos.guisupport.plots.TrendPlot',
              width=70, height=35, plotwindow=12*3600,
              devices=['T_htf01', 'T_htf01/setpoint', 'T_htf01/target'],
              names=['12h', 'Setpoint', 'Target'],
              ),
    ),
    ],
    setups='htf01',
)

_ccmsans = Block('SANS-1 5T Magnet', [
    BlockRow(Field(name='Field', dev='B_ccmsans', width=12),
             ),
    BlockRow(
             Field(name='Target', key='b_ccmsans/target', width=12),
             Field(name='Asymmetry', key='b_ccmsans/asymmetry', width=12),
            ),
    BlockRow(
             Field(name='Power Supply 1', dev='A_ccmsans_left', width=12),
             Field(name='Power Supply 2', dev='A_ccmsans_right', width=12),
            ),
    ],
    setups='ccmsans',
)

_ccmsans_temperature = Block('SANS-1 5T Magnet Temperatures', [
    BlockRow(
             Field(name='CH Stage 1', dev='ccmsans_T1', width=12),
             Field(name='CH Stage 2', dev='ccmsans_T2', width=12),
            ),
    BlockRow(
             Field(name='Shield Top', dev='ccmsans_T3', width=12),
             Field(name='Shield Bottom', dev='ccmsans_T4', width=12),
            ),
    BlockRow(
             Field(name='Magnet TL', dev='ccmsans_T5', width=12),
             Field(name='Magnet TR', dev='ccmsans_T6', width=12),
            ),
    BlockRow(
             Field(name='Magnet BL', dev='ccmsans_T8', width=12),
             Field(name='Magnet BR', dev='ccmsans_T7', width=12),
            ),
    ],
    setups='ccmsans',
)

_ccmsans_plot = Block('SANS-1 5T Magnet plot', [
    BlockRow(
        Field(widget='nicos.guisupport.plots.TrendPlot',
              width=60, height=25, plotwindow=1800,
              devices=['B_ccmsans', 'b_ccmsans/target'],
              names=['30min', 'Target'],
              ),
        Field(widget='nicos.guisupport.plots.TrendPlot',
              width=60, height=25, plotwindow=12*3600,
              devices=['B_ccmsans', 'b_ccmsans/target'],
              names=['12h', 'Target'],
              ),
        ),
    ],
    setups='ccmsans',
)

_miramagnet = Block('MIRA 0.5T Magnet', [
    BlockRow(Field(name='Field', dev='b_mira', width=12),
             Field(name='Target', key='b_mira/target', width=12),
             ),
    BlockRow(
             Field(name='Current', dev='i', width=12),
            ),
    ],
    setups='miramagnet',
)

_miramagnet_plot = Block('MIRA 0.5T Magnet plot', [
    BlockRow(
        Field(widget='nicos.guisupport.plots.TrendPlot',
              width=60, height=15, plotwindow=1800,
              devices=['B_mira', 'b_mira/target'],
              names=['30min', 'Target'],
              ),
        Field(widget='nicos.guisupport.plots.TrendPlot',
              width=60, height=15, plotwindow=24*3600,
              devices=['B_mira', 'b_mira/target'],
              names=['24h', 'Target'],
              ),
        ),
    ],
    setups='miramagnet',
)

_amagnet = Block('Antares Magnet', [
    BlockRow(Field(name='Field', dev='B_amagnet', width=12),
             Field(name='Target', key='B_amagnet/target', width=12),
             ),
    BlockRow(
             Field(name='Current', dev='amagnet_current', width=12),
             Field(name='ON/OFF', dev='amagnet_onoff', width=12),
             ),
    BlockRow(
             Field(name='Polarity', dev='amagnet_polarity', width=12),
             Field(name='Connection', dev='amagnet_connection', width=12),
            ),
    BlockRow(
             Field(name='Lambda out', dev='l_out', width=12),
            ),
    ],
    setups='amagnet',
)

_amagnet_plot = Block('Antares Magnet plot', [
    BlockRow(
        Field(widget='nicos.guisupport.plots.TrendPlot',
              width=60, height=15, plotwindow=1800,
              devices=['B_amagnet', 'b_amagnet/target'],
              names=['30min', 'Target'],
              ),
        Field(widget='nicos.guisupport.plots.TrendPlot',
              width=60, height=15, plotwindow=12*3600,
              devices=['B_amagnet', 'b_amagnet/target'],
              names=['12h', 'Target'],
              ),
        ),
    ],
    setups='amagnet',
)

_spinflipper = Block('Spin Flipper', [
    BlockRow(
             Field(name='P_spinflipper', dev='P_spinflipper'),
             #Field(name='F_spinflipper', dev='F_spinflipper'),
            ),
    BlockRow(
             Field(name='Forward', key='P_spinflipper/forward', unitkey='W'),
             Field(name='Reverse', key='P_spinflipper/reverse', unitkey='W'),
            ),
    BlockRow(Field(name='Temperature of Spinflipper', dev='T_spinflipper'),),
    BlockRow(
             Field(name='A_spinflipper_hp', dev='A_spinflipper_hp'),
             Field(name='F_spinflipper_hp', dev='F_spinflipper_hp'),
            ),
    ],
    setups='spinflipper',
)

newports = []
for k in range(1, 6 + 1):
    newports.append(Block('NewPort0%d' % k, [
        BlockRow(
            Field(name='Position', dev='sth_newport0%d' % k,
                   unitkey='t/unit'),
        ),
        ],
        setups='newport0%d' % k,
    ))

ccrs = []
for i in range(10, 22 + 1):
    ccrs.append(Block('CCR%d' % i, [
        BlockRow(
            Field(name='Setpoint', key='t_ccr%d_tube/setpoint' % i,
                   unitkey='t/unit'),
            Field(name='Target', key='t_ccr%d_tube/target' % i,
                   unitkey='t/unit'),
        ),
        BlockRow(
            Field(name='Manual Heater Power', key='t_ccr%d_tube/heaterpower' % i,
                   format='%.3f', unitkey='t/unit'),
        ),
        BlockRow(
             Field(name='A', dev='T_ccr%d_A' % i),
             Field(name='B', dev='T_ccr%d_B' % i),
        ),
        BlockRow(
             Field(name='C', dev='T_ccr%d_C' % i),
             Field(name='D', dev='T_ccr%d_D' % i),
        ),
        ],
        setups='ccr%d' % i,
    ))

T_Ts_plot = []
for k in range(10, 22 + 1):
    T_Ts_plot.append(Block('30min T and Ts plot', [
        BlockRow(
            Field(widget='nicos.guisupport.plots.TrendPlot',
                  width=50, height=5, plotwindow=30*60,
                  devices=['T', 'Ts', 'T/setpoint', 'T/target'],
                  names=['T', 'Ts', 'Setpoint', 'Target'],
                  ),
            ),
        ],
        setups='ccr%d' %k,
    ))

cryos = []
for cryo in 'cci3he1 cci3he2 cci3he3 cci3he4he1 cci3he4he2'.split():
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
        ],
        setups=cryo,
    ))

_birmag = Block('17 T Magnet', [
    BlockRow(
             Field(name='helium level', dev='helevel_birmag', width=13),
             Field(name='field birmag', dev='field_birmag', width=13),),
    BlockRow(
             Field(name='Setpoint 1 birmag', dev='sp1_birmag', width=13),
             Field(name='Setpoint 2 birmag', dev='sp2_birmag', width=13),),
    BlockRow(
             Field(name='Temp a birmag', dev='ta_birmag', width=13),
             Field(name='Temp b birmag', dev='tb_birmag', width=13),),
    ],
    setups='birmag',
)

_sans1reactor = Column(
    Block('Reactor', [
        BlockRow(
                 Field(name='Reactor', dev='ReactorPower'),
                 Field(name='6 Fold Shutter', dev='Sixfold'),
                 Field(name='NL4a', dev='NL4a'),
                ),
        ],
    ),
)

_sans1general = Column(
    Block('General', [
        BlockRow(
                 Field(name='T in', dev='t_in_memograph', unit='C', width=6.5),
                 Field(name='T out', dev='t_out_memograph', unit='C', width=6.5),
                 Field(name='Cooling', dev='cooling_memograph', unit='kW', width=6.5),
                 Field(name='Flow in', dev='flow_in_memograph', unit='l/min', width=6.5),
                 Field(name='Flow out', dev='flow_out_memograph', unit='l/min', width=6.5),
                 Field(name='Leakage', dev='leak_memograph', unit='l/min', width=6.5),
                 Field(name='P in', dev='p_in_memograph', unit='bar', width=6.5),
                 Field(name='P out', dev='p_out_memograph', unit='bar', width=6.5),
                ),
        ],
    ),
)

_sans1crane = Column(
    Block('Crane', [
        BlockRow(
                 Field(name='Crane Pos', dev='Crane'),
                ),
        ],
    ),
)


_sans1julabo = Block('Julabo', [
    BlockRow(
             Field(name='Target', key='T_julabo/target'),
             Field(name='Setpoint', key='T_julabo/setpoint'),
             ),
    BlockRow(
             Field(name='Intern', dev='T_intern'),
             Field(name='Extern', dev='T_julabo'),
             ),
    ],
    setups='julabo',
)

_julabo_plot = Block('Julabo plot', [
    BlockRow(
        Field(widget='nicos.guisupport.plots.TrendPlot',
              width=70, height=35, plotwindow=1800,
              devices=['T_julabo', 'T_julabo/setpoint'],
              names=['T 30min', 'Setpoint'],
              ),
    ),
    BlockRow(
        Field(widget='nicos.guisupport.plots.TrendPlot',
              width=70, height=35, plotwindow=12*3600,
              devices=['T_julabo', 'T_julabo/setpoint'],
              names=['T 12h', 'Setpoint'],
              ),
    ),
    ],
    setups='julabo',
)

devices = dict(
    Monitor = device('services.monitor.qt.Monitor',
                     description='Status monitor',
                     title='SANS-1 status monitor',
                     cache='sans1ctrl.sans1.frm2',
                     font='Luxi Sans',
                     fontsize=11,#12
                     loglevel='info',
                     padding=0,#3
                     prefix='nicos/',
                     valuefont='Consolas',
                     layout=[
                                Row(_sans1reactor, _sans1general, _sans1crane),
                                Row(
                                    Column(_sc1, _sc2, _st2, _st1, *newports),
                                    Column(_htf01, _htf03, _ccmsans, _ccmsans_temperature, _miramagnet, _amagnet, _sans1julabo),
                                    Column(_htf01_plot, _htf03_plot, _spinflipper, _julabo_plot) + Column(*T_Ts_plot),
                                    Column(*ccrs) + Column(*cryos) + Column(_birmag),
                                   ),
                                Row(
                                    Column(_ccmsans_plot),
                                   ),
                                Row(
                                    Column(_miramagnet_plot, _amagnet_plot),
                                   ),
                            ],
                    ),
)
