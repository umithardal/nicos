#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2013 by the NICOS contributors (see AUTHORS)
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

"""Session class used with the NICOS poller."""

from nicos.core import ConfigurationError, Device
from nicos.core.sessions.simple import NoninteractiveSession
from nicos.devices.generic.alias import DeviceAlias
from nicos.devices.generic.cache import CacheReader


class PollerSession(NoninteractiveSession):

    def getDevice(self, dev, cls=None, source=None):
        """Override device creation for the poller.

        With the "alias device" mechanism, aliases can point to any device in
        the currently loaded setups.  This leads to a problem with the poller,
        since the poller loads each setup in a different process, and in the
        process that polls the DeviceAlias, the pointee can be missing.

        Therefore, we replace devices that are not found by a CacheReader, in
        the hope that the actual pointee is contained in another setup that is
        polled by another process, and we can get current values for the device
        via the CacheReader.
        """
        try:
            # Note the change of any required baseclass to Device, so that the
            # CacheReader can stand in for any attached device.
            return NoninteractiveSession.getDevice(self, dev, Device, source)
        except ConfigurationError:  # device not found
            if isinstance(source, DeviceAlias):
                return CacheReader(dev, unit='')
            raise
