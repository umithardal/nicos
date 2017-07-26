#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""Class for delta (difference) axis."""

from nicos.core import Readable, Attach, Override


class DeltaAxis(Readable):

    attached_devices = {
        'axis1':  Attach('first axis', Readable),
        'axis2':  Attach('second axis', Readable),
    }

    parameter_overrides = {
        'unit':       Override(mandatory=False),
    }

    def doReadUnit(self):
        return self._attached_axis1.unit

    def doRead(self, maxage=0):
        return self._attached_axis2.read(maxage) - self._attached_axis1.read(maxage)