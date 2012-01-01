#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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
#   Tobias Weber <tobias.weber@frm2.tum.de>
#
# *****************************************************************************

from nicos import session
from nicos.core import NicosError, LimitError, ConfigurationError
from test.utils import raises

def setup_module():
    session.loadSetup('switcher')
    session.setMode('master')

def teardown_module():
    session.unloadSetup()

def test_switcher():
    switcher = session.getDevice('switcher_1')
    motor = session.getDevice('motor_1')

    switcher.doStart('10')
    motor.doWait()
    assert motor.doRead() == 10

    switcher.doStart('30')
    motor.doWait()
    assert motor.doRead() == 30

    switcher.doStart('0')
    motor.doWait()
    assert motor.doRead() == 0

    assert raises(NicosError, switcher.doStart, '#####')

    assert raises(LimitError, switcher.doStart, '1000')
    assert raises(LimitError, switcher.doStart, '-10')

    assert raises(ConfigurationError, session.getDevice, 'broken_switcher')
