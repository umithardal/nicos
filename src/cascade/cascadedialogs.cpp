﻿// *****************************************************************************
// NICOS-NG, the Networked Instrument Control System of the FRM-II
// Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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
// Cascade-Unterdialoge

#include "cascadedialogs.h"
#include <stdio.h>


// ************************* Server Command Dialog ********************
CommandDlg::CommandDlg(QWidget *pParent) : QDialog(pParent)
{
	setupUi(this);
}

CommandDlg::~CommandDlg()
{}
// ********************************************************************


// ************************* Kalibrierungs-Dialog *********************
CalibrationDlg::CalibrationDlg(QWidget *pParent, const Bins& bins) :
								QDialog(pParent), m_pgrid(0)
{
	setupUi(this);
	qwtPlot->setCanvasBackground(QColor(Qt::white));

	const QwtArray<QwtDoubleInterval>& intervals = bins.GetIntervals();
	const QwtArray<double>& values = bins.GetValues();

	m_pgrid = new QwtPlotGrid;
	m_pgrid->enableXMin(true);
	m_pgrid->enableYMin(true);
	m_pgrid->setMajPen(QPen(Qt::black, 0, Qt::DotLine));
	m_pgrid->setMinPen(QPen(Qt::gray, 0 , Qt::DotLine));
	m_pgrid->attach(qwtPlot);

	m_phistogram = new HistogramItem();
	m_phistogram->setColor(Qt::black);
	m_phistogram->attach(qwtPlot);

	qwtPlot->setAxisScale(QwtPlot::xBottom, 0., 360.);
	qwtPlot->setAxisScale(QwtPlot::yLeft, 0.0, bins.GetMaxVal());
	qwtPlot->axisWidget(QwtPlot::xBottom)->setTitle("Phase [DEG]");
	qwtPlot->axisWidget(QwtPlot::yLeft)->setTitle("Number");

	m_phistogram->setData(QwtIntervalData(intervals, values));
	qwtPlot->replot();
}

CalibrationDlg::~CalibrationDlg()
{
	if(m_pgrid) delete m_pgrid;
}
// *****************************************************************************




// ************************* Summierungs-Dialog mit Zeitkanälen ****************
void SumDlg::ShowIt()
{
	const TofConfig& conf = GlobalConfig::GetTofConfig();

	bool *pbChecked = new bool[conf.GetFoilCount()*conf.GetImagesPerFoil()];
	for(int iFolie=0; iFolie<conf.GetFoilCount(); ++iFolie)
	{
		for(int iKanal=0; iKanal<conf.GetImagesPerFoil(); ++iKanal)
		{
			bool bChecked =
				(m_pTreeItems[iFolie*conf.GetImagesPerFoil() +
				iKanal]->checkState(0)==Qt::Checked);
			pbChecked[iFolie*conf.GetImagesPerFoil() + iKanal] = bChecked;
		}
	}
	emit SumSignal(pbChecked, m_iMode);
	delete[] pbChecked;
}

void SumDlg::SelectAll()
{
	const TofConfig& conf = GlobalConfig::GetTofConfig();

	for(int iFolie=0; iFolie<conf.GetFoilCount(); ++iFolie)
	{
		m_pTreeItemsFolien[iFolie]->setCheckState(0,Qt::Checked);
		for(int iKanal=0; iKanal<conf.GetImagesPerFoil(); ++iKanal)
			m_pTreeItems[iFolie*conf.GetImagesPerFoil() + iKanal]
												->setCheckState(0,Qt::Checked);
	}
}

void SumDlg::SelectNone()
{
	const TofConfig& conf = GlobalConfig::GetTofConfig();

	for(int iFolie=0; iFolie<conf.GetFoilCount(); ++iFolie)
	{
		m_pTreeItemsFolien[iFolie]->setCheckState(0,Qt::Unchecked);
		for(int iKanal=0; iKanal<conf.GetImagesPerFoil(); ++iKanal)
			m_pTreeItems[iFolie*conf.GetImagesPerFoil() + iKanal]
												->setCheckState(0,Qt::Unchecked);
	}
}

void SumDlg::TreeWidgetClicked(QTreeWidgetItem *item, int column)
{
	const TofConfig& conf = GlobalConfig::GetTofConfig();

	int iFolie;
	for(iFolie=0; iFolie<conf.GetFoilCount(); ++iFolie)
		if(m_pTreeItemsFolien[iFolie]==item) break;

	// nicht auf Parent geklickt
	if(iFolie==conf.GetFoilCount()) return;

	for(int iKanal=0; iKanal<conf.GetImagesPerFoil(); ++iKanal)
		m_pTreeItems[iFolie*conf.GetImagesPerFoil() + iKanal]
				->setCheckState(0,m_pTreeItemsFolien[iFolie]->checkState(0));
}

SumDlg::SumDlg(QWidget *pParent) : QDialog(pParent)
{
	setupUi(this);

	const TofConfig& conf = GlobalConfig::GetTofConfig();

	m_pTreeItemsFolien = new QTreeWidgetItem*[conf.GetFoilCount()];
	m_pTreeItems = new QTreeWidgetItem*[conf.GetFoilCount()*
										conf.GetImagesPerFoil()];

	for(int iFolie=0; iFolie<conf.GetFoilCount(); ++iFolie)
	{
		m_pTreeItemsFolien[iFolie] = new QTreeWidgetItem(treeWidget);
		char pcName[256];
		sprintf(pcName, "Foil %d", iFolie+1);
		m_pTreeItemsFolien[iFolie]->setText(0, pcName);
		m_pTreeItemsFolien[iFolie]->setCheckState(0, Qt::Unchecked);

		for(int iKanal=0; iKanal<conf.GetImagesPerFoil(); ++iKanal)
		{
			m_pTreeItems[iFolie*conf.GetImagesPerFoil() + iKanal] =
								new QTreeWidgetItem(m_pTreeItemsFolien[iFolie]);
			m_pTreeItems[iFolie*conf.GetImagesPerFoil() + iKanal]
											->setCheckState(0, Qt::Unchecked);
			sprintf(pcName, "Time Channel %d", iKanal+1);
			m_pTreeItems[iFolie*conf.GetImagesPerFoil() + iKanal]
														->setText(0, pcName);
		}
	}

	connect(treeWidget, SIGNAL(itemClicked(QTreeWidgetItem *, int)), this,
								SLOT(TreeWidgetClicked(QTreeWidgetItem *, int)));
	connect(pushButtonShow, SIGNAL(clicked()), this, SLOT(ShowIt()));
	connect(pushButtonSelectAll, SIGNAL(clicked()), this, SLOT(SelectAll()));
	connect(pushButtonSelectNone, SIGNAL(clicked()), this, SLOT(SelectNone()));
}

SumDlg::~SumDlg()
{
	delete[] m_pTreeItemsFolien; m_pTreeItemsFolien = 0;
	delete[] m_pTreeItems; m_pTreeItems = 0;
}

void SumDlg::SetMode(int iMode) { m_iMode = iMode; }
// *****************************************************************************


// ************************* Summierungs-Dialog ohne Zeitkanäle ****************
void SumDlgNoChannels::ShowIt()
{
	const TofConfig& conf = GlobalConfig::GetTofConfig();

	bool *pbChecked = new bool[conf.GetFoilCount()];
	for(int iFolie=0; iFolie<conf.GetFoilCount(); ++iFolie)
	{
		bool bChecked = (m_pTreeItemsFolien[iFolie]->checkState(0)==Qt::Checked);
		pbChecked[iFolie] = bChecked;
	}
	emit SumSignal(pbChecked, m_iMode);
	delete[] pbChecked;
}

void SumDlgNoChannels::SelectAll()
{
	const TofConfig& conf = GlobalConfig::GetTofConfig();

	for(int iFolie=0; iFolie<conf.GetFoilCount(); ++iFolie)
		m_pTreeItemsFolien[iFolie]->setCheckState(0,Qt::Checked);
}

void SumDlgNoChannels::SelectNone()
{
	const TofConfig& conf = GlobalConfig::GetTofConfig();

	for(int iFolie=0; iFolie<conf.GetFoilCount(); ++iFolie)
		m_pTreeItemsFolien[iFolie]->setCheckState(0,Qt::Unchecked);
}

SumDlgNoChannels::SumDlgNoChannels(QWidget *pParent) : QDialog(pParent)
{
	setupUi(this);

	const TofConfig& conf = GlobalConfig::GetTofConfig();

	m_pTreeItemsFolien = new QTreeWidgetItem*[conf.GetFoilCount()];

	for(int iFolie=0; iFolie<conf.GetFoilCount(); ++iFolie)
	{
		m_pTreeItemsFolien[iFolie] = new QTreeWidgetItem(treeWidget);
		char pcName[256];
		sprintf(pcName, "Foil %d", iFolie+1);
		m_pTreeItemsFolien[iFolie]->setText(0, pcName);
		m_pTreeItemsFolien[iFolie]->setCheckState(0, Qt::Unchecked);
	}

	connect(pushButtonShow, SIGNAL(clicked()), this, SLOT(ShowIt()));
	connect(pushButtonSelectAll, SIGNAL(clicked()), this, SLOT(SelectAll()));
	connect(pushButtonSelectNone, SIGNAL(clicked()), this, SLOT(SelectNone()));
}

SumDlgNoChannels::~SumDlgNoChannels()
{
	delete[] m_pTreeItemsFolien; m_pTreeItemsFolien = 0;
}

void SumDlgNoChannels::SetMode(int iMode) { m_iMode = iMode; }
// *****************************************************************************



// ************************* Zeug für Graph-Dialog *****************************
void GraphDlg::UpdateGraph(void)
{
	const TofConfig& conf = GlobalConfig::GetTofConfig();

	// Messpunkte für eine Folie
	TmpGraph tmpGraph;
	m_pTofImg->GetGraph(spinBoxROIx1->value(),spinBoxROIx2->value(),spinBoxROIy1
			->value(),spinBoxROIy2->value(),spinBoxFolie->value()-1, &tmpGraph);

	double *pdx = new double[tmpGraph.GetWidth()];
	double *pdy = new double[tmpGraph.GetWidth()];
	for(int i=0; i<tmpGraph.GetWidth(); ++i)
	{
		pdx[i]=i;
		pdy[i]=tmpGraph.GetData(i);
	}
	m_curve.setData(pdx,pdy,tmpGraph.GetWidth());
	delete[] pdx;
	delete[] pdy;


	// Fit dieser Messpunkte
	double dPhase, dFreq, dAmp, dOffs;
	bool bFitValid = tmpGraph.FitSinus(dPhase, dFreq, dAmp, dOffs);

	char pcFit[256];
	if(bFitValid)
	{
		sprintf(pcFit, "Fit: y = %.0f * sin(%.4f*x + %.4f) + %.0f",
													dAmp, dFreq, dPhase, dOffs);
	}
	else
	{
		sprintf(pcFit, "Fit: invalid!");
		dAmp = dFreq = dPhase = dOffs = 0.;
	}

	labelFit->setText(pcFit);

	const int FITPUNKTE=16;
	pdx = new double[conf.GetImagesPerFoil()*FITPUNKTE];
	pdy = new double[conf.GetImagesPerFoil()*FITPUNKTE];
	for(int i=0; i<conf.GetImagesPerFoil()*FITPUNKTE; ++i)
	{
		double x = double(i)/double(FITPUNKTE);
		pdx[i] = x;
		pdy[i] = dAmp*sin(x*dFreq + dPhase) + dOffs;
	}
	m_curvefit.setData(pdx, pdy, conf.GetImagesPerFoil()*FITPUNKTE);
	delete[] pdx;
	delete[] pdy;

	/*
	// Gesamtkurve
	TmpGraph tmpGraphtotal;
	m_pTofImg->GetTotalGraph(spinBoxROIx1->value(),spinBoxROIx2->value(),
		spinBoxROIy1->value(),spinBoxROIy2->value(),spinBoxPhase->value(),
		&tmpGraphtotal);
	pdx = new double[tmpGraphtotal.GetWidth()];
	pdy = new double[tmpGraphtotal.GetWidth()];
	for(int i=0; i<tmpGraphtotal.GetWidth(); ++i)
	{
		pdx[i]=i;
		pdy[i]=tmpGraphtotal.GetData(i);
	}
	m_curvetotal.setData(pdx,pdy,tmpGraphtotal.GetWidth());
	delete[] pdx;
	delete[] pdy;
	*/

	qwtPlot->replot();
}

void GraphDlg::ROIy1changed(int iVal) { UpdateGraph(); }
void GraphDlg::ROIy2changed(int iVal) { UpdateGraph(); }
void GraphDlg::ROIx1changed(int iVal) { UpdateGraph(); }
void GraphDlg::ROIx2changed(int iVal) { UpdateGraph(); }
void GraphDlg::Foilchanged(int iVal) { UpdateGraph(); }
void GraphDlg::Phasechanged(double dVal) { UpdateGraph(); }

void GraphDlg::Init(int iROIx1, int iROIx2, int iROIy1, int iROIy2, int iFolie)
{
	const TofConfig& conf = GlobalConfig::GetTofConfig();

	qwtPlot->setAutoReplot(false);
	qwtPlot->setCanvasBackground(QColor(255,255,255));
	qwtPlot->axisWidget(QwtPlot::xBottom)->setTitle("Time Channels");
	qwtPlot->axisWidget(QwtPlot::yLeft)->setTitle("Counts");

	m_pgrid = new QwtPlotGrid;
	m_pgrid->enableXMin(true);
	m_pgrid->enableYMin(true);
	m_pgrid->setMajPen(QPen(Qt::black, 0, Qt::DotLine));
	m_pgrid->setMinPen(QPen(Qt::gray, 0 , Qt::DotLine));
	m_pgrid->attach(qwtPlot);

	spinBoxROIx1->setMinimum(0);
	spinBoxROIx1->setMaximum(conf.GetImageWidth());
	spinBoxROIx2->setMinimum(0);
	spinBoxROIx2->setMaximum(conf.GetImageWidth());
	spinBoxROIy1->setMinimum(0);
	spinBoxROIy1->setMaximum(conf.GetImageHeight());
	spinBoxROIy2->setMinimum(0);
	spinBoxROIy2->setMaximum(conf.GetImageHeight());
	spinBoxFolie->setMinimum(1);
	spinBoxFolie->setMaximum(conf.GetFoilCount());

	spinBoxROIx1->setValue(iROIx1);
	spinBoxROIx2->setValue(iROIx2);
	spinBoxROIy1->setValue(iROIy1);
	spinBoxROIy2->setValue(iROIy2);
	spinBoxFolie->setValue(iFolie+1);

	QwtLegend *m_plegend = new QwtLegend;
	//m_plegend->setItemMode(QwtLegend::CheckableItem);
	qwtPlot->insertLegend(m_plegend, QwtPlot::RightLegend);

	QObject::connect(spinBoxROIy1, SIGNAL(valueChanged(int)), this,
								   SLOT(ROIy1changed(int)));
	QObject::connect(spinBoxROIy2, SIGNAL(valueChanged(int)), this,
								   SLOT(ROIy2changed(int)));
	QObject::connect(spinBoxROIx1, SIGNAL(valueChanged(int)), this,
								   SLOT(ROIx1changed(int)));
	QObject::connect(spinBoxROIx2, SIGNAL(valueChanged(int)), this,
								   SLOT(ROIx2changed(int)));
	QObject::connect(spinBoxFolie, SIGNAL(valueChanged(int)), this,
								   SLOT(Foilchanged(int)));
	QObject::connect(spinBoxPhase, SIGNAL(valueChanged(double)), this,
								   SLOT(Phasechanged(double)));


	// Kurve für Messpunkte für eine Folie
	QwtSymbol sym;
	sym.setStyle(QwtSymbol::Ellipse);
	sym.setPen(QColor(Qt::blue));
	sym.setBrush(QColor(Qt::blue));
	sym.setSize(5);
	m_curve.setSymbol(sym);
	m_curve.setStyle(QwtPlotCurve::NoCurve);
	m_curve.setRenderHint(QwtPlotItem::RenderAntialiased);
	m_curve.setPen(QPen(Qt::blue));
	m_curve.attach(qwtPlot);

	// Kurve für Fits
	m_curvefit.setRenderHint(QwtPlotItem::RenderAntialiased);
	QPen penfit = QPen(Qt::red);
	m_curvefit.setPen(penfit);
	m_curvefit.attach(qwtPlot);

	// Gesamtkurve
	m_curvetotal.setRenderHint(QwtPlotItem::RenderAntialiased);
	QPen pentotal = QPen(Qt::black);
	pentotal.setWidth(2);
	m_curvetotal.setPen(pentotal);
	m_curvetotal.attach(qwtPlot);
}

GraphDlg::GraphDlg(QWidget *pParent, TofImage* pTof) : QDialog(pParent),
													   m_pTofImg(pTof),
													   m_curve("Foil"),
													   m_curvefit("Fit"),
													   m_curvetotal("Total"),
													   m_plegend(0),
													   m_pgrid(0)
{
	setupUi(this);

	const TofConfig& conf = GlobalConfig::GetTofConfig();

	Init(0, conf.GetImageWidth()-1, 0, conf.GetImageHeight()-1, 0);
	UpdateGraph();
}

GraphDlg::GraphDlg(QWidget *pParent, TofImage* pTof, int iROIx1, int iROIx2,
					int iROIy1, int iROIy2, int iFolie) : QDialog(pParent),
														  m_pTofImg(pTof),
														  m_curve("Foil"),
														  m_curvefit("Fit"),
														  m_curvetotal("Total"),
														  m_plegend(0),
														  m_pgrid(0)
{
	setupUi(this);
	Init(iROIx1, iROIx2, iROIy1, iROIy2, iFolie);
	UpdateGraph();
}

GraphDlg::~GraphDlg()
{
	if(m_pgrid) delete m_pgrid;
	if(m_plegend) delete m_plegend;
}
// *****************************************************************************




// ************************* Server-Dialog *************************************
ServerDlg::ServerDlg(QWidget *pParent) : QDialog(pParent)
{
	setupUi(this);
}

ServerDlg::~ServerDlg()
{}

ServerCfgDlg::ServerCfgDlg(QWidget *pParent) : QDialog(pParent)
{
	setupUi(this);
	QString str;

	str.setNum(s_dLastTime);
	editMeasTime->setText(str);

	str.setNum(s_iXRes);
	editxres->setText(str);

	str.setNum(s_iYRes);
	edityres->setText(str);

	str.setNum(s_iTRes);
	edittres->setText(str);

	checkBoxPseudoComp->setChecked(s_bUsePseudoComp);

	if(s_iMode==MODE_PAD)
	{
		radioButtonPad->setChecked(1);
		radioButtonTof->setChecked(0);
		toggledmode(0);
	}
	else if(s_iMode==MODE_TOF)
	{
		radioButtonTof->setChecked(1);
		radioButtonPad->setChecked(0);
		toggledmode(1);
	}
	connect(radioButtonTof, SIGNAL(toggled(bool)), this,
							SLOT(toggledmode(bool)));

	setFixedSize(width(),height());
}

ServerCfgDlg::~ServerCfgDlg()
{}

void ServerCfgDlg::toggledmode(bool bChecked)
{
	if(radioButtonTof->isChecked())
	{
		edittres->setEnabled(1);
	}
	else if(radioButtonPad->isChecked())
	{
		edittres->setEnabled(0);
	}
}

double ServerCfgDlg::GetMeasTime()
{
	s_dLastTime = editMeasTime->text().toDouble();
	return s_dLastTime;
}

unsigned int ServerCfgDlg::GetXRes()
{
	s_iXRes = editxres->text().toInt();
	return s_iXRes;
}

unsigned int ServerCfgDlg::GetYRes()
{
	s_iYRes = edityres->text().toInt();
	return s_iYRes;
}

unsigned int ServerCfgDlg::GetTRes()
{
	if(radioButtonPad->isChecked())
		return 1;

	s_iTRes = edittres->text().toInt();
	return s_iTRes;
}

int ServerCfgDlg::GetMode()
{
	if(radioButtonPad->isChecked())
		s_iMode = MODE_PAD;
	else if(radioButtonTof->isChecked())
		s_iMode = MODE_TOF;
	return s_iMode;
}

bool ServerCfgDlg::GetPseudoComp()
{
	s_bUsePseudoComp = checkBoxPseudoComp->isChecked();
	return s_bUsePseudoComp;
}


void ServerCfgDlg::SetStatXRes(int iXRes) { s_iXRes = iXRes; }
void ServerCfgDlg::SetStatYRes(int iYRes) { s_iYRes = iYRes; }
void ServerCfgDlg::SetStatTRes(int iTRes) { s_iTRes = iTRes; }
void ServerCfgDlg::SetStatMode(int iMode) { s_iMode = iMode; }
void ServerCfgDlg::SetStatTime(double dTime) { s_dLastTime = dTime; }
void ServerCfgDlg::SetStatComp(bool bComp) { s_bUsePseudoComp = bComp; }

int ServerCfgDlg::GetStatXRes() { return s_iXRes; }
int ServerCfgDlg::GetStatYRes() { return s_iYRes; }
int ServerCfgDlg::GetStatTRes() { return s_iTRes; }
int ServerCfgDlg::GetStatMode()  { return s_iMode; }
double ServerCfgDlg::GetStatTime() { return s_dLastTime; }
bool ServerCfgDlg::GetStatComp() { return s_bUsePseudoComp; }


double ServerCfgDlg::s_dLastTime = 10.0;
unsigned int ServerCfgDlg::s_iXRes = 128;
unsigned int ServerCfgDlg::s_iYRes = 128;
unsigned int ServerCfgDlg::s_iTRes = 128;
int ServerCfgDlg::s_iMode = 1;
bool ServerCfgDlg::s_bUsePseudoComp = 0;
// *****************************************************************************


// ************************* Roi-Dlg *******************************************
RoiDlg::RoiDlg(QWidget *pParent) : QDialog(pParent)
{
	setupUi(this);
}

RoiDlg::~RoiDlg()
{}
// *****************************************************************************
