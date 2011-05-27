#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
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

"""Scan commands for NICOS."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

from nicos import session
from nicos.scan import Scan, TimeScan, QScan, ContinuousScan, ManualScan
from nicos.device import Device, Measurable, Moveable, Readable
from nicos.errors import UsageError
from nicos.commands import usercommand


def _handleScanArgs(args, kwargs):
    preset, infostr, detlist, envlist, move, multistep = \
            {}, None, [], None, [], []
    for arg in args:
        if isinstance(arg, str):
            infostr = arg
        elif isinstance(arg, (int, long, float)):
            preset['t'] = arg
        elif isinstance(arg, Measurable):
            detlist.append(arg)
        elif isinstance(arg, list):
            detlist.extend(arg)
        elif isinstance(arg, Readable):
            if envlist is None:
                envlist = []
            envlist.append(arg)
        else:
            raise UsageError('unsupported scan argument: %r' % arg)
    for key, value in kwargs.iteritems():
        if key in session.devices and isinstance(session.devices[key], Moveable):
            if isinstance(value, list):
                if multistep and len(value) != len(multistep[-1][1]):
                    raise UsageError('all multi-step arguments must have the '
                                     'same length')
                multistep.append((session.devices[key], value))
            else:
                move.append((session.devices[key], value))
        else:
            # XXX this silently accepts wrong keys; restrict the possible keys?
            preset[key] = value
    return preset, infostr, detlist, envlist, move, multistep


def _fixType(dev, start, step):
    if isinstance(dev, list):
        dev = [session.getDevice(d, Moveable) for d in dev]
        l = len(dev)
        if not isinstance(start, list) or not len(start) == l:
            raise UsageError('start/center must be a list of length %d' % l)
        if not isinstance(step, list):
            step = [step] * l
        elif not len(step) == l:
            raise UsageError('step must be a single number or a list of '
                             'length %d' % l)
        return dev, start, step
    else:
        dev = session.getDevice(dev, Moveable)
    return [dev], [start], [step]

def _fixType2(dev, positions):
    if isinstance(dev, list):
        dev = [session.getDevice(d, Moveable) for d in dev]
        l = len(dev)
        if not isinstance(positions, list) or not len(positions) == l:
            raise UsageError('positions must be a list of length %d' % l)
        length = -1
        for x in positions:
            if not isinstance(x, list):
                raise UsageError('all positions entries must be lists')
            if length == -1:
                length = len(x)
            elif len(x) != length:
                raise UsageError('all position lists must be of same length')
        return dev, zip(*positions)
    return [dev], zip(positions)

def _infostr(fn, args, kwargs):
    def devrepr(x):
        if isinstance(x, Device):
            return x.name
        return repr(x)
    if kwargs:
        return '%s(%s, %s)' % (fn,
                               ', '.join(map(devrepr, args)),
                               ', '.join('%s=%r' % kv for kv in kwargs.items()))
    return '%s(%s)' % (fn, ', '.join(map(devrepr, args)))


@usercommand
def scan(dev, start, step=None, numsteps=None, *args, **kwargs):
    """Scan over device(s) and count detector(s).

    The general syntax is either to give start, step and number of steps:

        scan(dev, 0, 1, 10)   scans from 0 to 10 in steps of 1.

    or a list of positions to scan:

        scan(dev, [0, 1, 2, 3, 7, 8, 9])   scans at the given positions.

    """
    preset, infostr, detlist, envlist, move, multistep  = \
            _handleScanArgs(args, kwargs)
    if step is not None:
        infostr = infostr or \
                  _infostr('scan', (dev, start, step, numsteps) + args, kwargs)
        dev, start, step = _fixType(dev, start, step)
        if all(v == 0 for v in step) and numsteps > 1:
            raise UsageError('scanning with zero step width')
        values = [[x + i*y for x, y in zip(start, step)]
                  for i in range(numsteps)]
    else:
        infostr = infostr or \
                  _infostr('scan', (dev, start) + args, kwargs)
        dev, values = _fixType2(dev, start)
    scan = Scan(dev, values, move, multistep, detlist, envlist, preset, infostr)
    scan.run()

ADDSCANHELP = """
    Presets can be given using keyword arguments:

        scan(dev, ..., t=5)
        scan(dev, ..., m1=1000)

    By default, the detectors are those selected by SetDetectors().  They can be
    replaced by a custom set of detectors by giving them as arguments:

        scan(dev, ..., det1, det2)

    Other devices that should be recorded at every point (so-called environment
    devices) are by default those selected by SetEnvironment().  They can also
    be overridden by giving them as arguments:

        scan(dev, ..., T1, T2)

    Any devices can be moved to different positions *before* the scan starts.
    This is done by giving them as keyword arguments:

        scan(dev, ..., ki=1.55)
"""

scan.__doc__ += ADDSCANHELP

@usercommand
def cscan(dev, center, step, numperside, *args, **kwargs):
    """Scan around center.

    The general syntax is to give center, step and number of steps per side:

        cscan(dev, 0, 1, 5)    scans from -5 to 5 in steps of 1.
    """
    preset, infostr, detlist, envlist, move, multistep = \
            _handleScanArgs(args, kwargs)
    infostr = infostr or \
              _infostr('cscan', (dev, center, step, numperside) + args, kwargs)
    dev, center, step = _fixType(dev, center, step)
    if all(v == 0 for v in step) and numperside > 0:
        raise UsageError('scanning with zero step width')
    start = [x - numperside*y for x, y in zip(center, step)]
    values = [[x + i*y for x, y in zip(start, step)]
              for i in range(numperside*2 + 1)]
    scan = Scan(dev, values, move, multistep, detlist, envlist, preset, infostr)
    scan.run()

cscan.__doc__ += ADDSCANHELP.replace('scan(', 'cscan(')


@usercommand
def timescan(numsteps, *args, **kwargs):
    """Count a number of times without moving devices.

    "numsteps" can be -1 to scan for unlimited steps (break to quit).
    """
    preset, infostr, detlist, envlist, move, multistep = \
            _handleScanArgs(args, kwargs)
    infostr = infostr or _infostr('timescan', (numsteps,) + args, kwargs)
    scan = TimeScan(numsteps, move, multistep, detlist, envlist, preset, infostr)
    scan.run()


@usercommand
def contscan(dev, start, end, speed=None, *args, **kwargs):
    """Scan continuously with low speed."""
    dev = session.getDevice(dev, Moveable)
    if 'speed' not in dev.parameters:
        raise UsageError('continuous scan device must have a speed parameter')
    preset, infostr, detlist, envlist, move, multistep = \
            _handleScanArgs(args, kwargs)
    if preset:
        raise UsageError('preset not supported in continuous scan')
    if envlist:
        raise UsageError('environment devices not supported in continuous scan')
    if multistep:
        raise UsageError('multi-step not supported in continuous scan')
    infostr = infostr or \
              _infostr('contscan', (dev, start, end, speed) + args, kwargs)
    scan = ContinuousScan(dev, start, end, speed, move, detlist, infostr)
    scan.run()


def _getQ(v, name):
    try:
        if len(v) == 4:
            return list(v)
        elif len(v) == 3:
            return [v[0], v[1], v[2], 0]
        else:
            raise TypeError
    except TypeError:
        raise UsageError('%s must be a sequence of (h, k, l) or (h, k, l, E)'
                         % name)

def _handleQScanArgs(args, kwargs, Q, dQ):
    preset, infostr, detlist, envlist, move, multistep = {}, None, [], [], [], []
    for arg in args:
        if isinstance(arg, str):
            infostr = arg
        #elif isinstance(arg, (int, long, float)):
        #    preset['t'] = arg
        elif isinstance(arg, Measurable):
            detlist.append(arg)
        elif isinstance(arg, list):
            detlist.extend(arg)
        elif isinstance(arg, Readable):
            envlist.append(arg)
        else:
            raise UsageError('unsupported qscan argument: %r' % arg)
    for key, value in kwargs.iteritems():
        if key == 'h':
            Q[0] = value
        elif key == 'k':
            Q[1] = value
        elif key == 'l':
            Q[2] = value
        elif key == 'E':
            Q[3] = value
        elif key == 'dh':
            dQ[0] = value
        elif key == 'dk':
            dQ[1] = value
        elif key == 'dl':
            dQ[2] = value
        elif key == 'dE':
            dQ[3] = value
        elif key in session.devices and \
                 isinstance(session.devices[key], Moveable):
            if isinstance(value, list):
                if multistep and len(value) != len(multistep[-1][1]):
                    raise UsageError('all multi-step arguments must have the '
                                     'same length')
                multistep.append((session.devices[key], value))
            else:
                move.append((session.devices[key], value))
        else:
            # XXX this silently accepts wrong keys; restrict the possible keys?
            preset[key] = value
    return preset, infostr, detlist, envlist, move, multistep, Q, dQ


@usercommand
def qscan(Q, dQ, numsteps, *args, **kwargs):
    """Single-sided Q scan."""
    Q, dQ = _getQ(Q, 'Q'), _getQ(dQ, 'dQ')
    preset, infostr, detlist, envlist, move, multistep, Q, dQ = \
            _handleQScanArgs(args, kwargs, Q, dQ)
    if all(v == 0 for v in dQ) and numsteps > 1:
        raise UsageError('scanning with zero step width')
    infostr = infostr or _infostr('qscan', (Q, dQ, numsteps) + args, kwargs)
    values = [[Q[0]+i*dQ[0], Q[1]+i*dQ[1], Q[2]+i*dQ[2], Q[3]+i*dQ[3]]
               for i in range(numsteps)]
    scan = QScan(values, move, multistep, detlist, envlist, preset, infostr)
    scan.run()


@usercommand
def qcscan(Q, dQ, numperside, *args, **kwargs):
    """Centered Q scan."""
    Q, dQ = _getQ(Q, 'Q'), _getQ(dQ, 'dQ')
    preset, infostr, detlist, envlist, move, multistep, Q, dQ = \
            _handleQScanArgs(args, kwargs, Q, dQ)
    if all(v == 0 for v in dQ) and numperside > 0:
        raise UsageError('scanning with zero step width')
    infostr = infostr or _infostr('qcscan', (Q, dQ, numperside) + args, kwargs)
    values = [[Q[0]+i*dQ[0], Q[1]+i*dQ[1], Q[2]+i*dQ[2], Q[3]+i*dQ[3]]
               for i in range(-numperside, numperside+1)]
    scan = QScan(values, move, multistep, detlist, envlist, preset, infostr)
    scan.run()


class _ManualScan(object):
    def __init__(self, args, kwargs):
        preset, infostr, detlist, envlist, move, multistep = \
                _handleScanArgs(args, kwargs)
        infostr = infostr or _infostr('manualscan', args, kwargs)
        self.scan = ManualScan(move, multistep, detlist, envlist,
                               preset, infostr)

    def __enter__(self):
        session._manualscan = self.scan
        try:
            self.scan.manualBegin()
        except:  # yes, all exceptions
            session._manualscan = None
            raise

    def __exit__(self, *exc):
        self.scan.manualEnd()
        session._manualscan = None

@usercommand
def manualscan(*args, **kwargs):
    """Manual value scan."""
    if getattr(session, '_manualscan', None):
        raise UsageError('cannot start manual scan within manual scan')
    return _ManualScan(args, kwargs)
