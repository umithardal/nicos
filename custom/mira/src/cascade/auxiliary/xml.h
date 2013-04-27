// *****************************************************************************
// NICOS, the Networked Instrument Control System of the FRM-II
// Copyright (c) 2009-2013 by the NICOS contributors (see AUTHORS)
//
// This program is free software; you can redistribute it and/or modify it under
// the terms of the GNU General Public License as published by the Free Software
// Foundation; either version 2 of the License, or (at your option) any later
// version.
//
// This program is distributed in the hope that it will be useful, but WITHOUT
// ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
// FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
// details.
//
// You should have received a copy of the GNU General Public License along with
// this program; if not, write to the Free Software Foundation, Inc.,
// 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//
// Module authors:
//   Tobias Weber <tweber@frm2.tum.de>
//
// *****************************************************************************

#ifndef __CASCADE_XML__
#define __CASCADE_XML__

#include <string>

/**
 * \brief class for reading xml files
 */
class Xml
{
	private:
		static int s_iInstances;
		static void StartXml();
		static void StopXml();		
	
	protected:
		void *m_pxmldoc;
		void *m_ppathcontext;
		void Clear();

	public:
		Xml();
		virtual ~Xml();
		
		/// Load a XML file
		bool Load(const char* pcFile);

		//----------------------------------------------------------------------
		/// Query values in a given xpath
		int QueryInt(const char* pcXpath, int iDefault=0, bool* pOK=0);
		double QueryDouble(const char* pcXpath, double dDefault=0., bool* pOK=0);
		std::string QueryString(const char* pcXpath, const char* pcDefault, bool* pOK=0);
		//----------------------------------------------------------------------
};

#endif
