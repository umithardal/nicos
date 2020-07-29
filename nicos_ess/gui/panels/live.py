# -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************

from nicos.clients.gui.panels.live import LiveDataPanel as DefaultLiveDataPanel
from nicos.guisupport.qt import QToolBar

from nicos_ess.gui.panels import get_icon


class LiveDataPanel(DefaultLiveDataPanel):
    def __init__(self, parent, client, options):
        DefaultLiveDataPanel.__init__(self, parent, client, options)
        self.toolbar = self.createPanelToolbar()
        self.layout().setMenuBar(self.toolbar)
        self.set_icons()

    def createPanelToolbar(self):
        toolbar = QToolBar('Live data')
        toolbar.addAction(self.actionOpen)
        toolbar.addAction(self.actionPrint)
        toolbar.addSeparator()
        toolbar.addAction(self.actionLogScale)
        toolbar.addSeparator()
        toolbar.addAction(self.actionKeepRatio)
        toolbar.addAction(self.actionUnzoom)
        toolbar.addAction(self.actionColormap)
        toolbar.addAction(self.actionMarkCenter)
        toolbar.addAction(self.actionROI)
        return toolbar

    def set_icons(self):
        self.actionPrint.setIcon(get_icon('print-24px.svg'))
        self.actionPDF.setIcon(get_icon('save-24px.svg'))
        self.actionUnzoom.setIcon(get_icon('zoom_out-24px.svg'))
        self.actionOpen.setIcon(get_icon('folder_open-24px.svg'))

    def getToolbars(self):
        return []