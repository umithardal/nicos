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

from __future__ import with_statement

"""
Contains a process that polls devices automatically.
"""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import os
import time
import errno
import signal
import threading
import subprocess

from nicos import status, session
from nicos.utils import dictof, listof, whyExited
from nicos.device import Device, Readable, Param
from nicos.errors import NicosError


class Poller(Device):

    parameters = {
        'processes': Param('Poller processes', type=dictof(str, listof(str)),
                           mandatory=True),
    }

    def doInit(self):
        self._stoprequest = False
        self._workers = []
        self._creation_lock = threading.Lock()

    def _long_sleep(self, interval):
        te = time.time() + interval
        while time.time() < te:
            if self._stoprequest:
                return
            time.sleep(5)

    def _worker_thread(self, devname, event):
        state = ['unused']

        def reconfigure(key, value):
            if key.endswith('target'):
                state[0] = 'moving'
            elif key.endswith('pollinterval'):
                state[0] = 'newinterval'
            event.set()

        def poll_loop(dev):
            wait_event = event.wait
            clear_event = event.clear
            interval = dev.pollinterval
            errcount = 0
            i = 0
            while not self._stoprequest:
                i += 1
                try:
                    stval, rdval = dev.poll(i)
                    self.printdebug('%-10s status = %-25s, value = %s' %
                                    (dev, stval, rdval))
                except Exception, err:
                    if errcount < 5:
                        # only print the warning the first five times
                        self.printwarning('error reading %s' % dev, exc=err)
                    elif errcount == 5:
                        # make the interval a bit larger
                        interval *= 5
                    errcount += 1
                else:
                    if errcount > 0:
                        interval = dev.pollinterval
                        errcount = 0
                    if state[0] == 'moving':
                        interval = 0.5
                        if stval[0] != status.BUSY:
                            state[0] = 'normal'
                            interval = dev.pollinterval
                    elif state[0] == 'newinterval':
                        interval = dev.pollinterval
                        state[0] = 'normal'
                wait_event(interval)
                clear_event()

        dev  = None
        while not self._stoprequest:
            if dev is None:
                try:
                    with self._creation_lock:
                        dev = session.getDevice(devname, Readable)
                    session.cache.addCallback(dev, 'target', reconfigure)
                    session.cache.addCallback(dev, 'pollinterval', reconfigure)
                    state = ['normal']
                except NicosError, err:
                    self.printwarning('error creating %s, trying again in '
                                      '%d sec' % (devname, 30), exc=err)
                    self._long_sleep(30)
                    continue
            poll_loop(dev)

    def start(self, process=None):
        self._process = process
        if process is None:
            return self._start_master()
        self.printinfo('%s poller starting' % process)
        devices = self.processes[process]
        for devname in devices:
            self.printinfo('starting thread for %s' % devname)
            event = threading.Event()
            worker = threading.Thread(target=self._worker_thread,
                                      args=(devname, event))
            worker.event = event
            worker.setDaemon(True)
            worker.start()
            self._workers.append(worker)

    def wait(self):
        if self._process is None:
            return self._wait_master()
        while not self._stoprequest:
            time.sleep(1)
        for worker in self._workers:
            worker.join()

    def quit(self):
        if self._process is None:
            return self._quit_master()
        if self._stoprequest:
            return  # already quitting
        self.printinfo('poller quitting...')
        self._stoprequest = True
        for worker in self._workers:
            worker.event.set()
        for worker in self._workers:
            worker.join()
        self.printinfo('poller finished')

    def _start_master(self):
        self._children = {}

        for processname in self.processes:
            self._start_child(processname)

    def _start_child(self, name):
        if session.config.control_path:
            poller_script = os.path.normpath(
                os.path.join(session.config.control_path, 'bin', 'nicos-poller'))
        else:
            poller_script = 'nicos-poller'
        process = subprocess.Popen([poller_script, name])
        self._children[process.pid] = name
        session.log.info('started %s poller, PID %s' % (name, process.pid))

    def _wait_master(self):
        # wait for children to terminate; restart them if necessary
        while True:
            try:
                pid, ret = os.wait()
            except OSError, err:
                if err.errno == errno.EINTR:
                    # raised when the signal handler is fired
                    continue
                elif err.errno == errno.ECHILD:
                    # no further child processes found
                    break
                raise
            else:
                # a process exited; restart if necessary
                name = self._children[pid]
                if not self._stoprequest:
                    session.log.warning('%s poller terminated with %s, '
                                        'restarting' % (name, whyExited(ret)))
                    del self._children[pid]
                    self._start_child(name)
                else:
                    session.log.info('%s poller terminated with %s' %
                                     (name, whyExited(ret)))
        session.log.info('all pollers terminated')

    def _quit_master(self):
        self._stoprequest = True
        for pid in self._children:
            try:
                os.kill(pid, signal.SIGTERM)
            except OSError, err:
                if err.errno == errno.ESRCH:
                    # process was already terminated
                    continue
                raise
