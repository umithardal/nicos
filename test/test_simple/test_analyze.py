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

"""NICOS tests for nicos.commands.analyze."""

from __future__ import absolute_import, division, print_function

import pytest

from nicos.commands.analyze import center_of_mass, fwhm, gauss, poly, \
    root_mean_square
from nicos.core import FINAL

try:
    from scipy.optimize.minpack import leastsq
except ImportError:
    leastsq = None



session_setup = 'scanning'


@pytest.fixture(scope='class', autouse=True)
def generate_dataset(session):
    """Generate a dataset as if a scan has been run."""
    import numpy
    data = numpy.array((1, 2, 1, 2, 2, 2, 5, 20, 30, 20, 10, 2, 3, 1, 2, 1, 1, 1))
    xpoints = numpy.arange(-9, 9)
    assert len(data) == len(xpoints)
    tdev = session.getDevice('tdev')
    det = session.getDevice('det')
    dataman = session.experiment.data
    dataman.beginScan(devices=[tdev], detectors=[det])
    for (x, y) in zip(xpoints, data):
        dataman.beginPoint()
        dataman.putValues({'tdev': (None, x)})
        dataman.putResults(FINAL, {'det': ([0, 0, y, y*2], [])})
        dataman.finishPoint()
    dataman.finishScan()


class TestAnalyzers(object):

    def test_fwhm(self, session):
        result = fwhm(1, 3)
        assert result == (2.75, -1, 30, 1)

    def test_center_of_mass(self, session):
        result1 = center_of_mass()
        assert -0.840 < result1 < -0.839
        result2 = center_of_mass(4)  # center of mass from values*2 should be same
        assert result1 == result2

    def test_root_mean_square(self, session):
        result = root_mean_square()
        assert 10.176 < result < 10.177

    @pytest.mark.skipif(not leastsq, reason='scipy leastsq not available')
    def test_poly(self, session):
        result1 = poly(1, 1, 3)
        assert len(result1) == 2 and len(result1[0]) == 2
        assert 1.847 < result1[0][0] < 1.848
        result2 = poly(2)
        assert -0.047 < result2[0][2] < -0.046
        result3 = poly(2, 4)
        assert -0.094 < result3[0][2] < -0.093
        result4 = poly(2, 1, 4)
        assert result4 == result3

    @pytest.mark.skipif(not leastsq, reason='scipy leastsq not available')
    def test_gauss(self, session):
        result = gauss()
        assert len(result) == 2 and len(result[0]) == 4
        assert -0.874 < result[0][0] < -0.873
