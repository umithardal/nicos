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
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

"""NICOS GUI application startup."""

from __future__ import absolute_import, division, print_function

import argparse
import logging
import os
# Work around a crash on Py3/Bionic when readline is imported later in
# a callback from unpickling server data.
import readline  # pylint: disable=unused-import
import sys
import traceback
from os import path

from nicos import config
from nicos.clients.base import ConnectionData
from nicos.clients.gui.config import processGuiConfig
from nicos.clients.gui.dialogs.instr_select import InstrSelectDialog
from nicos.clients.gui.mainwindow import MainWindow
from nicos.clients.gui.utils import DebugHandler
from nicos.guisupport.qt import QApplication
from nicos.protocols.daemon.classic import DEFAULT_PORT
from nicos.utils import parseConnectionString
from nicos.utils.loggers import ColoredConsoleHandler, NicosLogfileHandler, \
    NicosLogger, initLoggers

log = None


def parseargs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config-file', dest='configfile', default=None,
                        help='use the configuration file CONFIGFILE')
    parser.add_argument('-v', '--view-only', dest='viewonly', default=False,
                        action='store_true', help='run in view-only mode')
    parser.add_argument('-t', '--use-tunnel', dest='tunnel', default='',
                        action='store', help='use a ssh tunnel to connect. '
                                             'TUNNEL is a string with the following form:'
                                             ' [user_name@]host.')
    parser.add_argument('connect', nargs='?', default=None,
                        help='''A connection string with the following form:

                        [user_name[:password[@host[:port]]]]''')
    return parser.parse_args()


def main(argv):
    global log  # pylint: disable=global-statement

    userpath = path.join(path.expanduser('~'), '.config', 'nicos')

    # Set up logging for the GUI instance.
    initLoggers()
    log = NicosLogger('gui')
    log.parent = None
    log.setLevel(logging.INFO)
    log.addHandler(ColoredConsoleHandler())
    log.addHandler(NicosLogfileHandler(path.join(userpath, 'log'), 'gui',
                                       use_subdir=False))

    # set up logging for unhandled exceptions in Qt callbacks
    def log_unhandled(*exc_info):
        traceback.print_exception(
            *exc_info)  # pylint: disable=no-value-for-parameter
        log.exception('unhandled exception in QT callback', exc_info=exc_info)

    sys.excepthook = log_unhandled

    app = QApplication(argv, organizationName='nicos', applicationName='gui')

    opts = parseargs()

    if opts.configfile is None:
        try:
            config.apply()
        except RuntimeError:
            pass
        # If "demo" is detected automatically, let the user choose their
        # instrument configuration.
        need_dialog = config.instrument is None or \
                      (config.setup_package == 'nicos_demo' and
                       config.instrument == 'demo' and
                       'INSTRUMENT' not in os.environ)
        if need_dialog:
            opts.configfile = InstrSelectDialog.select(
                'Your instrument could not be automatically detected.')
            if opts.configfile is None:
                return
        else:
            opts.configfile = path.join(config.setup_package_path,
                                        config.instrument, 'guiconfig.py')

    with open(opts.configfile, 'rb') as fp:
        configcode = fp.read()
    gui_conf = processGuiConfig(configcode)
    gui_conf.stylefile = ''

    instrumentpath = path.join('/', *os.path.abspath(opts.configfile).split(
        '/')[:-1])
    for f in os.listdir(instrumentpath):
        if f.endswith(".qss"):
            gui_conf.stylefile = path.join(instrumentpath, f)
            break

    stylefiles = [path.join(userpath, 'style-%s.qss' % sys.platform),
        path.join(userpath, 'style.qss'),
        path.splitext(opts.configfile)[0] + '-%s.qss' % sys.platform,
        path.splitext(opts.configfile)[0] + '.qss', ]

    for stylefile in [gui_conf.stylefile] or stylefiles:
        if path.isfile(stylefile):
            try:
                with open(stylefile, 'r') as fd:
                    app.setStyleSheet(fd.read())
                gui_conf.stylefile = stylefile
                break
            except Exception:
                log.warning('Error setting user style sheet from %s',
                            stylefile, exc=1)

    if 'ess_gui' in gui_conf.options and gui_conf.options['ess_gui']:
        from nicos_ess.gui.mainwindow import MainWindow as MainWindowESS
        mainwindow = MainWindowESS(log, gui_conf, opts.viewonly, opts.tunnel)
    else:
        mainwindow = MainWindow(log, gui_conf, opts.viewonly, opts.tunnel)
    log.addHandler(DebugHandler(mainwindow))

    if opts.connect:
        parsed = parseConnectionString(opts.connect, DEFAULT_PORT)
        if parsed:
            cdata = ConnectionData(**parsed)
            cdata.viewonly = opts.viewonly
            mainwindow.setConnData(cdata)
            if cdata.password is not None:
                # we have a password, connect right away
                mainwindow.client.connect(mainwindow.conndata)
            else:
                # we need to ask for password, override last preset (uses given
                # connection data) and force showing connect window
                mainwindow.lastpreset = ''
                mainwindow.autoconnect = True
    mainwindow.startup()

    return app.exec_()
