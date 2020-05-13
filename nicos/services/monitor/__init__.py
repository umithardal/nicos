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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Base class for instrument monitors."""

from __future__ import absolute_import, division, print_function

import re
from time import sleep, strftime, time as currenttime

from nicos import session
from nicos.core import ConfigurationError, Override, Param, none_or, oneof
from nicos.core.sessions.setups import SetupBlock
from nicos.devices.cacheclient import BaseCacheClient
from nicos.protocols.cache import OP_SUBSCRIBE, OP_TELL, OP_TELLOLD, \
    OP_WILDCARD, cache_load
from nicos.pycompat import to_utf8
from nicos.utils import createThread, reexecProcess, watchFileContent


class Monitor(BaseCacheClient):
    """
    A graphical window showing values of cache keys.

    For cache keys that correspond to NICOS devices, not only the devicevalue,
    but also the device status and unit are shown.
    """

    # server and prefix parameters come from BaseCacheClient
    parameters = {
        'title':     Param('Title of status window', type=str,
                           default='Status'),
        'layout':    Param('Status monitor layout', type=list,
                           mandatory=True),
        'font':      Param('Font name for the window', type=str,
                           default='Luxi Sans'),
        'valuefont': Param('Font name for the value displays', type=str),
        'fontsize':  Param('Basic font size', type=int, default=12,
                           settable=True),
        'timefontsize': Param('Time headline font size', type=none_or(int),
                              default=None, settable=True),
        'padding':   Param('Padding for the display fields', type=int,
                           default=2, settable=True),
        'geometry':  Param('Geometry for status window',
                           type=str, settable=True,
                           ext_desc='For the  allowed settings see '
                           ':option:`--geometry`.'),
        'resizable': Param('Whether the window is resizable', type=bool,
                           default=True),
        'colors':    Param('Color scheme for value displays (dark or light '
                           'background)', type=oneof('dark', 'light')),
        'showwatchdog':  Param('Whether to show watchdog warnings', type=bool,
                               default=True),
        'expectmaster':  Param('Whether a message should indicate that no '
                               'NICOS master is active', type=bool,
                               default=True),
    }

    parameter_overrides = {
        'prefix':    Override(mandatory=False, default='nicos/'),
    }

    # methods to be implemented in concrete implementations

    def initGui(self):
        raise NotImplementedError('Implement initGui() in subclasses')

    def mainLoop(self):
        raise NotImplementedError('Implement mainLoop() in subclasses')

    def closeGui(self):
        raise NotImplementedError('Implement closeGui() in subclasses')

    def signalKeyChange(self, field, *args):
        raise NotImplementedError('Implement signalKeyChange() in subclasses')

    def switchWarnPanel(self, on):
        raise NotImplementedError('Implement switchWarnPanel() in subclasses')

    def reconfigureBoxes(self):
        raise NotImplementedError('Implement reconfigureBoxes() in subclasses')

    def updateTitle(self, text):
        raise NotImplementedError('Implement updateTitle() in subclasses')

    # methods implemented here

    _keys_expired = False  # whether on disconnect all keys have been expired

    def start(self, options):  # pylint: disable=W0221
        self.log.info('monitor starting up, creating main window')

        self._fontsize = options.fontsize or self.fontsize
        self._fontsizebig = int(self._fontsize * 1.2)
        self._timefontsize = (options.timefontsize or self.timefontsize or
                              (self._fontsizebig + self._fontsize))
        self._padding = options.padding or self.padding
        self._geometry = options.geometry or self.geometry

        if self._geometry and self._geometry != 'fullscreen':
            try:
                m = re.match(r'(?:(\d+)x(\d+))?\+(\d+)\+(\d+)', self._geometry)
                w, h, x, y = m.groups()
                if w is None:
                    w = h = 0
                else:
                    w, h = int(w), int(h)
                x, y = int(x), int(y)
                self._geometry = (w, h, x, y)
            except Exception:
                self.log.warning('invalid geometry %s', self._geometry)
                self._geometry = None

        # timeout for select() call
        self._selecttimeout = 0.2
        # maps keys to field-dicts defined in self.layout (see above)
        self._keymap = {}
        # blocks to hide conditionally
        self._onlyblocks = []
        # fields to hide conditionally (only if not in a block)
        self._onlyfields = []
        # remembers loaded setups
        self._setups = set()
        # master active?
        self._masteractive = False
        # currently shown warnings
        self._currwarnings = ''

        # start a thread checking for modification of the setup file
        createThread('refresh checker', self._checker)

        self.initGui()

        # now start the worker thread
        self._worker.start()

        self.log.info('starting main loop')
        try:
            self.mainLoop()
        except KeyboardInterrupt:
            pass
        self._stoprequest = True

    def _checker(self):
        setupname = session.explicit_setups[0]
        fn = session._setup_info[setupname]['filenames']
        watchFileContent(fn, self.log)
        self.log.info('setup file changed; restarting monitor process')
        reexecProcess()

    def wait(self):
        self.log.info('monitor quitting')
        self._worker.join()
        self.log.info('done')

    def quit(self, *ignored, **kwds):
        self.closeGui()
        self._stoprequest = True

    def _connect_action(self):
        self._keys_expired = False
        BaseCacheClient._connect_action(self)
        if self.showwatchdog:
            # also ask for and subscribe to all watchdog events
            self._socket.sendall(to_utf8('@watchdog/%s\n' % OP_WILDCARD))
            self._socket.sendall(to_utf8('@watchdog/%s\n' % OP_SUBSCRIBE))

        # use appname to distinguish between different instances
        self.storeSysInfo(session.appname)

    # called between connection attempts
    def _wait_retry(self):
        if not self._keys_expired:
            time = currenttime()
            for key in self._keymap:
                for obj in self._keymap[key]:
                    self.signalKeyChange(obj, key, None, time, True)
            self._keys_expired = True
        self.updateTitle('Disconnected (%s)' % strftime('%d.%m.%Y %H:%M:%S'))
        sleep(1)

    # called while waiting for data
    def _wait_data(self):
        # update current time
        self.updateTitle('%s (%s)%s' %
                         (self.title, strftime('%d.%m.%Y %H:%M:%S'),
                          '' if self._masteractive or (not self.expectmaster)
                          else ', no master active'))

    def register(self, widget, key):
        """API used by NicosListener widgets to register keys for callback."""
        key = self._prefix + key.lower()
        self._keymap.setdefault(key, []).append(widget)
        return key

    # called to handle an incoming protocol message
    def _handle_msg(self, time, ttlop, ttl, tsop, key, op, value):
        if op not in (OP_TELL, OP_TELLOLD):
            return
        try:
            time = float(time)
        except (ValueError, TypeError):
            time = currenttime()
        try:
            value = cache_load(value)
        except ValueError:
            value = None

        if key == 'watchdog/warnings' and self.showwatchdog:
            self._process_warnings(value)
            return

        # self.log.debug('processing %s', [time, ttl, key, op, value])

        if key == self._prefix + 'session/master':
            self._masteractive = value and op != OP_TELLOLD

        if key == self._prefix + 'session/mastersetup':
            self._setups = set(value)
            # reconfigure displayed blocks
            self.reconfigureBoxes()
            self.log.info('reconfigured display for setups %s',
                          ', '.join(self._setups))

        expired = value is None or op == OP_TELLOLD

        # now check if we need to update something
        objs = self._keymap.get(key, [])
        for obj in objs:
            self.signalKeyChange(obj, key, value, time, expired)

    def _process_warnings(self, warnings):
        # self.log.debug('new warnings: %s', warnings)
        self._currwarnings = warnings
        self.switchWarnPanel(bool(warnings))

    def _resolve_block(self, block):
        # exchange SetupBlock objects by their definition, or raise
        # a ConfigurationError if it doesn't exist.
        if not isinstance(block, SetupBlock):
            return block
        setup, bname = block._setupname, block._blockname
        setupinfo = session.getSetupInfo()
        if setup not in setupinfo:
            raise ConfigurationError(self, 'Setup "%s" required by '
                                     'SetupBlock() does not exist' % setup)
        blocks = setupinfo[setup]['monitor_blocks']
        if bname not in blocks:
            raise ConfigurationError(self, 'Setup "%s" does not define a  '
                                     'monitor block called "%s"' %
                                     (setup, bname))
        return blocks[bname]
