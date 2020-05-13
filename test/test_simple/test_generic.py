#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""NICOS generic devices test suite."""

from __future__ import absolute_import, division, print_function

import mock

from nicos.commands.measure import count
from nicos.core import ConfigurationError, InvalidValueError, LimitError, \
    NicosError, PositionError, status

from test.utils import approx, raises

session_setup = 'generic'


class TestManualVirtual(object):

    def test_virtual_motor(self, session):
        v = session.getDevice('v1')
        v.maw(1)
        assert v.read() == 1
        v.move(0)
        v.stop()
        assert 0 <= v.read() <= 1

    def test_virtual_switch(self, session):
        v = session.getDevice('v2')
        # default is first entry in states list
        assert v.read(0) == 'up'
        v.maw('down')
        assert v.read() == 'down'
        assert raises(NicosError, v.move, 'sideways')
        assert v.read() == 'down'
        assert v.isAllowed('sideways')[0] is False
        assert v.isAllowed('up')[0] is True

    def test_manual_move(self, session):
        m4 = session.getDevice('m4')
        m4.move(10)
        assert m4.read() == 10
        assert m4.target == 10
        assert m4.status()[0] == status.OK

    def test_manual_switch(self, session):
        m = session.getDevice('m1')
        assert m.read() == 'up'
        m.maw('down')
        assert m.read() == 'down'
        assert raises(NicosError, m.move, 'sideways')
        assert m.read() == 'down'
        assert m.status()[0] == status.OK

    def test_manual_switch_2(self, session):
        assert raises(ConfigurationError, session.getDevice, 'm2')

    def test_manual_switch_illegal_position(self, session):
        m3 = session.getDevice('m3')
        assert raises(InvalidValueError, m3.maw, 'inbetween')
        # Enforce an illegal Position
        m3._setROParam('target', 'inbetween')
        assert raises(PositionError, m3.read, 0)


class TestSwitcher(object):

    def test_switcher(self, session):
        sw = session.getDevice('sw')
        v3 = session.getDevice('v3')
        v3.maw(1)
        assert sw.read(0) == 'left'
        v3.maw(3)
        assert sw.read(0) == 'right'
        sw.maw('left')
        assert v3.read() == 1
        sw.maw('right')
        assert v3.read() == 3

        assert sw.status()[0] == v3.status()[0]

        assert raises(NicosError, sw.start, '#####')
        assert raises(LimitError, sw.start, 'outside')
        assert raises(NicosError, sw.doStart, '#####')
        sw.stop()

        v3.maw(1.01)
        assert sw.read(0) == 'left'
        v3.maw(1.2)
        assert raises(PositionError, sw.read, 0)
        assert sw.status(0)[0] == status.NOTREACHED

        rsw = session.getDevice('rsw')
        rsw2 = session.getDevice('rsw2')
        assert raises(PositionError, rsw.read, 0)

        v3.maw(1)
        assert rsw.read(0) == 'left'
        assert rsw2.read(0) == 'left'
        v3.maw(3)
        assert rsw.read(0) == 'right'
        assert rsw2.read(0) == 'right'

        assert rsw.status()[0] == v3.status()[0]

        with mock.patch('nicos.devices.generic.virtual.VirtualMotor.doReset',
                        create=True) as m:
            sw.reset()
            assert m.called

    def test_switcher_fallback(self, session):
        swfb = session.getDevice('swfb')
        rswfb = session.getDevice('rswfb')
        v3 = session.getDevice('v3')
        v3.maw(2)
        assert swfb.read(0) == 'unknown'
        assert swfb.status()[0] == status.UNKNOWN
        assert rswfb.read(0) == 'unknown'
        assert rswfb.status()[0] == status.NOTREACHED

    def test_switcher_noblockingmove(self, session):
        sw2 = session.getDevice('sw2')
        v3 = session.getDevice('v3')
        sw2.maw('left')
        assert sw2.read(0) == 'left'
        sw2.move('right')
        assert v3.read(0) == 3.0

        # case 1: motor in position, but still busy
        v3.curstatus = (status.BUSY, 'busy')
        assert sw2.status(0)[0] != status.OK

        # case 2: motor idle, but wrong position
        v3.curstatus = (status.OK, 'on target')
        v3.curvalue = 2.0
        assert sw2.status(0)[0] != status.OK

        # position and status ok
        v3.curvalue = 3.0
        assert sw2.status(0)[0] == status.OK
        assert sw2.read(0) == 'right'


def test_paramdev(session):
    v1 = session.getDevice('v1')
    pd = session.getDevice('paramdev')

    assert pd() == v1.speed
    pd.maw(1)
    assert v1.speed == 1

    print(pd.unit)
    print(v1.unit)
    assert pd.unit == v1.unit + '/s'
    assert pd.status()[0] == status.OK


def test_freespace(session):
    freespace = session.getDevice('freespace')
    assert freespace._factor == 1024. ** 3
    fs = freespace.read(0)
    freespace.minfree = 0
    assert freespace.status(0)[0] == status.OK
    # (GiB) this should be large enough to not happen in a test system
    freespace.minfree = 10000000
    assert freespace.status(0)[0] != status.OK
    freespace2 = session.getDevice('freespace2')
    assert raises(NicosError, freespace2.read, 0)
    freespace.unit = 'KiB'
    fs2 = freespace.read(0)
    assert fs != fs2
    assert raises(ConfigurationError, freespace.doUpdateUnit, 'GB')


def test_scanning_detector(session):
    scandet = session.getDevice('scandet')

    count(scandet, t=0)
    dataset = session.experiment.data.getLastScans()[-1]

    # check correct length of executed scan
    assert len(scandet.positions) == dataset.npoints
    assert len(scandet.positions) == len(dataset.subsets)

    # check scandev positions for scan points
    assert scandet.positions == [entry[0] for entry in dataset.devvaluelists]


def test_magnet(session):
    current = session.getDevice('current')
    magnet = session.getDevice('magnet')

    # the default formula is B(I) = c0*I + c1*erf(c2*I) + c3*atan(c4*I)
    magnet.calibration = 1, 0, 0, 0, 0
    assert magnet.abslimits == (-100, 100)
    magnet.maw(1)
    assert magnet.read() == 1
    assert current.read() == 1

    magnet.calibration = 1, 1, 1, 1, 1
    assert magnet.abslimits[0] == approx(-102.56, abs=1e-2)
    magnet.maw(1)
    assert magnet.read() == 1
    assert current.read() == approx(0.33, abs=1e-2)
