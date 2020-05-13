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

"""Data sinks to copy some config files into data directories for QMesyDAQ type
detectors.
"""

from __future__ import absolute_import, division, print_function

import shutil
from os import path

from nicos.core import DataSinkHandler, Override, Param
from nicos.core.params import absolute_path

from nicos_mlz.devices.qmesydaqsinks import QMesyDAQSink


class CopySinkHandler(DataSinkHandler):

    _target = None

    def prepare(self):
        self.manager.assignCounter(self.dataset)
        self._datafile = self.manager.createDataFile(
            self.dataset, self.sink.filenametemplate, self.sink.subdir,
            nomeasdata=True)
        self._target = self._datafile.name
        self._datafile.close()

    def end(self):
        if self._target is None:  # prepare() not called
            return
        image = self.detector._attached_images[0]
        if not hasattr(image, '_taco_guard'):
            return
        shutil.copy(path.join(self.sink.path, self._read_source(image)),
                    self._target)

    def _read_source(self, image):
        return image._taco_guard(image._dev.deviceQueryResource,
                                 self.sink.source)


class CopySink(QMesyDAQSink):

    parameters = {
        'source': Param('Resource name containing the source file name',
                        type=str, mandatory=True, settable=False,
                        ),
        'path': Param('Directory where the source file is stored',
                      type=absolute_path, mandatory=True, settable=False,
                      ),
    }

    parameter_overrides = {
        'filenametemplate': Override(mandatory=False, userparam=False,
                                     default=['COPY_%(pointcounter)07d.mcfg']),
    }

    handlerclass = CopySinkHandler
