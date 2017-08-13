#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""Qt 4/5 compatibility layer.
"""

# pylint: disable=wildcard-import, unused-import, unused-wildcard-import
# PyQt4.QtCore re-exports the original bin, hex and oct builtins
# pylint: disable=redefined-builtin

if 1:  # pylint: disable=using-constant-test
    import sip
    sip.setapi('QString', 2)
    sip.setapi('QVariant', 2)

    from PyQt4.QtGui import *
    from PyQt4.QtCore import pyqtWrapperType
    from PyQt4.QtCore import *
    from PyQt4 import uic

    try:
        from PyQt4 import QtWebKit
    except (ImportError, RuntimeError):
        QWebView = QWebPage = None
    else:
        QWebView = QtWebKit.QWebView
        QWebPage = QtWebKit.QWebPage

    import nicos.guisupport.gui_rc_qt4

    try:
        from PyQt4.QtCore import QPyNullVariant  # pylint: disable=E0611
    except ImportError:
        class QPyNullVariant(object):
            pass

    propertyMetaclass = pyqtWrapperType