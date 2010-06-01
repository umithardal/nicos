#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   NICOS runtime environment class
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
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
Contains the NICOS class, which contains all low-level global state
of the NICOS runtime.

Only for internal usage by functions and methods.
"""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import os
import imp
import sys
import logging
from os import path

from nicm import loggers
from nicm.errors import NicmError, UsageError, ConfigurationError


class NicosNamespace(dict):
    """
    A dict subclass that has a list of identifiers that cannot be set, except
    using the setForbidden() method.
    """

    def __init__(self):
        self.__forbidden = set()

    def addForbidden(self, name):
        self.__forbidden.add(name)

    def removeForbidden(self, name):
        self.__forbidden.discard(name)

    def setForbidden(self, name, value):
        dict.__setitem__(self, name, value)

    def __setitem__(self, name, value):
        if name in self.__forbidden:
            raise UsageError('%s cannot be assigned to' % name)
        dict.__setitem__(self, name, value)

    def __delitem__(self, name):
        if name in self.__forbidden:
            raise UsageError('%s cannot be deleted' % name)
        dict.__delitem__(self, name)


class NICOS(object):
    """
    The NICOS class provides all low-level routines needed for NICOS
    operations and keeps the global state: devices, configuration,
    loggers.
    """

    def __init__(self):
        # contains all created device objects
        self.devices = {}
        # contains the name of all explicitly created devices
        self.explicit_devices = set()
        # contains the configuration for all configured devices
        self.configured_devices = {}
        # contains the name of all loaded modules with user commands
        self.user_modules = set()
        # contains all loaded setups
        self.loaded_setups = set()
        # contains all explicitly loaded setups
        self.explicit_setups = []
        # path to setup files
        self.__setup_path = path.join(path.dirname(__file__),
                                      '..', '..', 'setup')
        # info about all loadable setups
        self.__setup_info = {}
        # namespace to place user-accessible items in
        self.__namespace = NicosNamespace()
        self.__local_namespace = NicosNamespace()
        # contains all NICOS-exported names
        self.__exported_names = set()
        # the System device
        self.__system_device = None

        # set up logging interface
        self._initLogging()
        self.log = self.getLogger('nicos')

    def setNamespace(self, ns):
        """Set the namespace to export commands and devices into."""
        self.__namespace = ns
        self.__exported_names = set()

    def setSetupPath(self, path):
        """Set the path to the setup files."""
        self.__setup_path = path
        self.__readSetups()

    def __readSetups(self):
        """Read information of all existing setups.

        Setup modules are looked for in the setup/ directory which
        should be a sibling to this package's directory.
        """
        self.__setup_info.clear()
        for filename in os.listdir(self.__setup_path):
            if not filename.endswith('.py'):
                continue
            modname = filename[:-3]
            try:
                modfile = imp.find_module(modname, [self.__setup_path])
                code = modfile[0].read()
                modfile[0].close()
            except (ImportError, IOError), err:
                raise ConfigurationError('Could not find or read setup '
                                         'module %r: %s' % (modname, err))
            # device() is a helper function to make configuration prettier
            ns = {'device': lambda cls, **params: (cls, params)}
            try:
                exec code in ns
            except Exception, err:
                raise ConfigurationError('An error occurred while reading '
                                         'setup %s: %s' % (modname, err))
            info = {
                'name': ns.get('name', modname),
                'group': ns.get('group', 'base'),
                'includes': ns.get('includes', []),
                'modules': ns.get('modules', []),
                'devices': ns.get('devices', {}),
                'startupcode': ns.get('startupcode', ''),
            }
            self.__setup_info[modname] = info
        # check if all includes exist
        for name, info in self.__setup_info.iteritems():
            for include in info['includes']:
                if include not in self.__setup_info:
                    raise ConfigurationError('Setup %s includes setup %s which '
                                             'does not exist' % (name, include))

    def loadSetup(self, setupname):
        """Load a setup module and set up devices accordingly."""
        if not self.__setup_info:
            self.__readSetups()

        log = self.getLogger('nicos')
        if setupname in self.loaded_setups:
            log.warning('setup %s is already loaded' % setupname)
            return
        if setupname not in self.__setup_info:
            raise ConfigurationError('Setup %s does not exist' % setupname)

        log.info('loading setup %s' % setupname)

        from nicm.commands import usercommandWrapper
        failed_devs = []

        def load_module(modname):
            if modname in self.user_modules:
                return
            self.user_modules.add(modname)
            log.info('importing module %s... ' % modname)
            try:
                __import__(modname)
                mod = sys.modules[modname]
            except Exception, err:
                log.error('Exception importing %s: %s' % (modname, err))
                return
            for name, command in mod.__dict__.iteritems():
                if getattr(command, 'is_usercommand', False):
                    self.export(name, usercommandWrapper(command))

        def inner_load(name):
            if name in self.loaded_setups:
                return
            if name != setupname:
                log.info('loading include setup %s' % name)

            self.loaded_setups.add(name)
            info = self.__setup_info[name]

            for include in info['includes']:
                inner_load(include)

            for modname in info['modules']:
                load_module(modname)

            self.configured_devices.update(info['devices'])

            devlist = sorted(info['devices'].iteritems())
            for devname, (_, devconfig) in devlist:
                if not devconfig.get('autocreate', False):
                    continue
                log.info('creating device %r... ' % devname)
                try:
                    self.createDevice(devname, explicit=True)
                except Exception:
                    log.exception('failed')
                    failed_devs.append(devname)

            exec info['startupcode'] in self.__namespace

        # always load nicm.commands
        load_module('nicm.commands')

        inner_load(setupname)

        if failed_devs:
            log.warning('the following devices could not be created:')
            log.warning(', '.join(failed_devs))

        self.explicit_setups.append(setupname)
        expsetups = '+'.join(self.explicit_setups)
        sys.ps1 = '(%s) >>> ' % expsetups
        sys.ps2 = ' %s  ... ' % (' ' * len(expsetups))
        log.info('setup loaded')

    def unloadSetup(self):
        """Unload the current setup: destroy all devices and clear the
        NICOS namespace.
        """
        # XXX order shutdown by device dependencies
        for devname, dev in self.devices.items():
            dev.shutdown()
            self.unexport(devname)
            del self.devices[devname]
        self.configured_devices.clear()
        self.explicit_devices.clear()
        for name in list(self.__exported_names):
            self.unexport(name)
        self.loaded_setups = set()
        self.explicit_setups = []
        self.user_modules = set()

    def export(self, name, object):
        self.__namespace.setForbidden(name, object)
        self.__namespace.addForbidden(name)
        self.__local_namespace.addForbidden(name)
        self.__exported_names.add(name)

    def unexport(self, name):
        if name not in self.__namespace:
            self.log.warning('unexport: name %r not in namespace' % name)
            return
        if name not in self.__exported_names:
            self.log.warning('unexport: name %r not exported by NICOS' % name)
        self.__namespace.removeForbidden(name)
        self.__local_namespace.removeForbidden(name)
        del self.__namespace[name]
        self.__exported_names.remove(name)

    def getExportedObjects(self):
        for name in self.__exported_names:
            if name in self.__namespace:
                yield self.__namespace[name]

    # -- Device control --------------------------------------------------------

    def getSystem(self):
        if self.__system_device is None:
            from nicm.system import System
            self.__system_device = self.getDevice('System', System)
        return self.__system_device

    def getDevice(self, dev, cls=None):
        """Convenience: get a device by name or instance."""
        if isinstance(dev, str):
            if dev in self.devices:
                dev = self.devices[dev]
            elif dev in self.configured_devices:
                dev = self.createDevice(dev)
            else:
                raise UsageError('device %r not found in configuration' % dev)
        from nicm.device import Device
        if not isinstance(dev, cls or Device):
            raise UsageError('dev must be a %s' % (cls or Device).__name__)
        return dev

    def createDevice(self, devname, recreate=False, explicit=False):
        """Create device given by a device name.

        If device exists and *recreate* is true, destroy and create it again.
        """
        if devname not in self.configured_devices:
            raise ConfigurationError('device %r not found in configuration'
                                     % devname)
        if explicit:
            self.explicit_devices.add(devname)
        if devname in self.devices:
            if not recreate:
                return self.devices[devname]
            self.destroyDevice(devname)
        devclsname, devconfig = self.configured_devices[devname]
        modname, clsname = devclsname.rsplit('.', 1)
        try:
            devcls = getattr(__import__(modname, None, None, [clsname]),
                             clsname, None)
        except ImportError:
            # try with "nicm." prepended
            mod = __import__('nicm.' + modname, None, None, [clsname])
            devcls = getattr(mod, clsname, None)
        if devcls is None:
            raise ConfigurationError('type of device %r does not exist'
                                     % devclsname)
        dev = devcls(devname, devconfig)
        self.devices[devname] = dev
        self.export(devname, dev)
        dev.init()
        return dev

    def destroyDevice(self, devname):
        """Shutdown and destroy a device."""
        if devname not in self.devices:
            raise UsageError('device %r not created' % devname)
        self.devices[devname].shutdown()
        del self.devices[devname]
        self.explicit_devices.discard(devname)
        if devname in self.__namespace:
            self.unexport(devname)

    # -- Logging ---------------------------------------------------------------

    def _initLogging(self):
        loggers.initLoggers()
        self._loggers = {}
        self._log_manager = logging.Manager(None)
        # all interfaces should log to a logfile; more handlers can be
        # added by subclasses
        self._log_handlers = [loggers.NicmLogfileHandler()]

    def getLogger(self, name):
        if name in self._loggers:
            return self._loggers[name]
        logger = self._log_manager.getLogger(name)
        # XXX must be configurable
        logger.setLevel(logging.DEBUG)
        for handler in self._log_handlers:
            logger.addHandler(handler)
        self._loggers[name] = logger
        return logger

    def logUnhandledException(self, exc_info):
        """Log and unhandled exception.  Log using the originating device's
        logger, if that information is available.
        """
        if isinstance(exc_info[1], NicmError):
            if exc_info[1].device and exc_info[1].device._log:
                exc_info[1].device._log.error(exc_info=exc_info)
                return
        self.log.error(exc_info=exc_info)
