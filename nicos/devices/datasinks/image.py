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
#
# *****************************************************************************

"""Base Image data sink classes for NICOS."""

from __future__ import absolute_import, division, print_function

from nicos import session
from nicos.core import FINAL, INTERRUPTED, LIVE, Override
from nicos.core.constants import POINT
from nicos.core.data import DataFile, DataSink, DataSinkHandler
from nicos.devices.datasinks import FileSink
from nicos.pycompat import add_metaclass
from nicos.utils import ReaderRegistry, syncFile


class ImageSink(FileSink):
    """Base class for sinks that save arrays to "image" files."""

    parameter_overrides = {
        'subdir': Override(description='Filetype specific subdirectory name '
                           'for the image files'),
        'settypes': Override(default=[POINT])
    }

    def isActiveForArray(self, arraydesc):
        return True

    def isActive(self, dataset):
        if not DataSink.isActive(self, dataset):
            return False
        for det in dataset.detectors:
            arrayinfo = det.arrayInfo()
            if arrayinfo:
                # XXX: support multiple arrays
                return self.isActiveForArray(arrayinfo[0])
        return False


class SingleFileSinkHandler(DataSinkHandler):
    """Provide a convenient base class for writing a single data file.

    Normally, the file consists of a header part and a data part.
    """

    # this is the filetype as transferred to live-view
    filetype = 'raw'

    # set this to True to create the datafile as latest as possible
    defer_file_creation = False

    # set this to True to save only FINAL images
    accept_final_images_only = False

    # DataFile class used for creating the data file (descriptor).
    fileclass = DataFile

    def __init__(self, sink, dataset, detector):
        DataSinkHandler.__init__(self, sink, dataset, detector)
        self._file = None
        self._processArrayInfo(self.detector.arrayInfo())

    def _processArrayInfo(self, arrayinfo):
        # determine which index of the detector value is our data array
        # XXX support more than one array
        arrayinfo = self.detector.arrayInfo()
        if len(arrayinfo) > 1:
            self.log.warning('image sink only supports one array per detector')
        self._arraydesc = arrayinfo[0]

    def _createFile(self, **kwargs):
        if self._file is None:
            self.manager.assignCounter(self.dataset)
            self._file = self.manager.createDataFile(self.dataset,
                                                     self.sink.filenametemplate,
                                                     self.sink.subdir,
                                                     fileclass=self.fileclass,
                                                     **kwargs)
        return self._file

    def prepare(self):
        if not self.defer_file_creation:
            self._createFile()

    def writeHeader(self, fp, metainfo, image):
        """Write the header part of the file (first part).

        Note that *image* is None if defer_file_creation is false, because in
        that case `writeHeader` is called before the image data is available.
        """
        pass

    def writeData(self, fp, image):
        """Write the image data part of the file (second part)."""
        pass

    def _putResult(self, quality, result):
        image = result[1][0]
        if image is None:
            return
        if self.defer_file_creation:
            self._createFile()
            self.writeHeader(self._file, self.dataset.metainfo, image)
        self.writeData(self._file, image)
        syncFile(self._file)
        session.notifyDataFile(self.filetype, self.dataset.uid,
                               self.detector.name, self._file.filepath)

    def putResults(self, quality, results):
        if quality == LIVE:
            return
        if self.accept_final_images_only and \
           quality not in (FINAL, INTERRUPTED):
            return
        if self.detector.name in results:
            result = results[self.detector.name]
            if result is None:
                return
            self._putResult(quality, result)

    def putMetainfo(self, metainfo):
        if not self.defer_file_creation:
            self._file.seek(0)
            self.writeHeader(self._file, self.dataset.metainfo, None)

    def end(self):
        if self._file:
            self._file.close()


class MultipleFileSinkHandler(SingleFileSinkHandler):
    """Provide a convenient base class for writing multiple data files.

    This class creates one data file for each array in ``putResults`` per
    (point) dataset created by a single detector. Arrays are enumerated using
    the **arraynumber** counter type. The **arraynumber** can be used in
    nametemplates as usual.
    """

    def __init__(self, sink, dataset, detector):
        SingleFileSinkHandler.__init__(self, sink, dataset, detector)
        self._files = []

    def _processArrayInfo(self, arrayinfo):
        self._arrayinfo = self.detector.arrayInfo()

    def _putResult(self, quality, result):
        if result[1][0] is None:
            return
        if self.defer_file_creation:
            self._createFile()
        for i, image in enumerate(result[1]):
            fp = self._files[i]
            self.writeHeader(fp, self.dataset.metainfo, image)
            self.writeData(fp, image)
            syncFile(fp)
        session.notifyDataFile(self.filetype, self.dataset.uid,
                               self.detector.name,
                               [fp.filepath for fp in self._files])

    def _createFile(self, **kwargs):
        if self._file is None:
            kwds = dict(kwargs)
            for i in range(len(self._arrayinfo)):
                kwds['additionalinfo'] = {
                    'arraynumber': i + 1
                }
                self._files.append(
                    SingleFileSinkHandler._createFile(self, **kwds))
                self._file = None
        if self._files:
            self._file = self._files[0]
        return self._file

    def putMetainfo(self, metainfo):
        if not self.defer_file_creation:
            for fp in self._files:
                fp.seek(0)
                self.writeHeader(fp, self.dataset.metainfo, None)

    def end(self):
        for fp in self._files:
            fp.close()
        self._files = []  # clear


class ReaderMeta(type):
    """Reader metaclass.

    Metaclass that adds all `Reader` classes to the Reader registry.
    """

    def __new__(mcs, clsname, bases, attrs):
        new_class = type.__new__(mcs, clsname, bases, attrs)
        # Add the notification class to the registry.
        ReaderRegistry.registerReader(new_class)

        return new_class


@add_metaclass(ReaderMeta)
class ImageFileReader(object):
    filetypes = []  # list of (filetype abbreviation, QFileDialog filter str)

    @classmethod
    def fromfile(cls, filename):
        """Reads an Image from `filename` and returns a numpy array with
        correct shape.

        Can raise an error in case the file is unreadable.
        """
        raise NotImplementedError('implement classmethod fromfile')
