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
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#
# *****************************************************************************

from __future__ import absolute_import, division, print_function

from os.path import relpath

from nicos import session
from nicos.commands import helparglist, usercommand
from nicos.commands.device import maw
from nicos.commands.imaging import grtomo, tomo
from nicos.commands.measure import count
from nicos.devices.datasinks.image import ImageSink

__all__ = ['tomo', 'openbeamimage', 'darkimage', 'grtomo']


def changeImgSinkSubdir(newsubdir):
    for entry in session.datasinks:
        if isinstance(entry, ImageSink):
            entry._setROParam('subdir', newsubdir)


#pylint: disable=keyword-arg-before-vararg
@usercommand
@helparglist('shutter, [detectors], [presets]')
def openbeamimage(shutter=None, *detlist, **preset):
    """Acquire an open beam image."""
    exp = session.experiment
    det = exp.detectors[0]
    limadev = det._attached_images[0] if det._attached_images else None

    # TODO: better ideas for shutter control
    if shutter:
        # Shutter was given, so open it
        maw(shutter, 'open')
    elif limadev is not None and limadev._shutter is not None:
        # No shutter; try the lima way
        oldmode = limadev.shuttermode
        limadev.shuttermode = 'auto'

    try:
        exp.curimgtype = 'openbeam'
        changeImgSinkSubdir(relpath(exp.openbeamdir, exp.datapath))
        return count(*detlist, **preset)
    finally:
        changeImgSinkSubdir('')
        exp.curimgtype = 'standard'

        if shutter:
            maw(shutter, 'closed')
        elif limadev is not None and limadev._shutter is not None:
            limadev.shuttermode = oldmode


#pylint: disable=keyword-arg-before-vararg
@usercommand
@helparglist('shutter, [detectors], [presets]')
def darkimage(shutter=None, *detlist, **preset):
    """Acquire a dark image."""
    exp = session.experiment
    det = exp.detectors[0]
    limadev = det._attached_images[0] if det._attached_images else None

    # TODO: better ideas for shutter control
    if shutter:
        # Shutter was given, so open it
        maw(shutter, 'closed')
    elif limadev is not None and limadev._shutter is not None:
        # No shutter; try the lima way
        oldmode = limadev.shuttermode
        limadev.shuttermode = 'always_closed'

    try:
        exp.curimgtype = 'dark'
        changeImgSinkSubdir(relpath(exp.darkimagedir, exp.datapath))
        return count(*detlist, **preset)
    finally:
        changeImgSinkSubdir('')
        exp.curimgtype = 'standard'

        if shutter:
            maw(shutter, 'open')
        elif limadev is not None and limadev._shutter is not None:
            limadev.shuttermode = oldmode
