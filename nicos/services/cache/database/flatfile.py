#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2019 by the NICOS contributors (see AUTHORS)
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

from __future__ import absolute_import, division, print_function

import os
import shutil
import threading
from os import path
from time import localtime, mktime, sleep, time as currenttime

from nicos import config
from nicos.core import Param, oneof
from nicos.protocols.cache import FLAG_NO_STORE, OP_TELL, OP_TELLOLD
from nicos.pycompat import iteritems, listitems
from nicos.services.cache.database.base import CacheDatabase
from nicos.services.cache.entry import CacheEntry
from nicos.utils import allDays, createThread, ensureDirectory


class FlatfileCacheDatabase(CacheDatabase):
    """Cache database which writes historical values to disk in a flatfile
    (ASCII) format.

    The store format is the following:

    * Each cache key is separated at the last slash.  The part before the slash
      is called "category" (usually prefix + a device name).
    * The store consists of a two-level subdirectory hierarchy "YYYY/MM-DD"
      below the chosen store path.  The directories contain a file per category
      (with slashes in the name replaced by dashes).
    * If not deactivated, these files are also hardlinked at another hierarchy,
      starting with the category, and containing files by year and day.

    For example, the cache entries for category "nicos/slit" at 2012-01-05 are
    available in the files ``2012/01-05/nicos-slit`` and
    ``nicos-slit/2012/01-05``.

    The format of these files is a simple four-column tab-separated ascii
    format:

    * the first column is the last part of the cache key (which combined
      with the category gives the full key)
    * the second column is the Unix timestamp of the change
    * the third column is either ``+`` or ``-``, where ``-`` means "the key will
      expire at some point" (on re-loading old files, such values will be
      ignored)
    * the fourth column is the actual value or ``-`` meaning "expired"

    All values should be valid Python literals, but this is not enforced by the
    cache server, rather by the NICOS clients.  The value can also a single
    dash, this indicates that at the given timestamp the latest value for this
    key expired.
    """

    parameters = {
        'storepath': Param('Directory where history stores should be saved',
                           type=str, mandatory=True),
        'makelinks': Param('Selects the type of file links in the second '
                           'store hierarchy (auto meaning none on Windows, '
                           'hard else)', default='auto',
                           type=oneof('auto', 'hard', 'soft', 'none')),
    }

    def doInit(self, mode):
        self._cat = {}
        self._cat_lock = threading.Lock()
        CacheDatabase.doInit(self, mode)

        if self.makelinks == 'auto':
            # Windows compatibility: it does not provide os.link
            if not hasattr(os, 'link'):
                self._make_link = lambda a, b: None
            else:
                self._make_link = os.link
        elif self.makelinks == 'hard':
            self._make_link = os.link
        elif self.makelinks == 'soft':
            self._make_link = os.symlink
        else:
            self._make_link = lambda a, b: None

        self._basepath = path.join(config.nicos_root, self.storepath)
        ltime = localtime()
        self._year = str(ltime[0])
        self._currday = '%02d-%02d' % ltime[1:3]
        self._midnight = mktime(ltime[:3] + (0,) * (8-3) + (ltime[8],))
        self._nextmidnight = self._midnight + 86400

        self._stoprequest = False
        self._cleaner = createThread('cleaner', self._clean)

    def doShutdown(self):
        self._stoprequest = True
        self._cleaner.join()

    def _read_one_storefile(self, filename):
        with open(filename, 'r+') as fd:
            # read file format identification
            firstline = fd.readline()
            if firstline.startswith('# NICOS cache store file v2'):
                return self._read_one_storefile_v2(filename, fd)
        self.log.warning('ignoring store file %s with wrong format', filename)
        return {}

    def _read_one_storefile_v2(self, filename, fd):
        db = {}
        for line in fd:
            if '\x00' in line:
                self.log.warning('found nullbyte in store file %s', filename)
                continue
            try:
                subkey, time, hasttl, value = line.rstrip().split(None, 3)
                if hasttl == '+':
                    # the value is valid indefinitely, so we can use it
                    db[subkey] = CacheEntry(float(time), None, value)
                elif value != '-':
                    # the value is not valid indefinitely, add it but mark as expired
                    db[subkey] = CacheEntry(float(time), None, value)
                    db[subkey].expired = True
                elif subkey in db:  # implied: value == '-'
                    # the value is already present, but now explicitly invalidated
                    # => mark it as expired
                    db[subkey].expired = True
            except Exception:
                self.log.warning('could not interpret line from '
                                 'cache file %s: %r', filename, line, exc=1)
        return db

    def initDatabase(self):
        # read the last entry for each key from disk
        nkeys = 0
        do_rollover = False
        # read entries from today if they exist
        curdir = path.join(self._basepath, self._year, self._currday)
        # else read from last day with cache entries by default (lastday must be
        # a symlink to the last day directory)
        if not path.isdir(curdir):
            curdir = path.join(self._basepath, 'lastday')
            # in this case, we need to create new cache files for today, so we
            # perform a faux rollover immediately after reading the db
            do_rollover = True
        # and if that doesn't exist, give up
        if not path.isdir(curdir):
            # ... but at least set the symlink correctly for today
            self.log.info('no previous values found, setting "lastday" link '
                          'to %s/%s', self._year, self._currday)
            self._set_lastday()
            return
        with self._cat_lock:
            for fn in os.listdir(curdir):
                cat = fn.replace('-', '/')
                try:
                    db = self._read_one_storefile(path.join(curdir, fn))
                    lock = threading.Lock()
                    self._cat[cat] = [None, lock, db]
                    nkeys += len(db)
                except Exception:
                    self.log.warning('could not read cache file %s', fn, exc=1)
            if do_rollover:
                self._rollover()
        self.log.info('loaded %d keys from files in %s', nkeys, curdir)

    def clearDatabase(self):
        self.log.info('clearing database from %s', self._basepath)
        self._clearDatabaseDir(self._basepath)

    def _clearDatabaseDir(self, _path):
        for fn in os.listdir(_path):
            filename = path.join(_path, fn)
            if os.path.isdir(filename) and not os.path.islink(filename):
                self.log.info('removing cache directory %r', filename)
                shutil.rmtree(filename)
            elif fn != '.keep':
                self.log.info('removing cache file %r', filename)
                os.remove(filename)

    def _rollover(self):
        """Must be called with self._cat_lock held."""
        self.log.info('midnight passed, data file rollover started')
        ltime = localtime()
        # set the days and midnight time correctly
        self._year = str(ltime[0])
        self._currday = '%02d-%02d' % ltime[1:3]
        self._midnight = mktime(ltime[:3] + (0,) * (8-3) + (ltime[8],))
        self._nextmidnight = self._midnight + 86400
        # roll over all file descriptors
        for category, (fd, _, db) in iteritems(self._cat):
            if fd:
                fd.close()
                self._cat[category][0] = None
            fd = self._create_fd(category)
            for subkey, entry in iteritems(db):
                if entry.value:
                    fd.write('%s\t%s\t%s\t%s\n' % (
                        subkey, entry.time,
                        (entry.ttl or entry.expired) and '-' or '+',
                        entry.value))
            # don't keep fds open for *all* files with keys, rather reopen
            # those that are necessary when new updates come in
            fd.close()
        # set the 'lastday' symlink to the current day directory
        self._set_lastday()
        # old files could be compressed here, but it is probably not worth it

    def _set_lastday(self):
        if not hasattr(os, 'symlink'):
            return
        try:
            lname = path.join(self._basepath, 'lastday')
            if path.lexists(lname):
                os.unlink(lname)
            os.symlink(path.join(self._year, self._currday), lname)
        except Exception:
            self.log.warning('error setting "lastday" symlink', exc=1)

    def _create_fd(self, category):
        """Open the by-date output file for the current day for a given
        category, and create the by-category hard link if necessary.
        """
        category = category.replace('/', '-')
        bydate = path.join(self._basepath, self._year, self._currday)
        ensureDirectory(bydate)
        filename = path.join(bydate, category)
        fd = open(filename, 'a+')
        fd.seek(0, os.SEEK_END)
        # write version identification, but only for empty files
        if fd.tell() == 0:
            fd.write('# NICOS cache store file v2\n')
        bycat = path.join(self._basepath, category, self._year)
        ensureDirectory(bycat)
        linkname = path.join(bycat, self._currday)
        if not path.isfile(linkname):
            try:
                self._make_link(filename, linkname)
            except Exception:
                self.log.exception('linking %s -> %s', linkname, filename)
        return fd

    def ask(self, key, ts, time, ttl):
        try:
            category, subkey = key.rsplit('/', 1)
        except ValueError:
            category = 'nocat'
            subkey = key
        with self._cat_lock:
            if category not in self._cat:
                return [key + OP_TELLOLD + '\n']
            _, lock, db = self._cat[category]
        with lock:
            if subkey not in db:
                return [key + OP_TELLOLD + '\n']
            entry = db[subkey]
        # check for expired keys
        if entry.value is None:
            return [key + OP_TELLOLD + '\n']
        # check for expired keys
        op = entry.expired and OP_TELLOLD or OP_TELL
        if entry.ttl:
            if ts:
                return ['%r+%s@%s%s%s\n' % (entry.time, entry.ttl,
                                            key, op, entry.value)]
            else:
                return [key + op + entry.value + '\n']
        if ts:
            return ['%r@%s%s%s\n' % (entry.time, key, op, entry.value)]
        else:
            return [key + op + entry.value + '\n']

    def ask_wc(self, key, ts, time, ttl):
        ret = set()
        # look for matching keys
        for cat, (_, lock, db) in listitems(self._cat):
            prefix = cat + '/' if cat != 'nocat' else ''
            with lock:
                for subkey, entry in iteritems(db):
                    if key not in prefix+subkey:
                        continue
                    # check for removed keys
                    if entry.value is None:
                        continue
                    # check for expired keys
                    op = entry.expired and OP_TELLOLD or OP_TELL
                    if entry.ttl:
                        if ts:
                            ret.add('%r+%s@%s%s%s\n' %
                                    (entry.time, entry.ttl, prefix+subkey,
                                     op, entry.value))
                        else:
                            ret.add(prefix+subkey + op + entry.value + '\n')
                    elif ts:
                        ret.add('%r@%s%s%s\n' % (entry.time, prefix+subkey,
                                                 op, entry.value))
                    else:
                        ret.add(prefix+subkey + op + entry.value + '\n')
        return [''.join(ret)]

    def _read_one_histfile(self, year, monthday, category, subkey):
        fn = path.join(self._basepath, year, monthday, category)
        if not path.isfile(fn):
            return
        with open(fn, 'U') as fd:
            firstline = fd.readline()
            nsplit = 2
            if firstline.startswith('# NICOS cache store file v2'):
                nsplit = 3
            else:
                fd.seek(0, os.SEEK_SET)
            for line in fd:
                if '\x00' in line:
                    self.log.warning('found nullbyte in file %s', fn)
                    continue
                fields = line.rstrip().split(None, nsplit)
                if fields[0] == subkey:
                    time = float(fields[1])
                    value = fields[-1]
                    if value == '-':
                        value = ''
                    yield (time, value)

    def ask_hist(self, key, fromtime, totime):
        try:
            category, subkey = key.rsplit('/', 1)
            category = category.replace('/', '-')
        except ValueError:
            category = 'nocat'
            subkey = key
        if fromtime > totime:
            return
        elif fromtime >= self._midnight:
            days = [(self._year, self._currday)]
        else:
            days = allDays(fromtime, totime)
        # return the first value before the range too
        temp = []
        lastvalue = None
        inrange = False
        for year, monthday in days:
            try:
                for time, value in self._read_one_histfile(year, monthday,
                                                           category, subkey):
                    if fromtime <= time <= totime:
                        if not inrange and lastvalue:
                            temp.append(lastvalue)
                        temp.append('%r@%s=%s\n' % (time, key, value))
                        inrange = True
                        if len(temp) > 100:
                            # bunch up 100 entries at a time
                            yield ''.join(temp)
                            temp = []
                    elif not inrange and value:
                        lastvalue = '%r@%s=%s\n' % (time, key, value)
            except Exception:
                self.log.exception('error reading store file for history query')
        # return at least the last value, if none match the range
        if not inrange and lastvalue is not None:
            temp.append(lastvalue)
        yield ''.join(temp)

    def _clean(self):
        def cleanonce():
            with self._cat_lock:
                for cat, (fd, lock, db) in iteritems(self._cat):
                    with lock:
                        for subkey, entry in iteritems(db):
                            if not entry.value or entry.expired:
                                continue
                            time = currenttime()
                            if entry.ttl and (entry.time + entry.ttl < time):
                                entry.expired = True
                                for client in self._server._connected.values():
                                    client.update(cat + '/' + subkey,
                                                  OP_TELLOLD, entry.value,
                                                  time, None)
                                if fd is None:
                                    fd = self._create_fd(cat)
                                    self._cat[cat][0] = fd
                                fd.write('%s\t%s\t-\t-\n' % (subkey, time))
                                fd.flush()
        while not self._stoprequest:
            sleep(self._long_loop_delay)
            cleanonce()

    def tell(self, key, value, time, ttl, from_client):
        # self.log.debug('updating %s %s', key, value)
        if value is None:
            # deletes cannot have a TTL
            ttl = None
        now = currenttime()
        if time is None:
            time = now
        store_on_disk = True
        if key.endswith(FLAG_NO_STORE):
            key = key[:-len(FLAG_NO_STORE)]
            store_on_disk = False
        with self._cat_lock:
            if now > self._nextmidnight:
                self._rollover()
        try:
            category, subkey = key.rsplit('/', 1)
        except ValueError:
            category = 'nocat'
            subkey = key
        newcats = [category]
        if category in self._rewrites:
            newcats.extend(self._rewrites[category])
        for newcat in newcats:
            with self._cat_lock:
                if newcat not in self._cat:
                    # the first item, fd, is created on demand below
                    self._cat[newcat] = [None, threading.Lock(), {}]
                fd, lock, db = self._cat[newcat]
            update = True
            with lock:
                if subkey in db:
                    entry = db[subkey]
                    if entry.value == value and not entry.expired:
                        # existing entry with the same value: update the TTL
                        # but don't write an update to the history file
                        entry.time = time
                        entry.ttl = ttl
                        update = not store_on_disk
                    elif value is None and entry.expired:
                        # do not delete old value, it is already expired
                        update = not store_on_disk
                if update:
                    db[subkey] = CacheEntry(time, ttl, value)
                    if store_on_disk:
                        if fd is None:
                            fd = self._create_fd(newcat)
                            self._cat[newcat][0] = fd
                        fd.write('%s\t%s\t%s\t%s\n' % (
                            subkey, time,
                            ttl and '-' or (value and '+' or '-'),
                            value or '-'))
                        fd.flush()
            if update and (not ttl or time + ttl > now):
                key = newcat + '/' + subkey
                for client in self._server._connected.values():
                    if client is not from_client:
                        client.update(key, OP_TELL, value or '', time, ttl)
