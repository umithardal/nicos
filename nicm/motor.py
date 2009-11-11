#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   NICOS motor definition
#
# Author:
#   Jens Krüger <jens.krueger@frm2.tum.de>
#   $Author$
#
#   The basic NICOS methods for the NICOS daemon (http://nicos.sf.net)
#
#   Copyright (C) 2009 Jens Krüger <jens.krueger@frm2.tum.de>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# *****************************************************************************

"""
NICOS motor definition.
"""

__author__ = "Jens Krüger <jens.krueger@frm2.tum.de>"
__date__   = "2009/10/27"
__version__= "0.0.1"

from nicm import status
from nicm.device import Moveable


class Motor(Moveable):
    """Base class for all motors."""

    def setPosition(self, pos):
        self.doSetPosition(pos)

    def doInit(self):
        """Initializes the class."""
        pass

    def doStart(self, target):
        """Starts the movement of the motor to target."""
        pass

    def doRead(self) :
        """Returns the current position from motor controller."""
        return 0

    def doSetPosition(self, target) :
        """Sets the current position of the motor controller to the target."""
        pass

    def doStatus(self) :
        """Returns the status of the motor controller."""
        return status.OK

    def doReset(self) :
        """Resets the motor controller."""
        pass

    def doStop(self) :
        """Stops the movement of the motor."""
        pass
