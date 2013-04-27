﻿// *****************************************************************************
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
// Cascade sub dialogs

#include "../dialogs/cascadedialogs.h"
#include "../main/cascadewidget.h"
#include "../auxiliary/helper.h"
#include "../auxiliary/logger.h"
#include "../auxiliary/gc.h"
#include "../config/globals.h"

#include <stdio.h>
#include <sstream>
#include <fstream>
#include <algorithm>

#include <QVariant>
#include <QMenu>
#include <QFileDialog>
#include <QDir>
#include <QtGui/QMessageBox>
#include <qprinter.h>
#include <qprintdialog.h>

#include "cascadedialogs_pad.cpp"
#include "cascadedialogs_tof.cpp"
#include "cascadedialogs_server.cpp"



// ************************* Roi-Dlg *******************************************
RoiDlg::RoiDlg(CascadeWidget *pParent) : QDialog(pParent),
										 m_pwidget(pParent), m_pRoi(0), m_iCurrentItem(0)
{
	setupUi(this);

	connect(listRois, SIGNAL(itemSelectionChanged()),
			this, SLOT(ItemSelected()));
	connect(tableParams, SIGNAL(itemChanged(QTableWidgetItem *)),
			this, SLOT(ValueChanged(QTableWidgetItem *)));
	connect(btnDelete, SIGNAL(clicked()), this, SLOT(DeleteItem()));
	connect(btnCopy, SIGNAL(clicked()), this, SLOT(CopyItem()));
	connect(btnFit, SIGNAL(clicked()), this, SLOT(Fit()));


	//--------------------------------------------------------------------------
	QAction *actionNewRect = new QAction("Rectangle", this);
	QAction *actionNewCircle = new QAction("Circle", this);
	QAction *actionNewEllipse = new QAction("Ellipse", this);
	QAction *actionNewCircleRing = new QAction("Circle Ring", this);
	QAction *actionNewCircleSeg = new QAction("Circle Segment", this);

	QMenu *pMenu = new QMenu(this);
	pMenu->addAction(actionNewRect);
	pMenu->addAction(actionNewCircle);
	pMenu->addAction(actionNewEllipse);
	pMenu->addAction(actionNewCircleRing);
	pMenu->addAction(actionNewCircleSeg);

	connect(actionNewRect, SIGNAL(triggered()), this, SLOT(NewRect()));
	connect(actionNewCircle, SIGNAL(triggered()), this, SLOT(NewCircle()));
	connect(actionNewEllipse, SIGNAL(triggered()), this, SLOT(NewEllipse()));
	connect(actionNewCircleRing, SIGNAL(triggered()), this, SLOT(NewCircleRing()));
	connect(actionNewCircleSeg, SIGNAL(triggered()), this, SLOT(NewCircleSeg()));

	btnAdd->setMenu(pMenu);
	//--------------------------------------------------------------------------

	connect(buttonBox, SIGNAL(clicked(QAbstractButton*)),
			m_pwidget, SLOT(RoiDlgAccepted(QAbstractButton*)));
}

RoiDlg::~RoiDlg() { Deinit(); }

// an item (e.g. "circle", "rectangle", ... has been selected)
void RoiDlg::ItemSelected()
{
	if(!m_pRoi) return;

	m_iCurrentItem = listRois->currentRow();

	if(m_iCurrentItem<0 || m_iCurrentItem >= m_pRoi->GetNumElements())
		return;

	RoiElement& elem = m_pRoi->GetElement(m_iCurrentItem);

	tableParams->setRowCount(elem.GetParamCount());
	tableParams->setColumnCount(2);

	for(int iParam=0; iParam<elem.GetParamCount(); ++iParam)
	{
		std::string strParamName = elem.GetParamName(iParam);
		double dParamValue = elem.GetParam(iParam);

		std::ostringstream ostrValue;
		ostrValue << dParamValue;

		QTableWidgetItem *pItemName =
								new QTableWidgetItem(strParamName.c_str());
		pItemName->setFlags(pItemName->flags() & ~Qt::ItemIsEditable);
		tableParams->setItem(iParam, 0, pItemName);

		QTableWidgetItem *pItemValue =
								new QTableWidgetItem(ostrValue.str().c_str());

		pItemValue->setData(Qt::UserRole, iParam);
		pItemValue->setData(Qt::UserRole+1, 1);		// flag 'editable'

		//pItemValue->setData(Qt::UserRole, QVariant::fromValue(pvElem));
		tableParams->setItem(iParam, 1, pItemValue);
	}
}

// a property of the selected item has changed
void RoiDlg::ValueChanged(QTableWidgetItem* pItem)
{
	if(!m_pRoi) return;

	// only edit if this flag is set
	if(pItem->data(Qt::UserRole+1).value<int>() != 1)
		return;

	if(m_iCurrentItem<0 || m_iCurrentItem >= m_pRoi->GetNumElements())
		return;
	RoiElement& elem = m_pRoi->GetElement(m_iCurrentItem);

	QVariant var = pItem->data(Qt::UserRole);
	int iParam = var.value<int>();

	bool bOk = true;
	double dVal = pItem->text().toDouble(&bOk);
	if(!bOk)
	{	// reset to original value
		QString strOldVal;
		strOldVal.setNum(elem.GetParam(iParam));
		pItem->setText(strOldVal);
	}
	else
	{	// accept new value
		elem.SetParam(iParam,dVal);
	}
}

void RoiDlg::CopyItem()
{
	if(!m_pRoi) return;

	if(m_iCurrentItem<0 || m_iCurrentItem >= m_pRoi->GetNumElements())
		return;

	RoiElement& elem = m_pRoi->GetElement(m_iCurrentItem);
	NewElement(elem.copy());
}

void RoiDlg::Fit()
{
	if(!m_pwidget)
		return;

	TmpImage tmpimg;
	if(m_pwidget->IsTofLoaded())
		tmpimg = m_pwidget->GetTof()->GetOverview();
	else
		tmpimg.ConvertPAD(m_pwidget->GetPad());

	double dAmp=0., dCenterX=0., dCenterY=0., dSpreadX=0., dSpreadY=0.;
	bool bOk = tmpimg.FitGaussian(dAmp,dCenterX,dCenterY,dSpreadX,dSpreadY);

	if(bOk)
	{
		std::ostringstream ostr;
		ostr << "amp=" << dAmp << ", x=" << dCenterX << ", y="<<dCenterY
							   << ", sx=" << dSpreadX << ", sy=" << dSpreadY;

		labelFit->setText(ostr.str().c_str());
	}
	else
	{
		labelFit->setText("No valid Gaussian fit found.");
	}
}

void RoiDlg::NewElement(RoiElement* pNewElem)
{
	if(!m_pRoi) return;

	int iPos = m_pRoi->add(pNewElem);
	new QListWidgetItem(m_pRoi->GetElement(iPos).GetName().c_str(), listRois);

	listRois->setCurrentRow(iPos);
	checkBoxUseRoi->setCheckState(Qt::Checked);
}

void RoiDlg::NewCircle() { NewElement(new RoiCircle); }
void RoiDlg::NewEllipse() { NewElement(new RoiEllipse); }
void RoiDlg::NewCircleRing() { NewElement(new RoiCircleRing); }
void RoiDlg::NewCircleSeg() { NewElement(new RoiCircleSegment); }
void RoiDlg::NewRect() { NewElement(new RoiRect); }

void RoiDlg::DeleteItem()
{
	if(!m_pRoi) return;

	if(m_iCurrentItem<0 || m_iCurrentItem >= m_pRoi->GetNumElements())
		return;

	int iCurItem = m_iCurrentItem;

	QListWidgetItem* pItem = listRois->item(iCurItem);
	if(pItem)
	{
		tableParams->setRowCount(0);

		delete pItem;
		m_pRoi->DeleteElement(iCurItem);

		m_iCurrentItem = listRois->currentRow();
	}

	if(m_pRoi->GetNumElements()==0)
		checkBoxUseRoi->setCheckState(Qt::Unchecked);
}

void RoiDlg::ClearList()
{
	listRois->clear();
}

void RoiDlg::SetRoi(const Roi* pRoi)
{
	ClearList();

	if(m_pRoi)
		delete m_pRoi;

	m_pRoi = new Roi(*pRoi);

	// add all roi elements to list
	for(int i=0; i<m_pRoi->GetNumElements(); ++i)
	{
		new QListWidgetItem(m_pRoi->GetElement(i).GetName().c_str(), listRois);
	}

	if(m_pRoi->GetNumElements() > 0)
		listRois->setCurrentRow(0);
}

const Roi* RoiDlg::GetRoi(void) const
{
	return m_pRoi;
}

void RoiDlg::Deinit()
{
	if(m_pRoi)
		delete m_pRoi;
}

// *****************************************************************************





// ******************* Browse Dialog *******************************************

BrowseDlg::BrowseDlg(CascadeWidget *pParent)
			: QDialog(pParent), m_pwidget(pParent)
{
	setupUi(this);
	progressBar->setVisible(false);

	connect(btnBrowse, SIGNAL(clicked()),
			this, SLOT(SelectDir()));
	connect(listFiles,
			SIGNAL(currentItemChanged( QListWidgetItem *, QListWidgetItem *)),
			this, SLOT(SelectedFile()));
	connect(btnRefresh, SIGNAL(clicked()),
			this, SLOT(SetDir()));

	SetDir();
}

BrowseDlg::~BrowseDlg()
{}

void BrowseDlg::SetDir()
{	
	QString strDir(GlobalConfig::GetCurDir().c_str());

	listFiles->clear();
	labDir->setText(strDir);

	QDir dir(strDir);
	dir.setFilter(QDir::Files | QDir::Hidden);

	QStringList namefilters;
	namefilters << "*.pad" << "*.tof" << "*.PAD" << "*.TOF";
	dir.setNameFilters(namefilters);

	QFileInfoList filelist = dir.entryInfoList();

	progressBar->setValue(0);
	progressBar->setMaximum(filelist.size());
	progressBar->setVisible(true);

	for(int iFile=0; iFile<filelist.size(); ++iFile)
	{
		QFileInfo fileinfo = filelist.at(iFile);
		new QListWidgetItem(fileinfo.fileName(), listFiles);

		progressBar->setValue(iFile+1);
	}

	progressBar->setVisible(false);
}

void BrowseDlg::SelectDir()
{
	QString strDir = QFileDialog::getExistingDirectory(
				this,
				"Select Directory",
				QString(GlobalConfig::GetCurDir().c_str()),
				QFileDialog::ShowDirsOnly);

	if(strDir == "")
		return;

	GlobalConfig::SetCurDir(strDir.toAscii().data());
	SetDir();
}

void BrowseDlg::SelectedFile()
{
	QListWidgetItem *pCurItem = listFiles->currentItem();
	if(!pCurItem)
		return;

	QString strFile = labDir->text();
	strFile += "/";
	strFile += pCurItem->text();

	m_pwidget->LoadFile(strFile.toAscii().data());
}

// *****************************************************************************



// ************************ Range Dialog ***************************************

RangeDlg::RangeDlg(CascadeWidget *pParent)
		: QDialog(pParent), m_pWidget(pParent), m_bReadOnly(false)
{
	setupUi(this);
	Update();

	connect(btnAuto, SIGNAL(toggled(bool)), this, SLOT(SetAutoRange(bool)));

	connect(spinBoxMin, SIGNAL(valueChanged(double)),
			this, SLOT(RangeChanged()));
	connect(spinBoxMax, SIGNAL(valueChanged(double)),
			this, SLOT(RangeChanged()));
}

RangeDlg::~RangeDlg()
{}

void RangeDlg::SetAutoRange(bool bAuto)
{
	if(m_bReadOnly) return;

	spinBoxMin->setEnabled(!bAuto);
	spinBoxMax->setEnabled(!bAuto);

	bool bAutoRange = btnAuto->isChecked();
	m_pWidget->SetAutoCountRange(bAutoRange);

	if(!bAuto)
		RangeChanged();
}

void RangeDlg::RangeChanged()
{
	if(m_bReadOnly) return;

	btnAuto->setChecked(false);
	double dMin = spinBoxMin->value();
	double dMax = spinBoxMax->value();
	m_pWidget->SetCountRange(dMin, dMax);
}

void RangeDlg::Update()
{
	m_bReadOnly = true;

	QwtDoubleInterval interval = m_pWidget->GetData2d().range();
	spinBoxMin->setValue(interval.minValue());
	spinBoxMax->setValue(interval.maxValue());

	bool bUseAuto = m_pWidget->GetData2d().GetAutoCountRange();
	btnAuto->setChecked(bUseAuto);
	spinBoxMin->setEnabled(!bUseAuto);
	spinBoxMax->setEnabled(!bUseAuto);

	m_bReadOnly = false;
}

void RangeDlg::SetReadOnly(bool bReadOnly)
{ m_bReadOnly = bReadOnly; }

// *****************************************************************************




// ******************* Batch Dialog ********************************************

BatchDlg::BatchDlg(CascadeWidget *pParent) : QDialog(pParent),
											m_pwidget(pParent)
{
	setupUi(this);

	comboWhat->addItem("Plot PAD/TOF to PDF");
	comboWhat->addItem("Convert Text PAD/TOF to Binary");
	comboWhat->addItem("Convert PAD/TOF to DAT Format");

	connect(btnSrc, SIGNAL(clicked()), this, SLOT(SelectSrcDir()));
	connect(btnDst, SIGNAL(clicked()), this, SLOT(SelectDstDir()));
	connect(btnStart, SIGNAL(clicked()), this, SLOT(Start()));
}

BatchDlg::~BatchDlg() {}

void BatchDlg::Start()
{
	if(editSrc->text()=="")
	{
		QMessageBox::critical(0, "Error", "Please select a source directory.", QMessageBox::Ok);
		return;
	}
	else if(editDst->text()=="")
	{
		QMessageBox::critical(0, "Error", "Please select a destination directory.", QMessageBox::Ok);
		return;
	}

	QDir dir(editSrc->text());
	dir.setFilter(QDir::Files | QDir::Hidden);

	QStringList namefilters;
	namefilters << "*.pad" << "*.tof" << "*.PAD" << "*.TOF";
	dir.setNameFilters(namefilters);

	QFileInfoList filelist = dir.entryInfoList();
	if(filelist.size() == 0)
	{
		QMessageBox::critical(0, "Error", "No PAD/TOF files found in source directory.", QMessageBox::Ok);
		return;
	}

	progressBar->setMinimum(0);
	progressBar->setMaximum(filelist.size());
	progressBar->setValue(0);
	for(int iFile=0; iFile<filelist.size(); ++iFile)
	{
		QFileInfo fileinfo = filelist.at(iFile);
		QString strDstFile = editDst->text() + "/" + fileinfo.fileName();

		//std::cout << "Src: " << fileinfo.filePath().toAscii().data() << std::endl;
		//std::cout << "Dst: " << strDstFile.toAscii().data() << std::endl;

		switch(comboWhat->currentIndex())
		{
			case 0:	// convert to pdf
				strDstFile += ".pdf";
				ConvertToPDF(fileinfo.filePath().toAscii().data(), strDstFile.toAscii().data());
				break;

			case 1: // convert from text
				if(editSrc->text() == editDst->text())
				{
					QMessageBox::critical(0, "Error", "Please don't use the same directory as source and destination!", QMessageBox::Ok);
					return;
				}

				ConvertToBinary(fileinfo.filePath().toAscii().data(), strDstFile.toAscii().data());
				break;
		
			case 2: // convert to dat
				ConvertToDat(fileinfo.filePath().toAscii().data(), (strDstFile + QString(".dat")).toAscii().data());
				break;
		}

		progressBar->setValue(iFile+1);
		progressBar->setFormat(QString("%p% - ") + fileinfo.fileName());
	}

	progressBar->setFormat(QString("%p% - Batch Job Finished"));
}

void BatchDlg::SelectSrcDir()
{
	QString strDir = QFileDialog::getExistingDirectory(
		this,
		"Select Source Directory",
		".",
		QFileDialog::ShowDirsOnly);

	if(strDir == "")
		return;

	editSrc->setText(strDir);
}

void BatchDlg::SelectDstDir()
{
	QString strDir = QFileDialog::getExistingDirectory(
		this,
		"Select Source Directory",
		".",
		QFileDialog::ShowDirsOnly);

	if(strDir == "")
		return;

	editDst->setText(strDir);
}

void BatchDlg::ConvertToBinary(const char* pcSrc, const char* pcDst)
{
	bool bIsTof = 0;

	// tof has a special ascii format: [# timechannel] [counts] [data] per line
	std::string strSrcFileEnding = GetFileEnding(pcSrc);
	if(strSrcFileEnding=="TOF" || strSrcFileEnding=="tof")
		bIsTof = 1;

	std::ifstream ifstr(pcSrc);
	std::ofstream ofstr(pcDst, std::ios_base::binary);

	if(!ifstr.is_open())
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Conversion Dialog: Unable to open file \"" << pcSrc
			   << "\" for reading.\n";

		return;
	}

	if(!ofstr.is_open())
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Conversion Dialog: Unable to open file \"" << pcDst
				<< "\" for writing.\n";

		return;
	}

	if(bIsTof)					// two additional numbers per line in TOF
	{
		std::string strDstCounts = pcDst;
		strDstCounts += ".counts";
		std::ofstream ofstrCounts(strDstCounts.c_str());
		ofstrCounts << "# timechannel\tcounts\n";

		unsigned int uiTimeChannel = 0;
		while(1)
		{
			std::string strLine;
			std::getline(ifstr, strLine);
			std::istringstream istrLine(strLine);

			if(ifstr.eof())
				break;

			unsigned int uiLineIdx = 0;
			while(1)
			{
				unsigned int uiVal;
				istrLine >> uiVal;

				if(istrLine.eof())
					break;

				if(uiLineIdx==0)		// time channel
				{
					//std::cout << "timechannel: " << uiVal << std::endl;
					if(uiVal != uiTimeChannel+1)
					{
						logger.SetCurLogLevel(LOGLEVEL_WARN);
						logger << "Conversion Dialog: Mismatch in TOF time channel index, "
							   << "expected " << uiTimeChannel+1 << ", got " << uiVal << ".\n";
					}

					ofstrCounts << uiVal << "\t";
				}
				else if(uiLineIdx==1)	// counts
				{
					ofstrCounts << uiVal << "\n";
				}

				if(uiLineIdx >= 2)
					ofstr.write((char*)&uiVal, sizeof(uiVal));

				++uiLineIdx;
			}
			++uiTimeChannel;
		}

		logger.SetCurLogLevel(LOGLEVEL_INFO);
		logger << "Conversion Dialog: " << uiTimeChannel << " time channels in TOF "
				<< "\"" << pcSrc << "\".\n";

		ofstrCounts.close();
	}
	else						// raw convert (e.g. PAD)
	{
		while(1)
		{
			unsigned int uiVal;
			ifstr >> uiVal;

			if(ifstr.eof())
				break;

			ofstr.write((char*)&uiVal, sizeof(uiVal));
		}
	}
}

void BatchDlg::ConvertToDat(const char* pcSrc, const char* pcDst)
{
	bool bIsTof = 0;

	std::string strSrcFileEnding = GetFileEnding(pcSrc);
	if(strSrcFileEnding=="TOF" || strSrcFileEnding=="tof")
		bIsTof = 1;

	TofImage *pTof = 0;
	PadImage *pPad = 0;

	bool bWritten = false;

	if(bIsTof)	// TOF
	{
		pTof = new TofImage(pcSrc);
		if(!pTof->IsOk())
		{
			logger.SetCurLogLevel(LOGLEVEL_ERR);
			logger << "Conversion Dialog: Unable to open tof file \"" << pcSrc
				<< "\" for reading.\n";
		}
		else
		{
			bWritten = pTof->SaveAsDat(pcDst);
		}
	}
	else		// PAD
	{
		pPad = new PadImage(pcSrc);
		if(!pPad->IsOk())
		{
			logger.SetCurLogLevel(LOGLEVEL_ERR);
			logger << "Conversion Dialog: Unable to open pad file \"" << pcSrc
				<< "\" for reading.\n";
		}
		else
		{
			bWritten = pPad->SaveAsDat(pcDst);
		}
	}

	if(!bWritten)
	{
			logger.SetCurLogLevel(LOGLEVEL_ERR);
			logger << "Conversion Dialog: No data written to \"" << pcDst
				<< "\".\n";
	}

	if(pTof) delete pTof;
	if(pPad) delete pPad;
}

void BatchDlg::ConvertToPDF(const char* pcSrc, const char* pcDst)
{
	std::string strSrcFileEnding = GetFileEnding(pcSrc);

	if(strSrcFileEnding=="PAD" || strSrcFileEnding=="pad")
		m_pwidget->LoadPadFile(pcSrc);
	else if(strSrcFileEnding=="TOF" || strSrcFileEnding=="tof")
		m_pwidget->LoadTofFile(pcSrc);
	else
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Conversion Dialog: Unable to identify type of file \"" << pcSrc
				<< "\". Skipping.\n";
		return;
	}

	if(!m_pwidget->ToPDF(pcDst))
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Conversion Dialog: Could not convert image to PDF \"" << pcDst
				<< "\".\n";
	}
}
// *****************************************************************************




// ************************* *GC-Dialog ****************************************

GcDlg::GcDlg(QWidget *pParent) : QDialog(pParent)
{
	setupUi(this);

	Update();
}

GcDlg::~GcDlg() {}

void GcDlg::Update()
{
	std::vector<Gc_info> vecGc = gc.get_elems();
	unsigned int iNumElems = vecGc.size();

	table->setColumnCount(4);
	table->setRowCount(iNumElems);

	for(unsigned int iElem=0; iElem<iNumElems; ++iElem)
	{
		const Gc_info& info = vecGc[iElem];

		QTableWidgetItem *pItemName =
				new QTableWidgetItem(QString(info.strDesc.c_str()));
		QTableWidgetItem *pItemAddr =
				new QTableWidgetItem(QString("%1")
					.arg((unsigned long)info.pvMem, 0, 16));
		QTableWidgetItem *pItemSize =
				new QTableWidgetItem(QString(get_byte_str(info.iLen).c_str()));
		QTableWidgetItem *pItemRefs =
				new QTableWidgetItem(QString("%1").arg(info.iRefs));

		table->setItem(iElem, 0, pItemName);
		table->setItem(iElem, 1, pItemAddr);
		table->setItem(iElem, 2, pItemSize);
		table->setItem(iElem, 3, pItemRefs);
	}


	// total mem
	unsigned int iTotal = gc.memsize();
	QString strTotal = QString(get_byte_str(iTotal).c_str())
						+ QString(" of total objects in use.");
	labelTotal->setText(strTotal);
}

// *****************************************************************************

/*
#ifdef __MOC_EXTERN_BUILD__
//	// Qt-Metaobjekte
	#include "cascadedialogs.moc"
#endif
*/
