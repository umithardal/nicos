#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Author:
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
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
# *****************************************************************************

"""NICOS slit device."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

from time import sleep

from nicos import status
from nicos.utils import oneof
from nicos.device import Moveable, Param, Override, AutoDevice
from nicos.errors import UsageError, LimitError
from nicos.abstract import Axis


class Slit(Moveable):
    """A rectangular slit consisting of four blades."""

    attached_devices = {
        'right': Moveable,
        'left': Moveable,
        'bottom': Moveable,
        'top': Moveable,
    }

    parameters = {
        'opmode': Param('Mode of operation for the slit',
                        type=oneof(str, '4blades', 'centered', 'offcentered'),
                        settable=True),
    }

    parameter_overrides = {
        'fmtstr': Override(default='%.2f %.2f %.2f %.2f'),
        'unit': Override(mandatory=False),
    }

    def doInit(self):
        self._axes = [self._adevs['right'], self._adevs['left'],
                      self._adevs['bottom'], self._adevs['top']]
        self._axnames = ['right', 'left', 'bottom', 'top']

        for name, cls in [
            ('right', RightSlitAxis), ('left', LeftSlitAxis),
            ('bottom', BottomSlitAxis), ('top', TopSlitAxis),
            ('centerx', CenterXSlitAxis), ('centery', CenterYSlitAxis),
            ('width', WidthSlitAxis), ('height', HeightSlitAxis)]:
            self.__dict__[name] = cls(self.name+'.'+name, slit=self,
                                      unit=self.unit, lowlevel=True)

    def _getPositions(self, target):
        if self.opmode == '4blades':
            if len(target) != 4:
                raise UsageError(self, 'arguments required for 4-blades mode: '
                                 '[xmin, xmax, ymin, ymax]')
            positions = list(target)
        elif self.opmode == 'centered':
            if len(target) != 2:
                raise UsageError(self, 'arguments required for centered mode: '
                                 '[width, height]')
            positions = [-target[0]/2., target[0]/2.,
                         -target[1]/2., target[1]/2.]
        else:
            if len(target) != 4:
                raise UsageError(self, 'arguments required for offcentered mode: '
                                 '[xcenter, ycenter, width, height]')
            positions = [target[0] - target[2]/2., target[0] + target[2]/2.,
                         target[1] - target[3]/2., target[1] + target[3]/2.]
        return positions

    def doIsAllowed(self, target):
        return self._doIsAllowedPositions(self._getPositions(target))

    def _doIsAllowedPositions(self, positions):
        for ax, axname, pos in zip(self._axes, self._axnames, positions):
            ok, why = ax.isAllowed(pos)
            if not ok:
                return ok, '%s blade: %s' % (axname, why)
        if positions[1] < positions[0]:
            return False, 'horizontal slit opening is negative'
        if positions[3] < positions[2]:
            return False, 'vertical slit opening is negative'
        return True, ''

    def doStart(self, target):
        self._doStartPositions(self._getPositions(target))

    def _doStartPositions(self, positions):
        tr, tl, tb, tt = positions
        # determine which axes to move first, so that the blades can
        # not touch when one moves first
        cr, cl, cb, ct = map(lambda d: d.doRead(), self._axes)
        ar, al, ab, at = self._axes
        if tr < cr and tl < cl:
            # both move to smaller values, need to start right blade first
            ar.move(tr)
            sleep(0.25)
            al.move(tl)
        elif tr > cr and tl > cl:
            # both move to larger values, need to start left blade first
            al.move(tl)
            sleep(0.25)
            ar.move(tr)
        else:
            # don't care
            al.move(tl)
            ar.move(tr)
        if tb < cb and tt < ct:
            ab.move(tb)
            sleep(0.25)
            at.move(tt)
        elif tb > cb and tt > ct:
            at.move(tt)
            sleep(0.25)
            ab.move(tb)
        else:
            at.move(tt)
            ab.move(tb)

    def doReset(self):
        for ax in self._axes:
            ax.reset()
        for ax in self._axes:
            ax.wait()

    def doWait(self):
        for ax in self._axes:
            ax.wait()

    def doStop(self):
        for ax in self._axes:
            ax.stop()

    def doRead(self):
        positions = map(lambda d: d.read(), self._axes)
        r, l, b, t = positions
        if self.opmode == 'centered':
            if 'precision' in  self._adevs['left'].parameters:
                if abs((l+r)/2.) > self._adevs['left'].precision or \
                       abs((t+b)/2.) > self._adevs['top'].precision:
                    self.printwarning('slit seems to be offcentered, but is '
                                      'set to "centered" mode')
            return (l-r, t-b)
        elif self.opmode == 'offcentered':
            return ((l+r)/2, (t+b)/2, l-r, t-b)
        else:
            return tuple(positions)

    def doStatus(self):
        svalues = map(lambda d: d.status(), self._axes)
        return max(s[0] for s in svalues), 'axis status: ' + \
               ', '.join('%s=%s' % (n, s[1])
                         for (s, n) in zip(svalues, self._axnames))

    def doReadUnit(self):
        return self._adevs['left'].unit
    
    def doWriteOpmode(self, value):
        if value == '4blades':
            self.fmtstr = '%.2f %.2f %.2f %.2f'
        elif value == 'offcentered':
            self.fmtstr = '(%.2f, %.2f) %.2f x %.2f'
        else:
            self.fmtstr = '%.2f x %.2f'


class SlitAxis(Moveable, AutoDevice):
    """
    "Partial" devices for slit axes, useful for e.g. scanning
    over the device slit.centerx.
    """

    attached_devices = {
        'slit': Slit,
    }

    def doRead(self):
        positions = map(lambda d: d.read(), self._adevs['slit']._axes)
        return self._convertRead(positions)

    def doStart(self, target):
        currentpos = map(lambda d: d.doRead(), self._adevs['slit']._axes)
        positions = self._convertStart(target, currentpos)
        self._adevs['slit']._moveto(positions)

    def doIsAllowed(self, target):
        currentpos = map(lambda d: d.doRead(), self._adevs['slit']._axes)
        positions = self._convertStart(target, currentpos)
        return self._adevs['slit'].doIsAllowed(positions)


class RightSlitAxis(SlitAxis):
    def _convertRead(self, positions):
        return positions[0]
    def _convertStart(self, target, current):
        return (target, current[1], current[2], current[3])

class LeftSlitAxis(SlitAxis):
    def _convertRead(self, positions):
        return positions[1]
    def _convertStart(self, target, current):
        return (current[0], target, current[2], current[3])

class BottomSlitAxis(SlitAxis):
    def _convertRead(self, positions):
        return positions[2]
    def _convertStart(self, target, current):
        return (current[0], current[1], target, current[3])

class TopSlitAxis(SlitAxis):
    def _convertRead(self, positions):
        return positions[3]
    def _convertStart(self, target, current):
        return (current[0], current[1], current[2], target)

class CenterXSlitAxis(SlitAxis):
    def _convertRead(self, positions):
        return (positions[0] + positions[1]) / 2.
    def _convertStart(self, target, current):
        width = current[1] - current[0]
        return (target-width/2., target+width/2., current[2], current[3])

class CenterYSlitAxis(SlitAxis):
    def _convertRead(self, positions):
        return (positions[2] + positions[3]) / 2.
    def _convertStart(self, target, current):
        height = current[3] - current[2]
        return (current[0], current[1], target-height/2., target+height/2.)

class WidthSlitAxis(SlitAxis):
    def _convertRead(self, positions):
        return positions[1] - positions[0]
    def _convertStart(self, target, current):
        centerx = (current[0] + current[1]) / 2.
        return (centerx-target/2., centerx+target/2., current[2], current[3])

class HeightSlitAxis(SlitAxis):
    def _convertRead(self, positions):
        return positions[3] - positions[2]
    def _convertStart(self, target, current):
        centery = (current[2] + current[3]) / 2.
        return (current[0], current[1], centery-target/2., centery+target/2)

