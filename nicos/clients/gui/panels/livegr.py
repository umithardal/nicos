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

"""NICOS livewidget with GR."""

from __future__ import absolute_import, division, print_function

import os
from collections import OrderedDict
from os import path
from uuid import uuid4

import numpy
from gr import COLORMAPS as GR_COLORMAPS

from nicos.clients.gui.dialogs.filesystem import FileFilterDialog
from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import enumerateWithProgress, loadUi
from nicos.core.errors import NicosError
from nicos.guisupport.livewidget import DATATYPES, IntegralLiveWidget, \
    LiveWidget, LiveWidget1D
from nicos.guisupport.qt import QActionGroup, QByteArray, QListWidgetItem, \
    QMenu, QPoint, QSizePolicy, QStatusBar, Qt, QToolBar, pyqtSlot
from nicos.guisupport.qtgr import GUIConnector, MouseEvent
from nicos.protocols.cache import cache_load
from nicos.pycompat import iteritems, itervalues, string_types
from nicos.utils import BoundedOrderedDict, ReaderRegistry

COLORMAPS = OrderedDict(GR_COLORMAPS)

FILENAME = Qt.UserRole
FILEFORMAT = Qt.UserRole + 1
FILETAG = Qt.UserRole + 2
FILEUID = Qt.UserRole + 3


class LiveDataPanel(Panel):
    """Provides a generic "detector live view".

    For most instruments, a specific panel must be implemented that takes care
    of the individual live display needs.

    Options:

    * ``instrument`` -- the instrument name that is passed on to the livewidget
      module.
    * ``filetypes`` default[] - List of filename extensions whose content should
      be displayed.
    * ``detectors`` (default [] - list of detector devices whose data should be
      displayed.  If not set data from all configured detectors will be shown.
    * ``cachesize`` (default 20) - Number of entries in the live data cache.
      The live data cache allows to display of previous taken data.
    """

    panelName = 'Live data view'

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        loadUi(self, 'panels/live.ui')

        self._allowed_tags = set()
        self._allowed_detectors = set()
        self._ignore_livedata = False  # ignore livedata, e.g. wrong detector
        self._last_idx = 0
        self._last_tag = None
        self._last_fnames = None
        self._last_format = None
        self._runtime = 0
        self._range_active = False
        self._cachesize = 20
        self._livewidgets = {}  # livewidgets for rois: roi_key -> widget
        self._fileopen_filter = None
        self.widget = None
        self.menu = None

        self.statusBar = QStatusBar(self, sizeGripEnabled=False)
        policy = self.statusBar.sizePolicy()
        policy.setVerticalPolicy(QSizePolicy.Fixed)
        self.statusBar.setSizePolicy(policy)
        self.statusBar.setSizeGripEnabled(False)
        self.layout().addWidget(self.statusBar)

        self.toolbar = QToolBar('Live data')
        self.toolbar.addAction(self.actionOpen)
        self.toolbar.addAction(self.actionPrint)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.actionLogScale)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.actionKeepRatio)
        self.toolbar.addAction(self.actionUnzoom)
        self.toolbar.addAction(self.actionColormap)
        self.toolbar.addAction(self.actionMarkCenter)
        self.toolbar.addAction(self.actionROI)

        self._actions2D = [self.actionROI, self.actionColormap]
        self.setControlsEnabled(False)
        self.set2DControlsEnabled(False)

        # self.widget.setControls(Logscale | MinimumMaximum | BrightnessContrast |
        #                         Integrate | Histogram)

        self.liveitems = []
        self.setLiveItems(1)
        self._livechannel = 0

        self.splitter.setSizes([20, 80])
        self.splitter.restoreState(self.splitterstate)

        if hasattr(self.window(), 'closed'):
            self.window().closed.connect(self.on_closed)
        client.livedata.connect(self.on_client_livedata)
        client.liveparams.connect(self.on_client_liveparams)
        client.connected.connect(self.on_client_connected)
        client.cache.connect(self.on_cache)

        self.rois = {}
        self.detectorskey = None
        # configure instrument specific behavior
        self._instrument = options.get('instrument', '')
        # self.widget.setInstrumentOption(self._instrument)
        # if self._instrument == 'toftof':
        #     self.widget.setAxisLabels('time channels', 'detectors')
        # elif self._instrument == 'imaging':
        #     self.widget.setControls(ShowGrid | Logscale | Grayscale |
        #                             Normalize | Darkfield | Despeckle |
        #                             CreateProfile | Histogram | MinimumMaximum)
        #     self.widget.setStandardColorMap(True, False)
        # configure allowed file types
        supported_filetypes = ReaderRegistry.filetypes()
        opt_filetypes = set(options.get('filetypes', supported_filetypes))
        self._allowed_tags = opt_filetypes & set(supported_filetypes)

        # configure allowed detector device names
        detectors = options.get('detectors')
        if detectors:
            self._allowed_detectors = set(detectors)

        # configure caching
        self._cachesize = options.get('cachesize', self._cachesize)
        if self._cachesize < 1:
            self._cachesize = 1  # always cache the last live image
        self._datacache = BoundedOrderedDict(maxlen=self._cachesize)

    def setLiveItems(self, n):
        nitems = len(self.liveitems)
        if n < nitems:
            nfiles = self.fileList.count()
            for i in range(nitems - 1, n - 1, -1):
                self.liveitems.pop(i)
                self.fileList.takeItem(nfiles - nitems + i)
            if self._livechannel > n:
                self._livechannel = 0 if n > 0 else None
        else:
            for i in range(nitems, n):
                item = QListWidgetItem('<Live #%d>' % (i + 1))
                item.setData(FILENAME, i)
                item.setData(FILEFORMAT, '')
                item.setData(FILETAG, 'live')
                self.fileList.insertItem(self.fileList.count(), item)
                self.liveitems.append(item)
        if n == 1:
            self.liveitems[0].setText('<Live>')
        else:
            self.liveitems[0].setText('<Live #1>')

    def set2DControlsEnabled(self, flag):
        if flag != self.actionKeepRatio.isChecked():
            self.actionKeepRatio.trigger()
        for action in self._actions2D:
            action.setVisible(flag)

    def setControlsEnabled(self, flag):
        for action in self.toolbar.actions():
            action.setEnabled(flag)
        self.actionOpen.setEnabled(True)  # File Open action always available

    def initLiveWidget(self, widgetcls):
        if isinstance(self.widget, widgetcls):
            return

        if self.widget:
            self.widgetLayout.removeWidget(self.widget)
            self.widget.deleteLater()
        self.widget = widgetcls(self)
        # enable/disable controls and set defaults for new livewidget instances
        self.setControlsEnabled(True)
        if isinstance(self.widget, LiveWidget1D):
            self.set2DControlsEnabled(False)
        else:
            self.set2DControlsEnabled(True)
        # apply current settings
        self.widget.setCenterMark(self.actionMarkCenter.isChecked())
        self.widget.logscale(self.actionLogScale.isChecked())
        guiConn = GUIConnector(self.widget.gr)
        guiConn.connect(MouseEvent.MOUSE_MOVE, self.on_mousemove_gr)

        self.menuColormap = QMenu(self)
        self.actionsColormap = QActionGroup(self)
        activeMap = self.widget.getColormap()
        activeCaption = None
        for name, value in iteritems(COLORMAPS):
            caption = name.title()
            action = self.menuColormap.addAction(caption)
            action.setData(caption)
            action.setCheckable(True)
            if activeMap == value:
                action.setChecked(True)
                # update toolButton text later otherwise this may fail
                # depending on the setup and qt versions in use
                activeCaption = caption
            self.actionsColormap.addAction(action)
            action.triggered.connect(self.on_colormap_triggered)
        self.actionColormap.setMenu(self.menuColormap)
        self.widgetLayout.addWidget(self.widget)
        if activeCaption:
            self.toolbar.widgetForAction(self.actionColormap).setText(
                activeCaption)
        detectors = self.client.eval('session.experiment.detectors', [])
        self._register_rois(detectors)

    def loadSettings(self, settings):
        self.splitterstate = settings.value('splitter', '', QByteArray)

    def saveSettings(self, settings):
        settings.setValue('splitter', self.splitter.saveState())
        settings.setValue('geometry', self.saveGeometry())

    def getMenus(self):
        if not self.menu:
            menu = QMenu('&Live data', self)
            menu.addAction(self.actionOpen)
            menu.addAction(self.actionPrint)
            menu.addSeparator()
            menu.addAction(self.actionKeepRatio)
            menu.addAction(self.actionUnzoom)
            menu.addAction(self.actionLogScale)
            menu.addAction(self.actionColormap)
            menu.addAction(self.actionMarkCenter)
            menu.addAction(self.actionROI)
            self.menu = menu
        return [self.menu]

    def _get_all_widgets(self):
        yield self.widget
        for w in itervalues(self._livewidgets):
            yield w

    def getToolbars(self):
        return [self.toolbar]

    def on_mousemove_gr(self, event):
        xyz = None
        if event.getWindow():  # inside plot
            xyz = self.widget.getZValue(event)
        if xyz:
            fmt = '(%g, %g)'  # x, y data 1D integral plots
            if len(xyz) == 3:
                fmt += ': %g'  # x, y, z data for 2D image plot
            self.statusBar.showMessage(fmt % xyz)
        else:
            self.statusBar.clearMessage()

    def on_actionColormap_triggered(self):
        w = self.toolbar.widgetForAction(self.actionColormap)
        m = self.actionColormap.menu()
        if m:
            m.popup(w.mapToGlobal(QPoint(0, w.height())))

    def on_colormap_triggered(self):
        action = self.actionsColormap.checkedAction()
        name = action.data()
        for widget in self._get_all_widgets():
            widget.setColormap(COLORMAPS[name.upper()])
        self.toolbar.widgetForAction(
            self.actionColormap).setText(name.title())

    def _getLiveWidget(self, roi):
        return self._livewidgets.get(roi + '/roi', None)

    def showRoiWindow(self, roikey):
        key = roikey + '/roi'
        widget = self._getLiveWidget(roikey)
        region = self.widget._rois[key]
        if not widget:
            widget = LiveWidget(None)
            widget.setWindowTitle(roikey)
            widget.setColormap(self.widget.getColormap())
            widget.setCenterMark(self.actionMarkCenter.isChecked())
            widget.logscale(self.actionLogScale.isChecked())
            widget.gr.setAdjustSelection(False)  # don't use adjust on ROIs
            for name, roi in iteritems(self.rois):
                widget.setROI(name, roi)
            width = max(region.x) - min(region.x)
            height = max(region.y) - min(region.y)
            if width > height:
                dwidth = 500
                dheight = 500 * height // width
            else:
                dheight = 500
                dwidth = 500 * width // height
            widget.resize(dwidth, dheight)
            widget.closed.connect(self.on_roiWindowClosed)
        widget.setWindowForRoi(region)
        widget.update()
        widget.show()
        widget.activateWindow()
        self._livewidgets[key] = widget

    def closeRoiWindow(self, roi):
        widget = self._getLiveWidget(roi)
        if widget:
            widget.close()

    def on_closed(self):
        for w in self._livewidgets.values():
            w.close()

    def _register_rois(self, detectors):
        self.rois.clear()
        self.actionROI.setVisible(False)
        self.menuROI = QMenu(self)
        self.actionsROI = QActionGroup(self)
        self.actionsROI.setExclusive(False)
        for detname in detectors:
            self.log.debug('checking rois for detector \'%s\'', detname)
            for tup in self.client.eval(detname + '.postprocess', ''):
                roi = tup[0]
                cachekey = roi + '/roi'
                # check whether or not this is a roi (cachekey exists).
                keyval = self.client.getCacheKey(cachekey)
                if keyval:
                    self.on_roiChange(cachekey, keyval[1])
                    self.log.debug('register roi: %s', roi)
                    # create roi menu
                    action = self.menuROI.addAction(roi)
                    action.setData(roi)
                    action.setCheckable(True)
                    self.actionsROI.addAction(action)
                    action.triggered.connect(self.on_roi_triggered)
                    self.actionROI.setMenu(self.menuROI)
                    self.actionROI.setVisible(True)

    def on_actionROI_triggered(self):
        w = self.toolbar.widgetForAction(self.actionROI)
        self.actionROI.menu().popup(w.mapToGlobal(QPoint(0, w.height())))

    def on_roi_triggered(self):
        action = self.sender()
        roi = action.data()
        if action.isChecked():
            self.showRoiWindow(roi)
        else:
            self.closeRoiWindow(roi)

    def on_roiWindowClosed(self):
        widget = self.sender()
        if widget:
            key = None
            for key, w in iteritems(self._livewidgets):
                if w == widget:
                    self.log.debug('delete roi: %s', key)
                    del self._livewidgets[key]
                    break
            if key:
                roi = key.rsplit('/', 1)[0]
                for action in self.actionsROI.actions():
                    if action.data() == roi:
                        action.setChecked(False)
                        self.log.debug('uncheck roi: %s', roi)

    def on_roiChange(self, key, value):
        self.log.debug('on_roiChange: %s %s', key, (value,))
        self.rois[key] = value
        for widget in self._get_all_widgets():
            widget.setROI(key, value)
        widget = self._livewidgets.get(key, None)
        if widget:
            widget.setWindowForRoi(self.widget._rois[key])

    def on_cache(self, data):
        _time, key, _op, svalue = data
        try:
            value = cache_load(svalue)
        except ValueError:
            value = None
        if key in self.rois:
            self.on_roiChange(key, value)
        elif key == self.detectorskey and self.widget:
            self._register_rois(value)

    def on_client_connected(self):
        self.client.tell('eventunmask', ['livedata', 'liveparams'])
        datapath = self.client.eval('session.experiment.datapath', '')
        if not datapath or not path.isdir(datapath):
            return
        if self._instrument == 'imaging':
            for fn in sorted(os.listdir(datapath)):
                if fn.endswith('.fits'):
                    self.add_to_flist(path.join(datapath, fn), '', 'fits',
                                      False)
        self.detectorskey = (self.client.eval('session.experiment.name')
                             + '/detlist').lower()

    def on_client_liveparams(self, params):
        tag, uid, det, fname, dtype, nx, ny, nz, runtime = params
        # TODO: remove compatibility code
        if isinstance(fname, string_types):
            fname, nx, ny, nz = [fname], [nx], [ny], [nz]

        if self._allowed_detectors and det not in self._allowed_detectors:
            self._ignore_livedata = True
            return
        self._ignore_livedata = False
        self._runtime = runtime
        self._last_uid = uid
        if dtype:
            self.setLiveItems(len(fname))
            self._last_fnames = None
            normalized_type = numpy.dtype(dtype).str
            if normalized_type not in DATATYPES:
                self._last_format = None
                self.log.warning('Unsupported live data format: %s', (params,))
                return
            self._last_format = normalized_type
        elif fname:
            self._last_fnames = fname
            self._last_format = None
        self._last_tag = tag.lower()
        self._nx = nx
        self._ny = ny
        self._nz = nz
        self._last_idx = 0

    def _initLiveWidget(self, array):
        """Initialize livewidget based on array's shape"""
        if len(array.shape) == 1:
            widgetcls = LiveWidget1D
        else:
            widgetcls = IntegralLiveWidget
        self.initLiveWidget(widgetcls)

    def setData(self, array, uid=None, display=True):
        """Dispatch data array to corresponding live widgets.
        Cache array based on uid parameter. No caching if uid is ``None``.
        """
        if uid:
            if uid not in self._datacache:
                self.log.debug('add to cache: %s', uid)
            self._datacache[uid] = array
        if display:
            self._initLiveWidget(array)
            for widget in self._get_all_widgets():
                widget.setData(array)

    def setDataFromFile(self, filename, tag, uid=None, display=True):
        """Load data array from file and dispatch to live widgets using
        ``setData``. Do not use caching if uid is ``None``.
        """
        try:
            array = ReaderRegistry.getReaderCls(tag).fromfile(filename)
        except KeyError:
            raise NicosError('Unsupported fileformat %r' % tag)
        if array is not None:
            self.setData(array, uid, display=display)
        else:
            raise NicosError('Cannot read file %r' % filename)

    def on_client_livedata(self, data):
        if self._ignore_livedata:  # ignore all live events
            return

        idx = self._last_idx  # 0 <= array number < n
        self._last_idx += 1
        # check for allowed tags but always allow live data
        if self._last_tag in self._allowed_tags or self._last_tag == 'live':
            # pylint: disable=len-as-condition
            if len(data) and self._last_format:
                # we got live data with a specified format
                uid = str(self._last_uid) + '-' + str(idx)
                array = numpy.frombuffer(data, self._last_format)
                if self._nz[idx] > 1:
                    array = array.reshape((self._nz[idx], self._ny[idx],
                                           self._nx[idx]))
                elif self._ny[idx] > 1:
                    array = array.reshape((self._ny[idx], self._nx[idx]))
                # update display for selected live channel, just cache
                # otherwise
                self.setData(array, uid, display=(idx == self._livechannel))
                self.liveitems[idx].setData(FILEUID, uid)
            else:
                # we got no live data, but a filename with the data
                # filename corresponds to full qualififed path here
                for i, filename in enumerate(self._last_fnames):
                    uid = str(self._last_uid) + '-' + str(i)
                    self.add_to_flist(filename, self._last_format,
                                      self._last_tag, uid)
                    try:
                        # update display for selected live channel, just cache
                        # otherwise
                        self.setDataFromFile(filename,
                                             self._last_tag,
                                             uid,
                                             display=(i == self._livechannel))
                    except Exception as e:
                        if uid in self._datacache:
                            # image is already cached
                            # suppress error message for cached image
                            self.log.debug(e)
                        else:
                            # image is not cached and could not be loaded
                            self.log.exception(e)

    def remove_obsolete_cached_files(self):
        """Removes outdated cached files from the file list or set cached flag
        to False if the file is still available on the filesystem.
        """
        cached_item_rows = []
        for row in range(self.fileList.count()):
            item = self.fileList.item(row)
            if item.data(FILEUID):
                cached_item_rows.append(row)
        if len(cached_item_rows) > self._cachesize:
            for row in cached_item_rows[0:-self._cachesize]:
                item = self.fileList.item(row)
                self.log.debug('remove from cache %s %s',
                               item.data(FILEUID), item.data(FILENAME))
                if path.isfile(item.data(FILENAME)):
                    item.setData(FILEUID, None)
                else:
                    self.fileList.takeItem(row)

    def add_to_flist(self, filename, fformat, ftag, uid=None, scroll=True):
        shortname = path.basename(filename)
        item = QListWidgetItem(shortname)
        item.setData(FILENAME, filename)
        item.setData(FILEFORMAT, fformat)
        item.setData(FILETAG, ftag)
        item.setData(FILEUID, uid)
        self.fileList.insertItem(self.fileList.count() - len(self.liveitems),
                                 item)
        if uid:
            self.remove_obsolete_cached_files()
        if scroll:
            self.fileList.scrollToBottom()
        return item

    def on_fileList_itemClicked(self, item):
        if item is None:
            return

        fname = item.data(FILENAME)
        ftag = item.data(FILETAG)
        if item in self.liveitems and ftag == 'live':  # show live image
            self._livechannel = int(fname)
            fname = None
            self.log.debug("set livechannel: %d", self._livechannel)
        else:
            self._livechannel = None
            self.log.debug("no direct display")

        uid = item.data(FILEUID)
        if uid:  # show image from cache
            array = self._datacache.get(uid, None)
            if array is not None and array.size:
                self.setData(array)
                return
        if fname:
            # show image from file
            self.setDataFromFile(fname, ftag)

    def on_fileList_currentItemChanged(self, item, previous):
        self.on_fileList_itemClicked(item)

    @pyqtSlot()
    def on_actionOpen_triggered(self):
        """Open image file using registered reader classes."""
        ftypes = {ffilter: ftype
                  for ftype, ffilter in ReaderRegistry.filefilters()}
        fdialog = FileFilterDialog(self, "Open data files", "",
                                   ";;".join(ftypes.keys()))
        if self._fileopen_filter:
            fdialog.selectNameFilter(self._fileopen_filter)
        if fdialog.exec_() == fdialog.Accepted:
            self._fileopen_filter = fdialog.selectedNameFilter()
            tag = ftypes[self._fileopen_filter]
            files = fdialog.selectedFiles()
            if files:
                def _cacheFile(fn, tag):
                    uid = uuid4()
                    # setDataFromFile may raise an `NicosException`, e.g.
                    # if the file cannot be opened.
                    self.setDataFromFile(fn, tag, uid, display=False)
                    return self.add_to_flist(fn, None, tag, uid)

                # load and display first item
                f = files.pop(0)
                self.fileList.setCurrentItem(_cacheFile(f, tag))
                cachesize = self._cachesize - 1
                # add first `cachesize` files to cache
                for _, f in enumerateWithProgress(files[:cachesize],
                                                  "Loading data files...",
                                                  parent=fdialog):
                    _cacheFile(f, tag)
                # add further files to file list (open on request/itemClicked)
                for f in files[cachesize:]:
                    self.add_to_flist(f, None, tag)

    @pyqtSlot()
    def on_actionUnzoom_triggered(self):
        self.widget.unzoom()

    @pyqtSlot()
    def on_actionPrint_triggered(self):
        self.widget.printDialog()

    @pyqtSlot()
    def on_actionLogScale_triggered(self):
        for widget in self._get_all_widgets():
            widget.logscale(self.actionLogScale.isChecked())

    @pyqtSlot()
    def on_actionMarkCenter_triggered(self):
        flag = self.actionMarkCenter.isChecked()
        for widget in self._get_all_widgets():
            widget.setCenterMark(flag)

    @pyqtSlot()
    def on_actionKeepRatio_triggered(self):
        self.widget.gr.setAdjustSelection(self.actionKeepRatio.isChecked())
