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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

from __future__ import absolute_import, division, print_function

import ast
import logging
import os
import re
import traceback
from os import path

from nicos.clients.gui import config as guicfg
from nicos.clients.gui.config import prepareGuiNamespace
from nicos.core.errors import ConfigurationError
from nicos.core.params import nicosdev_re
from nicos.core.sessions.setups import SETUP_GROUPS, fixup_stacked_devices, \
    prepareNamespace
from nicos.pycompat import exec_, integer_types, string_types
from nicos.utils import checkSetupSpec, importString
from nicos.utils.files import findSetupRoots, iterSetups
from nicos.utils.loggers import StreamHandler

try:
    import nicos.guisupport.qt as qt
    from nicos.clients.gui.panels import Panel
except ImportError:
    qt = None
    Panel = None

interpol_re = re.compile(
    r'%[-#0 +]*(?:[0-9]+)?(?:\.(?:[0-9]*))?'
    r'[hlL]?[diouxXeEfFgGcrs%]'
)


class FileHandler(StreamHandler):

    def __init__(self, *args):
        StreamHandler.__init__(self, *args)
        self.setFormatter(
            logging.Formatter('! %(name)s: %(levelname)s: %(message)s')
        )


class Logger(logging.Logger):

    def handle(self, record):
        record.message = record.getMessage()
        record.filename = ''
        # the ColoredConsoleHandler does not use "line", make it part of name
        if getattr(record, 'line', 0):
            record.name = '%s:%s' % (record.name, record.line)
            record.line = ''
        logging.Logger.handle(self, record)


class SetupChecker(object):
    all_setups_cache = {}

    def __init__(self, filename, devs_seen, setup_info):
        self.filename = filename
        self.devs_seen = devs_seen
        self.setup_info = setup_info
        self.setupname = path.basename(filename)[:-3]
        self.log = logging.getLogger(filename)
        self.is_guiconfig = self.setupname.startswith('guiconfig')
        setup_roots = findSetupRoots(filename)
        if setup_roots in SetupChecker.all_setups_cache:
            all_setups = SetupChecker.all_setups_cache[setup_roots]
        else:
            SetupChecker.all_setups_cache[setup_roots] = all_setups = \
                dict(iterSetups(setup_roots))
        if self.is_guiconfig:
            self.ns = prepareGuiNamespace()
        else:
            self.ns = prepareNamespace(self.setupname, filename, all_setups)
        self.good = True

        # filled by check()
        self.code = None
        self.ast = None

    def log_exception(self, exception):
        formatted_lines = traceback.format_exc().splitlines()
        msg = 'Exception while executing: %s\n|' % str(exception)
        msg += '\n|'.join(formatted_lines[-3:])
        self.log_error(msg)

    def log_error(self, msg, *args, **kw):
        self.good = False
        self.log.error(msg, *args, **kw)

    error = log_error  # disguise ourself as a logger object

    # find line numbers in the AST

    def _find_binding(self, binding):
        assign = [
            x for x in self.ast.body if isinstance(x, ast.Assign)
            and isinstance(x.targets[0], ast.Name) and x.targets[0].id == binding
        ]
        if not assign:
            return None
        return assign[0]

    def find_global(self, binding):
        assign = self._find_binding(binding)
        if assign:
            return {'line': assign.lineno}
        return {'line': 0}

    def find_deventry(self, devname, parname=None):
        # find a binding for 'devices'
        assign = self._find_binding('devices')
        if not assign:
            return {'line': 0}
        dev_val = assign.value
        # now we look for the device() call that belongs to the given devname
        #
        # the 'devices' dict can be in two forms: either a dict literal
        if isinstance(dev_val, ast.Dict):
            # find index of the device we need in the keys
            for (i, key) in enumerate(dev_val.keys):
                if isinstance(key, ast.Str) and key.s == devname:
                    dev_call = dev_val.values[i]
                    break
                if isinstance(key, ast.BinOp):
                    try:
                        code = compile(
                            ast.fix_missing_locations(ast.Expression(key)),
                            '<string>', 'eval'
                        )
                        val = eval(code, self.ns)
                    except Exception:
                        self.log.error(
                            '%s: Error evaluating definition', ast.dump(key),
                            extra={'line': key.lineno}
                        )
                        continue
                    if val == devname:
                        dev_call = dev_val.values[i]
                        break
            else:
                # device not found
                return {'line': 0}
        # or a dict() call
        elif isinstance(dev_val, ast.Call) and dev_val.func.id == 'dict':
            # look for our device name in the kwargs
            for devkw in dev_val.keywords:
                if devkw.arg == devname:
                    dev_call = devkw.value
                    break
            else:
                # device not found
                return {'line': 0}
        # else it's something strange
        else:
            return {'line': 0}
        # we have our Call node in dev_call
        # do we need to look for param?
        if parname and isinstance(dev_call, ast.Call):
            for parkw in dev_call.keywords:
                if parkw.arg == parname:
                    return {'line': parkw.value.lineno}
        return {'line': dev_call.lineno}

    # check individual parameters

    def check_parameter(self, devname, name, value):
        # for format strings, check interpolations for syntax errors
        if name == 'fmtstr':
            if '%' not in value:
                self.log_error(
                    '%s: parameter fmtstr has a value without any '
                    'interpolation placeholders', devname,
                    extra=self.find_deventry(devname, name)
                )
                return False
            else:
                # split() returns all pieces not part of a string
                # interpolation placeholder, so they must not contain
                # any % signs
                pieces = interpol_re.split(value)
                for piece in pieces:
                    if '%' in piece:
                        self.log_error(
                            '%s: parameter fmtstr has an invalid '
                            'placeholder (%r)', devname, piece,
                            extra=self.find_deventry(devname, name)
                        )
                        return False
        return True

    def check_device(self, devname, devconfig, is_special=False):
        # check for valid name
        if not nicosdev_re.match(devname):
            self.log_error(
                '%s: device name is invalid (must be a valid '
                'Python identifier)' % devname,
                extra=self.find_deventry(devname)
            )
        # check for format of config entry
        if not isinstance(devconfig, tuple) or len(devconfig) != 2:
            self.log_error(
                '%s: device entry has wrong format (should be '
                'device() or a 2-entry tuple)' % devname,
                extra=self.find_deventry(devname)
            )
            return False
        # try to import the device class
        try:
            cls = importString(devconfig[0])
        except (ImportError, RuntimeError) as err:
            self.log.warning(
                'device class %r for %r not importable: %s', devconfig[0],
                devname, err, extra=self.find_deventry(devname)
            )
            return
        except Exception as e:
            self.log_error(
                'could not get device class %r for %r:', devconfig[0], devname,
                extra=self.find_deventry(devname)
            )
            return self.log_exception(e)
        config = devconfig[1]

        # check missing attached devices
        if not hasattr(cls, 'attached_devices'):
            self.log.warning(
                "%s: class %r has no 'attached_devices'", devname, cls.__name__
            )
        else:
            for aname, ainfo in cls.attached_devices.items():
                try:
                    ainfo.check(None, aname, config.get(aname))
                except ConfigurationError as err:
                    self.log_error(
                        '%s: attached device %s (%s) is '
                        'wrongly configured: %s' %
                        (devname, aname, cls.__name__, err),
                        extra=self.find_deventry(devname, aname)
                    )
                if aname in config:
                    del config[aname]

        # check missing and unsupported parameter config entries
        if not hasattr(cls, 'parameters'):
            self.log.warning(
                "%s: class %r has no 'parameters'", devname, cls.__name__
            )
        else:
            if not config.get('lowlevel', cls.parameters['lowlevel'].default) and \
               cls.__name__ != 'DeviceAlias':
                if not config.get('description') and not is_special:
                    self.log.warning(
                        '%s: device has no description', devname,
                        extra=self.find_deventry(devname)
                    )
            for pname, pinfo in cls.parameters.items():
                if pname in config:
                    if pinfo.internal:
                        self.log_error(
                            "%s: '%s' is configured in a setup file although "
                            "declared as internal parameter", devname, pname,
                            extra=self.find_deventry(devname, pname)
                        )
                        del config[pname]
                        continue
                    try:
                        pinfo.type(config[pname])
                    except (ValueError, TypeError) as e:
                        self.log_error(
                            '%s: parameter %r value %r is '
                            'invalid: %s', devname, pname, config[pname], e,
                            extra=self.find_deventry(devname, pname)
                        )
                    # check value of certain parameters
                    self.check_parameter(devname, pname, config[pname])
                    del config[pname]
                elif pinfo.mandatory:
                    self.log_error(
                        '%s: mandatory parameter %r missing', devname, pname,
                        extra=self.find_deventry(devname)
                    )
        if config:
            onepar = list(config)[0]
            self.log_error(
                '%s: configured parameters not accepted by the '
                'device class: %s', devname, ', '.join(config),
                extra=self.find_deventry(devname, onepar)
            )

    def check(self):
        # check syntax
        try:
            with open(self.filename) as fp:
                self.code = fp.read()
            exec_(self.code, self.ns)
            self.ast = ast.parse(self.code)
        except SyntaxError as e:
            msg = 'SyntaxError:\t%s' % e.msg
            msg += '\n|line: %s : %s ' % (
                e.lineno, e.text.strip() if e.text else ''
            )
            self.log_error(msg, extra={'line': e.lineno})
            return self.good
        except Exception as e:
            self.log_exception(e)
            return self.good
        self.log.info('syntax ok')
        self.setup_info[self.setupname] = self.ns

        if self.is_guiconfig:
            return self.check_guiconfig()

        # check for valid group
        group = self.ns.get('group', 'optional')
        if group not in SETUP_GROUPS:
            self.log_error(
                'invalid setup group %r', group, extra=self.find_global('group')
            )

        # check for a description
        description = self.ns.get('description', None)
        if description in (None, ''):
            self.log_error(
                'missing user-friendly setup description',
                extra=self.find_global('description')
            )

        self.ns['devices'
                ] = fixup_stacked_devices(self, self.ns.get('devices', {}))
        # check if devices are duplicated
        if group != 'special':
            devs = self.ns.get('devices', {})
            for devname in devs:
                if devname not in self.devs_seen:
                    self.devs_seen[devname] = self.setupname
                    continue
                # we have a duplicate: it's okay if we exclude the other setup
                # or if we are both basic setups
                other = self.devs_seen[devname]
                self_group = self.ns.get('group', 'optional')
                other_group = self.setup_info[other].get('group', 'optional')
                if self_group == 'basic' and other_group == 'basic':
                    continue
                if other in self.ns.get('excludes', []) or \
                   self.setupname in self.setup_info[other].get('excludes', []):
                    continue
                # it's also ok if it is a sample, experiment, or instrument
                # device
                if devname in ['Sample', 'Exp'] or \
                   'instrument' in devs[devname][1]:
                    continue
                self.log.warning(
                    'device name %s duplicate: also in %s', devname,
                    self.devs_seen[devname], extra=self.find_deventry(devname)
                )

        # check for common misspelling of "includes"
        if 'include' in self.ns:
            self.log_error(
                "'include' list should be called 'includes'",
                extra=self.find_global('include')
            )

        # check for common misspelling of "excludes"
        if 'exclude' in self.ns:
            self.log_error(
                "'exclude' list should be called 'excludes'",
                extra=self.find_global('exclude')
            )

        if os.path.basename(self.filename) == 'startup.py':
            if self.ns.get('includes', []):
                self.log_error(
                    "The 'includes' in 'startup.py' must be empty!",
                    extra=self.find_global('includes')
                )

        # check for types of recognized variables
        for (vname, vtype) in [
            ('description', string_types),
            # group is already checked against a fixed list
            ('sysconfig', dict),
            ('includes', list),
            ('excludes', list),
            ('modules', list),
            ('devices', dict),
            ('alias_config', dict),
            ('startupcode', str),
            ('extended', dict)
        ]:
            if vname in self.ns and not isinstance(self.ns[vname], vtype):
                self.log_error(
                    '%r must be of type %s (but is %s)' %
                    (vname, vtype, type(self.ns[vname])),
                    extra=self.find_global(vname)
                )

        # check for importability of modules
        for module in self.ns.get('modules', []):
            # try to import the device class
            try:
                importString(module)
            except Exception as err:
                self.log_error(
                    'module %r not importable: %s', module, err,
                    extra=self.find_global('modules')
                )

        # check for validity of alias_config
        aliascfg = self.ns.get('alias_config', {})
        if isinstance(aliascfg, dict):  # else we complained above already
            for aliasname, entrydict in aliascfg.items():
                if not (
                    isinstance(aliasname, string_types)
                    and isinstance(entrydict, dict)
                ):
                    self.log_error(
                        'alias_config entries should map alias '
                        'device names to a dictionary',
                        extra=self.find_global('alias_config')
                    )
                    continue
                for target, prio in entrydict.items():
                    if not (
                        isinstance(target, string_types)
                        and isinstance(prio, integer_types)
                        and not (isinstance(prio, bool))
                    ):
                        self.log_error(
                            'alias_config entries should map device '
                            'names to integer priorities',
                            extra=self.find_global('alias_config')
                        )
                        break
                    if target not in self.ns.get('devices', {}):
                        basedev = target.partition('.')[0]
                        if basedev not in self.ns.get('devices'):
                            self.log_error(
                                'alias_config device target should '
                                'be a device from the current setup',
                                extra=self.find_global('alias_config')
                            )
                            break

        # check for validity of display_order
        display_order = self.ns.get('display_order', 50)
        if not isinstance(display_order, integer_types) or \
           not 0 <= display_order <= 100:
            self.log_error(
                'display_order should be an integer between '
                '0 and 100', extra=self.find_global('display_order')
            )

        # check for validity of extended representative
        representative = self.ns.get('extended', {}).get('representative')
        if representative is not None:
            if representative not in self.ns.get('devices', {}):
                self.log_error(
                    'extended["representative"] should be a device '
                    'defined in the current setup',
                    extra=self.find_global('extended')
                )

        # check for valid device classes (if importable) and parameters
        for devname, devconfig in self.ns.get('devices', {}).items():
            self.check_device(
                devname, devconfig, group in ('special', 'configdata')
            )

        # return overall "ok" flag
        return self.good

    def check_guiconfig(self):
        # special checks for guiconfig setups

        # check for main window
        if 'main_window' not in self.ns:
            self.log_error('main window spec is missing')
        else:
            self.check_guiconfig_panel_spec(self.ns['main_window'])

        for window in self.ns.get('windows', []):
            self.check_guiconfig_window_spec(window)

        for tool in self.ns.get('tools', []):
            self.check_guiconfig_tool_spec(tool)

        return self.good

    def check_guiconfig_panel_spec(self, spec, context='main window'):
        qt5_incompatibles = [
            'nicos.clients.gui.panels.liveqwt.LiveDataPanel',
        ]
        # recursively check a panel spec
        if isinstance(spec, (guicfg.hsplit, guicfg.vsplit, guicfg.hbox,
                             guicfg.vbox)):
            for child in spec.children:
                self.check_guiconfig_panel_spec(child, context)
        elif isinstance(spec, guicfg.tabbed):
            for child in spec.children:
                self.check_guiconfig_panel_spec(child[1], context)
        elif isinstance(spec, guicfg.docked):
            self.check_guiconfig_panel_spec(spec[0])
            for child in spec[1]:
                if not (isinstance(child, tuple) and len(child) == 2):
                    self.log_error(
                        'dock item should be a (name, panel) tuple,'
                        ' found %r', child
                    )
                else:
                    self.check_guiconfig_panel_spec(child[1], context)
        elif isinstance(spec, guicfg.panel):
            if os.environ.get('NICOS_QT', 4) == '5' and \
               spec.clsname in qt5_incompatibles:
                self.log.warning('%r is not compatible with QT5', spec.clsname)
                return
            try:
                cls = importString(spec.clsname)
            except Exception as err:
                self.log_error(
                    'class %r for %s not importable: %s', spec.clsname, context,
                    err
                )
            else:
                if qt and not issubclass(cls, Panel):
                    self.log.warning(
                        'class %r for %s is not a Panel '
                        'subclass', spec.clsname, context
                    )
            self.validate_setup_spec(spec)
        else:
            self.log_error('found unsupported panel item %r', spec)

    def check_guiconfig_window_spec(self, spec):
        # recursively check a window spec
        if not isinstance(spec, guicfg.window):
            self.log_error('window spec %r is not a window()', spec)

        self.check_guiconfig_panel_spec(spec.contents, 'window %s' % spec.name)
        self.validate_setup_spec(spec)

    def check_guiconfig_tool_spec(self, spec):
        # recursively check a tool spec
        if not isinstance(spec, (guicfg.tool, guicfg.cmdtool, guicfg.menu)):
            self.log_error('tool spec %r is not a tool() or cmdtool()', spec)

        if isinstance(spec, guicfg.menu):
            for tool in spec.items:
                self.check_guiconfig_tool_spec(tool)

        if isinstance(spec, guicfg.tool):
            try:
                cls = importString(spec.clsname)
            except Exception as err:
                self.log_error(
                    'class %r for tool %r not importable: %s', spec.clsname,
                    spec.name, err
                )
            else:
                if qt and not issubclass(cls, (qt.QDialog, qt.QMainWindow)):
                    self.log.warning(
                        'class %r for tool %r is not a QDialog or'
                        ' QMainWindow', spec.clsname, spec.name
                    )
            self.validate_setup_spec(spec)

    def validate_setup_spec(self, spec):
        """Validate the 'setups' option.

        If there is a definitions of the old style of setup dependenciest a
        warning will be given.
        """
        setupspec = spec.options.get('setups', '')
        checkSetupSpec(setupspec, '', log=self.log)


class SetupValidator(object):
    def __init__(self):
        self.devs_seen = {}
        self.setup_info = {}
        self.result = True

    def walk(self, paths, separate=False):
        for p in paths:
            if separate:
                self.devs_seen = {}
                self.setup_info = {}
            if path.isdir(p):
                self.validateRecursive(p)
            elif path.isfile(p):
                self.validateOne(p)
            if not path.exists(p):
                # Explicitly no negative return value as the rest of the paths
                # may have been checked.
                log = logging.getLogger(p)
                log.error('File not found')
        return self.result

    def validateRecursive(self, p):
        for root, _dirs, files in os.walk(p):
            for f in files:
                if f.endswith('.py'):
                    self.validateOne(path.join(root, f))

    def validateOne(self, p):
        self.result &= SetupChecker(p, self.devs_seen, self.setup_info).check()
