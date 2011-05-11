#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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
# *****************************************************************************

"""
NICOS PANDA Experiment.
"""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import os
import time
from os import path

from nicos import session
from nicos.utils import disableDirectory, enableDirectory, ensureDirectory
from nicos.device import Device, Param
from nicos.errors import UsageError
from nicos.experiment import Experiment, queryCycle


class PandaExperiment(Experiment):

    parameters = {
        'cycle': Param('Current reactor cycle', type=str, settable=True),
    }

    def _expdir(self, suffix):
        return '/data/exp/' + suffix

    def new(self, proposal, title=None, **kwds):
        # panda-specific handling of proposal number
        if isinstance(proposal, int):
            proposal = 'p%s' % proposal
        if proposal in ('template', 'current'):
            raise UsageError(self, 'The proposal names "template" and "current"'
                             ' are reserved and cannot be used')

        try:
            old_proposal = os.readlink(self._expdir('current'))
        except Exception:
            if path.exists(self._expdir('current')):
                self.printerror('"current" link to old experiment dir exists '
                                'but cannot be read', exc=1)
            else:
                self.printwarning('no old experiment dir is currently set',
                                  exc=1)
        else:
            if old_proposal.startswith('p'):
                disableDirectory(self._expdir(old_proposal))
            os.unlink(self._expdir('current'))

        # query new cycle
        if 'cycle' not in kwds:
            if self._propdb:
                cycle, started = queryCycle(self._propdb)
                kwds['cycle'] = cycle
            else:
                self.printerror('cannot query reactor cycle, please give a '
                                '"cycle" keyword to this function')
        self.cycle = kwds['cycle']

        # checks are done, set the new experiment
        Experiment.new(self, proposal, title)

        # fill proposal info from database
        if proposal.startswith('p'):
            try:
                propnumber = int(proposal[1:])
            except ValueError:
                pass
            else:
                self._fillProposal(propnumber)

        # create new data path and expand templates
        exp_datapath = self._expdir(proposal)
        ensureDirectory(exp_datapath)
        enableDirectory(exp_datapath)
        os.symlink(proposal, self._expdir('current'))

        ensureDirectory(path.join(exp_datapath, 'scripts'))
        self.scriptdir = path.join(new_datapath, 'scripts')

        self._handleTemplates(proposal, kwds)

        self.datapath = [
            exp_datapath,
            '/data/%s/cycle_%s' % (time.strftime('%Y'), self.cycle),
        ]

    def _handleTemplates(self, proposal, kwds):
        pass

    def finish(self):
        pass
