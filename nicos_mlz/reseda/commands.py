#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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
#   Christian Franz  <christian.franz@frm2.tum.de>
#
# *****************************************************************************

"""Module for RESEDA specific commands."""

from nicos import session
from nicos.commands import usercommand
from nicos.commands.device import move
from nicos.commands.scan import manualscan
from nicos.commands.measure import count
from nicos.commands.device import maw

__all__ = ['set_cascade', 'pol', 'miezescan']

@usercommand
def set_cascade():
    """Set Cascade Frequency Generator Freqs and Trigger"""
    echotime = session.getDevice('echotime')
    psd_chop_freq = session.getDevice('psd_chop_freq')
    psd_timebin_freq = session.getDevice('psd_timebin_freq')
    fg_test = session.getDevice('fg_test')
    tau = echotime.target
    f1 = echotime.currenttable[tau]['cbox_0a_fg_freq']
    f2 = echotime.currenttable[tau]['cbox_0b_fg_freq']
    move(psd_chop_freq, 2*(f2-f1))
    move(psd_timebin_freq, 32*(f2-f1))
    move(fg_test, 'arm')
    move(fg_test, 'trigger')

@usercommand
def miezescan(echolist, counttime):
    echotime = session.getDevice('echotime')
    with manualscan(echotime, counttime):
        for etime in echolist:
            maw(echotime, etime)
            set_cascade()
            count(counttime)

@usercommand
def pol(up, down):
    '''Calculate contrast or polarisation'''
    return (up-down)/(up+down)