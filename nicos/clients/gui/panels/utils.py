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

"""Support for "auxiliary" windows containing panels."""

from __future__ import absolute_import, division, print_function

from nicos.clients.gui.config import docked, hbox, hsplit, panel, tabbed, \
    vbox, vsplit
from nicos.clients.gui.panels import Panel
from nicos.clients.gui.panels.boxed import Boxed, HorizontalBoxed, \
    VerticalBoxed
from nicos.clients.gui.panels.splitter import HorizontalSplitter, \
    VerticalSplitter
from nicos.clients.gui.panels.tabwidget import TearOffTabWidget
from nicos.guisupport.qt import QDockWidget, QSplitter, Qt, QTabWidget
from nicos.utils import importString


def createPanel(item, window, menuwindow, topwindow, log):
    try:
        cls = importString(item.clsname)
    except Exception:
        log.exception('Could not import class %s to create panel', item.clsname)
        return None
    log.debug('creating panel: %s', item.clsname)
    p = cls(menuwindow, window.client, item.options or {})
    window.addPanel(p)
    topwindow.addPanel(p, False)

    for toolbar in p.getToolbars():
        # this helps for serializing window state
        toolbar.setObjectName(toolbar.windowTitle())
        if hasattr(menuwindow, 'toolBarWindows'):
            menuwindow.insertToolBar(menuwindow.toolBarWindows, toolbar)
        else:
            menuwindow.addToolBar(toolbar)
        toolbar.setVisible(False)
    for menu in p.getMenus():
        if hasattr(menuwindow, 'menuWindows'):
            p.actions.update((
            menuwindow.menuBar().insertMenu(menuwindow.menuWindows.menuAction(),
                menu),))
        else:
            p.actions.update((menuwindow.menuBar().addMenu(menu),))

    p.setCustomStyle(window.user_font, window.user_color)
    if window.client.isconnected and hasattr(p, 'on_client_connected'):
        p.on_client_connected()
    return p


def createVerticalSplitter(item, window, menuwindow, topwindow, log):
    return VerticalSplitter(item, window, menuwindow, topwindow)


def createHorizontalSplitter(item, window, menuwindow, topwindow, log):
    return HorizontalSplitter(item, window, menuwindow, topwindow)


def createDockedWidget(item, window, menuwindow, topwindow, log):
    dockPosMap = {'left': Qt.LeftDockWidgetArea,
                  'right': Qt.RightDockWidgetArea, 'top': Qt.TopDockWidgetArea,
                  'bottom': Qt.BottomDockWidgetArea}

    mainitem, dockitems = item
    main = createWindowItem(mainitem, window, menuwindow, topwindow, log)
    for title, ditem in dockitems:
        dw = QDockWidget(title, window)
        # prevent closing the dock widget
        dw.setFeatures(
            QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        # make the dock title bold
        dw.setStyleSheet('QDockWidget { font-weight: bold; }')
        dw.setObjectName(title)
        sub = createWindowItem(ditem, window, menuwindow, topwindow, log)
        if isinstance(sub, Panel):
            sub.hideTitle()
        dw.setWidget(sub)
        dw.setContentsMargins(6, 6, 6, 6)
        dockPos = ditem.options.get('dockpos', 'left')
        if dockPos not in dockPosMap:
            log.warning('Illegal dockpos specification %s for panel %r',
                        dockPos, title)
            dockPos = 'left'
        menuwindow.addDockWidget(dockPosMap[dockPos], dw)
    return main


def createTabWidget(item, window, menuwindow, topwindow, log):
    return TearOffTabWidget(item, window, menuwindow)


def createVerticalBoxed(item, window, menuwindow, topwindow, log):
    return VerticalBoxed(item, window, menuwindow, topwindow)


def createHorizontalBoxed(item, window, menuwindow, topwindow, log):
    return HorizontalBoxed(item, window, menuwindow, topwindow)


def createWindowItem(item, window, menuwindow, topwindow, log):
    if isinstance(item, panel):
        return createPanel(item, window, menuwindow, topwindow, log)
    elif isinstance(item, hsplit):
        return createHorizontalSplitter(item, window, menuwindow, topwindow,
                                        log)
    elif isinstance(item, vsplit):
        return createVerticalSplitter(item, window, menuwindow, topwindow, log)
    elif isinstance(item, tabbed):
        return createTabWidget(item, window, menuwindow, topwindow, log)
    elif isinstance(item, docked):
        return createDockedWidget(item, window, menuwindow, topwindow, log)
    elif isinstance(item, vbox):
        return createVerticalBoxed(item, window, menuwindow, topwindow, log)
    elif isinstance(item, hbox):
        return createHorizontalBoxed(item, window, menuwindow, topwindow, log)


def showPanel(panel):
    """Ensure that the given panel is visible in its window."""
    widget = panel
    parents = []
    while 1:
        parent = widget.parent()
        if parent is None:
            # reached toplevel!
            break
        elif isinstance(parent, QTabWidget):
            # tab widget: select tab (it is wrapped in a QStackedWidget)
            index = parent.indexOf(parents[-2])
            parent.setCurrentIndex(index)
        elif isinstance(parent, (QSplitter, Boxed)):
            # splitter: make sure the widget is not collapsed
            index = parent.indexOf(widget)
            sizes = parent.sizes()
            if sizes[index] == 0:
                sizes[index] = sum(sizes)
                parent.setSizes(sizes)
        parents.append(parent)
        widget = parent
    panel.activateWindow()
