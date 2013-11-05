#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2013 by the NICOS contributors (see AUTHORS)
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
#
# *****************************************************************************

"""Class for CASCADE detector measurement and readout."""

import gzip
from math import pi
from time import sleep, time as currenttime

from nicos import session
from nicos.devices.tas import Monochromator
from nicos.core import status, tupleof, listof, oneof, Param, Override, Value, \
     CommunicationError, TimeoutError, NicosError, Readable
from nicos.mira import cascadeclient  # pylint: disable=E0611
from nicos.devices.abstract import ImageStorage, AsyncDetector
from nicos.devices.generic import MultiChannelDetector


class CascadeDetector(AsyncDetector, ImageStorage):

    attached_devices = {
        'master':    (MultiChannelDetector, 'Master to control measurement time'
                      ' in slave mode and to read monitor counts'),
        'mono':      (Monochromator, 'Monochromator device to read out'),
        'sampledet': (Readable, 'Sample-detector distance readout'),
    }

    parameters = {
        'server':       Param('"host:port" of the cascade server to connect to',
                              type=str, mandatory=True, preinit=True),
        'debugmsg':     Param('Whether to print debug messages from the client',
                              type=bool, settable=True, default=False),
        'roi':          Param('Region of interest, given as (x1, y1, x2, y2)',
                              type=tupleof(int, int, int, int),
                              default=(-1, -1, -1, -1), settable=True),
        'mode':         Param('Data acquisition mode (tof or image)',
                              type=oneof('tof', 'image'), settable=True),
        'slave':        Param('Slave mode: start together with master device',
                              type=bool, settable=True),
        'preselection': Param('Current preselection (if not in slave mode)',
                              unit='s', settable=True, type=float),
        'lastcounts':   Param('Counts of the last measurement',
                              type=listof(int), settable=True),
        'lastcontrast': Param('Contrast of the last measurement',
                              type=listof(float), settable=True),
        'monchannel':   Param('Monitor channel to read from master detector',
                              type=int, settable=True),
        'fitfoil':      Param('Foil for contrast fitting', type=int, default=0,
                              settable=True),
        'writexml':     Param('Whether to save files in XML format', type=bool,
                              settable=True, default=True),
        'gziptof':      Param('Whether to compress TOF files with gzip', type=bool,
                              settable=True, default=False),
    }

    parameter_overrides = {
        'fmtstr':   Override(default='roi %s, total %s, file %s'),
    }

    def doPreinit(self, mode):
        if mode != 'simulation':
            self._client = cascadeclient.NicosClient()
            self._padimg = cascadeclient.PadImage()
            self.doReset()

    def doInit(self, mode):
        self._last_preset = self.preselection
        self._started = 0
        AsyncDetector.doInit(self, mode)

        # self._tres is set by doUpdateMode
        self._xres, self._yres = (128, 128)

    def doReset(self):
        self._client.communicate('CMD_kill')
        self._client.disconnect()
        host, port = self.server.split(':')
        port = int(port)
        self.log.info('waiting for CASCADE server restart...')
        for _ in range(4):
            sleep(0.5)
            if self._client.connecttohost(host, port):
                break
        else:
            raise CommunicationError(self, 'could not connect to server')
        if self.slave:
            self._adevs['master'].reset()
        # reset parameters in case the server forgot them
        self.log.info('re-setting to %s mode' % self.mode.upper())
        self.doWriteMode(self.mode)
        self.doWritePreselection(self.preselection)

    def valueInfo(self):
        cvals = (Value(self.name + '.roi', unit='cts', type='counter',
                       errors='sqrt', active=self.roi != (-1, -1, -1, -1),
                       fmtstr='%d'),
                 Value(self.name + '.total', unit='cts', type='counter',
                       errors='sqrt', fmtstr='%d'))
        if self.mode == 'tof':
            cvals = cvals + (
                 Value(self.name + '.c_roi', unit='', type='counter',
                       errors='next', fmtstr='%.4f'),
                 Value(self.name + '.dc_roi', unit='', type='error',
                       fmtstr = '%.4f'),
                 Value(self.name + '.c_tot', unit='', type='counter',
                       errors='next', fmtstr='%.4f'),
                 Value(self.name + '.dc_tot', unit='', type='error',
                       fmtstr = '%.4f'))
        cvals = cvals + (Value(self.name + '.file', type='info', fmtstr='%s'),)
        if self.slave:
            return self._adevs['master'].valueInfo() + cvals
        return cvals

    def presetInfo(self):
        return ['t']

    def doUpdateDebugmsg(self, value):
        if self._mode != 'simulation':
            cascadeclient.GlobalConfig.SetLogLevel(value and 3 or 0)

    def doShutdown(self):
        self._client.disconnect()

    def doStop(self):
        if self.slave:
            self._adevs['master'].stop()
        else:
            reply = str(self._client.communicate('CMD_stop'))
            if reply != 'OKAY':
                self._raise_reply('could not stop measurement', reply)

    def doRead(self, maxage=0):
        if self.mode == 'tof':
            myvalues = self.lastcounts + self.lastcontrast + [self.lastfilename]
        else:
            myvalues = self.lastcounts + [self.lastfilename]
        if self.slave:
            return self._adevs['master'].read(maxage) + myvalues
        return myvalues

    def _getconfig(self):
        cfg = self._client.communicate('CMD_getconfig_cdr')
        if cfg[:4] != 'MSG_':
            self._raise_reply('could not get configuration', cfg)
        return dict(v.split('=') for v in str(cfg[4:]).split(' '))

    def doReadMode(self):
        return self._getconfig()['mode']

    def doWriteMode(self, value):
        reply = self._client.communicate('CMD_config_cdr mode=%s tres=%d' %
            (value, 128 if value == 'tof' else 1))
        if reply != 'OKAY':
            self._raise_reply('could not set mode', reply)

    def doUpdateMode(self, value):
        self._dataprefix = (value == 'image') and 'IMAG' or 'DATA'
        self._datashape = (value == 'image') and (128, 128) or (128, 128, 128)
        self._tres = (value == 'image') and 1 or 128

    def doReadPreselection(self):
        return float(self._getconfig()['time'])

    def doWritePreselection(self, value):
        reply = self._client.communicate('CMD_config_cdr time=%s' % value)
        if reply != 'OKAY':
            self._raise_reply('could not set measurement time', reply)

    def _devStatus(self):
        if not self._client.isconnected():
            return status.ERROR, 'disconnected from server'

    def doSetPreset(self, **preset):
        if preset.get('t'):
            self.preselection = self._last_preset = preset['t']

    def _getFilename(self, counter):
        if self.mode == 'tof':
            return '%08d.tof' % counter
        return '%08d.pad' % counter

    def _startAction(self, **preset):
        self._newFile()
        if self.slave:
            self.preselection = 1000000  # master controls preset
            if preset.get('t'):
                self._last_preset = preset['t']
        elif preset.get('t'):
            self.preselection = self._last_preset = preset['t']
        self.lastcounts = [0, 0]
        self.lastcontrast = [0., 0., 0., 0.]

        config = cascadeclient.GlobalConfig.GetTofConfig()
        config.SetImageWidth(self._xres)
        config.SetImageHeight(self._yres)
        config.SetImageCount(self._tres)
        config.SetPseudoCompression(False)

        sleep(0.005)
        reply = str(self._client.communicate('CMD_start'))
        if reply != 'OKAY':
            self._raise_reply('could not start measurement', reply)
        if self.slave:
            self._adevs['master'].start(**preset)
        self._started = currenttime()

    def _measurementComplete(self):
        if currenttime() - self._started > self._last_preset + 10:
            try:
                self.doStop()
            except NicosError:
                pass
            raise TimeoutError(self, 'measurement not finished within '
                               'selected preset time')
        status = self._client.communicate('CMD_status_cdr')
        if status == '':
            raise CommunicationError(self, 'no response from server')
        #self.log.debug('got status %r' % status)
        status = dict(v.split('=') for v in str(status[4:]).split(' '))
        return status.get('stop', '0') == '1'

    def _duringMeasureAction(self, elapsedtime):
        self._readLiveData(elapsedtime)

    def _afterMeasureAction(self):
        # get final data including all events from detector
        buf = self._readLiveData(self._last_preset, self.lastfilename)
        # and write into measurement file
        def writer(fp, buf):
            if self.gziptof:
                fp = gzip.GzipFile(mode='wb', fileobj=fp)
            # write main data
            fp.write(buf)
            # write separator
            fp.write('\n# begin instrument status\n')
            # write device info() results
            for _, device in sorted(session.devices.iteritems()):
                if device.lowlevel:
                    continue
                for _, key, value in device.info():
                    fp.write('%s_%s : %s\n' % (device, key, value))
            fp.write('# end instrument status\n')
            if self.gziptof:
                fp.close()
        self.log.debug('writing data file to %s' % self.lastfilename)
        self._writeFile(buf, writer=writer)
        # also write as XML file
        if self.mode == 'image' and self.writexml:
            try:
                self._writeXml(buf)
            except Exception:
                self.log.warning('Error saving measurement as XML', exc=1)

    def _measurementFailedAction(self, err):
        self.lastfilename = '<error>'

    def _readLiveData(self, elapsedtime, filename=''):
        # get current data array from detector
        data = self._client.communicate('CMD_readsram')
        if data[:4] != self._dataprefix:
            self._raise_reply('error receiving data from server', data)
        buf = buffer(data, 4)
        # send image to live plots
        session.updateLiveData(
            'cascade', filename, '<u4', self._xres, self._yres,
            self._tres, elapsedtime, buf)
        # determine total and roi counts
        total = self._client.counts(data)
        ctotal, dctotal = 0., 0.
        if self.mode == 'tof':
            fret = self._client.contrast(data, self.fitfoil)
            if fret[0]:
                ctotal = fret[1]
                dctotal = fret[3]
        if self.roi != (-1, -1, -1, -1):
            x1, y1, x2, y2 = self.roi
            roi = self._client.counts(data, x1, x2, y1, y2)
            croi, dcroi = 0., 0.
            if self.mode == 'tof':
                fret = self._client.contrast(data, self.fitfoil, x1, x2, y1, y2)
                if fret[0]:
                    croi = fret[1]
                    dcroi = fret[3]
        else:
            roi = total
            croi, dcroi = ctotal, dctotal
        self.lastcounts = [roi, total]
        self.lastcontrast = [croi, dcroi, ctotal, dctotal]
        return buf

    def _writeXml(self, buf):
        exp = session.experiment
        s, l, _ = exp.createImageFile('mira_cas_%05d.xml', self.subdir, nofile=True)
        xml_fn = l
        self.log.debug('writing XML file to %s' % s)
        tmp = cascadeclient.TmpImage()
        self._padimg.LoadMem(buf, 128*128*4)
        tmp.ConvertPAD(self._padimg)
        mon = self._adevs['master']._adevs['monitors'][self.monchannel - 1]
        tmp.WriteXML(xml_fn, self._adevs['sampledet'].read(),
                     2*pi/self._adevs['mono']._readInvAng(),
                     self._last_preset, mon.read()[0])

    def _raise_reply(self, message, reply):
        if not reply:
            raise CommunicationError(self,
                message + ': empty reply (reset device to reconnect)')
        raise CommunicationError(self, message + ': ' + str(reply[4:]))
