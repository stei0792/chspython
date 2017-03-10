# -*- coding: utf-8 -*-
"""
Created on Thu Feb 23 12:13:17 2017

@author: MSteinme
"""

from PyQt4.QtCore import * 
from PyQt4.QtGui import * 
from PyQt4 import QtCore, QtGui, uic
import sys 
from PyQt4.QtCore import QDateTime
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import statsmodels.api as sm
import seaborn as sns
from CRTdb3 import *
import matplotlib.cm as cm
import math
#from matplotlib.ticker import MaxNLocator
import matplotlib.lines as mlines
import matplotlib.dates as mdates

class popup(QWidget):
    def __init__(self, parent = None, widget=None):    
        QWidget.__init__(self, parent)
        layout = QGridLayout(self)
        msg = QMessageBox()
        layout.addWidget(msg)
        msg.setIcon(QMessageBox.Question)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.adjustSize()
        self.setWindowFlags(Qt.Popup)
        point = widget.rect().bottomRight()
        global_point = widget.mapToGlobal(point)
        self.move(global_point - QPoint(self.width(), 0))
        msg.setText("Help Box")
        msg.setInformativeText("For Help Click on Show Details")
        msg.setWindowTitle("Help")
        msg.setDetailedText("1.)Choose dates of interest  2.) select variables of interest 3.) click Get data from database 4.) If you want to save that data save as csv 5.) Choose graphs you would like to look at and click execute below corresponding graph")

class popupinfo(QWidget):
    def __init__(self, parent = None, widget=None):    
        QWidget.__init__(self, parent)
        layout = QGridLayout(self)
        msginfo = QMessageBox()
        layout.addWidget(msginfo)
        msginfo.setIcon(QMessageBox.Information)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.adjustSize()
        self.setWindowFlags(Qt.Popup)
        point = widget.rect().bottomRight()
        global_point = widget.mapToGlobal(point)
        self.move(global_point - QPoint(self.width(), 0))
        msginfo.setText("Information Box")
        msginfo.setInformativeText("For General Information Click on Show Details")
        msginfo.setWindowTitle("Information")
        msginfo.setDetailedText("go to Agronomy Chart Layout")

qtCreatorFile = "SimpleGraphs.ui" # Enter file here.
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class MyApp(QtGui.QMainWindow, Ui_MainWindow):  
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.setWindowTitle('Model Accuracy Using Database')
        datetypelist = ['Daily','Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Month End','Year End']       
        self.datetype_comboBox.addItems(datetypelist)
        #setting date margins
        max_date = datetime.datetime.today()
        self.start_calendarWidget.setMaximumDate(max_date)
        self.end_calendarWidget.setMaximumDate(max_date)      
        #connecting buttons to functions
        self.db_pushButton.clicked.connect(self.execute)
        self.db_pushButton_2.clicked.connect(self.Graphs) 
        self.help_pushButton.clicked.connect(self.handleOpenDialog) #help
        self.info_pushButton.clicked.connect(self.handleOpenDialoginfo) 
        self.pie_pushButton.clicked.connect(self.pie)
        self.line_pushButton.clicked.connect(self.line)
        self.time_pushButton.clicked.connect(self.timeseries)
        self.histogram_pushButton.clicked.connect(self.histogram) 
        self.bar_pushButton.clicked.connect(self.bar)
        self.scatter_pushButton.clicked.connect(self.scatter)
        self.scattermatrix_pushButton.clicked.connect(self.scattermatrix)
        self.boxplot_pushButton.clicked.connect(self.boxplot)
        self.corrheat_pushButton.clicked.connect(self.corrheat)
        self.corr_pushButton.clicked.connect(self.corrgraph)
        self.fitplot_pushButton.clicked.connect(self.fitplot)
        self.qqplot_pushButton.clicked.connect(self.qqplot)
        self.clear_pushButton.clicked.connect(self.clearselection)       
        self.show()
    
    def handleOpenDialog(self):
        self.popup = popup(self, self.help_pushButton)
        self.popup.show()
    
    def handleOpenDialoginfo(self):
        self.popupinfo = popupinfo(self, self.info_pushButton)
        self.popupinfo.show()
        
    def execute(self):
        #dates
        date_start_old = (self.start_calendarWidget.selectedDate())
        qdatestart = QDateTime(date_start_old)
        date_start = qdatestart.toPyDateTime() #putting in datetime format
        start_date = str(date_start)
        date_end_old = (self.end_calendarWidget.selectedDate())
        qdateend = QDateTime(date_end_old)
        date_end = qdateend.toPyDateTime() #putting in datetime format 
        end_date = str(date_end)
        datetype = (self.datetype_comboBox.currentText())
        if datetype == 'Daily':
            cal_type = 'WD'
        elif datetype == 'Sunday':
            cal_type = 'S1'
        elif datetype == 'Monday':
            cal_type = 'S2'
        elif datetype == 'Tuesday':
            cal_type = 'S3'
        elif datetype == 'Wednesday':
            cal_type = 'S4'
        elif datetype == 'Thursday':
            cal_type = 'S5'
        elif datetype == 'Friday':
            cal_type = 'S6'
        elif datetype == 'Saturday':
            cal_type = 'S7'
        elif datetype == 'Year End':
            cal_type = 'Y'
        else:
            cal_type = 'M'      
        datetypelist = ['Daily','Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Month End','Year End']
        
        #getting all listWidgets into a python list so I can use later when creating dictionaries
        #fertilizer 
        ureagrancfr_list = [str(self.ureagrancfr_listWidget.item(i).text()) for i in range(self.ureagrancfr_listWidget.count())]
        ureagrandel_list = [str(self.ureagrandel_listWidget.item(i).text()) for i in range(self.ureagrandel_listWidget.count())]
        ureagranfca_list = [str(self.ureagranfca_listWidget.item(i).text()) for i in range(self.ureagranfca_listWidget.count())]
        ureagranfob_list = [str(self.ureagranfob_listWidget.item(i).text()) for i in range(self.ureagranfob_listWidget.count())]
        ureagranfobfis_list = [str(self.ureagranfobfis_listWidget.item(i).text()) for i in range(self.ureagranfobfis_listWidget.count())]        
        ureaprillcfr_list = [str(self.ureaprillcfr_listWidget.item(i).text()) for i in range(self.ureaprillcfr_listWidget.count())]
        ureaprillcpt_list = [str(self.ureaprillcpt_listWidget.item(i).text()) for i in range(self.ureaprillcpt_listWidget.count())]
        ureaprillfob_list = [str(self.ureaprillfob_listWidget.item(i).text()) for i in range(self.ureaprillfob_listWidget.count())]
        ureaprillfobfis_list = [str(self.ureaprillfobfis_listWidget.item(i).text()) for i in range(self.ureaprillfobfis_listWidget.count())]
        ureaother_list = [str(self.ureaother_listWidget.item(i).text()) for i in range(self.ureaother_listWidget.count())]
        uan2830_list = [str(self.uan2830_listWidget.item(i).text()) for i in range(self.uan2830_listWidget.count())]
        uan32_list = [str(self.uan32_listWidget.item(i).text()) for i in range(self.uan32_listWidget.count())]
        uanother_list = [str(self.uanother_listWidget.item(i).text()) for i in range(self.uanother_listWidget.count())]
        potgran_list = [str(self.potgran_listWidget.item(i).text()) for i in range(self.potgran_listWidget.count())]
        potstan_list = [str(self.potstan_listWidget.item(i).text()) for i in range(self.potstan_listWidget.count())]
        ammspot_list = [str(self.ammspot_listWidget.item(i).text()) for i in range(self.ammspot_listWidget.count())]
        ammtotcfr_list = [str(self.ammtotcfr_listWidget.item(i).text()) for i in range(self.ammtotcfr_listWidget.count())]
        ammtotdel_list = [str(self.ammtotdel_listWidget.item(i).text()) for i in range(self.ammtotdel_listWidget.count())]
        ammtotfob_list = [str(self.ammtotfob_listWidget.item(i).text()) for i in range(self.ammtotfob_listWidget.count())]  
        ammcontract_list = [str(self.ammcontract_listWidget.item(i).text()) for i in range(self.ammcontract_listWidget.count())]
        anbag_list = [str(self.anbag_listWidget.item(i).text()) for i in range(self.anbag_listWidget.count())]
        anbulk_list = [str(self.anbulk_listWidget.item(i).text()) for i in range(self.anbulk_listWidget.count())]
        antotcfr_list = [str(self.antotcfr_listWidget.item(i).text()) for i in range(self.antotcfr_listWidget.count())]
        antotfob_list = [str(self.antotfob_listWidget.item(i).text()) for i in range(self.antotfob_listWidget.count())]
        asother_list = [str(self.asother_listWidget.item(i).text()) for i in range(self.asother_listWidget.count())]
        asstan_list = [str(self.asstan_listWidget.item(i).text()) for i in range(self.asstan_listWidget.count())]
        aswcfr_list = [str(self.aswcfr_listWidget.item(i).text()) for i in range(self.aswcfr_listWidget.count())]     
        aswfob_list = [str(self.aswfob_listWidget.item(i).text()) for i in range(self.aswfob_listWidget.count())]  
        can_list = [str(self.can_listWidget.item(i).text()) for i in range(self.can_listWidget.count())]  
        dapfob_list = [str(self.dapfob_listWidget.item(i).text()) for i in range(self.dapfob_listWidget.count())]  
        dapother_list = [str(self.dapother_listWidget.item(i).text()) for i in range(self.dapother_listWidget.count())] 
        map10_list = [str(self.map10_listWidget.item(i).text()) for i in range(self.map10_listWidget.count())] 
        mapother_list = [str(self.mapother_listWidget.item(i).text()) for i in range(self.mapother_listWidget.count())]
        npk10_list = [str(self.npk10_listWidget.item(i).text()) for i in range(self.npk10_listWidget.count())] 
        npk15_list = [str(self.npk15_listWidget.item(i).text()) for i in range(self.npk15_listWidget.count())] 
        npk16_list = [str(self.npk16_listWidget.item(i).text()) for i in range(self.npk16_listWidget.count())] 
        npk17_list = [str(self.npk17_listWidget.item(i).text()) for i in range(self.npk17_listWidget.count())] 
        npk20_list = [str(self.npk20_listWidget.item(i).text()) for i in range(self.npk20_listWidget.count())] 
        phosrock_list = [str(self.phosrock_listWidget.item(i).text()) for i in range(self.phosrock_listWidget.count())] 
        phosacid_list = [str(self.phosacid_listWidget.item(i).text()) for i in range(self.phosacid_listWidget.count())] 
        sopssp_list = [str(self.sopssp_listWidget.item(i).text()) for i in range(self.sopssp_listWidget.count())] 
        sspot_list = [str(self.sspot_listWidget.item(i).text()) for i in range(self.sspot_listWidget.count())]
        stot_list = [str(self.stot_listWidget.item(i).text()) for i in range(self.stot_listWidget.count())]
        s6m_list = [str(self.s6m_listWidget.item(i).text()) for i in range(self.s6m_listWidget.count())]
        sgreat_list = [str(self.sgreat_listWidget.item(i).text()) for i in range(self.sgreat_listWidget.count())]
        sliq_list = [str(self.sliq_listWidget.item(i).text()) for i in range(self.sliq_listWidget.count())]
        smonth_list = [str(self.smonth_listWidget.item(i).text()) for i in range(self.smonth_listWidget.count())]
        sq_list = [str(self.sq_listWidget.item(i).text()) for i in range(self.sq_listWidget.count())]
        saspot_list = [str(self.saspot_listWidget.item(i).text()) for i in range(self.saspot_listWidget.count())]
        satot_list = [str(self.satot_listWidget.item(i).text()) for i in range(self.satot_listWidget.count())]
        sacon_list = [str(self.sacon_listWidget.item(i).text()) for i in range(self.sacon_listWidget.count())]
        tsp_list = [str(self.tsp_listWidget.item(i).text()) for i in range(self.tsp_listWidget.count())]
        #energy 
        coalcom_list = [str(self.coalcom_listWidget.item(i).text()) for i in range(self.coalcom_listWidget.count())]
        coale_list = [str(self.coale_listWidget.item(i).text()) for i in range(self.coale_listWidget.count())]
        coalara_list = [str(self.coalara_listWidget.item(i).text()) for i in range(self.coalara_listWidget.count())]
        coalr_list = [str(self.coalr_listWidget.item(i).text()) for i in range(self.coalr_listWidget.count())]
        petrolinv_list = [str(self.petrolinv_listWidget.item(i).text()) for i in range(self.petrolinv_listWidget.count())]
        ngnclose_list = [str(self.ngnclose_listWidget.item(i).text()) for i in range(self.ngnclose_listWidget.count())]
        ngnhigh_list = [str(self.ngnhigh_listWidget.item(i).text()) for i in range(self.ngnhigh_listWidget.count())]
        ngnlow_list = [str(self.ngnlow_listWidget.item(i).text()) for i in range(self.ngnlow_listWidget.count())]
        ngnopen_list = [str(self.ngnopen_listWidget.item(i).text()) for i in range(self.ngnopen_listWidget.count())]
        ngnvol_list = [str(self.ngnvol_listWidget.item(i).text()) for i in range(self.ngnvol_listWidget.count())]
        ngnbp_list = [str(self.ngnbp_listWidget.item(i).text()) for i in range(self.ngnbp_listWidget.count())]
        wticlose_list = [str(self.wticlose_listWidget.item(i).text()) for i in range(self.wticlose_listWidget.count())]
        wtihigh_list = [str(self.wtihigh_listWidget.item(i).text()) for i in range(self.wtihigh_listWidget.count())]
        wtilow_list = [str(self.wtilow_listWidget.item(i).text()) for i in range(self.wtilow_listWidget.count())]
        wtiopen_list = [str(self.wtiopen_listWidget.item(i).text()) for i in range(self.wtiopen_listWidget.count())]
        wtivol_list = [str(self.wtivol_listWidget.item(i).text()) for i in range(self.wtivol_listWidget.count())]
        brentclose_list = [str(self.brentclose_listWidget.item(i).text()) for i in range(self.brentclose_listWidget.count())]
        brenthigh_list = [str(self.brenthigh_listWidget.item(i).text()) for i in range(self.brenthigh_listWidget.count())]
        brentlow_list = [str(self.brentlow_listWidget.item(i).text()) for i in range(self.brentlow_listWidget.count())]
        brentopen_list = [str(self.brentopen_listWidget.item(i).text()) for i in range(self.brentopen_listWidget.count())]
        brentvol_list = [str(self.brentvol_listWidget.item(i).text()) for i in range(self.brentvol_listWidget.count())]
        hoclose_list = [str(self.hoclose_listWidget.item(i).text()) for i in range(self.hoclose_listWidget.count())]
        hohigh_list = [str(self.hohigh_listWidget.item(i).text()) for i in range(self.hohigh_listWidget.count())]
        holow_list = [str(self.holow_listWidget.item(i).text()) for i in range(self.holow_listWidget.count())]
        hoopen_list = [str(self.hoopen_listWidget.item(i).text()) for i in range(self.hoopen_listWidget.count())]
        hovol_list = [str(self.hovol_listWidget.item(i).text()) for i in range(self.hovol_listWidget.count())]
        rbobclose_list = [str(self.rbobclose_listWidget.item(i).text()) for i in range(self.rbobclose_listWidget.count())]
        rbobhigh_list = [str(self.rbobhigh_listWidget.item(i).text()) for i in range(self.rbobhigh_listWidget.count())]
        rboblow_list = [str(self.rboblow_listWidget.item(i).text()) for i in range(self.rboblow_listWidget.count())]
        rbobopen_list = [str(self.rbobopen_listWidget.item(i).text()) for i in range(self.rbobopen_listWidget.count())]
        rbobvol_list = [str(self.rbobvol_listWidget.item(i).text()) for i in range(self.rbobvol_listWidget.count())]
        #metals 
        alclose_list = [str(self.alclose_listWidget.item(i).text()) for i in range(self.alclose_listWidget.count())]
        alhigh_list = [str(self.alhigh_listWidget.item(i).text()) for i in range(self.alhigh_listWidget.count())]
        allow_list = [str(self.allow_listWidget.item(i).text()) for i in range(self.allow_listWidget.count())]
        alopen_list = [str(self.alopen_listWidget.item(i).text()) for i in range(self.alopen_listWidget.count())]
        alvol_list = [str(self.alvol_listWidget.item(i).text()) for i in range(self.alvol_listWidget.count())]  
        cuclose_list = [str(self.cuclose_listWidget.item(i).text()) for i in range(self.cuclose_listWidget.count())]
        cuhigh_list = [str(self.cuhigh_listWidget.item(i).text()) for i in range(self.cuhigh_listWidget.count())]
        culow_list = [str(self.culow_listWidget.item(i).text()) for i in range(self.culow_listWidget.count())]
        cuopen_list = [str(self.cuopen_listWidget.item(i).text()) for i in range(self.cuopen_listWidget.count())]
        cuvol_list = [str(self.cuvol_listWidget.item(i).text()) for i in range(self.cuvol_listWidget.count())]
        auclose_list = [str(self.auclose_listWidget.item(i).text()) for i in range(self.auclose_listWidget.count())]
        auhigh_list = [str(self.auhigh_listWidget.item(i).text()) for i in range(self.auhigh_listWidget.count())]
        aulow_list = [str(self.aulow_listWidget.item(i).text()) for i in range(self.aulow_listWidget.count())]
        auopen_list = [str(self.auopen_listWidget.item(i).text()) for i in range(self.auopen_listWidget.count())]
        auvol_list = [str(self.auvol_listWidget.item(i).text()) for i in range(self.auvol_listWidget.count())] 
        feclose_list = [str(self.feclose_listWidget.item(i).text()) for i in range(self.feclose_listWidget.count())]
        fehigh_list = [str(self.fehigh_listWidget.item(i).text()) for i in range(self.fehigh_listWidget.count())]
        felow_list = [str(self.felow_listWidget.item(i).text()) for i in range(self.felow_listWidget.count())]
        feopen_list = [str(self.feopen_listWidget.item(i).text()) for i in range(self.feopen_listWidget.count())]
        fevol_list = [str(self.fevol_listWidget.item(i).text()) for i in range(self.fevol_listWidget.count())]   
        pbclose_list = [str(self.pbclose_listWidget.item(i).text()) for i in range(self.pbclose_listWidget.count())]
        pbhigh_list = [str(self.pbhigh_listWidget.item(i).text()) for i in range(self.pbhigh_listWidget.count())]
        pblow_list = [str(self.pblow_listWidget.item(i).text()) for i in range(self.pblow_listWidget.count())]
        pbopen_list = [str(self.pbopen_listWidget.item(i).text()) for i in range(self.pbopen_listWidget.count())]
        pbvol_list = [str(self.pbvol_listWidget.item(i).text()) for i in range(self.pbvol_listWidget.count())] 
        niclose_list = [str(self.niclose_listWidget.item(i).text()) for i in range(self.niclose_listWidget.count())]
        nihigh_list = [str(self.nihigh_listWidget.item(i).text()) for i in range(self.nihigh_listWidget.count())]
        nilow_list = [str(self.nilow_listWidget.item(i).text()) for i in range(self.nilow_listWidget.count())]
        niopen_list = [str(self.niopen_listWidget.item(i).text()) for i in range(self.niopen_listWidget.count())]
        nivol_list = [str(self.nivol_listWidget.item(i).text()) for i in range(self.nivol_listWidget.count())] 
        paclose_list = [str(self.paclose_listWidget.item(i).text()) for i in range(self.paclose_listWidget.count())]
        pahigh_list = [str(self.pahigh_listWidget.item(i).text()) for i in range(self.pahigh_listWidget.count())]
        palow_list = [str(self.palow_listWidget.item(i).text()) for i in range(self.palow_listWidget.count())]
        paopen_list = [str(self.paopen_listWidget.item(i).text()) for i in range(self.paopen_listWidget.count())]
        pavol_list = [str(self.pavol_listWidget.item(i).text()) for i in range(self.pavol_listWidget.count())] 
        plclose_list = [str(self.plclose_listWidget.item(i).text()) for i in range(self.plclose_listWidget.count())]
        plhigh_list = [str(self.plhigh_listWidget.item(i).text()) for i in range(self.plhigh_listWidget.count())]
        pllow_list = [str(self.pllow_listWidget.item(i).text()) for i in range(self.pllow_listWidget.count())]
        plopen_list = [str(self.plopen_listWidget.item(i).text()) for i in range(self.plopen_listWidget.count())]
        plvol_list = [str(self.plvol_listWidget.item(i).text()) for i in range(self.plvol_listWidget.count())]
        agclose_list = [str(self.agclose_listWidget.item(i).text()) for i in range(self.agclose_listWidget.count())]
        aghigh_list = [str(self.aghigh_listWidget.item(i).text()) for i in range(self.aghigh_listWidget.count())]
        aglow_list = [str(self.aglow_listWidget.item(i).text()) for i in range(self.aglow_listWidget.count())]
        agopen_list = [str(self.agopen_listWidget.item(i).text()) for i in range(self.agopen_listWidget.count())]
        agvol_list = [str(self.agvol_listWidget.item(i).text()) for i in range(self.agvol_listWidget.count())]  
        stclose_list = [str(self.stclose_listWidget.item(i).text()) for i in range(self.stclose_listWidget.count())]
        sthigh_list = [str(self.sthigh_listWidget.item(i).text()) for i in range(self.sthigh_listWidget.count())]
        stlow_list = [str(self.stlow_listWidget.item(i).text()) for i in range(self.stlow_listWidget.count())]
        stopen_list = [str(self.stopen_listWidget.item(i).text()) for i in range(self.stopen_listWidget.count())]
        stvol_list = [str(self.stvol_listWidget.item(i).text()) for i in range(self.stvol_listWidget.count())]  
        tnclose_list = [str(self.tnclose_listWidget.item(i).text()) for i in range(self.tnclose_listWidget.count())]
        tnhigh_list = [str(self.tnhigh_listWidget.item(i).text()) for i in range(self.tnhigh_listWidget.count())]
        tnlow_list = [str(self.tnlow_listWidget.item(i).text()) for i in range(self.tnlow_listWidget.count())]
        tnopen_list = [str(self.tnopen_listWidget.item(i).text()) for i in range(self.tnopen_listWidget.count())]
        tnvol_list = [str(self.tnvol_listWidget.item(i).text()) for i in range(self.tnvol_listWidget.count())]  
        urclose_list = [str(self.urclose_listWidget.item(i).text()) for i in range(self.urclose_listWidget.count())]
        urhigh_list = [str(self.urhigh_listWidget.item(i).text()) for i in range(self.urhigh_listWidget.count())]
        urlow_list = [str(self.urlow_listWidget.item(i).text()) for i in range(self.urlow_listWidget.count())]
        uropen_list = [str(self.uropen_listWidget.item(i).text()) for i in range(self.uropen_listWidget.count())]
        urvol_list = [str(self.urvol_listWidget.item(i).text()) for i in range(self.urvol_listWidget.count())]  
        znclose_list = [str(self.znclose_listWidget.item(i).text()) for i in range(self.znclose_listWidget.count())]
        znhigh_list = [str(self.znhigh_listWidget.item(i).text()) for i in range(self.znhigh_listWidget.count())]
        znlow_list = [str(self.znlow_listWidget.item(i).text()) for i in range(self.znlow_listWidget.count())]
        znopen_list = [str(self.znopen_listWidget.item(i).text()) for i in range(self.znopen_listWidget.count())]
        znvol_list = [str(self.znvol_listWidget.item(i).text()) for i in range(self.znvol_listWidget.count())]  
        #crops
        cornclose_list = [str(self.cornclose_listWidget.item(i).text()) for i in range(self.cornclose_listWidget.count())]
        cornhigh_list = [str(self.cornhigh_listWidget.item(i).text()) for i in range(self.cornhigh_listWidget.count())]
        cornlow_list = [str(self.cornlow_listWidget.item(i).text()) for i in range(self.cornlow_listWidget.count())]
        cornopen_list = [str(self.cornopen_listWidget.item(i).text()) for i in range(self.cornopen_listWidget.count())]
        cornvol_list = [str(self.cornvol_listWidget.item(i).text()) for i in range(self.cornvol_listWidget.count())]   
        wheatclose_list = [str(self.wheatclose_listWidget.item(i).text()) for i in range(self.wheatclose_listWidget.count())]
        wheathigh_list = [str(self.wheathigh_listWidget.item(i).text()) for i in range(self.wheathigh_listWidget.count())]
        wheatlow_list = [str(self.wheatlow_listWidget.item(i).text()) for i in range(self.wheatlow_listWidget.count())]
        wheatopen_list = [str(self.wheatopen_listWidget.item(i).text()) for i in range(self.wheatopen_listWidget.count())]
        wheatvol_list = [str(self.wheatvol_listWidget.item(i).text()) for i in range(self.wheatvol_listWidget.count())] 
        soyclose_list = [str(self.soyclose_listWidget.item(i).text()) for i in range(self.soyclose_listWidget.count())]
        soyhigh_list = [str(self.soyhigh_listWidget.item(i).text()) for i in range(self.soyhigh_listWidget.count())]
        soylow_list = [str(self.soylow_listWidget.item(i).text()) for i in range(self.soylow_listWidget.count())]
        soyopen_list = [str(self.soyopen_listWidget.item(i).text()) for i in range(self.soyopen_listWidget.count())]
        soyvol_list = [str(self.soyvol_listWidget.item(i).text()) for i in range(self.soyvol_listWidget.count())] 
        soclose_list = [str(self.soclose_listWidget.item(i).text()) for i in range(self.soclose_listWidget.count())]
        sohigh_list = [str(self.sohigh_listWidget.item(i).text()) for i in range(self.sohigh_listWidget.count())]
        solow_list = [str(self.solow_listWidget.item(i).text()) for i in range(self.solow_listWidget.count())]
        soopen_list = [str(self.soopen_listWidget.item(i).text()) for i in range(self.soopen_listWidget.count())]
        sovol_list = [str(self.sovol_listWidget.item(i).text()) for i in range(self.sovol_listWidget.count())] 
        cotclose_list = [str(self.cotclose_listWidget.item(i).text()) for i in range(self.cotclose_listWidget.count())]
        cothigh_list = [str(self.cothigh_listWidget.item(i).text()) for i in range(self.cothigh_listWidget.count())]
        cotlow_list = [str(self.cotlow_listWidget.item(i).text()) for i in range(self.cotlow_listWidget.count())]
        cotopen_list = [str(self.cotopen_listWidget.item(i).text()) for i in range(self.cotopen_listWidget.count())]
        cotvol_list = [str(self.cotvol_listWidget.item(i).text()) for i in range(self.cotvol_listWidget.count())]
        sbclose_list = [str(self.sbclose_listWidget.item(i).text()) for i in range(self.sbclose_listWidget.count())]
        sbhigh_list = [str(self.sbhigh_listWidget.item(i).text()) for i in range(self.sbhigh_listWidget.count())]
        sblow_list = [str(self.sblow_listWidget.item(i).text()) for i in range(self.sblow_listWidget.count())]
        sbopen_list = [str(self.sbopen_listWidget.item(i).text()) for i in range(self.sbopen_listWidget.count())]
        sbvol_list = [str(self.sbvol_listWidget.item(i).text()) for i in range(self.sbvol_listWidget.count())]  
        #currency, equity, sentiment
        sincurrency_list = [str(self.sincurrency_listWidget.item(i).text()) for i in range(self.sincurrency_listWidget.count())] 
        crosscurrency_list = [str(self.crosscurrency_listWidget.item(i).text()) for i in range(self.crosscurrency_listWidget.count())] 
        equity_list = [str(self.equity_listWidget.item(i).text()) for i in range(self.equity_listWidget.count())]
        sent_list = [str(self.sent_listWidget.item(i).text()) for i in range(self.sent_listWidget.count())]
        #imports
        imammtot_list = [str(self.imammtot_listWidget.item(i).text()) for i in range(self.imammtot_listWidget.count())]
        imamman_list = [str(self.imamman_listWidget.item(i).text()) for i in range(self.imamman_listWidget.count())]
        imammnittot_list = [str(self.imammnittot_listWidget.item(i).text()) for i in range(self.imammnittot_listWidget.count())]
        imammnitaq_list = [str(self.imammnitaq_listWidget.item(i).text()) for i in range(self.imammnitaq_listWidget.count())]
        imammsu_list = [str(self.imammsu_listWidget.item(i).text()) for i in range(self.imammsu_listWidget.count())]
        imdap_list = [str(self.imdap_listWidget.item(i).text()) for i in range(self.imdap_listWidget.count())]
        imint_list = [str(self.imint_listWidget.item(i).text()) for i in range(self.imint_listWidget.count())]
        immaptot_list = [str(self.immaptot_listWidget.item(i).text()) for i in range(self.immaptot_listWidget.count())]
        immapmix_list = [str(self.immapmix_listWidget.item(i).text()) for i in range(self.immapmix_listWidget.count())]
        imphosac_list = [str(self.imphosac_listWidget.item(i).text()) for i in range(self.imphosac_listWidget.count())]
        impot_list = [str(self.impot_listWidget.item(i).text()) for i in range(self.impot_listWidget.count())]
        imtsptot_list = [str(self.imtsptot_listWidget.item(i).text()) for i in range(self.imtsptot_listWidget.count())]
        imtspless_list = [str(self.imtspless_listWidget.item(i).text()) for i in range(self.imtspless_listWidget.count())]
        imtspgreat_list = [str(self.imtspgreat_listWidget.item(i).text()) for i in range(self.imtspgreat_listWidget.count())]
        imuantot_list = [str(self.imuantot_listWidget.item(i).text()) for i in range(self.imuantot_listWidget.count())]
        imuanmix_list = [str(self.imuanmix_listWidget.item(i).text()) for i in range(self.imuanmix_listWidget.count())]
        imureatot_list = [str(self.imureatot_listWidget.item(i).text()) for i in range(self.imureatot_listWidget.count())]
        imureadef_list = [str(self.imureadef_listWidget.item(i).text()) for i in range(self.imureadef_listWidget.count())]
        imureanesoi_list = [str(self.imureanesoi_listWidget.item(i).text()) for i in range(self.imureanesoi_listWidget.count())]
        imureasolid_list = [str(self.imureasolid_listWidget.item(i).text()) for i in range(self.imureasolid_listWidget.count())]
        imureaaq_list = [str(self.imureaaq_listWidget.item(i).text()) for i in range(self.imureaaq_listWidget.count())]
        #exports
        exammtot_list = [str(self.exammtot_listWidget.item(i).text()) for i in range(self.exammtot_listWidget.count())]
        examman_list = [str(self.examman_listWidget.item(i).text()) for i in range(self.examman_listWidget.count())]
        exammnittot_list = [str(self.exammnittot_listWidget.item(i).text()) for i in range(self.exammnittot_listWidget.count())]
        exammnitaq_list = [str(self.exammnitaq_listWidget.item(i).text()) for i in range(self.exammnitaq_listWidget.count())]
        exammsu_list = [str(self.exammsu_listWidget.item(i).text()) for i in range(self.exammsu_listWidget.count())]
        exdap_list = [str(self.exdap_listWidget.item(i).text()) for i in range(self.exdap_listWidget.count())]
        exnpk_list = [str(self.exnpk_listWidget.item(i).text()) for i in range(self.exnpk_listWidget.count())]
        exmaptot_list = [str(self.exmaptot_listWidget.item(i).text()) for i in range(self.exmaptot_listWidget.count())]
        exmapmix_list = [str(self.exmapmix_listWidget.item(i).text()) for i in range(self.exmapmix_listWidget.count())]
        exphosac_list = [str(self.exphosac_listWidget.item(i).text()) for i in range(self.exphosac_listWidget.count())]
        expot_list = [str(self.expot_listWidget.item(i).text()) for i in range(self.expot_listWidget.count())]
        extsptot_list = [str(self.extsptot_listWidget.item(i).text()) for i in range(self.extsptot_listWidget.count())]
        extspless_list = [str(self.extspless_listWidget.item(i).text()) for i in range(self.extspless_listWidget.count())]
        extspgreat_list = [str(self.extspgreat_listWidget.item(i).text()) for i in range(self.extspgreat_listWidget.count())]
        exuantot_list = [str(self.exuantot_listWidget.item(i).text()) for i in range(self.exuantot_listWidget.count())]
        exuanmix_list = [str(self.exuanmix_listWidget.item(i).text()) for i in range(self.exuanmix_listWidget.count())]
        exureatot_list = [str(self.exureatot_listWidget.item(i).text()) for i in range(self.exureatot_listWidget.count())]
        exureaaq_list = [str(self.exureaaq_listWidget.item(i).text()) for i in range(self.exureaaq_listWidget.count())]
        #supply/demand
        sdamm_list = [str(self.sdamm_listWidget.item(i).text()) for i in range(self.sdamm_listWidget.count())]
        sddapmapus_list = [str(self.sddapmapus_listWidget.item(i).text()) for i in range(self.sddapmapus_listWidget.count())]
        sddapmapall_list = [str(self.sddapmapall_listWidget.item(i).text()) for i in range(self.sddapmapall_listWidget.count())]
        sdpotus_list = [str(self.sdpotus_listWidget.item(i).text()) for i in range(self.sdpotus_listWidget.count())]
        sdpotall_list = [str(self.sdpotall_listWidget.item(i).text()) for i in range(self.sdpotall_listWidget.count())]    
        sduan_list = [str(self.sduan_listWidget.item(i).text()) for i in range(self.sduan_listWidget.count())]
        sdureaus_list = [str(self.sdureaus_listWidget.item(i).text()) for i in range(self.sdureaus_listWidget.count())]
        sdureaall_list = [str(self.sdureaall_listWidget.item(i).text()) for i in range(self.sdureaall_listWidget.count())] 
        #freight
        dapbid_list = [str(self.dapbid_listWidget.item(i).text()) for i in range(self.dapbid_listWidget.count())] 
        dapoffer_list = [str(self.dapoffer_listWidget.item(i).text()) for i in range(self.dapoffer_listWidget.count())] 
        dapmid_list = [str(self.dapmid_listWidget.item(i).text()) for i in range(self.dapmid_listWidget.count())] 
        mopbid_list = [str(self.mopbid_listWidget.item(i).text()) for i in range(self.mopbid_listWidget.count())] 
        mopoffer_list = [str(self.mopoffer_listWidget.item(i).text()) for i in range(self.mopoffer_listWidget.count())] 
        mopmid_list = [str(self.mopmid_listWidget.item(i).text()) for i in range(self.mopmid_listWidget.count())] 
        phorockbid_list = [str(self.phorockbid_listWidget.item(i).text()) for i in range(self.phorockbid_listWidget.count())] 
        phorockoffer_list = [str(self.phorockoffer_listWidget.item(i).text()) for i in range(self.phorockoffer_listWidget.count())] 
        phorockmid_list = [str(self.phorockmid_listWidget.item(i).text()) for i in range(self.phorockmid_listWidget.count())]   
        sulfurbid_list = [str(self.sulfurbid_listWidget.item(i).text()) for i in range(self.sulfurbid_listWidget.count())] 
        sulfuroffer_list = [str(self.sulfuroffer_listWidget.item(i).text()) for i in range(self.sulfuroffer_listWidget.count())] 
        sulfurmid_list = [str(self.sulfurmid_listWidget.item(i).text()) for i in range(self.sulfurmid_listWidget.count())] 
        ureabid_list = [str(self.ureabid_listWidget.item(i).text()) for i in range(self.ureabid_listWidget.count())] 
        ureaoffer_list = [str(self.ureaoffer_listWidget.item(i).text()) for i in range(self.ureaoffer_listWidget.count())] 
        ureamid_list = [str(self.ureamid_listWidget.item(i).text()) for i in range(self.ureamid_listWidget.count())]    
        ammbid_list = [str(self.ammbid_listWidget.item(i).text()) for i in range(self.ammbid_listWidget.count())] 
        ammoffer_list = [str(self.ammoffer_listWidget.item(i).text()) for i in range(self.ammoffer_listWidget.count())] 
        ammmid_list = [str(self.ammmid_listWidget.item(i).text()) for i in range(self.ammmid_listWidget.count())]    
        phoacbid_list = [str(self.phoacbid_listWidget.item(i).text()) for i in range(self.phoacbid_listWidget.count())] 
        phoacoffer_list = [str(self.phoacoffer_listWidget.item(i).text()) for i in range(self.phoacoffer_listWidget.count())] 
        phoacmid_list = [str(self.phoacmid_listWidget.item(i).text()) for i in range(self.phoacmid_listWidget.count())]    
        sulacbid_list = [str(self.sulacbid_listWidget.item(i).text()) for i in range(self.sulacbid_listWidget.count())] 
        sulacoffer_list = [str(self.sulacoffer_listWidget.item(i).text()) for i in range(self.sulacoffer_listWidget.count())] 
        sulacmid_list = [str(self.sulacmid_listWidget.item(i).text()) for i in range(self.sulacmid_listWidget.count())] 
        uanbid_list = [str(self.uanbid_listWidget.item(i).text()) for i in range(self.uanbid_listWidget.count())] 
        uanoffer_list = [str(self.uanoffer_listWidget.item(i).text()) for i in range(self.uanoffer_listWidget.count())] 
        uanmid_list = [str(self.uanmid_listWidget.item(i).text()) for i in range(self.uanmid_listWidget.count())]  
        #forecast
        chsdap_list = [str(self.chsdap_listWidget.item(i).text()) for i in range(self.chsdap_listWidget.count())]
        chspot_list = [str(self.chspot_listWidget.item(i).text()) for i in range(self.chspot_listWidget.count())]
        chsuan_list = [str(self.chsuan_listWidget.item(i).text()) for i in range(self.chsuan_listWidget.count())]
        chsurea_list = [str(self.chsurea_listWidget.item(i).text()) for i in range(self.chsurea_listWidget.count())]
        buckdap_list = [str(self.buckdap_listWidget.item(i).text()) for i in range(self.buckdap_listWidget.count())]
        buckpot_list = [str(self.buckpot_listWidget.item(i).text()) for i in range(self.buckpot_listWidget.count())]
        buckuan_list = [str(self.buckuan_listWidget.item(i).text()) for i in range(self.buckuan_listWidget.count())]
        buckurea_list = [str(self.buckurea_listWidget.item(i).text()) for i in range(self.buckurea_listWidget.count())] 
        cru_list = [str(self.CRU_listWidget.item(i).text()) for i in range(self.CRU_listWidget.count())]
        avgcorn_list = [str(self.avg_listWidget.item(i).text()) for i in range(self.avg_listWidget.count())]
        lowcorn_list = [str(self.low_listWidget.item(i).text()) for i in range(self.low_listWidget.count())]
        highcorn_list = [str(self.high_listWidget.item(i).text()) for i in range(self.high_listWidget.count())]
        avgsoy_list = [str(self.avg_listWidget_2.item(i).text()) for i in range(self.avg_listWidget_2.count())]
        lowsoy_list = [str(self.low_listWidget_2.item(i).text()) for i in range(self.low_listWidget_2.count())]
        highsoy_list = [str(self.high_listWidget_2.item(i).text()) for i in range(self.high_listWidget_2.count())]   
        avgso_list = [str(self.avg_listWidget_3.item(i).text()) for i in range(self.avg_listWidget_3.count())]
        lowso_list = [str(self.low_listWidget_3.item(i).text()) for i in range(self.low_listWidget_3.count())]
        highso_list = [str(self.high_listWidget_3.item(i).text()) for i in range(self.high_listWidget_3.count())]  
        avgwheat_list = [str(self.avg_listWidget_4.item(i).text()) for i in range(self.avg_listWidget_4.count())]
        lowwheat_list = [str(self.low_listWidget_4.item(i).text()) for i in range(self.low_listWidget_4.count())]
        highwheat_list = [str(self.high_listWidget_4.item(i).text()) for i in range(self.high_listWidget_4.count())]  
        avgwti_list = [str(self.avg_listWidget_5.item(i).text()) for i in range(self.avg_listWidget_5.count())]
        lowwti_list = [str(self.low_listWidget_5.item(i).text()) for i in range(self.low_listWidget_5.count())]
        highwti_list = [str(self.high_listWidget_5.item(i).text()) for i in range(self.high_listWidget_5.count())]   
        avgng_list = [str(self.avg_listWidget_6.item(i).text()) for i in range(self.avg_listWidget_6.count())]
        lowng_list = [str(self.low_listWidget_6.item(i).text()) for i in range(self.low_listWidget_6.count())]
        highng_list = [str(self.high_listWidget_6.item(i).text()) for i in range(self.high_listWidget_6.count())]   
        avgcot_list = [str(self.avg_listWidget_7.item(i).text()) for i in range(self.avg_listWidget_7.count())]
        lowcot_list = [str(self.low_listWidget_7.item(i).text()) for i in range(self.low_listWidget_7.count())]
        highcot_list = [str(self.high_listWidget_7.item(i).text()) for i in range(self.high_listWidget_7.count())]  
        avgal_list = [str(self.avg_listWidget_8.item(i).text()) for i in range(self.avg_listWidget_8.count())]
        lowal_list = [str(self.low_listWidget_8.item(i).text()) for i in range(self.low_listWidget_8.count())]
        highal_list = [str(self.high_listWidget_8.item(i).text()) for i in range(self.high_listWidget_8.count())] 
        avgara_list = [str(self.avg_listWidget_9.item(i).text()) for i in range(self.avg_listWidget_9.count())]
        lowara_list = [str(self.low_listWidget_9.item(i).text()) for i in range(self.low_listWidget_9.count())]
        highara_list = [str(self.high_listWidget_9.item(i).text()) for i in range(self.high_listWidget_9.count())]  
        avgrb_list = [str(self.avg_listWidget_10.item(i).text()) for i in range(self.avg_listWidget_10.count())]
        lowrb_list = [str(self.low_listWidget_10.item(i).text()) for i in range(self.low_listWidget_10.count())]
        highrb_list = [str(self.high_listWidget_10.item(i).text()) for i in range(self.high_listWidget_10.count())]      
        avgcu_list = [str(self.avg_listWidget_11.item(i).text()) for i in range(self.avg_listWidget_11.count())]
        lowcu_list = [str(self.low_listWidget_11.item(i).text()) for i in range(self.low_listWidget_11.count())]
        highcu_list = [str(self.high_listWidget_11.item(i).text()) for i in range(self.high_listWidget_11.count())]  
        avgau_list = [str(self.avg_listWidget_12.item(i).text()) for i in range(self.avg_listWidget_12.count())]
        lowau_list = [str(self.low_listWidget_12.item(i).text()) for i in range(self.low_listWidget_12.count())]
        highau_list = [str(self.high_listWidget_12.item(i).text()) for i in range(self.high_listWidget_12.count())]   
        avgho_list = [str(self.avg_listWidget_13.item(i).text()) for i in range(self.avg_listWidget_13.count())]
        lowho_list = [str(self.low_listWidget_13.item(i).text()) for i in range(self.low_listWidget_13.count())]
        highho_list = [str(self.high_listWidget_13.item(i).text()) for i in range(self.high_listWidget_13.count())] 
        avgice_list = [str(self.avg_listWidget_14.item(i).text()) for i in range(self.avg_listWidget_14.count())]
        lowice_list = [str(self.low_listWidget_14.item(i).text()) for i in range(self.low_listWidget_14.count())]
        highice_list = [str(self.high_listWidget_14.item(i).text()) for i in range(self.high_listWidget_14.count())]
        avgfe_list = [str(self.avg_listWidget_15.item(i).text()) for i in range(self.avg_listWidget_15.count())]
        lowfe_list = [str(self.low_listWidget_15.item(i).text()) for i in range(self.low_listWidget_15.count())]
        highfe_list = [str(self.high_listWidget_15.item(i).text()) for i in range(self.high_listWidget_15.count())] 
        avgpb_list = [str(self.avg_listWidget_16.item(i).text()) for i in range(self.avg_listWidget_16.count())]
        lowpb_list = [str(self.low_listWidget_16.item(i).text()) for i in range(self.low_listWidget_16.count())]
        highpb_list = [str(self.high_listWidget_16.item(i).text()) for i in range(self.high_listWidget_16.count())]    
        avgnbp_list = [str(self.avg_listWidget_17.item(i).text()) for i in range(self.avg_listWidget_17.count())]
        lownbp_list = [str(self.low_listWidget_17.item(i).text()) for i in range(self.low_listWidget_17.count())]
        highnbp_list = [str(self.high_listWidget_17.item(i).text()) for i in range(self.high_listWidget_17.count())]  
        avgni_list = [str(self.avg_listWidget_18.item(i).text()) for i in range(self.avg_listWidget_18.count())]
        lowni_list = [str(self.low_listWidget_18.item(i).text()) for i in range(self.low_listWidget_18.count())]
        highni_list = [str(self.high_listWidget_18.item(i).text()) for i in range(self.high_listWidget_18.count())]      
        avgpa_list = [str(self.avg_listWidget_19.item(i).text()) for i in range(self.avg_listWidget_19.count())]
        lowpa_list = [str(self.low_listWidget_19.item(i).text()) for i in range(self.low_listWidget_19.count())]
        highpa_list = [str(self.high_listWidget_19.item(i).text()) for i in range(self.high_listWidget_19.count())] 
        avgpt_list = [str(self.avg_listWidget_20.item(i).text()) for i in range(self.avg_listWidget_20.count())]
        lowpt_list = [str(self.low_listWidget_20.item(i).text()) for i in range(self.low_listWidget_20.count())]
        highpt_list = [str(self.high_listWidget_20.item(i).text()) for i in range(self.high_listWidget_20.count())]
        avgrbob_list = [str(self.avg_listWidget_21.item(i).text()) for i in range(self.avg_listWidget_21.count())]
        lowrbob_list = [str(self.low_listWidget_21.item(i).text()) for i in range(self.low_listWidget_21.count())]
        highrbob_list = [str(self.high_listWidget_21.item(i).text()) for i in range(self.high_listWidget_21.count())]  
        avgag_list = [str(self.avg_listWidget_22.item(i).text()) for i in range(self.avg_listWidget_22.count())]
        lowag_list = [str(self.low_listWidget_22.item(i).text()) for i in range(self.low_listWidget_22.count())]
        highag_list = [str(self.high_listWidget_22.item(i).text()) for i in range(self.high_listWidget_22.count())] 
        avgst_list = [str(self.avg_listWidget_23.item(i).text()) for i in range(self.avg_listWidget_23.count())]
        lowst_list = [str(self.low_listWidget_23.item(i).text()) for i in range(self.low_listWidget_23.count())]
        highst_list = [str(self.high_listWidget_23.item(i).text()) for i in range(self.high_listWidget_23.count())]  
        avgsb_list = [str(self.avg_listWidget_24.item(i).text()) for i in range(self.avg_listWidget_24.count())]
        lowsb_list = [str(self.low_listWidget_24.item(i).text()) for i in range(self.low_listWidget_24.count())]
        highsb_list = [str(self.high_listWidget_24.item(i).text()) for i in range(self.high_listWidget_24.count())]  
        avgtn_list = [str(self.avg_listWidget_25.item(i).text()) for i in range(self.avg_listWidget_25.count())]
        lowtn_list = [str(self.low_listWidget_25.item(i).text()) for i in range(self.low_listWidget_25.count())]
        hightn_list = [str(self.high_listWidget_25.item(i).text()) for i in range(self.high_listWidget_25.count())] 
        avgur_list = [str(self.avg_listWidget_26.item(i).text()) for i in range(self.avg_listWidget_26.count())]
        lowur_list = [str(self.low_listWidget_26.item(i).text()) for i in range(self.low_listWidget_26.count())]
        highur_list = [str(self.high_listWidget_26.item(i).text()) for i in range(self.high_listWidget_26.count())] 
        avgzn_list = [str(self.avg_listWidget_27.item(i).text()) for i in range(self.avg_listWidget_27.count())]
        lowzn_list = [str(self.low_listWidget_27.item(i).text()) for i in range(self.low_listWidget_27.count())]
        highzn_list = [str(self.high_listWidget_27.item(i).text()) for i in range(self.high_listWidget_27.count())]        
#############################################################################################################################################################################
        #corresponding tickers to text lists
        ureagrancfr_ticlist = ['UREA_GRAN','UREA_GRAN_FRONT','UREA_GRAN_FRONT2','UREA_GRAN_FRONT3','UREA_GRAN_FRONT4','UREA_GRAN','UREA_GRAN','UREA_GRAN_FRONT','UREA_GRAN_FRONT2','UREA_GRAN_FRONT3',
                               'UREA_GRAN_FRONT4','UREA_GRAN','UREA_GRAN_FRONT','UREA_GRAN_FRONT2','UREA_GRAN_FRONT3','UREA_GRAN_FRONT4','UREA_GRAN','UREA_GRAN','UREA_GRAN'] 
        ureagrandel_ticlist = ['UREA_GRAN'] * 4 
        ureagranfca_ticlist = ['UREA_GRAN']
        ureagranfob_ticlist = ['UREA_GRAN'] * 54 
        ureagranfobfis_ticlist = (['UREA_GRAN_FRONT','UREA_GRAN_FRONT2','UREA_GRAN_FRONT3','UREA_GRAN_FRONT4']*6)+(['UREA_GRAN_FRONT','UREA_GRAN_FRONT2','UREA_GRAN_FRONT3','UREA_GRAN_FRONT4',
                                'UREA_GRAN_FRONT5','UREA_GRAN_FRONT6','UREA_GRAN_FRONT7','UREA_GRAN_FRONT8','UREA_GRAN_FRONT9','UREA_GRAN_FRONT10','UREA_GRAN_FRONT11']*3)
        ureaprillcfr_ticlist = ['UREA_PRILL'] * 6 
        ureaprillcpt_ticlist = ['UREA_PRILL'] * 2  
        ureaprillfob_ticlist = ['UREA_PRILL'] * 7 
        ureaprillfobfis_ticlist = (['UREA_PRILL_FRONT','UREA_PRILL_FRONT2','UREA_PRILL_FRONT3','UREA_PRILL_FRONT4']*6)    
        ureaother_ticlist = ['UREA'] 
        uan2830_ticlist = ['UAN_28N','UAN_30N']+(['UAN_30N_FRONT','UAN_30N_FRONT2','UAN_30N_FRONT3','UAN_30N_FRONT4']*3)   
        uan32_ticlist = (['UAN_32N']*9)+['UAN_32N_FRONT','UAN_32N_FRONT2','UAN_32N_FRONT3','UAN_32N_FRONT4','UAN_32N_FRONT5','UAN_32N_FRONT6','UAN_32N_FRONT7','UAN_32N_FRONT8','UAN_32N_FRONT9']+(['UAN_32N']*2)+['UAN_32N_FRONT',
                        'UAN_32N_FRONT2','UAN_32N_FRONT3','UAN_32N_FRONT4','UAN_32N_FRONT5','UAN_32N_FRONT6','UAN_32N_FRONT7','UAN_32N_FRONT8','UAN_32N_FRONT9']+['UAN_32N']+['UAN_32N_FRONT','UAN_32N_FRONT2','UAN_32N_FRONT3',
                        'UAN_32N_FRONT4','UAN_32N_FRONT5','UAN_32N_FRONT6','UAN_32N_FRONT7','UAN_32N_FRONT8','UAN_32N_FRONT9'] 
        uanother_ticlist = ['UAN_TOT'] * 18 
        potgran_ticlist = ['POT_GRAN'] * 11
        potstan_ticlist = ['POT_STD'] * 9
        ammspot_ticlist = ['AMM_CLOSE']
        ammtotcfr_ticlist = (['AMM_TOT']*14)
        ammtotdel_ticlist = ['AMM_TOT','AMM_TOT']
        ammtotfob_ticlist = (['AMM_TOT']*14)
        ammcontract_ticlist = ['AMM_CTRCT'] 
        anbag_ticlist = ['AMNT_BAG'] * 2
        anbulk_ticlist = ['AMNT_BULK']
        antotcfr_ticlist = ['AMNT_TOT'] * 2
        antotfob_ticlist = ['AMNT_TOT'] * 6
        asother_ticlist = ['AMSF_TOT'] * 2
        asstan_ticlist = ['AMSF_STD']
        aswcfr_ticlist = ['AMSF_WHT'] * 2
        aswfob_ticlist = ['AMSF_WHT'] * 2
        can_ticlist = ['CA-AMNT_TOT'] * 2
        dapfob_ticlist = (['DAP_TOT']*7)+['DAP_TOT_FRONT','DAP_TOT_FRONT2','DAP_TOT_FRONT3','DAP_TOT_FRONT4','DAP_TOT_FRONT5','DAP_TOT']+(['DAP_TOT_FRONT','DAP_TOT_FRONT2','DAP_TOT_FRONT3','DAP_TOT_FRONT4','DAP_TOT_FRONT5']*2)+(['DAP_TOT']*12)
        dapother_ticlist = ['DAP_TOT'] * 8
        map10_ticlist = ['MAP_10-50-0','MAP_11-44-0']
        mapother_ticlist = ['MAP_TOT'] * 7
        npk10_ticlist = ['NPK_10-26-26'] * 2
        npk15_ticlist = ['NPK_15-15-15','NPK_15-15-15','NPK_15-15-15CL','NPK_15-15-15S']
        npk16_ticlist = ['NPK_16-16-16','NPK_16-16-16','NPK_16-16-16']
        npk17_ticlist = ['NPK_17-17-17']
        npk20_ticlist = ['NPK_20-10-10']
        phosrock_ticlist = ['PHO-RCK_60-68BPL','PHO-RCK_63-68BPL','PHO-RCK_65-70BPL','PHO-RCK_66-72BPL','PHO-RCK_68-72BPL','PHO-RCK_71-75BPL','PHO-RCK_73-75BPL']
        phosacid_ticlist = ['PHO-ACD_100P2O5'] * 4
        sopssp_ticlist = ['SOP_STD','SSP_18-20P2O5']
        sspot_ticlist = ['SUL_CLOSE'] * 4
        stot_ticlist = ['SUL_TOT'] * 4
        s6m_ticlist = ['SUL_6M','SUL_6M','SUL_6M']
        sgreat_ticlist = ['SUL_GT10K','SUL_LT10K']
        sliq_ticlist = ['SUL_LQD'] * 3
        smonth_ticlist = ['SUL_M-CTRCT'] * 3
        sq_ticlist = ['SUL_Q-CTRCT'] * 4
        saspot_ticlist = ['SUL-ACD_CLOSE'] * 3
        satot_ticlist = ['SUL-ACD_TOT'] * 4
        sacon_ticlist = ['SUL-ACD_30D','SUL-ACD_CTRCT','SUL-ACD_CTRCT']
        tsp_ticlist = ['TSP_GRAN'] * 5
        coale_ticlist = ['XW_FRONT'] * 5
        coalara_ticlist = ['COA_FRONT'] * 4
        coalr_ticlist = ['XO_FRONT'] * 4
        petrolinv_ticlist = ['INDEX_PETROLEUM']
        ngnclose_ticlist = ['NG_FRONT','NG_FRONT2','NG_FRONT3','NG_FRONT4','NG_FRONT5','NG_FRONT6','NG_FRONT7','NG_FRONT8','NG_FRONT9','NG_FRONT10','NG_FRONT11','NG_FRONT12']
        ngnhigh_ticlist = ['NG_FRONT','NG_FRONT2','NG_FRONT3','NG_FRONT4','NG_FRONT5','NG_FRONT6','NG_FRONT7','NG_FRONT8','NG_FRONT9','NG_FRONT10','NG_FRONT11','NG_FRONT12']
        ngnlow_ticlist = ['NG_FRONT','NG_FRONT2','NG_FRONT3','NG_FRONT4','NG_FRONT5','NG_FRONT6','NG_FRONT7','NG_FRONT8','NG_FRONT9','NG_FRONT10','NG_FRONT11','NG_FRONT12']
        ngnopen_ticlist = ['NG_FRONT','NG_FRONT2','NG_FRONT3','NG_FRONT4','NG_FRONT5','NG_FRONT6','NG_FRONT7','NG_FRONT8','NG_FRONT9','NG_FRONT10','NG_FRONT11','NG_FRONT12']
        ngnvol_ticlist = ['NG_FRONT','NG_FRONT2','NG_FRONT3','NG_FRONT4','NG_FRONT5','NG_FRONT6','NG_FRONT7','NG_FRONT8','NG_FRONT9','NG_FRONT10','NG_FRONT11','NG_FRONT12']
        ngnbp_ticlist = ['NG-NBP_FRONT','NG-NBP_FRONT2','NG-NBP_FRONT3','NG-NBP_FRONT4']
        wticlose_ticlist = ['CL_FRONT','CL_FRONT2','CL_FRONT3','CL_FRONT4','CL_FRONT5','CL_FRONT6','CL_FRONT7','CL_FRONT8','CL_FRONT9','CL_FRONT10','CL_FRONT11','CL_FRONT12']
        wtihigh_ticlist = ['CL_FRONT','CL_FRONT2','CL_FRONT3','CL_FRONT4','CL_FRONT5','CL_FRONT6','CL_FRONT7','CL_FRONT8','CL_FRONT9','CL_FRONT10','CL_FRONT11','CL_FRONT12']
        wtilow_ticlist = ['CL_FRONT','CL_FRONT2','CL_FRONT3','CL_FRONT4','CL_FRONT5','CL_FRONT6','CL_FRONT7','CL_FRONT8','CL_FRONT9','CL_FRONT10','CL_FRONT11','CL_FRONT12']
        wtiopen_ticlist = ['CL_FRONT','CL_FRONT2','CL_FRONT3','CL_FRONT4','CL_FRONT5','CL_FRONT6','CL_FRONT7','CL_FRONT8','CL_FRONT9','CL_FRONT10','CL_FRONT11','CL_FRONT12']
        wtivol_ticlist = ['CL_FRONT','CL_FRONT2','CL_FRONT3','CL_FRONT4','CL_FRONT5','CL_FRONT6','CL_FRONT7','CL_FRONT8','CL_FRONT9','CL_FRONT10','CL_FRONT11','CL_FRONT12']
        brentclose_ticlist = ['CO_FRONT','CO_FRONT2','CO_FRONT3','CO_FRONT4','CO_FRONT5','CO_FRONT6','CO_FRONT7','CO_FRONT8','CO_FRONT9','CO_FRONT10']
        brenthigh_ticlist = ['CO_FRONT','CO_FRONT2','CO_FRONT3','CO_FRONT4','CO_FRONT5','CO_FRONT6','CO_FRONT7','CO_FRONT8','CO_FRONT9','CO_FRONT10']
        brentlow_ticlist = ['CO_FRONT','CO_FRONT2','CO_FRONT3','CO_FRONT4','CO_FRONT5','CO_FRONT6','CO_FRONT7','CO_FRONT8','CO_FRONT9','CO_FRONT10']
        brentopen_ticlist = ['CO_FRONT','CO_FRONT2','CO_FRONT3','CO_FRONT4','CO_FRONT5','CO_FRONT6','CO_FRONT7','CO_FRONT8','CO_FRONT9','CO_FRONT10']
        brentvol_ticlist = ['CO_FRONT','CO_FRONT2','CO_FRONT3','CO_FRONT4','CO_FRONT5','CO_FRONT6','CO_FRONT7','CO_FRONT8','CO_FRONT9','CO_FRONT10']
        hoclose_ticlist = ['HO_FRONT','HO_FRONT2','HO_FRONT3','HO_FRONT4','HO_FRONT5','HO_FRONT6','HO_FRONT7','HO_FRONT8','HO_FRONT9','HO_FRONT10','HO_FRONT11','HO_FRONT12','HO_FRONT13','HO_FRONT14','HO_FRONT15','HO_FRONT16','HO_FRONT17']
        hohigh_ticlist = ['HO_FRONT','HO_FRONT2','HO_FRONT3','HO_FRONT4','HO_FRONT5','HO_FRONT6','HO_FRONT7','HO_FRONT8','HO_FRONT9','HO_FRONT10','HO_FRONT11','HO_FRONT12','HO_FRONT13','HO_FRONT14','HO_FRONT15','HO_FRONT16','HO_FRONT17']
        holow_ticlist = ['HO_FRONT','HO_FRONT2','HO_FRONT3','HO_FRONT4','HO_FRONT5','HO_FRONT6','HO_FRONT7','HO_FRONT8','HO_FRONT9','HO_FRONT10','HO_FRONT11','HO_FRONT12','HO_FRONT13','HO_FRONT14','HO_FRONT15','HO_FRONT16','HO_FRONT17']
        hoopen_ticlist = ['HO_FRONT','HO_FRONT2','HO_FRONT3','HO_FRONT4','HO_FRONT5','HO_FRONT6','HO_FRONT7','HO_FRONT8','HO_FRONT9','HO_FRONT10','HO_FRONT11','HO_FRONT12','HO_FRONT13','HO_FRONT14','HO_FRONT15','HO_FRONT16','HO_FRONT17']
        hovol_ticlist = ['HO_FRONT','HO_FRONT2','HO_FRONT3','HO_FRONT4','HO_FRONT5','HO_FRONT6','HO_FRONT7','HO_FRONT8','HO_FRONT9','HO_FRONT10','HO_FRONT11','HO_FRONT12','HO_FRONT13','HO_FRONT14','HO_FRONT15','HO_FRONT16','HO_FRONT17']
        rbobclose_ticlist = ['XB_FRONT','XB_FRONT2','XB_FRONT3','XB_FRONT4','XB_FRONT5','XB_FRONT6','XB_FRONT7','XB_FRONT8','XB_FRONT9','XB_FRONT10','XB_FRONT11','XB_FRONT12']
        rbobhigh_ticlist = ['XB_FRONT','XB_FRONT2','XB_FRONT3','XB_FRONT4','XB_FRONT5','XB_FRONT6','XB_FRONT7','XB_FRONT8','XB_FRONT9','XB_FRONT10','XB_FRONT11','XB_FRONT12']
        rboblow_ticlist = ['XB_FRONT','XB_FRONT2','XB_FRONT3','XB_FRONT4','XB_FRONT5','XB_FRONT6','XB_FRONT7','XB_FRONT8','XB_FRONT9','XB_FRONT10','XB_FRONT11','XB_FRONT12']
        rbobopen_ticlist = ['XB_FRONT','XB_FRONT2','XB_FRONT3','XB_FRONT4','XB_FRONT5','XB_FRONT6','XB_FRONT7','XB_FRONT8','XB_FRONT9','XB_FRONT10','XB_FRONT11','XB_FRONT12']
        rbobvol_ticlist = ['XB_FRONT','XB_FRONT2','XB_FRONT3','XB_FRONT4','XB_FRONT5','XB_FRONT6','XB_FRONT7','XB_FRONT8','XB_FRONT9','XB_FRONT10','XB_FRONT11','XB_FRONT12']
        alclose_ticlist = ['LA_FRONT','LA_FRONT2']
        alhigh_ticlist = ['LA_FRONT','LA_FRONT2']
        allow_ticlist = ['LA_FRONT','LA_FRONT2']
        alopen_ticlist = ['LA_FRONT','LA_FRONT2']
        alvol_ticlist = ['LA_FRONT','LA_FRONT2']
        cuclose_ticlist = ['HG_FRONT','HG_FRONT2','HG_FRONT3','HG_FRONT4','HG_FRONT5','HG_FRONT6','HG_FRONT7','HG_FRONT8','HG_FRONT9','HG_FRONT10','HG_FRONT11','HG_FRONT12']
        cuhigh_ticlist = ['HG_FRONT','HG_FRONT2','HG_FRONT3','HG_FRONT4','HG_FRONT5','HG_FRONT6','HG_FRONT7','HG_FRONT8','HG_FRONT9','HG_FRONT10','HG_FRONT11','HG_FRONT12']
        culow_ticlist = ['HG_FRONT','HG_FRONT2','HG_FRONT3','HG_FRONT4','HG_FRONT5','HG_FRONT6','HG_FRONT7','HG_FRONT8','HG_FRONT9','HG_FRONT10','HG_FRONT11','HG_FRONT12']
        cuopen_ticlist = ['HG_FRONT','HG_FRONT2','HG_FRONT3','HG_FRONT4','HG_FRONT5','HG_FRONT6','HG_FRONT7','HG_FRONT8','HG_FRONT9','HG_FRONT10','HG_FRONT11','HG_FRONT12']
        cuvol_ticlist = ['HG_FRONT','HG_FRONT2','HG_FRONT3','HG_FRONT4','HG_FRONT5','HG_FRONT6','HG_FRONT7','HG_FRONT8','HG_FRONT9','HG_FRONT10','HG_FRONT11','HG_FRONT12']
        auclose_ticlist = ['GC_FRONT','GC_FRONT2','GC_FRONT3','GC_FRONT4','GC_FRONT5','GC_FRONT6','GC_FRONT7','GC_FRONT8','GC_FRONT9','GC_FRONT10','GC_FRONT11','GC_FRONT12',
                           'GC_FRONT13','GC_FRONT14','GC_FRONT15','GC_FRONT16','GC_FRONT17','GC_FRONT18','GC_FRONT19','GC_FRONT20','GC_FRONT21','GC_FRONT22']
        auhigh_ticlist = ['GC_FRONT','GC_FRONT2','GC_FRONT3','GC_FRONT4','GC_FRONT5','GC_FRONT6','GC_FRONT7','GC_FRONT8','GC_FRONT9','GC_FRONT10','GC_FRONT11','GC_FRONT12',
                           'GC_FRONT13','GC_FRONT14','GC_FRONT15','GC_FRONT16','GC_FRONT17','GC_FRONT18','GC_FRONT19','GC_FRONT20','GC_FRONT21','GC_FRONT22']
        aulow_ticlist = ['GC_FRONT','GC_FRONT2','GC_FRONT3','GC_FRONT4','GC_FRONT5','GC_FRONT6','GC_FRONT7','GC_FRONT8','GC_FRONT9','GC_FRONT10','GC_FRONT11','GC_FRONT12',
                           'GC_FRONT13','GC_FRONT14','GC_FRONT15','GC_FRONT16','GC_FRONT17','GC_FRONT18','GC_FRONT19','GC_FRONT20','GC_FRONT21','GC_FRONT22']
        auopen_ticlist = ['GC_FRONT','GC_FRONT2','GC_FRONT3','GC_FRONT4','GC_FRONT5','GC_FRONT6','GC_FRONT7','GC_FRONT8','GC_FRONT9','GC_FRONT10','GC_FRONT11','GC_FRONT12',
                           'GC_FRONT13','GC_FRONT14','GC_FRONT15','GC_FRONT16','GC_FRONT17','GC_FRONT18','GC_FRONT19','GC_FRONT20','GC_FRONT21','GC_FRONT22']
        auvol_ticlist = ['GC_FRONT','GC_FRONT2','GC_FRONT3','GC_FRONT4','GC_FRONT5','GC_FRONT6','GC_FRONT7','GC_FRONT8','GC_FRONT9','GC_FRONT10','GC_FRONT11','GC_FRONT12',
                           'GC_FRONT13','GC_FRONT14','GC_FRONT15','GC_FRONT16','GC_FRONT17','GC_FRONT18','GC_FRONT19','GC_FRONT20','GC_FRONT21','GC_FRONT22']
        feclose_ticlist = ['IOE_FRONT','IOE_FRONT2']
        fehigh_ticlist = ['IOE_FRONT','IOE_FRONT2']
        felow_ticlist = ['IOE_FRONT','IOE_FRONT2']
        feopen_ticlist = ['IOE_FRONT','IOE_FRONT2']
        fevol_ticlist = ['IOE_FRONT','IOE_FRONT2']
        pbclose_ticlist = ['LL_FRONT','LL_FRONT2']
        pbhigh_ticlist = ['LL_FRONT','LL_FRONT2']
        pblow_ticlist = ['LL_FRONT','LL_FRONT2']
        pbopen_ticlist = ['LL_FRONT','LL_FRONT2']
        pbvol_ticlist = ['LL_FRONT','LL_FRONT2']
        niclose_ticlist = ['LN_FRONT','LN_FRONT2']
        nihigh_ticlist = ['LN_FRONT','LN_FRONT2']
        nilow_ticlist = ['LN_FRONT','LN_FRONT2']
        niopen_ticlist = ['LN_FRONT','LN_FRONT2']
        nivol_ticlist = ['LN_FRONT','LN_FRONT2']
        paclose_ticlist = ['PA_FRONT','PA_FRONT2']
        pahigh_ticlist = ['PA_FRONT','PA_FRONT2']
        palow_ticlist = ['PA_FRONT','PA_FRONT2']  
        paopen_ticlist = ['PA_FRONT','PA_FRONT2']
        pavol_ticlist = ['PA_FRONT','PA_FRONT2']    
        plclose_ticlist = ['PL_FRONT','PL_FRONT2']  
        plhigh_ticlist = ['PL_FRONT','PL_FRONT2'] 
        pllow_ticlist = ['PL_FRONT','PL_FRONT2'] 
        plopen_ticlist = ['PL_FRONT','PL_FRONT2'] 
        plvol_ticlist = ['PL_FRONT','PL_FRONT2']  
        agclose_ticlist = ['SI_FRONT','SI_FRONT2','SI_FRONT3','SI_FRONT4','SI_FRONT5','SI_FRONT6','SI_FRONT7']
        aghigh_ticlist = ['SI_FRONT','SI_FRONT2','SI_FRONT3','SI_FRONT4','SI_FRONT5','SI_FRONT6','SI_FRONT7']
        aglow_ticlist = ['SI_FRONT','SI_FRONT2','SI_FRONT3','SI_FRONT4','SI_FRONT5','SI_FRONT6','SI_FRONT7']
        agopen_ticlist = ['SI_FRONT','SI_FRONT2','SI_FRONT3','SI_FRONT4','SI_FRONT5','SI_FRONT6','SI_FRONT7']
        agvol_ticlist = ['SI_FRONT','SI_FRONT2','SI_FRONT3','SI_FRONT4','SI_FRONT5','SI_FRONT6','SI_FRONT7']
        stclose_ticlist = ['HRC_FRONT','HRC_FRONT2']
        sthigh_ticlist = ['HRC_FRONT','HRC_FRONT2']
        stlow_ticlist = ['HRC_FRONT','HRC_FRONT2']
        stopen_ticlist = ['HRC_FRONT','HRC_FRONT2']
        stvol_ticlist = ['HRC_FRONT','HRC_FRONT2']
        tnclose_ticlist = ['LT_FRONT','LT_FRONT2']
        tnhigh_ticlist = ['LT_FRONT','LT_FRONT2']
        tnlow_ticlist = ['LT_FRONT','LT_FRONT2']
        tnopen_ticlist = ['LT_FRONT','LT_FRONT2']
        tnvol_ticlist = ['LT_FRONT','LT_FRONT2']
        urclose_ticlist = ['UXA_FRONT','UXA_FRONT2']
        urhigh_ticlist = ['UXA_FRONT','UXA_FRONT2']
        urlow_ticlist = ['UXA_FRONT','UXA_FRONT2']
        uropen_ticlist = ['UXA_FRONT','UXA_FRONT2']
        urvol_ticlist = ['UXA_FRONT','UXA_FRONT2']
        znclose_ticlist = ['LX_FRONT','LX_FRONT2']
        znhigh_ticlist = ['LX_FRONT','LX_FRONT2']
        znlow_ticlist = ['LX_FRONT','LX_FRONT2']
        znopen_ticlist = ['LX_FRONT','LX_FRONT2']
        znvol_ticlist = ['LX_FRONT','LX_FRONT2']
        cornclose_ticlist = ['C_FRONT','C_FRONT2','C_FRONT3','C_FRONT4','C_FRONT5','C_FRONT6','C_FRONT7','C_FRONT8','C_FRONT9','C_FRONT10','C_FRONT11','C_FRONT12','C_FRONT13','C_FRONT14','C_FRONT15']
        cornhigh_ticlist = ['C_FRONT','C_FRONT2','C_FRONT3','C_FRONT4','C_FRONT5','C_FRONT6','C_FRONT7','C_FRONT8','C_FRONT9','C_FRONT10','C_FRONT11','C_FRONT12','C_FRONT13','C_FRONT14','C_FRONT15']
        cornlow_ticlist = ['C_FRONT','C_FRONT2','C_FRONT3','C_FRONT4','C_FRONT5','C_FRONT6','C_FRONT7','C_FRONT8','C_FRONT9','C_FRONT10','C_FRONT11','C_FRONT12','C_FRONT13','C_FRONT14','C_FRONT15']
        cornopen_ticlist = ['C_FRONT','C_FRONT2','C_FRONT3','C_FRONT4','C_FRONT5','C_FRONT6','C_FRONT7','C_FRONT8','C_FRONT9','C_FRONT10','C_FRONT11','C_FRONT12','C_FRONT13','C_FRONT14','C_FRONT15']
        cornvol_ticlist = ['C_FRONT','C_FRONT2','C_FRONT3','C_FRONT4','C_FRONT5','C_FRONT6','C_FRONT7','C_FRONT8','C_FRONT9','C_FRONT10','C_FRONT11','C_FRONT12','C_FRONT13','C_FRONT14','C_FRONT15']
        wheatclose_ticlist = ['W_FRONT','W_FRONT2','W_FRONT3','W_FRONT4','W_FRONT5','W_FRONT6','W_FRONT7','W_FRONT8','W_FRONT9','W_FRONT10','W_FRONT11','W_FRONT12','W_FRONT13','W_FRONT14','W_FRONT15']
        wheathigh_ticlist = ['W_FRONT','W_FRONT2','W_FRONT3','W_FRONT4','W_FRONT5','W_FRONT6','W_FRONT7','W_FRONT8','W_FRONT9','W_FRONT10','W_FRONT11','W_FRONT12','W_FRONT13','W_FRONT14','W_FRONT15']
        wheatlow_ticlist = ['W_FRONT','W_FRONT2','W_FRONT3','W_FRONT4','W_FRONT5','W_FRONT6','W_FRONT7','W_FRONT8','W_FRONT9','W_FRONT10','W_FRONT11','W_FRONT12','W_FRONT13','W_FRONT14','W_FRONT15']
        wheatopen_ticlist = ['W_FRONT','W_FRONT2','W_FRONT3','W_FRONT4','W_FRONT5','W_FRONT6','W_FRONT7','W_FRONT8','W_FRONT9','W_FRONT10','W_FRONT11','W_FRONT12','W_FRONT13','W_FRONT14','W_FRONT15']
        wheatvol_ticlist = ['W_FRONT','W_FRONT2','W_FRONT3','W_FRONT4','W_FRONT5','W_FRONT6','W_FRONT7','W_FRONT8','W_FRONT9','W_FRONT10','W_FRONT11','W_FRONT12','W_FRONT13','W_FRONT14','W_FRONT15']        
        soyclose_ticlist = ['S_FRONT','S_FRONT2','S_FRONT3','S_FRONT4','S_FRONT5','S_FRONT6','S_FRONT7','S_FRONT8','S_FRONT9','S_FRONT10','S_FRONT11','S_FRONT12','S_FRONT13','S_FRONT14','S_FRONT15']
        soyhigh_ticlist = ['S_FRONT','S_FRONT2','S_FRONT3','S_FRONT4','S_FRONT5','S_FRONT6','S_FRONT7','S_FRONT8','S_FRONT9','S_FRONT10','S_FRONT11','S_FRONT12','S_FRONT13','S_FRONT14','S_FRONT15']
        soylow_ticlist = ['S_FRONT','S_FRONT2','S_FRONT3','S_FRONT4','S_FRONT5','S_FRONT6','S_FRONT7','S_FRONT8','S_FRONT9','S_FRONT10','S_FRONT11','S_FRONT12','S_FRONT13','S_FRONT14','S_FRONT15']
        soyopen_ticlist = ['S_FRONT','S_FRONT2','S_FRONT3','S_FRONT4','S_FRONT5','S_FRONT6','S_FRONT7','S_FRONT8','S_FRONT9','S_FRONT10','S_FRONT11','S_FRONT12','S_FRONT13','S_FRONT14','S_FRONT15']
        soyvol_ticlist = ['S_FRONT','S_FRONT2','S_FRONT3','S_FRONT4','S_FRONT5','S_FRONT6','S_FRONT7','S_FRONT8','S_FRONT9','S_FRONT10','S_FRONT11','S_FRONT12','S_FRONT13','S_FRONT14','S_FRONT15']
        soclose_ticlist = ['BO_FRONT','BO_FRONT2','BO_FRONT3','BO_FRONT4','BO_FRONT5','BO_FRONT6','BO_FRONT7','BO_FRONT8','BO_FRONT9','BO_FRONT10','BO_FRONT11','BO_FRONT12','BO_FRONT13','BO_FRONT14','BO_FRONT15']
        sohigh_ticlist = ['BO_FRONT','BO_FRONT2','BO_FRONT3','BO_FRONT4','BO_FRONT5','BO_FRONT6','BO_FRONT7','BO_FRONT8','BO_FRONT9','BO_FRONT10','BO_FRONT11','BO_FRONT12','BO_FRONT13','BO_FRONT14','BO_FRONT15']
        solow_ticlist = ['BO_FRONT','BO_FRONT2','BO_FRONT3','BO_FRONT4','BO_FRONT5','BO_FRONT6','BO_FRONT7','BO_FRONT8','BO_FRONT9','BO_FRONT10','BO_FRONT11','BO_FRONT12','BO_FRONT13','BO_FRONT14','BO_FRONT15']
        soopen_ticlist = ['BO_FRONT','BO_FRONT2','BO_FRONT3','BO_FRONT4','BO_FRONT5','BO_FRONT6','BO_FRONT7','BO_FRONT8','BO_FRONT9','BO_FRONT10','BO_FRONT11','BO_FRONT12','BO_FRONT13','BO_FRONT14','BO_FRONT15']
        sovol_ticlist = ['BO_FRONT','BO_FRONT2','BO_FRONT3','BO_FRONT4','BO_FRONT5','BO_FRONT6','BO_FRONT7','BO_FRONT8','BO_FRONT9','BO_FRONT10','BO_FRONT11','BO_FRONT12','BO_FRONT13','BO_FRONT14','BO_FRONT15']
        cotclose_ticlist = ['CT_FRONT','CT_FRONT2','CT_FRONT3','CT_FRONT4','CT_FRONT5','CT_FRONT6','CT_FRONT7']
        cothigh_ticlist = ['CT_FRONT','CT_FRONT2','CT_FRONT3','CT_FRONT4','CT_FRONT5','CT_FRONT6','CT_FRONT7']
        cotlow_ticlist = ['CT_FRONT','CT_FRONT2','CT_FRONT3','CT_FRONT4','CT_FRONT5','CT_FRONT6','CT_FRONT7']
        cotopen_ticlist = ['CT_FRONT','CT_FRONT2','CT_FRONT3','CT_FRONT4','CT_FRONT5','CT_FRONT6','CT_FRONT7']
        cotvol_ticlist = ['CT_FRONT','CT_FRONT2','CT_FRONT3','CT_FRONT4','CT_FRONT5','CT_FRONT6','CT_FRONT7']
        sbclose_ticlist = ['SB_FRONT','SB_FRONT2','SB_FRONT3','SB_FRONT4','SB_FRONT5','SB_FRONT6','SB_FRONT7','SB_FRONT8','SB_FRONT9','SB_FRONT10','SB_FRONT11','SB_FRONT12']
        sbhigh_ticlist = ['SB_FRONT','SB_FRONT2','SB_FRONT3','SB_FRONT4','SB_FRONT5','SB_FRONT6','SB_FRONT7','SB_FRONT8','SB_FRONT9','SB_FRONT10','SB_FRONT11','SB_FRONT12']
        sblow_ticlist = ['SB_FRONT','SB_FRONT2','SB_FRONT3','SB_FRONT4','SB_FRONT5','SB_FRONT6','SB_FRONT7','SB_FRONT8','SB_FRONT9','SB_FRONT10','SB_FRONT11','SB_FRONT12']
        sbopen_ticlist = ['SB_FRONT','SB_FRONT2','SB_FRONT3','SB_FRONT4','SB_FRONT5','SB_FRONT6','SB_FRONT7','SB_FRONT8','SB_FRONT9','SB_FRONT10','SB_FRONT11','SB_FRONT12']
        sbvol_ticlist = ['SB_FRONT','SB_FRONT2','SB_FRONT3','SB_FRONT4','SB_FRONT5','SB_FRONT6','SB_FRONT7','SB_FRONT8','SB_FRONT9','SB_FRONT10','SB_FRONT11','SB_FRONT12']
        sincurrency_ticlist = ['FX_CNY','FX_CNY_1M','FX_CNY_2M','FX_CNY_3M','FX_CNY_6M','FX_CNY_9M','FX_CNY_12M','FX_CNY_2Y','FX_EUR','FX_MYR','FX_DXY']
        crosscurrency_ticlist = ['FX_AUD','FX_BRL','FX_CAD','FX_INR','FX_YEN','FX_RUB']
        equity_ticlist = (['EQUITY_CF']*5)+(['EQUITY_MOS']*5)+(['EQUITY_POT']*5)
        sent_ticlist = ['INDEX_USCONSCOMFORT','INDEX_INDU','INDEX_DTN-SENTIMENTS_AG-CROP-EXPECT','INDEX_DTN-SENTIMENTS_AG-CROP-PRESENT']+(['INDEX_ISEE_MRKT-SENTIMENTS']*6) + ['INDEX_NDX','INDEX_SPX','INDEX_SHCOMP']
        imammtot_ticlist = ['AMM_WOR_USA','AMM_WOR_CHN','AMM_DZA_USA','AMM_ARG_USA','AMM_AUS_USA','AMM_BHR_USA','AMM_BEL_USA','AMM_BRA_USA','AMM_CAN_USA','AMM_CYM_USA','AMM_CHL_USA','AMM_CHN_USA','AMM_COL_USA','AMM_EGY_USA',
                            'AMM_EST_USA','AMM_FRA_USA','AMM_DEU_USA','AMM_GRC_USA','AMM_HUN_USA','AMM_IDN_USA','AMM_ITA_USA','AMM_JPN_USA','AMM_KWT_USA','AMM_LVA_USA','AMM_LBY_USA','AMM_LTU_USA','AMM_MYS_USA','AMM_MEX_USA',
                            'AMM_NLD_USA','AMM_NOR_USA','AMM_OMN_USA','AMM_PER_USA','AMM_PRT_USA','AMM_QAT_USA','AMM_KOR_USA','AMM_RUS_USA','AMM_SAU_USA','AMM_SGP_USA','AMM_ESP_USA','AMM_CHE_USA','AMM_TWN_USA','AMM_THA_USA',
                            'AMM_TTO_USA','AMM_TUR_USA','AMM_UKR_USA','AMM_ARE_USA','AMM_GBR_USA','AMM_VEN_USA']
        imamman_ticlist = ['AMM_AHYD_WOR_USA','AMM_AHYD_DZA_USA','AMM_AHYD_ARG_USA','AMM_AHYD_AUS_USA','AMM_AHYD_BHR_USA','AMM_AHYD_BEL_USA','AMM_AHYD_BRA_USA','AMM_AHYD_CAN_USA','AMM_AHYD_CYM_USA','AMM_AHYD_CHL_USA',
                           'AMM_AHYD_CHN_USA','AMM_AHYD_COL_USA','AMM_AHYD_EGY_USA','AMM_AHYD_EST_USA','AMM_AHYD_FRA_USA','AMM_AHYD_DEU_USA','AMM_AHYD_GRC_USA','AMM_AHYD_HUN_USA','AMM_AHYD_IDN_USA','AMM_AHYD_ITA_USA',
                           'AMM_AHYD_JPN_USA','AMM_AHYD_KWT_USA','AMM_AHYD_LVA_USA','AMM_AHYD_LBY_USA','AMM_AHYD_LTU_USA','AMM_AHYD_MYS_USA','AMM_AHYD_MEX_USA','AMM_AHYD_NLD_USA','AMM_AHYD_NOR_USA','AMM_AHYD_OMN_USA',
                           'AMM_AHYD_PER_USA','AMM_AHYD_PRT_USA','AMM_AHYD_QAT_USA','AMM_AHYD_KOR_USA','MM_AHYD_RUS_USA','AMM_AHYD_SAU_USA','AMM_AHYD_SGP_USA','AMM_AHYD_ESP_USA','AMM_AHYD_CHE_USA','AMM_AHYD_TWN_USA',
                           'AMM_AHYD_THA_USA','AMM_AHYD_TTO_USA','AMM_AHYD_TUR_USA','AMM_AHYD_UKR_USA','AMM_AHYD_ARE_USA','AMM_AHYD_GBR_USA','AMM_AHYD_VEN_USA']                    
        imammnittot_ticlist = ['AMNT_WOR_USA','AMNT_AUS_USA','AMNT_AUT_USA','AMNT_BHR_USA','AMNT_BEL_USA','AMNT_BRA_USA','AMNT_BGR_USA','AMNT_CAN_USA','AMNT_CHL_USA','AMNT_CHN_USA','AMNT_COL_USA','AMNT_CRI_USA','AMNT_DNK_USA',
                               'AMNT_DOM_USA','AMNT_EGY_USA','AMNT_EST_USA','AMNT_FRA_USA','AMNT_GEO_USA','AMNT_DEU_USA','AMNT_GRC_USA','AMNT_HKG_USA','AMNT_IND_USA','AMNT_IRL_USA','AMNT_ITA_USA','AMNT_JPN_USA','AMNT_LBN_USA',
                               'AMNT_LBY_USA','AMNT_LTU_USA','AMNT_MEX_USA','AMNT_NLD_USA','AMNT_NER_USA','AMNT_NGA_USA','AMNT_NOR_USA','AMNT_PAK_USA','AMNT_PER_USA','AMNT_POL_USA','AMNT_QAT_USA','AMNT_ROU_USA','AMNT_RUS_USA',
                               'AMNT_SLB_USA','AMNT_ZAF_USA','AMNT_ESP_USA','AMNT_SWE_USA','AMNT_CHE_USA','AMNT_TWN_USA','AMNT_TTO_USA','AMNT_TUN_USA','AMNT_TUR_USA','AMNT_UKR_USA','AMNT_GBR_USA','AMNT_VEN_USA']
        imammnitaq_ticlist = ['AMNT_AQUES_WOR_USA','AMNT_AQUES_AUS_USA','AMNT_AQUES_AUT_USA','AMNT_AQUES_BHR_USA','AMNT_AQUES_BEL_USA','AMNT_AQUES_BRA_USA','AMNT_AQUES_BGR_USA','AMNT_AQUES_CAN_USA','AMNT_AQUES_CHL_USA','AMNT_AQUES_CHN_USA','AMNT_AQUES_COL_USA','AMNT_AQUES_CRI_USA','AMNT_AQUES_DNK_USA',
                               'AMNT_AQUES_DOM_USA','AMNT_AQUES_EGY_USA','AMNT_AQUES_EST_USA','AMNT_AQUES_FRA_USA','AMNT_AQUES_GEO_USA','AMNT_AQUES_DEU_USA','AMNT_AQUES_GRC_USA','AMNT_AQUES_HKG_USA','AMNT_AQUES_IND_USA','AMNT_AQUES_IRL_USA','AMNT_AQUES_ITA_USA','AMNT_AQUES_JPN_USA','AMNT_AQUES_LBN_USA',
                               'AMNT_AQUES_LBY_USA','AMNT_AQUES_LTU_USA','AMNT_AQUES_MEX_USA','AMNT_AQUES_NLD_USA','AMNT_AQUES_NER_USA','AMNT_AQUES_NGA_USA','AMNT_AQUES_NOR_USA','AMNT_AQUES_PAK_USA','AMNT_AQUES_PER_USA','AMNT_AQUES_POL_USA','AMNT_AQUES_QAT_USA','AMNT_AQUES_ROU_USA','AMNT_AQUES_RUS_USA',
                               'AMNT_AQUES_SLB_USA','AMNT_AQUES_ZAF_USA','AMNT_AQUES_ESP_USA','AMNT_AQUES_SWE_USA','AMNT_AQUES_CHE_USA','AMNT_AQUES_TWN_USA','AMNT_AQUES_TTO_USA','AMNT_AQUES_TUN_USA','AMNT_AQUES_TUR_USA','AMNT_AQUES_UKR_USA','AMNT_AQUES_GBR_USA','AMNT_AQUES_VEN_USA']
        imammsu_ticlist = ['AMSF_WOR_USA','AMSF_AUS_USA','AMSF_BLR_USA','AMSF_BEL_USA','AMSF_BRA_USA','AMSF_CAN_USA','AMSF_CHN_USA','AMSF_COL_USA','AMSF_CRI_USA','AMSF_CZE_USA','AMSF_DNK_USA','AMSF_DOM_USA','AMSF_EGY_USA','AMSF_FIN_USA','AMSF_FRA_USA','AMSF_GEO_USA','AMSF_DEU_USA','AMSF_GRC_USA',
                           'AMSF_HKG_USA','AMSF_IND_USA','AMSF_IDN_USA','AMSF_ITA_USA','AMSF_JAM_USA','AMSF_JPN_USA','AMSF_KWT_USA','AMSF_LTU_USA','AMSF_MEX_USA','AMSF_NLD_USA','AMSF_NER_USA','AMSF_NOR_USA','AMSF_POL_USA','AMSF_KOR_USA','AMSF_RUS_USA','AMSF_SAU_USA','AMSF_ZAF_USA','AMSF_ESP_USA',
                           'AMSF_SWE_USA','AMSF_CHE_USA','AMSF_TWN_USA','AMSF_TTO_USA','AMSF_GBR_USA','AMSF_VEN_USA']
        imdap_ticlist = ['DAP_WOR_AFR','DAP_WOR_EUR-CTL','DAP_WOR_CHN','DAP_WOR_ASIA-E','DAP_WOR_EUR-E-ASIA-CTL','DAP_WOR_E25','DAP_WOR_LTA','DAP_WOR_NA','DAP_WOR_OCE','DAP_WOR_ASIA-S','DAP_WOR_USA','DAP_WOR_ASIA-W','DAP_WOR_EUR-W','DAP_BEL_USA','DAP_CAN_USA','DAP_CHN_USA','DAP_CZE_USA','DAP_DNK_USA',
                         'DAP_DOM_USA','DAP_FRA_USA','DAP_DEU_USA','DAP_HKG_USA','DAP_IND_USA','DAP_ITA_USA','DAP_JAM_USA','DAP_JPN_USA','DAP_LTU_USA','DAP_MYS_USA','DAP_MEX_USA','DAP_MAR_USA','DAP_NLD_USA','DAP_RUS_USA','DAP_ESP_USA','DAP_SWE_USA','DAP_CHE_USA','DAP_TWN_USA','DAP_TUN_USA','DAP_UKR_USA','DAP_GBR_USA']
        imint_ticlist = ['ITF_WOR_BRA','NPK_WOR_CHN']
        immaptot_ticlist = ['MAP_WOR_AFR','MAP_WOR_EUR-CTL','MAP_WOR_CHN','MAP_WOR_ASIA-E','MAP_WOR_EUR-E-ASIA-CTL','MAP_WOR_E25','MAP_WOR_LTA','MAP_WOR_NA','MAP_WOR_OCE','MAP_WOR_ASIA-S','MAP_WOR_USA','MAP_WOR_VAR','MAP_WOR_ASIA-W','MAP_WOR_EUR-W','MAP_ARG_USA','MAP_AUS_USA','MAP_BLR_USA','MAP_BEL_USA','MAP_CAN_USA',
                            'MAP_CHN_USA','MAP_COL_USA','MAP_DNK_USA','MAP_DOM_USA','MAP_EST_USA','MAP_FIN_USA','MAP_FRA_USA','MAP_DEU_USA','MAP_HKG_USA','MAP_IND_USA','MAP_ISR_USA','MAP_ITA_USA','MAP_JPN_USA','MAP_MUS_USA','MAP_MEX_USA','MAP_MAR_USA','MAP_NLD_USA','MAP_PER_USA','MAP_POL_USA','MAP_KOR_USA',
                            'MAP_RUS_USA','MAP_SVK_USA','MAP_ESP_USA','MAP_CHE_USA','MAP_TWN_USA','MAP_THA_USA','MAP_UKR_USA','MAP_GBR_USA']
        immapmix_ticlist = ['MAP_OMDAP_WOR_USA','MAP_OMDAP_AUS_USA','MAP_OMDAP_BEL_USA','MAP_OMDAP_CAN_USA','MAP_OMDAP_CHN_USA','MAP_OMDAP_DNK_USA','MAP_OMDAP_FIN_USA','MAP_OMDAP_DEU_USA','MAP_OMDAP_HKG_USA','MAP_OMDAP_ISR_USA','MAP_OMDAP_ITA_USA','MAP_OMDAP_JPN_USA','MAP_OMDAP_MEX_USA','MAP_OMDAP_MAR_USA',
                            'MAP_OMDAP_NLD_USA','MAP_OMDAP_PER_USA','MAP_OMDAP_RUS_USA','MAP_OMDAP_ESP_USA','MAP_OMDAP_THA_USA','MAP_OMDAP_UKR_USA','MAP_OMDAP_GBR_USA']
        imphosac_ticlist = ['PHO-ACD_TOT_WOR','PHO-ACD_WOR_AFR','PHO-ACD_WOR_EUR-CTL','PHO-ACD_WOR_ASIA-E','PHO-ACD_WOR_EUR-E-ASIA-CTL','PHO-ACD_WOR_E25','PHO-ACD_WOR_LTA','PHO-ACD_WOR_NA','PHO-ACD_WOR_OCE','PHO-ACD_WOR_ASIA-S','PHO-ACD_WOR_ASIA-W','PHO-ACD_WOR_EUR-W']
        impot_ticlist = ['POT_TOT_WOR','POT_WOR_AFR','POT_WOR_EUR-CTL','POT_WOR_CHN','POT_WOR_ASIA-E','POT_WOR_EUR-E-ASIA-CTL','POT_WOR_E25','POT_WOR_LTA','POT_WOR_NA','POT_WOR_OCE','POT_WOR_ASIA-S','POT_WOR_USA','POT_WOR_ASIA-W','POT_WOR_EUR-W','POT_AUS_USA','POT_BLR_USA','POT_BEL_USA','POT_BGR_USA',
                         'POT_CMR_USA','POT_CAN_USA','POT_CHL_USA','POT_CHN_USA','POT_CZE_USA','POT_DNK_USA','POT_ETH_USA','POT_FRA_USA','POT_GEO_USA','POT_DEU_USA','POT_ISL_USA','POT_IND_USA','POT_ISR_USA','POT_ITA_USA','POT_JPN_USA','POT_JOR_USA','POT_LAO_USA','POT_LVA_USA','POT_LTU_USA',
                         'POT_MEX_USA','POT_NLD_USA','POT_NOR_USA','POT_ROU_USA','POT_RUS_USA','POT_SYC_USA','POT_SVK_USA','POT_ESP_USA','POT_SWE_USA','POT_CHE_USA','POT_GBR_USA','POT_VEN_USA']
        imtsptot_ticlist = ['TSP_WOR_USA','TSP_AUS_USA','TSP_BEL_USA','TSP_BGR_USA','TSP_CAN_USA','TSP_CHN_USA','TSP_DOM_USA','TSP_EGY_USA','TSP_FRA_USA','TSP_GEO_USA','TSP_DEU_USA','TSP_GRC_USA','TSP_IND_USA','TSP_ISR_USA','TSP_ITA_USA','TSP_JPN_USA','TSP_LBN_USA','TSP_MEX_USA','TSP_MAR_USA','TSP_NLD_USA',
                            'TSP_NZL_USA','TSP_RUS_USA','TSP_ESP_USA','TSP_SWE_USA','TSP_TWN_USA','TSP_TGO_USA','TSP_TUN_USA','TSP_ARE_USA','TSP_GBR_USA']
        imtspless_ticlist = ['TSP_T-LT40_WOR_USA','TSP_T-LT40_CAN_USA','TSP_T-LT40_CHN_USA','TSP_T-LT40_EGY_USA','TSP_T-LT40_FRA_USA','TSP_T-LT40_IND_USA','TSP_T-LT40_ISR_USA','TSP_T-LT40_ITA_USA','TSP_T-LT40_JPN_USA','SP_T-LT40_LBN_USA','TSP_T-LT40_MEX_USA','TSP_T-LT40_NLD_USA','TSP_T-LT40_NZL_USA',
                             'TSP_T-LT40_ESP_USA','TSP_T-LT40_SWE_USA','TSP_T-LT40_TUN_USA','TSP_T-LT40_GBR_USA']
        imtspgreat_ticlist = ['TSP_T-GE40_WOR_USA','TSP_T-GE40_AUS_USA','TSP_T-GE40_BEL_USA','TSP_T-GE40_BGR_USA','TSP_T-GE40_CAN_USA','TSP_T-GE40_CHN_USA','TSP_T-GE40_DOM_USA','TSP_T-GE40_EGY_USA','TSP_T-GE40_FRA_USA','TSP_T-GE40_GEO_USA','TSP_T-GE40_DEU_USA','TSP_T-GE40_GRC_USA','TSP_T-GE40_IND_USA',
                              'TSP_T-GE40_ISR_USA','TSP_T-GE40_ITA_USA','TSP_T-GE40_JPN_USA','TSP_T-GE40_LBN_USA','TSP_T-GE40_MEX_USA','TSP_T-GE40_MAR_USA','TSP_T-GE40_NLD_USA','TSP_T-GE40_RUS_USA','TSP_T-GE40_ESP_USA','TSP_T-GE40_TWN_USA','TSP_T-GE40_TGO_USA','TSP_T-GE40_TUN_USA','TSP_T-GE40_ARE_USA','TSP_T-GE40_GBR_USA']
        imuantot_ticlist = ['UAN_WOR_USA','UAN_DZA_USA','UAN_BHR_USA','UAN_BLR_USA','UAN_BEL_USA','UAN_BGR_USA','UAN_CAN_USA','UAN_CHN_USA','UAN_EGY_USA','UAN_EST_USA','UAN_FRA_USA','UAN_GEO_USA','UAN_DEU_USA','UAN_IND_USA','UAN_IDN_USA','UAN_IRL_USA','UAN_JPN_USA','UAN_LVA_USA','UAN_LIE_USA','UAN_LTU_USA',
                            'UAN_MYS_USA','UAN_MEX_USA','UAN_NLD_USA','UAN_NOR_USA','UAN_OMN_USA','UAN_POL_USA','UAN_QAT_USA','UAN_ROU_USA','UAN_RUS_USA','UAN_SAU_USA','UAN_ZAF_USA','UAN_ESP_USA','UAN_SUR_USA','UAN_CHE_USA','UAN_TTO_USA','UAN_TUR_USA','UAN_UKR_USA','UAN_ARE_USA','UAN_GBR_USA','UAN_VEN_USA']
        imuanmix_ticlist = ['UAN_MUNAN_WOR_USA','UAN_MUNAN_DZA_USA','UAN_MUNAN_BHR_USA','UAN_MUNAN_BLR_USA','UAN_MUNAN_BEL_USA','UAN_MUNAN_BGR_USA','UAN_MUNAN_CAN_USA','UAN_MUNAN_CHN_USA','UAN_MUNAN_EGY_USA','UAN_MUNAN_EST_USA','UAN_MUNAN_FRA_USA','UAN_MUNAN_GEO_USA','UAN_MUNAN_DEU_USA','UAN_MUNAN_IND_USA',
                            'UAN_MUNAN_IDN_USA','UAN_MUNAN_IRL_USA','UAN_MUNAN_JPN_USA','UAN_MUNAN_LVA_USA','UAN_MUNAN_LIE_USA','UAN_MUNAN_LTU_USA','UAN_MUNAN_MYS_USA','UAN_MUNAN_MEX_USA','UAN_MUNAN_NLD_USA','UAN_MUNAN_NOR_USA','UAN_MUNAN_OMN_USA','UAN_MUNAN_POL_USA','UAN_MUNAN_QAT_USA','UAN_MUNAN_ROU_USA',
                            'UAN_MUNAN_RUS_USA','UAN_MUNAN_SAU_USA','UAN_MUNAN_ZAF_USA','UAN_MUNAN_ESP_USA','UAN_MUNAN_SUR_USA','UAN_MUNAN_CHE_USA','UAN_MUNAN_TTO_USA','UAN_MUNAN_TUR_USA','UAN_MUNAN_UKR_USA','UAN_MUNAN_ARE_USA','UAN_MUNAN_GBR_USA','UAN_MUNAN_VEN_USA']
        imureatot_ticlist = ['UREA_TOT_WOR','UREA_WOR_AFR','UREA_WOR_EUR-CTL','UREA_WOR_ASIA-E','UREA_WOR_EUR-E-ASIA-CTL','UREA_WOR_E25','UREA_WOR_LTA','UREA_WOR_NA','UREA_WOR_OCE','UREA_WOR_ASIA-S','UREA_WOR_USA','UREA_WOR_ASIA-W','UREA_WOR_EUR-W','UREA_DZA_USA','UREA_ARG_USA','UREA_AUS_USA','UREA_AUT_USA',
                             'UREA_BHS_USA','UREA_BHR_USA','UREA_BGD_USA','UREA_BLR_USA','UREA_BEL_USA','UREA_BLZ_USA','UREA_BIH_USA','UREA_BRA_USA','UREA_BGR_USA','UREA_CAN_USA','UREA_TCD_USA','UREA_CHL_USA','UREA_CHN_USA','UREA_HRV_USA','UREA_DNK_USA','UREA_DOM_USA','UREA_EGY_USA','UREA_EST_USA',
                             'UREA_FIN_USA','UREA_FRA_USA','UREA_GEO_USA','UREA_DEU_USA','UREA_GRC_USA','UREA_HKG_USA','UREA_IND_USA','UREA_IDN_USA','UREA_IRL_USA','UREA_ISR_USA','UREA_ITA_USA','UREA_JAM_USA','UREA_JPN_USA','UREA_KWT_USA','UREA_LVA_USA','UREA_LBY_USA','UREA_LIE_USA','UREA_LTU_USA',
                             'UREA_LUX_USA','UREA_MYS_USA','UREA_MEX_USA','UREA_NAM_USA','UREA_NLD_USA','UREA_NER_USA','UREA_NGA_USA','UREA_NOR_USA','UREA_OMN_USA','UREA_PHL_USA','UREA_POL_USA','UREA_QAT_USA','UREA_KOR_USA','UREA_ROU_USA','UREA_RUS_USA','UREA_SAU_USA','UREA_SGP_USA','UREA_SVK_USA',
                             'UREA_ZAF_USA','UREA_ESP_USA','UREA_CHE_USA','UREA_TWN_USA','UREA_THA_USA','UREA_TTO_USA','UREA_TUR_USA','UREA_TKM_USA','UREA_UKR_USA','UREA_ARE_USA','UREA_GBR_USA','UREA_VEN_USA']
        imureadef_ticlist = ['UREA_DEF_WOR_USA','UREA_DEF_CAN_USA','UREA_DEF_CHN_USA','UREA_DEF_EGY_USA','UREA_DEF_DEU_USA','UREA_DEF_NLD_USA','UREA_DEF_QAT_USA','UREA_DEF_TTO_USA']
        imureanesoi_ticlist = ['UREA_NESOI_WOR_USA','UREA_NESOI_DZA_USA','UREA_NESOI_BHR_USA','UREA_NESOI_BRA_USA','UREA_NESOI_CAN_USA','UREA_NESOI_CHN_USA','UREA_NESOI_HRV_USA','UREA_NESOI_DOM_USA','UREA_NESOI_EGY_USA','UREA_NESOI_FIN_USA','UREA_NESOI_FRA_USA','UREA_NESOI_DEU_USA','UREA_NESOI_HKG_USA',
                               'UREA_NESOI_IND_USA','UREA_NESOI_IDN_USA','UREA_NESOI_JPN_USA','UREA_NESOI_KWT_USA','UREA_NESOI_LBY_USA','UREA_NESOI_LTU_USA','UREA_NESOI_MEX_USA','UREA_NESOI_NLD_USA','UREA_NESOI_OMN_USA','UREA_NESOI_POL_USA','UREA_NESOI_QAT_USA','UREA_NESOI_KOR_USA','UREA_NESOI_RUS_USA',
                               'UREA_NESOI_SAU_USA','UREA_NESOI_SVK_USA','UREA_NESOI_ESP_USA','UREA_NESOI_CHE_USA','UREA_NESOI_TTO_USA','UREA_NESOI_TKM_USA','UREA_NESOI_ARE_USA','UREA_NESOI_GBR_USA','UREA_NESOI_VEN_USA']
        imureasolid_ticlist = ['UREA_SOLID_WOR_USA','UREA_SOLID_DZA_USA','UREA_SOLID_AUT_USA','UREA_SOLID_BHR_USA','UREA_SOLID_BRA_USA','UREA_SOLID_CAN_USA','UREA_SOLID_CHN_USA','UREA_SOLID_HRV_USA','UREA_SOLID_DOM_USA','UREA_SOLID_EGY_USA','UREA_SOLID_FIN_USA','UREA_SOLID_DEU_USA','UREA_SOLID_GRC_USA',
                               'UREA_SOLID_HKG_USA','UREA_SOLID_IND_USA','UREA_SOLID_IDN_USA','UREA_SOLID_IRL_USA','UREA_SOLID_ISR_USA','UREA_SOLID_JPN_USA','UREA_SOLID_KWT_USA','UREA_SOLID_LBY_USA','UREA_SOLID_LTU_USA','UREA_SOLID_MYS_USA','UREA_SOLID_MEX_USA','UREA_SOLID_NLD_USA','UREA_SOLID_NGA_USA',
                               'UREA_SOLID_OMN_USA','UREA_SOLID_QAT_USA','UREA_SOLID_RUS_USA','UREA_SOLID_SAU_USA','UREA_SOLID_CHE_USA','UREA_SOLID_TTO_USA','UREA_SOLID_ARE_USA','UREA_SOLID_VEN_USA']
        imureaaq_ticlist = ['UREA_AQUES_WOR_USA','UREA_AQUES_ARG_USA','UREA_AQUES_AUS_USA','UREA_AQUES_AUT_USA','UREA_AQUES_BHS_USA','UREA_AQUES_BHR_USA','UREA_AQUES_BGD_USA','UREA_AQUES_BLR_USA','UREA_AQUES_BEL_USA','UREA_AQUES_BLZ_USA','UREA_AQUES_BIH_USA','UREA_AQUES_BRA_USA','UREA_AQUES_BGR_USA',
                            'UREA_AQUES_CAN_USA','UREA_AQUES_TCD_USA','UREA_AQUES_CHL_USA','UREA_AQUES_CHN_USA','UREA_AQUES_HRV_USA','UREA_AQUES_DNK_USA','UREA_AQUES_DOM_USA','UREA_AQUES_EGY_USA','UREA_AQUES_EST_USA','UREA_AQUES_FIN_USA','UREA_AQUES_FRA_USA','UREA_AQUES_GEO_USA','UREA_AQUES_DEU_USA',
                            'UREA_AQUES_HKG_USA','UREA_AQUES_IND_USA','UREA_AQUES_IDN_USA','UREA_AQUES_IRL_USA','UREA_AQUES_ISR_USA','UREA_AQUES_ITA_USA','UREA_AQUES_JAM_USA','UREA_AQUES_JPN_USA','UREA_AQUES_KWT_USA','UREA_AQUES_LVA_USA','UREA_AQUES_LBY_USA','UREA_AQUES_LIE_USA','UREA_AQUES_LTU_USA',
                            'UREA_AQUES_LUX_USA','UREA_AQUES_MYS_USA','UREA_AQUES_MEX_USA','UREA_AQUES_NAM_USA','UREA_AQUES_NLD_USA','UREA_AQUES_NER_USA','UREA_AQUES_NGA_USA','UREA_AQUES_NOR_USA','UREA_AQUES_OMN_USA','UREA_AQUES_PHL_USA','UREA_AQUES_POL_USA','UREA_AQUES_QAT_USA','UREA_AQUES_KOR_USA',
                            'UREA_AQUES_ROU_USA','UREA_AQUES_RUS_USA','UREA_AQUES_SAU_USA','UREA_AQUES_SGP_USA','UREA_AQUES_SVK_USA','UREA_AQUES_ZAF_USA','UREA_AQUES_ESP_USA','UREA_AQUES_CHE_USA','UREA_AQUES_TWN_USA','UREA_AQUES_THA_USA','UREA_AQUES_TTO_USA','UREA_AQUES_TUR_USA','UREA_AQUES_UKR_USA',
                            'UREA_AQUES_ARE_USA','UREA_AQUES_GBR_USA','UREA_AQUES_VEN_USA']
        exammtot_ticlist = ['AMM_CAN_WOR','AMM_CAN_GRL','AMM_CAN_JPN','AMM_CAN_MEX','AMM_CAN_NOR','AMM_CAN_PHL','AMM_CAN_KOR','AMM_CAN_SPM','AMM_CAN_TWN','AMM_CAN_USA','AMM_USA_WOR','AMM_USA_AGO','AMM_USA_ATG','AMM_USA_ABW','AMM_USA_AUS','AMM_USA_AUT','AMM_USA_BHS','AMM_USA_BRB','AMM_USA_BEL','AMM_USA_BLZ',
                            'AMM_USA_BRA','AMM_USA_VGB','AMM_USA_CAN','AMM_USA_CHL','AMM_USA_CHN','AMM_USA_COL','AMM_USA_CRI','AMM_USA_DOM','AMM_USA_FRA','AMM_USA_DEU','AMM_USA_GUY','AMM_USA_HTI','AMM_USA_HND','AMM_USA_HKG','AMM_USA_IND','AMM_USA_IRL','AMM_USA_ISR','AMM_USA_ITA','AMM_USA_JAM','AMM_USA_JPN',
                            'AMM_USA_JOR','AMM_USA_KWT','AMM_USA_LBR','AMM_USA_MDG','AMM_USA_MHL','AMM_USA_MEX','AMM_USA_MAR','AMM_USA_NLD-CUR','AMM_USA_NLD','AMM_USA_ANT','AMM_USA_NGA','AMM_USA_NOR','AMM_USA_PAN','AMM_USA_PER','AMM_USA_POL','AMM_USA_QAT','AMM_USA_KOR','AMM_USA_ROU','AMM_USA_RUS','AMM_USA_KNA',
                            'AMM_USA_SAU','AMM_USA_SGP','AMM_USA_ESP','AMM_USA_SUR','AMM_USA_SWE','AMM_USA_TWN','AMM_USA_THA','AMM_USA_TTO','AMM_USA_TUR','AMM_USA_ARE','AMM_USA_GBR','AMM_USA_VEN']
        examman_ticlist = ['AMM_AHYD_USA_WOR','AMM_AHYD_USA_AGO','AMM_AHYD_USA_ATG','AMM_AHYD_USA_ABW','AMM_AHYD_USA_AUS','AMM_AHYD_USA_AUT','AMM_AHYD_USA_BHS','AMM_AHYD_USA_BRB','AMM_AHYD_USA_BEL','AMM_AHYD_USA_BLZ','AMM_AHYD_USA_BRA','AMM_AHYD_USA_VGB','AMM_AHYD_USA_CAN','AMM_AHYD_USA_CHL','AMM_AHYD_USA_CHN',
                           'AMM_AHYD_USA_COL','AMM_AHYD_USA_CRI','AMM_AHYD_USA_DOM','AMM_AHYD_USA_FRA','AMM_AHYD_USA_DEU','AMM_AHYD_USA_GUY','AMM_AHYD_USA_HTI','AMM_AHYD_USA_HND','AMM_AHYD_USA_HKG','AMM_AHYD_USA_IND','AMM_AHYD_USA_IRL','AMM_AHYD_USA_ISR','AMM_AHYD_USA_ITA','AMM_AHYD_USA_JAM','AMM_AHYD_USA_JPN',
                           'AMM_AHYD_USA_JOR','AMM_AHYD_USA_KWT','AMM_AHYD_USA_LBR','AMM_AHYD_USA_MDG','AMM_AHYD_USA_MHL','AMM_AHYD_USA_MEX','AMM_AHYD_USA_MAR','AMM_AHYD_USA_NLD-CUR','AMM_AHYD_USA_NLD','AMM_AHYD_USA_ANT','AMM_AHYD_USA_NGA','AMM_AHYD_USA_NOR','AMM_AHYD_USA_PAN','AMM_AHYD_USA_PER',
                           'AMM_AHYD_USA_POL','AMM_AHYD_USA_QAT','AMM_AHYD_USA_KOR','AMM_AHYD_USA_ROU','AMM_AHYD_USA_RUS','AMM_AHYD_USA_KNA','AMM_AHYD_USA_SAU','AMM_AHYD_USA_SGP','AMM_AHYD_USA_ESP','AMM_AHYD_USA_SUR','AMM_AHYD_USA_SWE','AMM_AHYD_USA_TWN','AMM_AHYD_USA_THA','AMM_AHYD_USA_TTO','AMM_AHYD_USA_TUR',
                           'AMM_AHYD_USA_ARE','AMM_AHYD_USA_GBR','AMM_AHYD_USA_VEN']
        exammnittot_ticlist = ['AMNT_USA_WOR','AMNT_USA_AFG','AMNT_USA_AIA','AMNT_USA_ATG','AMNT_USA_ARG','AMNT_USA_AUS','AMNT_USA_AUT','AMNT_USA_BHS','AMNT_USA_BEL','AMNT_USA_BLZ','AMNT_USA_BRA','AMNT_USA_VGB','AMNT_USA_CAN','AMNT_USA_CYM','AMNT_USA_CHN','AMNT_USA_COL','AMNT_USA_CRI','AMNT_USA_DMA',
                               'AMNT_USA_DOM','AMNT_USA_ECU','AMNT_USA_ETH','AMNT_USA_FRA','AMNT_USA_PYF','AMNT_USA_DEU','AMNT_USA_GTM','AMNT_USA_HND','AMNT_USA_HKG','AMNT_USA_IDN','AMNT_USA_ISR','AMNT_USA_JAM','AMNT_USA_MEX','AMNT_USA_NLD','AMNT_USA_NZL','AMNT_USA_PAN','AMNT_USA_PHL','AMNT_USA_QAT',
                               'AMNT_USA_KOR','AMNT_USA_LCA','AMNT_USA_VCT','AMNT_USA_SGP','AMNT_USA_TWN','AMNT_USA_TUR','AMNT_USA_UKR','AMNT_USA_GBR']
        exammnitaq_ticlist = ['AMNT_AQUES_USA_WOR','AMNT_AQUES_USA_AFG','AMNT_AQUES_USA_AIA','AMNT_AQUES_USA_ATG','AMNT_AQUES_USA_ARG','AMNT_AQUES_USA_AUS','AMNT_AQUES_USA_AUT','AMNT_AQUES_USA_BHS','AMNT_AQUES_USA_BEL','AMNT_AQUES_USA_BLZ','AMNT_AQUES_USA_BRA','AMNT_AQUES_USA_VGB','AMNT_AQUES_USA_CAN',
                              'AMNT_AQUES_USA_CYM','AMNT_AQUES_USA_CHN','AMNT_AQUES_USA_COL','AMNT_AQUES_USA_CRI','AMNT_AQUES_USA_DMA','AMNT_AQUES_USA_DOM','AMNT_AQUES_USA_ECU','AMNT_AQUES_USA_ETH','AMNT_AQUES_USA_FRA','AMNT_AQUES_USA_PYF','AMNT_AQUES_USA_DEU','AMNT_AQUES_USA_GTM','AMNT_AQUES_USA_HND',
                              'AMNT_AQUES_USA_HKG','AMNT_AQUES_USA_IDN','AMNT_AQUES_USA_ISR','AMNT_AQUES_USA_JAM','AMNT_AQUES_USA_MEX','AMNT_AQUES_USA_NLD','AMNT_AQUES_USA_NZL','AMNT_AQUES_USA_PAN','AMNT_AQUES_USA_PHL','AMNT_AQUES_USA_QAT','AMNT_AQUES_USA_KOR','AMNT_AQUES_USA_LCA','AMNT_AQUES_USA_VCT',
                              'AMNT_AQUES_USA_SGP','AMNT_AQUES_USA_TWN','AMNT_AQUES_USA_TUR','AMNT_AQUES_USA_UKR','AMNT_AQUES_USA_GBR']
        exammsu_ticlist = ['AMSF_CAN_WOR','AMSF_CAN_ARG','AMSF_CAN_AUS','AMSF_CAN_BMU','AMSF_CAN_BRA','AMSF_CAN_CRI','AMSF_CAN_SLV','AMSF_CAN_FJI','AMSF_CAN_FRA','AMSF_CAN_DEU','AMSF_CAN_GTM','AMSF_CAN_GUY','AMSF_CAN_IDN','AMSF_CAN_JPN','AMSF_CAN_MYS','AMSF_CAN_MEX','AMSF_CAN_NZL','AMSF_CAN_PHL',
                           'AMSF_CAN_RUS','AMSF_CAN_SGP','AMSF_CAN_THA','AMSF_CAN_USA','AMSF_USA_WOR','AMSF_USA_ARG','AMSF_USA_AUS','AMSF_USA_AUT','AMSF_USA_BHS','AMSF_USA_BRB','AMSF_USA_BEL','AMSF_USA_BLZ','AMSF_USA_BOL','AMSF_USA_BIH','AMSF_USA_BRA','AMSF_USA_CMR','AMSF_USA_CAN','AMSF_USA_CYM',
                           'AMSF_USA_CHL','AMSF_USA_CHN','AMSF_USA_COL','AMSF_USA_CRI','AMSF_USA_CIV','AMSF_USA_DNK','AMSF_USA_DOM','AMSF_USA_ECU','AMSF_USA_SLV','AMSF_USA_ETH','AMSF_USA_FRA','AMSF_USA_DEU','AMSF_USA_GHA','AMSF_USA_GTM','AMSF_USA_GUY','AMSF_USA_HTI','AMSF_USA_HND','AMSF_USA_HKG',
                           'AMSF_USA_IND','AMSF_USA_IRL','AMSF_USA_ISR','AMSF_USA_JAM','AMSF_USA_JPN','AMSF_USA_MEX','AMSF_USA_MOZ','AMSF_USA_NAM','AMSF_USA_NLD-CUR','AMSF_USA_NLD','AMSF_USA_ANT','AMSF_USA_NZL','AMSF_USA_NIC','AMSF_USA_NGA','AMSF_USA_PAN','AMSF_USA_PRY','AMSF_USA_PER','AMSF_USA_PHL',
                           'AMSF_USA_POL','AMSF_USA_KOR','AMSF_USA_RUS','AMSF_USA_KNA','AMSF_USA_SAU','AMSF_USA_SEN','AMSF_USA_SGP','AMSF_USA_ZAF','AMSF_USA_ESP','AMSF_USA_CHE','AMSF_USA_TWN','AMSF_USA_THA','AMSF_USA_TGO','AMSF_USA_TTO','AMSF_USA_TUR','AMSF_USA_ARE','AMSF_USA_GBR','AMSF_USA_URY']
        exdap_ticlist = ['DAP_AFR_WOR','DAP_EUR-CTL_WOR','DAP_CHN_WOR','DAP_ASIA-E_WOR','DAP_EUR-E-ASIA-CTL_WOR','DAP_E25_WOR','DAP_LTA_WOR','DAP_NA_WOR','DAP_OCE_WOR','DAP_ASIA-S_WOR','DAP_USA_WOR','DAP_USA_ATG','DAP_USA_ARG','DAP_USA_AUS','DAP_USA_BGD','DAP_USA_BRB','DAP_USA_BEL','DAP_USA_BLZ',
                         'DAP_USA_BRA','DAP_USA_CMR','DAP_USA_CAN','DAP_USA_CAF','DAP_USA_CHL','DAP_USA_CHN','DAP_USA_COL','DAP_USA_CRI','DAP_USA_CIV','DAP_USA_CUB','DAP_USA_DJI','DAP_USA_DOM','DAP_USA_ECU','DAP_USA_SLV','DAP_USA_ETH','DAP_USA_FRA','DAP_USA_DEU','DAP_USA_GHA','DAP_USA_GLP','DAP_USA_GTM',
                         'DAP_USA_GUY','DAP_USA_HND','DAP_USA_IND','DAP_USA_ITA','DAP_USA_JAM','DAP_USA_JPN','DAP_USA_KEN','DAP_USA_LBR','DAP_USA_MWI','DAP_USA_MLI','DAP_USA_MTQ','DAP_USA_MEX','DAP_USA_NPL','DAP_USA_NLD','DAP_USA_NZL','DAP_USA_NIC','DAP_USA_NGA','DAP_USA_NOR','DAP_USA_PAK','DAP_USA_PAN',
                         'DAP_USA_PER','DAP_USA_PHL','DAP_USA_KOR','DAP_USA_SAU','DAP_USA_SEN','DAP_USA_ZAF','DAP_USA_TWN','DAP_USA_THA','DAP_USA_TGO','DAP_USA_TUR','DAP_USA_UGA','DAP_USA_GBR','DAP_USA_TZA','DAP_USA_URY','DAP_USA_VEN','DAP_USA_VNM','DAP_VAR_WOR','DAP_ASIA-W_WOR','DAP_EUR-W_WOR']
        exnpk_ticlist = ['NPK-F_BRA_WOR']
        exmaptot_ticlist = ['MAP_AFR_WOR','MAP_EUR-CTL_WOR','MAP_CHN_WOR','MAP_ASIA-E_WOR','MAP_EUR-E-ASIA-CTL_WOR','MAP_E25_WOR','MAP_LTA_WOR','MAP_NA_WOR','MAP_OCE_WOR','MAP_ASIA-S_WOR','MAP_USA_WOR','MAP_USA_ARG','MAP_USA_AUS','MAP_USA_BHS','MAP_USA_BRB','MAP_USA_BEL','MAP_USA_BLZ','MAP_USA_BRA',
                            'MAP_USA_CAN','MAP_USA_CYM','MAP_USA_CHL','MAP_USA_CHN','MAP_USA_COL','MAP_USA_CRI','MAP_USA_DOM','MAP_USA_ECU','MAP_USA_SLV','MAP_USA_GNQ','MAP_USA_FRA','MAP_USA_DEU','MAP_USA_GTM','MAP_USA_GUY','MAP_USA_HND','MAP_USA_ISL','MAP_USA_IND','MAP_USA_IDN','MAP_USA_IRQ',
                            'MAP_USA_ISR','MAP_USA_ITA','MAP_USA_JAM','MAP_USA_JPN','MAP_USA_KEN','MAP_USA_MYS','MAP_USA_MTQ','MAP_USA_MEX','MAP_USA_NLD','MAP_USA_NZL','MAP_USA_NIC','MAP_USA_NGA','MAP_USA_NOR','MAP_USA_OMN','MAP_USA_PAK','MAP_USA_PAN','MAP_USA_PER','MAP_USA_PRT','MAP_USA_KOR','MAP_USA_SGP',
                            'MAP_USA_ZAF','MAP_USA_ESP','MAP_USA_TWN','MAP_USA_THA','MAP_USA_MKD','MAP_USA_TUR','MAP_USA_ARE','MAP_USA_GBR','MAP_USA_TZA','MAP_USA_URY','MAP_USA_VEN','MAP_USA_VNM','MAP_VAR_WOR','MAP_ASIA-W_WOR','MAP_EUR-W_WOR']
        exmapmix_ticlist = ['MAP_MMDAP_USA_WOR','MAP_MMDAP_USA_ARG','MAP_MMDAP_USA_AUS','MAP_MMDAP_USA_BHS','MAP_MMDAP_USA_BRB','MAP_MMDAP_USA_BEL','MAP_MMDAP_USA_BLZ','MAP_MMDAP_USA_BRA','MAP_MMDAP_USA_CAN','MAP_MMDAP_USA_CYM','MAP_MMDAP_USA_CHL','MAP_MMDAP_USA_CHN','MAP_MMDAP_USA_COL','MAP_MMDAP_USA_CRI',
                            'MAP_MMDAP_USA_DOM','MAP_MMDAP_USA_ECU','MAP_MMDAP_USA_SLV','MAP_MMDAP_USA_GNQ','MAP_MMDAP_USA_FRA','MAP_MMDAP_USA_DEU','MAP_MMDAP_USA_GTM','MAP_MMDAP_USA_GUY','MAP_MMDAP_USA_HND','MAP_MMDAP_USA_ISL','MAP_MMDAP_USA_IND','MAP_MMDAP_USA_IDN','MAP_MMDAP_USA_IRQ','MAP_MMDAP_USA_ISR',
                            'MAP_MMDAP_USA_ITA','MAP_MMDAP_USA_JAM','MAP_MMDAP_USA_JPN','MAP_MMDAP_USA_KEN','MAP_MMDAP_USA_MYS','MAP_MMDAP_USA_MTQ','MAP_MMDAP_USA_MEX','MAP_MMDAP_USA_NLD','MAP_MMDAP_USA_NZL','MAP_MMDAP_USA_NIC','MAP_MMDAP_USA_NGA','MAP_MMDAP_USA_NOR','MAP_MMDAP_USA_OMN','MAP_MMDAP_USA_PAK',
                            'MAP_MMDAP_USA_PAN','MAP_MMDAP_USA_PER','MAP_MMDAP_USA_PRT','MAP_MMDAP_USA_KOR','MAP_MMDAP_USA_SGP','MAP_MMDAP_USA_ZAF','MAP_MMDAP_USA_ESP','MAP_MMDAP_USA_TWN','MAP_MMDAP_USA_THA','MAP_MMDAP_USA_MKD','MAP_MMDAP_USA_TUR','MAP_MMDAP_USA_ARE','MAP_MMDAP_USA_GBR','MAP_MMDAP_USA_TZA',
                            'MAP_MMDAP_USA_URY','MAP_MMDAP_USA_VEN','MAP_MMDAP_USA_VNM']
        exphosac_ticlist = ['PHO-ACD_WOR_TOT','PHO-ACD_AFR_WOR','PHO-ACD_EUR-CTL_WOR','PHO-ACD_ASIA-E_WOR','PHO-ACD_EUR-E-ASIA-CTL_WOR','PHO-ACD_E25_WOR','PHO-ACD_LTA_WOR','PHO-ACD_NA_WOR','PHO-ACD_OCE_WOR','PHO-ACD_ASIA-S_WOR','PHO-ACD_ASIA-W_WOR','PHO-ACD_EUR-W_WOR']
        expot_ticlist = ['POT_WOR_TOT','POT_AFR_WOR','POT_CAN_WOR','POT_CAN_ARG','POT_CAN_AUS','POT_CAN_BGD','POT_CAN_BRB','POT_CAN_BEL','POT_CAN_BLZ','POT_CAN_BRA','POT_CAN_CMR','POT_CAN_CHL','POT_CAN_CHN','POT_CAN_COL','POT_CAN_CRI','POT_CAN_CIV','POT_CAN_CUB','POT_CAN_DNK','POT_CAN_DMA','POT_CAN_DOM',
                         'POT_CAN_ECU','POT_CAN_SLV','POT_CAN_FJI','POT_CAN_FRA','POT_CAN_DEU','POT_CAN_GHA','POT_CAN_GTM','POT_CAN_GUY','POT_CAN_HND','POT_CAN_IND','POT_CAN_IDN','POT_CAN_IRL','POT_CAN_ISR','POT_CAN_ITA','POT_CAN_JAM','POT_CAN_JPN','POT_CAN_LVA','POT_CAN_LBR','POT_CAN_MWI','POT_CAN_MYS',
                         'POT_CAN_MTQ','POT_CAN_MEX','POT_CAN_MAR','POT_CAN_NLD','POT_CAN_ANT','POT_CAN_NZL','POT_CAN_NIC','POT_CAN_NGA','POT_CAN_PAK','POT_CAN_PAN','POT_CAN_PER','POT_CAN_PHL','POT_CAN_PRT','POT_CAN_SAU','POT_CAN_SEN','POT_CAN_SGP','POT_CAN_ZAF','POT_CAN_KOR','POT_CAN_ESP','POT_CAN_TWN',
                         'POT_CAN_THA','POT_CAN_TGO','POT_CAN_GBR','POT_CAN_USA','POT_CAN_URY','POT_CAN_VEN','POT_CAN_VNM','POT_EUR-CTL_WOR','POT_ASIA-E_WOR','POT_EUR-E-ASIA-CTL_WOR','POT_E25_WOR','POT_LTA_WOR','POT_NA_WOR','POT_OCE_WOR','POT_ASIA-S_WOR','POT_USA_WOR','POT_USA_AFG','POT_USA_AND',
                         'POT_USA_AGO','POT_USA_ARG','POT_USA_AUS','POT_USA_AUT','POT_USA_BHS','POT_USA_BHR','POT_USA_BRB','POT_USA_BEL','POT_USA_BLZ','POT_USA_BOL','POT_USA_BRA','POT_USA_CAN','POT_USA_CHL','POT_USA_CHN','POT_USA_COL','POT_USA_CRI','POT_USA_CIV','POT_USA_CZE','POT_USA_COD','POT_USA_DNK',
                         'POT_USA_DOM','POT_USA_ECU','POT_USA_EGY','POT_USA_SLV','POT_USA_GNQ','POT_USA_FRA','POT_USA_GAB','POT_USA_DEU','POT_USA_GHA','POT_USA_GLP','POT_USA_GTM','POT_USA_GUY','POT_USA_HTI','POT_USA_HND','POT_USA_IND','POT_USA_IDN','POT_USA_IRL','POT_USA_ISR','POT_USA_ITA','POT_USA_JAM',
                         'POT_USA_JPN','POT_USA_LBN','POT_USA_LBR','POT_USA_LBY','POT_USA_MDG','POT_USA_MYS','POT_USA_MLT','POT_USA_MTQ','POT_USA_MEX','POT_USA_MCO','POT_USA_NLD','POT_USA_NZL','POT_USA_NIC','POT_USA_NGA','POT_USA_OMN','POT_USA_PAN','POT_USA_PER','POT_USA_PHL','POT_USA_POL','POT_USA_QAT',
                         'POT_USA_KOR','POT_USA_ROU','POT_USA_RUS','POT_USA_KNA','POT_USA_SAU','POT_USA_SGP','POT_USA_SVN','POT_USA_ZAF','POT_USA_ESP','POT_USA_CHE','POT_USA_TWN','POT_USA_THA','POT_USA_TTO','POT_USA_TUN','POT_USA_TUR','POT_USA_TKM','POT_USA_ARE','POT_USA_GBR','POT_USA_URY','POT_USA_VUT',
                         'POT_USA_VEN','POT_USA_VNM','POT_ASIA-W_WOR','POT_EUR-W_WOR']
        extsptot_ticlist = ['TSP_CHN_WOR','TSP_USA_WOR','TSP_USA_AUT','TSP_USA_BHS','TSP_USA_BOL','TSP_USA_BRA','TSP_USA_CMR','TSP_USA_CAN','TSP_USA_CHL','TSP_USA_CHN','TSP_USA_COL','TSP_USA_CRI','TSP_USA_DOM','TSP_USA_ECU','TSP_USA_SLV','TSP_USA_FRA','TSP_USA_DEU','TSP_USA_GHA','TSP_USA_GTM','TSP_USA_GUY',
                            'TSP_USA_HND','TSP_USA_HKG','TSP_USA_IND','TSP_USA_LBN','TSP_USA_MYS','TSP_USA_MEX','TSP_USA_NOR','TSP_USA_PAK','TSP_USA_PER','TSP_USA_KOR','TSP_USA_ESP','TSP_USA_SWE','TSP_USA_TTO','TSP_USA_UKR','TSP_USA_GBR','TSP_USA_VEN','TSP_USA_VNM']  
        extspless_ticlist = ['TSP_T-LT40_USA_WOR','TSP_T-LT40_USA_AUT','TSP_T-LT40_USA_BHS','TSP_T-LT40_USA_BOL','TSP_T-LT40_USA_CMR','TSP_T-LT40_USA_CAN','TSP_T-LT40_USA_CHN','TSP_T-LT40_USA_COL','TSP_T-LT40_USA_CRI','TSP_T-LT40_USA_DOM','TSP_T-LT40_USA_ECU','TSP_T-LT40_USA_FRA','TSP_T-LT40_USA_DEU',
                             'TSP_T-LT40_USA_GHA','TSP_T-LT40_USA_GTM','TSP_T-LT40_USA_GUY','TSP_T-LT40_USA_HND','TSP_T-LT40_USA_HKG','TSP_T-LT40_USA_IND','TSP_T-LT40_USA_MYS','TSP_T-LT40_USA_MEX','TSP_T-LT40_USA_PAK','TSP_T-LT40_USA_ESP','TSP_T-LT40_USA_SWE','TSP_T-LT40_USA_TTO','TSP_T-LT40_USA_UKR',
                             'TSP_T-LT40_USA_GBR','TSP_T-LT40_USA_VEN','TSP_T-LT40_USA_VNM']
        extspgreat_ticlist = ['TSP_T-GE40_USA_WOR','TSP_T-GE40_USA_BHS','TSP_T-GE40_USA_BRA','TSP_T-GE40_USA_CAN','TSP_T-GE40_USA_CHL','TSP_T-GE40_USA_CHN','TSP_T-GE40_USA_CRI','TSP_T-GE40_USA_DOM','TSP_T-GE40_USA_ECU','TSP_T-GE40_USA_SLV','TSP_T-GE40_USA_HKG','TSP_T-GE40_USA_LBN','TSP_T-GE40_USA_MEX',
                              'TSP_T-GE40_USA_NOR','TSP_T-GE40_USA_PER','TSP_T-GE40_USA_KOR','TSP_T-GE40_USA_ESP','TSP_T-GE40_USA_SWE','TSP_T-GE40_USA_VEN','TSP_T-GE40_USA_VNM']
        exuantot_ticlist = ['UAN_USA_WOR','UAN_USA_ARG','UAN_USA_ABW','UAN_USA_AUS','UAN_USA_BHS','UAN_USA_BRB','UAN_USA_BEL','UAN_USA_BRA','UAN_USA_CAN','UAN_USA_CYM','UAN_USA_CHL','UAN_USA_CHN','UAN_USA_COL','UAN_USA_DMA','UAN_USA_FRA','UAN_USA_GTM','UAN_USA_HND','UAN_USA_IND','UAN_USA_IRL','UAN_USA_ISR',
                            'UAN_USA_ITA','UAN_USA_JPN','UAN_USA_LBN','UAN_USA_MEX','UAN_USA_NLD','UAN_USA_NZL','UAN_USA_PER','UAN_USA_PHL','UAN_USA_PRT','UAN_USA_KOR','UAN_USA_ZAF','UAN_USA_TUR','UAN_USA_GBR','UAN_USA_URY']
        exuanmix_ticlist = ['UAN_MUNAN_USA_WOR','UAN_MUNAN_USA_ARG','UAN_MUNAN_USA_ABW','UAN_MUNAN_USA_AUS','UAN_MUNAN_USA_BHS','UAN_MUNAN_USA_BRB','UAN_MUNAN_USA_BEL','UAN_MUNAN_USA_BRA','UAN_MUNAN_USA_CAN','UAN_MUNAN_USA_CYM','UAN_MUNAN_USA_CHL','UAN_MUNAN_USA_CHN','UAN_MUNAN_USA_COL','UAN_MUNAN_USA_DMA',
                            'UAN_MUNAN_USA_FRA','UAN_MUNAN_USA_GTM','UAN_MUNAN_USA_HND','UAN_MUNAN_USA_IND','UAN_MUNAN_USA_IRL','UAN_MUNAN_USA_ISR','UAN_MUNAN_USA_ITA','UAN_MUNAN_USA_JPN','UAN_MUNAN_USA_LBN','UAN_MUNAN_USA_MEX','UAN_MUNAN_USA_NLD','UAN_MUNAN_USA_NZL','UAN_MUNAN_USA_PER','UAN_MUNAN_USA_PHL',
                            'UAN_MUNAN_USA_PRT','UAN_MUNAN_USA_KOR','UAN_MUNAN_USA_ZAF','UAN_MUNAN_USA_TUR','UAN_MUNAN_USA_GBR','UAN_MUNAN_USA_URY']
        exureatot_ticlist = ['UREA_WOR_TOT','UREA_AFR_WOR','UREA_CAN_WOR','UREA_CAN_ARG','UREA_CAN_AUS','UREA_CAN_AUT','UREA_CAN_BEL','UREA_CAN_BMU','UREA_CAN_BRA','UREA_CAN_CHL','UREA_CAN_CHN','UREA_CAN_CUB','UREA_CAN_DOM','UREA_CAN_FRA','UREA_CAN_DEU','UREA_CAN_HKG','UREA_CAN_IRL','UREA_CAN_ITA',
                             'UREA_CAN_JPN','UREA_CAN_MYS','UREA_CAN_MEX','UREA_CAN_NLD','UREA_CAN_NZL','UREA_CAN_NIC','UREA_CAN_QAT','UREA_CAN_KOR','UREA_CAN_SPM','UREA_CAN_SAU','UREA_CAN_SGP','UREA_CAN_ESP','UREA_CAN_SDN','UREA_CAN_SWE','UREA_CAN_CHE','UREA_CAN_GBR','UREA_CAN_USA','UREA_EUR-CTL_WOR',
                             'UREA_CHN_WOR','UREA_ASIA-E_WOR','UREA_EUR-E-ASIA-CTL_WOR','UREA_E25_WOR','UREA_LTA_WOR','UREA_NA_WOR','UREA_OCE_WOR','UREA_ASIA-S_WOR','UREA_USA_WOR','UREA_USA_ARG','UREA_USA_AUS','UREA_USA_AUT','UREA_USA_BHS','UREA_USA_BHR','UREA_USA_BGD','UREA_USA_BRB','UREA_USA_BEL',
                             'UREA_USA_BLZ','UREA_USA_BMU','UREA_USA_BOL','UREA_USA_BRA','UREA_USA_CAN','UREA_USA_CYM','UREA_USA_CHL','UREA_USA_CHN','UREA_USA_COL','UREA_USA_CRI','UREA_USA_CIV','UREA_USA_CYP','UREA_USA_CZE','UREA_USA_COD','UREA_USA_DNK','UREA_USA_DOM','UREA_USA_ECU','UREA_USA_EGY',
                             'UREA_USA_SLV','UREA_USA_GNQ','UREA_USA_FRA','UREA_USA_GEO','UREA_USA_DEU','UREA_USA_GHA','UREA_USA_GRC','UREA_USA_GTM','UREA_USA_GUY','UREA_USA_HTI','UREA_USA_HND','UREA_USA_HKG','UREA_USA_ISL','UREA_USA_IND','UREA_USA_IDN','UREA_USA_IRL','UREA_USA_ISR','UREA_USA_ITA',
                             'UREA_USA_JAM','UREA_USA_JPN','UREA_USA_JOR','UREA_USA_KAZ','UREA_USA_MAC','UREA_USA_MYS','UREA_USA_MTQ','UREA_USA_MEX','UREA_USA_MAR','UREA_USA_NLD-CUR','UREA_USA_NLD','UREA_USA_NZL','UREA_USA_NIC','UREA_USA_NOR','UREA_USA_PAN','UREA_USA_PER','UREA_USA_PHL','UREA_USA_POL',
                             'UREA_USA_PRT','UREA_USA_KOR','UREA_USA_RUS','UREA_USA_LCA','UREA_USA_SAU','UREA_USA_SGP','UREA_USA_ZAF','UREA_USA_ESP','UREA_USA_SWE','UREA_USA_CHE','UREA_USA_TWN','UREA_USA_THA','UREA_USA_TTO','UREA_USA_TUR','UREA_USA_UKR','UREA_USA_ARE','UREA_USA_GBR','UREA_USA_URY',
                             'UREA_USA_VEN','UREA_USA_VNM','UREA_ASIA-W_WOR','UREA_EUR-W_WOR']
        exureaaq_ticlist = ['UREA_AQUES_USA_WOR','UREA_AQUES_USA_ARG','UREA_AQUES_USA_AUS','UREA_AQUES_USA_AUT','UREA_AQUES_USA_BHS','UREA_AQUES_USA_BHR','UREA_AQUES_USA_BGD','UREA_AQUES_USA_BRB','UREA_AQUES_USA_BEL','UREA_AQUES_USA_BLZ','UREA_AQUES_USA_BMU','UREA_AQUES_USA_BOL','UREA_AQUES_USA_BRA',
                            'UREA_AQUES_USA_CAN','UREA_AQUES_USA_CYM','UREA_AQUES_USA_CHL','UREA_AQUES_USA_CHN','UREA_AQUES_USA_COL','UREA_AQUES_USA_CRI','UREA_AQUES_USA_CIV','UREA_AQUES_USA_CYP','UREA_AQUES_USA_CZE','UREA_AQUES_USA_COD','UREA_AQUES_USA_DNK','UREA_AQUES_USA_DOM','UREA_AQUES_USA_ECU',
                            'UREA_AQUES_USA_EGY','UREA_AQUES_USA_SLV','UREA_AQUES_USA_GNQ','UREA_AQUES_USA_FRA','UREA_AQUES_USA_GEO','UREA_AQUES_USA_DEU','UREA_AQUES_USA_GHA','UREA_AQUES_USA_GRC','UREA_AQUES_USA_GTM','UREA_AQUES_USA_GUY','UREA_AQUES_USA_HTI','UREA_AQUES_USA_HND','UREA_AQUES_USA_HKG',
                            'UREA_AQUES_USA_ISL','UREA_AQUES_USA_IND','UREA_AQUES_USA_IDN','UREA_AQUES_USA_IRL','UREA_AQUES_USA_ISR','UREA_AQUES_USA_ITA','UREA_AQUES_USA_JAM','UREA_AQUES_USA_JPN','UREA_AQUES_USA_JOR','UREA_AQUES_USA_KAZ','UREA_AQUES_USA_MAC','UREA_AQUES_USA_MYS','UREA_AQUES_USA_MTQ',
                            'UREA_AQUES_USA_MEX','UREA_AQUES_USA_MAR','UREA_AQUES_USA_NLD-CUR','UREA_AQUES_USA_NLD','UREA_AQUES_USA_NZL','UREA_AQUES_USA_NIC','UREA_AQUES_USA_NOR','UREA_AQUES_USA_PAN','UREA_AQUES_USA_PER','UREA_AQUES_USA_PHL','UREA_AQUES_USA_POL','UREA_AQUES_USA_PRT','UREA_AQUES_USA_KOR',
                            'UREA_AQUES_USA_RUS','UREA_AQUES_USA_LCA','UREA_AQUES_USA_SAU','UREA_AQUES_USA_SGP','UREA_AQUES_USA_ZAF','UREA_AQUES_USA_ESP','UREA_AQUES_USA_SWE','UREA_AQUES_USA_CHE','UREA_AQUES_USA_TWN','UREA_AQUES_USA_THA','UREA_AQUES_USA_TTO','UREA_AQUES_USA_TUR','UREA_AQUES_USA_UKR',
                            'UREA_AQUES_USA_ARE','UREA_AQUES_USA_GBR','UREA_AQUES_USA_URY','UREA_AQUES_USA_VEN','UREA_AQUES_USA_VNM']
        sdamm_ticlist = ['AMM_SD_WOR'] * 9  
        sddapmapus_ticlist = ['DAP-MAP_SD_USA'] * 6
        sddapmapall_ticlist = ['DAP-MAP_SD_WOR'] * 9     
        sdpotus_ticlist = ['POT_SD_N-A'] * 6
        sdpotall_ticlist = ['POT_SD_WOR'] * 9  
        sduan_ticlist = ['UAN_SD_USA'] * 6 
        sdureaus_ticlist = ['UREA_SD_USA'] * 6
        sdureaall_ticlist = ['UREA_SD_WOR'] * 9 
        dapbid_ticlist = ['DAP-MAP_BAL_BRA','DAP-MAP_BAL_IND-WC','DAP-MAP_CHN_IND-WC','DAP-MAP_CHN_MSS-RVR','DAP-MAP_CHN_PAK','DAP-MAP_MAR_BRA','DAP-MAP_MAR_MSS-RVR','DAP-MAP_RED-SEA_IND-WC','DAP-MAP_TAMPA_BRA','DAP-MAP_TAMPA_CHN','DAP-MAP_TAMPA_IND-WC','DAP-MAP_TAMPA_PAK','DAP-MAP_TUN_PAK','DAP-MAP_TUN_TUR'] 
        dapoffer_ticlist = ['DAP-MAP_BAL_BRA','DAP-MAP_BAL_IND-WC','DAP-MAP_CHN_IND-WC','DAP-MAP_CHN_MSS-RVR','DAP-MAP_CHN_PAK','DAP-MAP_MAR_BRA','DAP-MAP_MAR_MSS-RVR','DAP-MAP_RED-SEA_IND-WC','DAP-MAP_TAMPA_BRA','DAP-MAP_TAMPA_CHN','DAP-MAP_TAMPA_IND-WC','DAP-MAP_TAMPA_PAK','DAP-MAP_TUN_PAK','DAP-MAP_TUN_TUR'] 
        dapmid_ticlist = ['DAP-MAP_BAL_BRA','DAP-MAP_BAL_IND-WC','DAP-MAP_CHN_IND-WC','DAP-MAP_CHN_MSS-RVR','DAP-MAP_CHN_PAK','DAP-MAP_MAR_BRA','DAP-MAP_MAR_MSS-RVR','DAP-MAP_RED-SEA_IND-WC','DAP-MAP_TAMPA_BRA','DAP-MAP_TAMPA_CHN','DAP-MAP_TAMPA_IND-WC','DAP-MAP_TAMPA_PAK','DAP-MAP_TUN_PAK','DAP-MAP_TUN_TUR']           
        mopbid_ticlist = ['MOP_BAL_BRA','MOP_BAL_CHN','MOP_BAL_IND-WC','MOP_BAL_ASIA-SE','MOP_BLK-SEA_IDN','MOP_ISR_BRA','MOP_RED-SEA_CHN','MOP_RED-SEA_IND-WC','MOP_RED-SEA_ASIA-SE','MOP_VAN_BRA','MOP_VAN_CHN','MOP_VAN_IND','MOP_VAN_ASIA-SE']
        mopoffer_ticlist = ['MOP_BAL_BRA','MOP_BAL_CHN','MOP_BAL_IND-WC','MOP_BAL_ASIA-SE','MOP_BLK-SEA_IDN','MOP_ISR_BRA','MOP_RED-SEA_CHN','MOP_RED-SEA_IND-WC','MOP_RED-SEA_ASIA-SE','MOP_VAN_BRA','MOP_VAN_CHN','MOP_VAN_IND','MOP_VAN_ASIA-SE']
        mopmid_ticlist = ['MOP_BAL_BRA','MOP_BAL_CHN','MOP_BAL_IND-WC','MOP_BAL_ASIA-SE','MOP_BLK-SEA_IDN','MOP_ISR_BRA','MOP_RED-SEA_CHN','MOP_RED-SEA_IND-WC','MOP_RED-SEA_ASIA-SE','MOP_VAN_BRA','MOP_VAN_CHN','MOP_VAN_IND','MOP_VAN_ASIA-SE']        
        phorockbid_ticlist = ['PHO-RCK_MAR_IND-WC','PHO-RCK_RED-SEA_IND-WC']
        phorockoffer_ticlist = ['PHO-RCK_MAR_IND-WC','PHO-RCK_RED-SEA_IND-WC']
        phorockmid_ticlist = ['PHO-RCK_MAR_IND-WC','PHO-RCK_RED-SEA_IND-WC']
        sulfurbid_ticlist = ['SUL_BLK-SEA_MAR','SUL_MEST_CHN','SUL_MEST_IND-EC','SUL_MEST_IND-WC','SUL_MEST_MAR','SUL_VAN_BRA','SUL_VAN_CHN']
        sulfuroffer_ticlist = ['SUL_BLK-SEA_MAR','SUL_MEST_CHN','SUL_MEST_IND-EC','SUL_MEST_IND-WC','SUL_MEST_MAR','SUL_VAN_BRA','SUL_VAN_CHN']
        sulfurmid_ticlist = ['SUL_BLK-SEA_MAR','SUL_MEST_CHN','SUL_MEST_IND-EC','SUL_MEST_IND-WC','SUL_MEST_MAR','SUL_VAN_BRA','SUL_VAN_CHN']
        ureabid_ticlist = ['UREA_BAL_BRA','UREA_BAL_IND-WC','UREA_BAL_MEX-EC','UREA_BAL_MEX-WC','UREA_CHN_USG','UREA_EGY_USG','UREA_IDN_THA','UREA_MEST_IND-WC','UREA_MEST_MSS-RVR','UREA_MEST_VNM','UREA_CHN-N_IND-EC','UREA_YUZHNY_BRA','UREA_YUZHNY_IND-WC','UREA_YUZHNY_MEX-EC','UREA_YUZHNY_MEX-WC','UREA_YUZHNY_MDRA','UREA_YUZHNY_TUR']
        ureaoffer_ticlist = ['UREA_BAL_BRA','UREA_BAL_IND-WC','UREA_BAL_MEX-EC','UREA_BAL_MEX-WC','UREA_CHN_USG','UREA_EGY_USG','UREA_IDN_THA','UREA_MEST_IND-WC','UREA_MEST_MSS-RVR','UREA_MEST_VNM','UREA_CHN-N_IND-EC','UREA_YUZHNY_BRA','UREA_YUZHNY_IND-WC','UREA_YUZHNY_MEX-EC','UREA_YUZHNY_MEX-WC','UREA_YUZHNY_MDRA','UREA_YUZHNY_TUR'] 
        ureamid_ticlist = ['UREA_BAL_BRA','UREA_BAL_IND-WC','UREA_BAL_MEX-EC','UREA_BAL_MEX-WC','UREA_CHN_USG','UREA_EGY_USG','UREA_IDN_THA','UREA_MEST_IND-WC','UREA_MEST_MSS-RVR','UREA_MEST_VNM','UREA_CHN-N_IND-EC','UREA_YUZHNY_BRA','UREA_YUZHNY_IND-WC','UREA_YUZHNY_MEX-EC','UREA_YUZHNY_MEX-WC','UREA_YUZHNY_MDRA','UREA_YUZHNY_TUR']        
        ammbid_ticlist = ['AMM_BAL_EUR-NW','AMM_MEST_FE','AMM_MEST_IND-EC','AMM_MEST_IND-WC','AMM_YUZHNY_FE','AMM_YUZHNY_MAR','AMM_YUZHNY_ASIA-NSE','AMM_YUZHNY_EUR-NW','AMM_YUZHNY_EUR-S','AMM_YUZHNY_TAMPA']
        ammoffer_ticlist = ['AMM_BAL_EUR-NW','AMM_MEST_FE','AMM_MEST_IND-EC','AMM_MEST_IND-WC','AMM_YUZHNY_FE','AMM_YUZHNY_MAR','AMM_YUZHNY_ASIA-NSE','AMM_YUZHNY_EUR-NW','AMM_YUZHNY_EUR-S','AMM_YUZHNY_TAMPA']
        ammmid_ticlist = ['AMM_BAL_EUR-NW','AMM_MEST_FE','AMM_MEST_IND-EC','AMM_MEST_IND-WC','AMM_YUZHNY_FE','AMM_YUZHNY_MAR','AMM_YUZHNY_ASIA-NSE','AMM_YUZHNY_EUR-NW','AMM_YUZHNY_EUR-S','AMM_YUZHNY_TAMPA']
        phoacbid_ticlist = ['PHO-ACD_MAR_IND-WC','PHO-ACD_MAR_EUR-NW']
        phoacoffer_ticlist = ['PHO-ACD_MAR_IND-WC','PHO-ACD_MAR_EUR-NW']
        phoacmid_ticlist = ['PHO-ACD_MAR_IND-WC','PHO-ACD_MAR_EUR-NW']
        sulacbid_ticlist = ['SUL-ACD_JPN-KOR_CHL','SUL-ACD_JPN-KOR_CHN','SUL-ACD_JPN-KOR_IND','SUL-ACD_EUR-NW_BRA','SUL-ACD_EUR-NW_AFR-N','SUL-ACD_EUR-NW_USG']
        sulacoffer_ticlist = ['SUL-ACD_JPN-KOR_CHL','SUL-ACD_JPN-KOR_CHN','SUL-ACD_JPN-KOR_IND','SUL-ACD_EUR-NW_BRA','SUL-ACD_EUR-NW_AFR-N','SUL-ACD_EUR-NW_USG']
        sulacmid_ticlist = ['SUL-ACD_JPN-KOR_CHL','SUL-ACD_JPN-KOR_CHN','SUL-ACD_JPN-KOR_IND','SUL-ACD_EUR-NW_BRA','SUL-ACD_EUR-NW_AFR-N','SUL-ACD_EUR-NW_USG']
        uanbid_ticlist = ['UAN_BLK-SEA_FRA-ATL','UAN_BLK-SEA_USA-EC']
        uanoffer_ticlist = ['UAN_BLK-SEA_FRA-ATL','UAN_BLK-SEA_USA-EC']
        uanmid_ticlist = ['UAN_BLK-SEA_FRA-ATL','UAN_BLK-SEA_USA-EC']
        chsdap_ticlist = ['DAP_TOT_ACT','DAP_TOT_FRONT','DAP_TOT_FRONT2','DAP_TOT_FRONT3','DAP_TOT_FRONT4','DAP_TOT_FRONT5','DAP_TOT_FRONT6','DAP_TOT_FRONT7','DAP_TOT_FRONT8','DAP_TOT_FRONT9','DAP_TOT_FRONT10','DAP_TOT_FRONT11','DAP_TOT_FRONT12'] * 2
        chspot_ticlist = ['POT_TOT_ACT','POT_TOT_FRONT','POT_TOT_FRONT2','POT_TOT_FRONT3','POT_TOT_FRONT4','POT_TOT_FRONT5','POT_TOT_FRONT6','POT_TOT_FRONT7','POT_TOT_FRONT8','POT_TOT_FRONT9','POT_TOT_FRONT10','POT_TOT_FRONT11','POT_TOT_FRONT12'] * 2
        chsuan_ticlist = ['UAN_TOT_ACT','DAP_TOT_FRONT','UAN_TOT_FRONT2','UAN_TOT_FRONT3','UAN_TOT_FRONT4','UAN_TOT_FRONT5','UAN_TOT_FRONT6','UAN_TOT_FRONT7','UAN_TOT_FRONT8','UAN_TOT_FRONT9','UAN_TOT_FRONT10','UAN_TOT_FRONT11','UAN_TOT_FRONT12'] * 2
        chsurea_ticlist = ['UREA_GRAN_ACT','UREA_GRAN_FRONT','UREA_GRAN_FRONT2','UREA_GRAN_FRONT3','UREA_GRAN_FRONT4','UREA_GRAN_FRONT5','UREA_GRAN_FRONT6','UREA_GRAN_FRONT7','UREA_GRAN_FRONT8','UREA_GRAN_FRONT9','UREA_GRAN_FRONT10','UREA_GRAN_FRONT11','UREA_GRAN_FRONT12'] * 2
        buckdap_ticlist = ['DAP_TOT_ACT','DAP_TOT_FRONT','DAP_TOT_FRONT2','DAP_TOT_FRONT3','DAP_TOT_FRONT4','DAP_TOT_FRONT5','DAP_TOT_FRONT6','DAP_TOT_FRONT7','DAP_TOT_FRONT8','DAP_TOT_FRONT9','DAP_TOT_FRONT10','DAP_TOT_FRONT11','DAP_TOT_FRONT12'] * 2
        buckpot_ticlist = ['POT_TOT_ACT','POT_TOT_FRONT','POT_TOT_FRONT2','POT_TOT_FRONT3','POT_TOT_FRONT4','POT_TOT_FRONT5','POT_TOT_FRONT6','POT_TOT_FRONT7','POT_TOT_FRONT8','POT_TOT_FRONT9','POT_TOT_FRONT10','POT_TOT_FRONT11','POT_TOT_FRONT12'] * 2
        buckuan_ticlist = ['UAN_TOT_ACT','DAP_TOT_FRONT','UAN_TOT_FRONT2','UAN_TOT_FRONT3','UAN_TOT_FRONT4','UAN_TOT_FRONT5','UAN_TOT_FRONT6','UAN_TOT_FRONT7','UAN_TOT_FRONT8','UAN_TOT_FRONT9','UAN_TOT_FRONT10','UAN_TOT_FRONT11','UAN_TOT_FRONT12'] * 2
        buckurea_ticlist = ['UREA_GRAN_ACT','UREA_GRAN_FRONT','UREA_GRAN_FRONT2','UREA_GRAN_FRONT3','UREA_GRAN_FRONT4','UREA_GRAN_FRONT5','UREA_GRAN_FRONT6','UREA_GRAN_FRONT7','UREA_GRAN_FRONT8','UREA_GRAN_FRONT9','UREA_GRAN_FRONT10','UREA_GRAN_FRONT11','UREA_GRAN_FRONT12'] * 2        
        cru_ticlist = ['DAP_TOT_ACT','DAP_TOT_FRONT','DAP_TOT_FRONT2','DAP_TOT_FRONT3','DAP_TOT_FRONT4','DAP_TOT_FRONT5','DAP_TOT_FRONT6','DAP_TOT_FRONT7','DAP_TOT_FRONT8','DAP_TOT_FRONT9','DAP_TOT_FRONT10','DAP_TOT_FRONT11','DAP_TOT_FRONT12',
                       'UREA_GRAN_ACT','UREA_GRAN_FRONT','UREA_GRAN_FRONT2','UREA_GRAN_FRONT3','UREA_GRAN_FRONT4','UREA_GRAN_FRONT5','UREA_GRAN_FRONT6','UREA_GRAN_FRONT7','UREA_GRAN_FRONT8','UREA_GRAN_FRONT9','UREA_GRAN_FRONT10','UREA_GRAN_FRONT11','UREA_GRAN_FRONT12']
        avgcorn_ticlist = ['C_Q1','C_Q2','C_Q3','C_Q4','C_Q5','C_Q6','C_Y2','C_Y3']  
        lowcorn_ticlist = ['C_Q1','C_Q2','C_Q3','C_Q4','C_Q5','C_Q6','C_Y2','C_Y3'] 
        highcorn_ticlist = ['C_Q1','C_Q2','C_Q3','C_Q4','C_Q5','C_Q6','C_Y2','C_Y3'] 
        avgsoy_ticlist = ['S_Q1','S_Q2','S_Q3','S_Q4','S_Q5','S_Q6','S_Y2','S_Y3']  
        lowsoy_ticlist = ['S_Q1','S_Q2','S_Q3','S_Q4','S_Q5','S_Q6','S_Y2','S_Y3'] 
        highsoy_ticlist = ['S_Q1','S_Q2','S_Q3','S_Q4','S_Q5','S_Q6','S_Y2','S_Y3']  
        avgso_ticlist = ['BO_Q1','BO_Q2','BO_Q3','BO_Q4','BO_Q5','BO_Q6','BO_Y2','BO_Y3']  
        lowso_ticlist = ['BO_Q1','BO_Q2','BO_Q3','BO_Q4','BO_Q5','BO_Q6','BO_Y2','BO_Y3'] 
        highso_ticlist = ['BO_Q1','BO_Q2','BO_Q3','BO_Q4','BO_Q5','BO_Q6','BO_Y2','BO_Y3']  
        avgwheat_ticlist = ['W_Q1','W_Q2','W_Q3','W_Q4','W_Q5','W_Q6','W_Y2','W_Y3']  
        lowwheat_ticlist = ['W_Q1','W_Q2','W_Q3','W_Q4','W_Q5','W_Q6','W_Y2','W_Y3'] 
        highwheat_ticlist = ['W_Q1','W_Q2','W_Q3','W_Q4','W_Q5','W_Q6','W_Y2','W_Y3']  
        avgwti_ticlist = ['CL_Q1','CL_Q2','CL_Q3','CL_Q4','CL_Q5','CL_Q6','CL_Y2','CL_Y3']  
        lowwti_ticlist = ['CL_Q1','CL_Q2','CL_Q3','CL_Q4','CL_Q5','CL_Q6','CL_Y2','CL_Y3'] 
        highwti_ticlist = ['CL_Q1','CL_Q2','CL_Q3','CL_Q4','CL_Q5','CL_Q6','CL_Y2','CL_Y3']  
        avgng_ticlist = ['NG_Q1','NG_Q2','NG_Q3','NG_Q4','NG_Q5','NG_Q6','NG_Y2','NG_Y3']  
        lowng_ticlist = ['NG_Q1','NG_Q2','NG_Q3','NG_Q4','NG_Q5','NG_Q6','NG_Y2','NG_Y3'] 
        highng_ticlist = ['NG_Q1','NG_Q2','NG_Q3','NG_Q4','NG_Q5','NG_Q6','NG_Y2','NG_Y3']  
        avgcot_ticlist = ['CT_Q1','CT_Q2','CT_Q3','CT_Q4','CT_Q5','CT_Q6','CT_Y2','CT_Y3']  
        lowcot_ticlist = ['CT_Q1','CT_Q2','CT_Q3','CT_Q4','CT_Q5','CT_Q6','CT_Y2','CT_Y3'] 
        highcot_ticlist = ['CT_Q1','CT_Q2','CT_Q3','CT_Q4','CT_Q5','CT_Q6','CT_Y2','CT_Y3'] 
        avgal_ticlist = ['LA_Q1','LA_Q2','LA_Q3','LA_Q4','LA_Q5','LA_Q6','LA_Y2','LA_Y3']  
        lowal_ticlist = ['LA_Q1','LA_Q2','LA_Q3','LA_Q4','LA_Q5','LA_Q6','LA_Y2','LA_Y3'] 
        highal_ticlist = ['LA_Q1','LA_Q2','LA_Q3','LA_Q4','LA_Q5','LA_Q6','LA_Y2','LA_Y3']
        avgara_ticlist = ['COA_Q1','COA_Q2','COA_Q3','COA_Q4','COA_Q5','COA_Q6','COA_Y2','COA_Y3']  
        lowara_ticlist = ['COA_Q1','COA_Q2','COA_Q3','COA_Q4','COA_Q5','COA_Q6','COA_Y2','COA_Y3'] 
        highara_ticlist = ['COA_Q1','COA_Q2','COA_Q3','COA_Q4','COA_Q5','COA_Q6','COA_Y2','COA_Y3']  
        avgrb_ticlist = ['XO_Q1','XO_Q2','XO_Q3','XO_Q4','XO_Q5','XO_Q6','XO_Y2','XO_Y3']  
        lowrb_ticlist = ['XO_Q1','XO_Q2','XO_Q3','XO_Q4','XO_Q5','XO_Q6','XO_Y2','XO_Y3'] 
        highrb_ticlist = ['XO_Q1','XO_Q2','XO_Q3','XO_Q4','XO_Q5','XO_Q6','XO_Y2','XO_Y3']  
        avgcu_ticlist = ['HG_Q1','HG_Q2','HG_Q3','HG_Q4','HG_Q5','HG_Q6','HG_Y2','HG_Y3']  
        lowcu_ticlist = ['HG_Q1','HG_Q2','HG_Q3','HG_Q4','HG_Q5','HG_Q6','HG_Y2','HG_Y3'] 
        highcu_ticlist = ['HG_Q1','HG_Q2','HG_Q3','HG_Q4','HG_Q5','HG_Q6','HG_Y2','HG_Y3'] 
        avgau_ticlist = ['GC_Q1','GC_Q2','GC_Q3','GC_Q4','GC_Q5','GC_Q6','GC_Y2','GC_Y3']  
        lowau_ticlist = ['GC_Q1','GC_Q2','GC_Q3','GC_Q4','GC_Q5','GC_Q6','GC_Y2','GC_Y3'] 
        highau_ticlist = ['GC_Q1','GC_Q2','GC_Q3','GC_Q4','GC_Q5','GC_Q6','GC_Y2','GC_Y3'] 
        avgho_ticlist = ['HO_Q1','HO_Q2','HO_Q3','HO_Q4','HO_Q5','HO_Q6','HO_Y2','HO_Y3']  
        lowho_ticlist = ['HO_Q1','HO_Q2','HO_Q3','HO_Q4','HO_Q5','HO_Q6','HO_Y2','HO_Y3'] 
        highho_ticlist = ['HO_Q1','HO_Q2','HO_Q3','HO_Q4','HO_Q5','HO_Q6','HO_Y2','HO_Y3']  
        avgice_ticlist = ['CO_Q1','CO_Q2','CO_Q3','CO_Q4','CO_Q5','CO_Q6','CO_Y2','CO_Y3']  
        lowice_ticlist = ['CO_Q1','CO_Q2','CO_Q3','CO_Q4','CO_Q5','CO_Q6','CO_Y2','CO_Y3'] 
        highice_ticlist = ['CO_Q1','CO_Q2','CO_Q3','CO_Q4','CO_Q5','CO_Q6','CO_Y2','CO_Y3']   
        avgfe_ticlist = ['IOE_Q1','IOE_Q2','IOE_Q3','IOE_Q4','IOE_Q5','IOE_Q6','IOE_Y2','IOE_Y3']  
        lowfe_ticlist = ['IOE_Q1','IOE_Q2','IOE_Q3','IOE_Q4','IOE_Q5','IOE_Q6','IOE_Y2','IOE_Y3'] 
        highfe_ticlist = ['IOE_Q1','IOE_Q2','IOE_Q3','IOE_Q4','IOE_Q5','IOE_Q6','IOE_Y2','IOE_Y3']  
        avgpb_ticlist = ['LL_Q1','LL_Q2','LL_Q3','LL_Q4','LL_Q5','LL_Q6','LL_Y2','XO_Y3']  
        lowpb_ticlist = ['LL_Q1','LL_Q2','LL_Q3','LL_Q4','LL_Q5','LL_Q6','LL_Y2','XO_Y3'] 
        highpb_ticlist = ['LL_Q1','LL_Q2','LL_Q3','LL_Q4','LL_Q5','LL_Q6','LL_Y2','XO_Y3'] 
        avgnbp_ticlist = ['FN_Q1','FN_Q2','FN_Q3','FN_Q4','FN_Q5','FN_Q6','FN_Y2','XO_Y3']  
        lowrnbp_ticlist = ['FN_Q1','FN_Q2','FN_Q3','FN_Q4','FN_Q5','FN_Q6','FN_Y2','XO_Y3'] 
        highnbp_ticlist = ['FN_Q1','FN_Q2','FN_Q3','FN_Q4','FN_Q5','FN_Q6','FN_Y2','XO_Y3'] 
        avgni_ticlist = ['LN_Q1','LN_Q2','LN_Q3','LN_Q4','LN_Q5','LN_Q6','LN_Y2','LN_Y3']  
        lowni_ticlist = ['LN_Q1','LN_Q2','LN_Q3','LN_Q4','LN_Q5','LN_Q6','LN_Y2','LN_Y3'] 
        highni_ticlist = ['LN_Q1','LN_Q2','LN_Q3','LN_Q4','LN_Q5','LN_Q6','LN_Y2','LN_Y3'] 
        avgpa_ticlist = ['PA_Q1','PA_Q2','PA_Q3','PA_Q4','PA_Q5','PA_Q6','PA_Y2','PA_Y3']  
        lowpa_ticlist = ['PA_Q1','PA_Q2','PA_Q3','PA_Q4','PA_Q5','PA_Q6','PA_Y2','PA_Y3'] 
        highpa_ticlist = ['PA_Q1','PA_Q2','PA_Q3','PA_Q4','PA_Q5','PA_Q6','PA_Y2','PA_Y3']
        avgpt_ticlist = ['PL_Q1','PL_Q2','PL_Q3','PL_Q4','PL_Q5','PL_Q6','PL_Y2','PL_Y3']  
        lowpt_ticlist = ['PL_Q1','PL_Q2','PL_Q3','PL_Q4','PL_Q5','PL_Q6','PL_Y2','PL_Y3'] 
        highpt_ticlist = ['PL_Q1','PL_Q2','PL_Q3','PL_Q4','PL_Q5','PL_Q6','PL_Y2','PL_Y3']
        avgrbob_ticlist = ['XB_Q1','XB_Q2','XB_Q3','XB_Q4','XB_Q5','XB_Q6','XB_Y2','XB_Y3']  
        lowrbob_ticlist = ['XB_Q1','XB_Q2','XB_Q3','XB_Q4','XB_Q5','XB_Q6','XB_Y2','XB_Y3'] 
        highrbob_ticlist = ['XB_Q1','XB_Q2','XB_Q3','XB_Q4','XB_Q5','XB_Q6','XB_Y2','XB_Y3']    
        avgag_ticlist = ['SI_Q1','SI_Q2','SI_Q3','SI_Q4','SI_Q5','SI_Q6','SI_Y2','SI_Y3']  
        lowag_ticlist = ['SI_Q1','SI_Q2','SI_Q3','SI_Q4','SI_Q5','SI_Q6','SI_Y2','SI_Y3'] 
        highag_ticlist = ['SI_Q1','SI_Q2','SI_Q3','SI_Q4','SI_Q5','SI_Q6','SI_Y2','SI_Y3'] 
        avgst_ticlist = ['HRC_Q1','HRC_Q2','HRC_Q3','HRC_Q4','HRC_Q5','HRC_Q6','HRC_Y2','HRC_Y3']  
        lowst_ticlist = ['HRC_Q1','HRC_Q2','HRC_Q3','HRC_Q4','HRC_Q5','HRC_Q6','HRC_Y2','HRC_Y3'] 
        highst_ticlist = ['HRC_Q1','HRC_Q2','HRC_Q3','HRC_Q4','HRC_Q5','HRC_Q6','HRC_Y2','HRC_Y3'] 
        avgsb_ticlist = ['SB_Q1','SB_Q2','SB_Q3','SB_Q4','SB_Q5','SB_Q6','SB_Y2','SB_Y3']  
        lowsb_ticlist = ['SB_Q1','SB_Q2','SB_Q3','SB_Q4','SB_Q5','SB_Q6','SB_Y2','SB_Y3'] 
        highsb_ticlist = ['SB_Q1','SB_Q2','SB_Q3','SB_Q4','SB_Q5','SB_Q6','SB_Y2','SB_Y3']  
        avgtn_ticlist = ['LT_Q1','LT_Q2','LT_Q3','LT_Q4','LT_Q5','LT_Q6','LT_Y2','LT_Y3']  
        lowtn_ticlist = ['LT_Q1','LT_Q2','LT_Q3','LT_Q4','LT_Q5','LT_Q6','LT_Y2','LT_Y3'] 
        hightn_ticlist = ['LT_Q1','LT_Q2','LT_Q3','LT_Q4','LT_Q5','LT_Q6','LT_Y2','LT_Y3']    
        avgur_ticlist = ['UXA_Q1','UXA_Q2','UXA_Q3','UXA_Q4','UXA_Q5','UXA_Q6','UXA_Y2','UXA_Y3']  
        lowur_ticlist = ['UXA_Q1','UXA_Q2','UXA_Q3','UXA_Q4','UXA_Q5','UXA_Q6','UXA_Y2','UXA_Y3'] 
        highur_ticlist = ['UXA_Q1','UXA_Q2','UXA_Q3','UXA_Q4','UXA_Q5','UXA_Q6','UXA_Y2','UXA_Y3'] 
        avgzn_ticlist = ['LX_Q1','LX_Q2','LX_Q3','LX_Q4','LX_Q5','LX_Q6','LX_Y2','LX_Y3']  
        lowzn_ticlist = ['LX_Q1','LX_Q2','LX_Q3','LX_Q4','LX_Q5','LX_Q6','LX_Y2','LX_Y3'] 
        highzn_ticlist = ['LX_Q1','LX_Q2','LX_Q3','LX_Q4','LX_Q5','LX_Q6','LX_Y2','LX_Y3']         
#############################################################################################################################################################################
        #corresponding fieldnames to text lists
        ureagrancfr_fieldlist = ['FLAT_CFR_BRA_BID','CFR_INT_BRA_BID','CFR_INT_BRA_BID','CFR_INT_BRA_BID','CFR_INT_BRA_BID','FLAT_CFR_BRA_MID','FLAT_CFR_BRA',
                                 'CFR_INT_BRA_MID','CFR_INT_BRA_MID','CFR_INT_BRA_MID','CFR_INT_BRA_MID','FLAT_CFR_BRA_OFFER','CFR_INT_BRA_OFFER','CFR_INT_BRA_OFFER','CFR_INT_BRA_OFFER',
                                 'CFR_INT_BRA_OFFER','FLAT_CFR_MDTRN','FLAT_CFR_KOR','FLAT_CFR_ASIA-SE']
        ureagrandel_fieldlist = ['FLAT_DEL_CA','FLAT_DEL_USA-NP','FLAT_DEL_USA-PNW-NW','FLAT_DEL_CAN-W']
        ureagranfca_fieldlist = ['FLAT_FCA_FRA']
        ureagranfob_fieldlist = ['FLAT_FOB_DZA','FLAT_FOB_ARB-GULF-ALL-NB_BID','FLAT_FOB_ARB-GULF-ALL-NB_MID','FLAT_FOB_ARB-GULF-ALL-NB_OFFER','FLAT_FOB_ARB-GULF-NOUS-NB_BID',
                                 'FLAT_FOB_ARB-GULF-NOUS-NB_MID','FLAT_FOB_ARB-GULF-NOUS-NB_OFFER','FLAT_FOB_ARB-GULF-US-NB_BID','FLAT_FOB_ARB-GULF-US-NB_MID','FLAT_FOB_ARB-GULF-US-NB_OFFER',
                                 'FLAT_FOB_AR-RVR','FLAT_FOB_BAL_BID','FLAT_FOB_BAL_MID','FLAT_FOB_BAL','FLAT_FOB_BAL_OFFER','FLAT_FOB_BLK-SEA','FLAT_FOB_CHN_BID','FLAT_FOB_CHN_MID',
                                 'FLAT_FOB_CHN','FLAT_FOB_CHN_OFFER','FLAT_FOB_EGY_BID','FLAT_FOB_EGY_MID','FLAT_FOB_EGY','FLAT_FOB_EGY_OFFER','FLAT_FOB_IDN','FLAT_FOB_IRN_BID',
                                 'FLAT_FOB_IRN_MID','FLAT_FOB_IRN','FLAT_FOB_IRN_OFFER','FLAT_FOB_MYS','FLAT_FOB_MEST-ALL-NB','FLAT_FOB_MEST-NOUS-NB','FLAT_FOB_MEST-US-NB',
                                 'FLAT_FOB_CBLT_ASK','FLAT_FOB_CBLT_BID','FLAT_FOB_CBLT_MID','FLAT_FOB_CBLT_OFFER','FLAT_FOB_GULF_ASK','FLAT_FOB_GULF_BID','FLAT_FOB_NOLA','FLAT_FOB_GULF_MID',
                                 'FLAT_FOB_GULF_OFFER','FLAT_FOB_AFR-N','FLAT_FOB_USA-S','FLAT_FOB_TX-C','FLAT_FOB_MN-MSP','FLAT_FOB_USA-EC','FLAT_FOB_USA-LKS','FLAT_FOB_USG_BID',
                                 'FLAT_FOB_USG_MID','FLAT_FOB_USG_OFFER','FLAT_FOB_USA-MW','FLAT_FOB_USA-SP','FLAT_FOB_VEN-TTO']
        ureagranfobfis_fieldlist = ['FOB_INT_EGY_BID','FOB_INT_EGY_BID','FOB_INT_EGY_BID','FOB_INT_EGY_BID','FOB_INT_EGY_MID','FOB_INT_EGY_MID','FOB_INT_EGY_MID','FOB_INT_EGY_MID',
                                    'FOB_INT_EGY_OFFER','FOB_INT_EGY_OFFER','FOB_INT_EGY_OFFER','FOB_INT_EGY_OFFER','FOB_INT_MEAST_BID','FOB_INT_MEAST_BID','FOB_INT_MEAST_BID',
                                    'FOB_INT_MEAST_BID','FOB_INT_MEAST_MID','FOB_INT_MEAST_MID','FOB_INT_MEAST_MID','FOB_INT_MEAST_MID','FOB_INT_MEAST_OFFER','FOB_INT_MEAST_OFFER',
                                    'FOB_INT_MEAST_OFFER','FOB_INT_MEAST_OFFER']+(['FOB_USA_NOLA_BID']*11)+(['FOB_USA_NOLA_MID']*11)+(['FOB_USA_NOLA_OFFER']*11) 
        ureaprillcfr_fieldlist = ['FLAT_CFR_BRA','FLAT_CFR_USA-CTL','FLAT_CFR_IND','FLAT_CFR_MDTRN','FLAT_CFR_PHL','FLAT_CFR_VNM']
        ureaprillcpt_fieldlist = ['FLAT_CPT_CHN','FLAT_EXW_CHN']
        ureaprillfob_fieldlist = ['FLAT_FOB_BAL-SEA','FLAT_FOB_BLK-SEA','FLAT_FOB_BGR-HRV-ROU','FLAT_FOB_CHN','FLAT_FOB_IDN','FLAT_FOB_MEST','FLAT_FOB_NOLA']
        ureaprillfobfis_fieldlist = (['FOB_INT_CHN_BID']*4)+(['FOB_INT_CHN_MID']*4)+(['FOB_INT_CHN_OFFER']*4)+(['FOB_INT_YUZHNY_BID']*4)+(['FOB_INT_YUZHNY_MID']*4)+(['FOB_INT_YUZHNY_OFFER']*4)
        ureaother_fieldlist = ['IPT_CHN_CLOSE']
        uan2830_fieldlist = ['FLAT_FCA_DEU','FLAT_FCA_URO']+(['FOT_INT_ROUEN_BID']*4)+(['FOT_INT_ROUEN_MID']*4)+(['FOT_INT_ROUEN_OFFER']*4)
        uan32_fieldlist = ['FLAT_CFR_USA-EC','FLAT_FOB_BAL_BID','FLAT_FOB_BAL_MID','FLAT_FOB_BAL_OFFER','FLAT_FOB_BLK-SEA_BID','FLAT_FOB_BLK-SEA_MID','FLAT_FOB_BLK-SEA','FLAT_FOB_BLK-SEA_OFFER',
                           'FLAT_FOB_NOLA_BID']+(['FOB_USA_NOLA_BID']*9)+['FLAT_FOB_NOLA_MID','FLAT_FOB_NOLA']+(['FOB_USA_NOLA_MID']*9)+['FLAT_FOB_NOLA_OFFER']+(['FOB_USA_NOLA_OFFER']*9)
        uanother_fieldlist = ['FLAT_DEL_CA','FLAT_FOB_BAL','FLAT_FOB_EGY','FLAT_FOB_CBLT_ASK','FLAT_FOB_CBLT_BID','FLAT_FOB_CBLT_MID','FLAT_FOB_CBLT_OFFER','FLAT_FOB_GULF_ASK',
                              'FLAT_FOB_GULF_BID','FLAT_FOB_NOLA','FLAT_FOB_GULF_MID','FLAT_FOB_GULF_OFFER','FLAT_FOB_USA-EC','FLAT_FOB_USA-MW','FLAT_FOB_USA-MW-E',
                              'FLAT_FOB_USA-MW-W','FLAT_FOB_USA-PNW-NW','FLAT_FOB_USA-SP']
        potgran_fieldlist = ['FLAT_CFR_BRA','FLAT_CIF_EUR-NW','FLAT_DEL_USA-MW','FLAT_FOB_BAL-SEA','FLAT_FOB_NOLA','FLAT_FOB_CAN-SK','FLAT_FOB_USA-S','FLAT_FOB_USA-CNM',
                             'FLAT_FOB_USA-MW-E','FLAT_FOB_USA-MW-W','FLAT_FOB_VAN']
        potstan_fieldlist = ['FLAT_CFR_CHN','FLAT_CFR_IND','FLAT_CFR_ASIA-SE','FLAT_CPT_CHN-RUS','FLAT_FCA_CHN','FLAT_FOB_BAL-SEA','FLAT_FOB_JOR-ISR','FLAT_FOB_USA-CNM','FLAT_FOB_VAN']
        ammspot_fieldlist = ['FLAT_FOB_MEST']
        ammtotcfr_fieldlist = ['FLAT_CFR_IND','FLAT_CFR_MAR','FLAT_CFR_NOLA-TX','FLAT_CFR_EUR-NW','FLAT_CFR_KOR-TWN','FLAT_CFR_EUR-S','FLAT_CFR_ASIA-SE','FLAT_CFR_TAMPA_ASK',
                               'FLAT_CFR_TAMPA_BID','FLAT_CFR_TAMPA','FLAT_CFR_TAMPA_MID','FLAT_CFR_TAMPA_OFFER','FLAT_CFR_TUR','FLAT_CFR_USG']
        ammtotdel_fieldlist = ['FLAT_DEL_CA','FLAT_DEL_USA-MW']
        ammtotfob_fieldlist = ['FLAT_FOB_BAL','FLAT_FOB_BLK-SEA','FLAT_FOB_CAR','FLAT_FOB_MEST','FLAT_FOB_CBLT_BID','FLAT_FOB_CBLT_MID','FLAT_FOB_CBLT_OFFER','FLAT_FOB_NOLA',
                               'FLAT_FOB_ASIA-SE','FLAT_FOB_USA-MW','FLAT_FOB_USA-MW-E','FLAT_FOB_USA-MW-W','FLAT_FOB_USA-NP','FLAT_FOB_USA-SP']
        ammcontract_fieldlist = ['FLAT_FOB_MEST']
        anbag_fieldlist = ['FLAT_FCA_FRA','FLAT_FCA_GBR']
        anbulk_fieldlist = ['FLAT_CPT_FRA']
        antotcfr_fieldlist = ['FLAT_CFR_BRA','FLAT_DEL_USA-S']
        antotfob_fieldlist = ['FLAT_FOB_BAL-SEA','FLAT_FOB_BLK-SEA','FLAT_FOB_NOLA','FLAT_FOB_USA-SE','FLAT_FOB_USA-MW','FLAT_FOB_USA-SP']
        asother_fieldlist = ['FLAT_FOB_BAL','FLAT_FOB_USA-MW']
        asstan_fieldlist = ['FLAT_FOB_BLK-SEA']
        aswcfr_fieldlist = ['FLAT_CFR_BRA','FLAT_CFR_ASIA-SE']
        aswfob_fieldlist = ['FLAT_FOB_BLK-SEA','FLAT_FOB_CHN']
        can_fieldlist = ['FLAT_CIF_BEL-NLD-LUX','FLAT_CIF_DEU']
        dapfob_fieldlist = ['FLAT_FOB_AUS','FLAT_FOB_BAL-BLK-SEA','FLAT_FOB_FL-CTL','FLAT_FOB_CHN','FLAT_FOB_JOR','FLAT_FOB_MEX','FLAT_FOB_MAR']+(['FOB_USA_NOLA_BID']*5)+['FLAT_FOB_NOLA']+(['FOB_USA_NOLA_MID']*5)+(['FOB_USA_NOLA_OFFER']*5)+['FLAT_FOB_AFR-N',
                            'FLAT_FOB_SAU','FLAT_FOB_USA-S','FLAT_FOB_TUN','FLAT_FOB_USG_BID','FLAT_FOB_USG_MID','FLAT_FOB_USG_OFFER','FLAT_FOB_USG-TAMPA',
                            'FLAT_FOB_USA-MW','FLAT_FOB_USA-MW-E','FLAT_FOB_USA-MW-W','FLAT_FOB_USA-SP']
        dapother_fieldlist = ['FLAT_CFR_ARG-URY','FLAT_CFR_IND','FLAT_CFR_PAK','FLAT_CPT_CHN','FLAT_DEL_CA','FLAT_DEL_USA-NW','FLAT_EXW_CHN','FLAT_FCA_BEL-GHE']
        map10_fieldlist = ['FLAT_EXW_CHN','FLAT_EXW_CHN']
        mapother_fieldlist = ['FLAT_CFR_BRA','FLAT_FOB_BAL-BLK-SEA','FLAT_FOB_FL-CTL','FLAT_FOB_MEX','FLAT_FOB_MAR','FLAT_FOB_NOLA','FLAT_FOB_USG-TAMPA']
        npk10_fieldlist = ['FLAT_CFR_IND','FLAT_FOB_BAL-BLK-SEA']
        npk15_fieldlist = ['FLAT_CIF_DEU','FLAT_FOB_BAL-SEA','FLAT_EXW_CHN','FLAT_EXW_CHN']
        npk16_fieldlist = ['FLAT_CFR_CHN','FLAT_CFR_ASIA-SE','FLAT_FOB_BAL-SEA']
        npk17_fieldlist = ['FLAT_CPT_FRA']
        npk20_fieldlist = ['FLAT_CPT_GBR']
        phosrock_fieldlist = ['FLAT_FOB_EGY','FLAT_FOB_PER','FLAT_CFR_IND','FLAT_FOB_JOR','FLAT_FOB_MAR','FLAT_CFR_IND','FLAT_FOB_JOR']
        phosacid_fieldlist = ['FLAT_CFR_IND','FLAT_CFR_MDTRN','FLAT_CFR_EUR-NW','FLAT_FOB_AFR-N']
        sopssp_fieldlist = ['FLAT_FCA_EUR-NW','FLAT_CPT_BRA']
        sspot_fieldlist = ['FLAT_CFR_CHN','FLAT_CFR_IND','FLAT_FOB_MEST','FLAT_FOB_VAN']
        stot_fieldlist = ['FLAT_CFR_BRA','FLAT_EXW_CHN','FLAT_FCA_CHN','FLAT_FOB_BLK-SEA']
        s6m_fieldlist = ['FLAT_CFR_AFR-N','FLAT_FOB_MEST','FLAT_FOB_VAN']
        sgreat_fieldlist = ['FLAT_CFR_MDTRN-AFR-N-CTRCT','FLAT_CFR_MDTRN-EXD-CTRCT']
        sliq_fieldlist = ['FLAT_CFR_BEL-NLD-LUX','FLAT_CPT_EUR-NW','FLAT_FOB_TAMPA']
        smonth_fieldlist = ['FLAT_FOB_ADNOC','FLAT_FOB_ARMCO','FLAT_FOB_TSWQ']
        sq_fieldlist = ['FLAT_CFR_CHN','FLAT_CFR_AFR-N','FLAT_FOB_MEST','FLAT_FOB_VAN']
        saspot_fieldlist = ['FLAT_CFR_CHL','FLAT_CFR_IND','FLAT_CFR_USG']
        satot_fieldlist = ['FLAT_CFR_BRA','FLAT_CFR_EUR-NW','FLAT_CFR_TUR','FLAT_FOB_JAP-KOR']
        sacon_fieldlist = ['FLAT_FOB_EUR-NW','FLAT_CFR_CHL','FLAT_CFR_TUN']
        tsp_fieldlist = ['FLAT_CFR_BRA','FLAT_FCA_BEL-NLD-LUX','FLAT_FOB_CHN','FLAT_FOB_MAR','FLAT_FOB_TUN']
        coale_fieldlist = ['CLOSE','HIGH','LOW','OPEN','VOLUME']
        coalara_fieldlist = ['CLOSE'] * 4
        coalr_fieldlist = ['CLOSE'] * 4
        petrolinv_fieldlist = ['TOTALSTOCKEXCLSPR']
        ngnclose_fieldlist = ['CLOSE'] * 12
        ngnhigh_fieldlist = ['HIGH'] * 12
        ngnlow_fieldlist = ['LOW'] * 12
        ngnopen_fieldlist = ['OPEN'] * 12
        ngnvol_fieldlist = ['VOLUME'] * 12
        ngnbp_fieldlist = ['CLOSE'] * 4
        wticlose_fieldlist = ['CLOSE'] * 12
        wtihigh_fieldlist = ['HIGH'] * 12
        wtilow_fieldlist = ['LOW'] * 12
        wtiopen_fieldlist = ['OPEN'] * 12
        wtivol_fieldlist = ['VOLUME'] * 12
        brentclose_fieldlist = ['CLOSE'] * 10
        brenthigh_fieldlist = ['HIGH'] * 10
        brentlow_fieldlist = ['LOW'] * 10
        brentopen_fieldlist = ['OPEN'] * 10
        brentvol_fieldlist = ['VOLUME'] * 10
        hoclose_fieldlist = ['CLOSE'] * 17
        hohigh_fieldlist = ['HIGH'] * 17
        holow_fieldlist = ['LOW'] * 17
        hoopen_fieldlist = ['OPEN'] * 17
        hovol_fieldlist = ['VOLUME'] * 17
        rbobclose_fieldlist = ['CLOSE'] * 12
        rbobhigh_fieldlist = ['HIGH'] * 12
        rboblow_fieldlist = ['LOW'] * 12
        rbobopen_fieldlist = ['OPEN'] * 12
        rbobvol_fieldlist = ['VOLUME'] * 12
        alclose_fieldlist = ['CLOSE'] * 2
        alhigh_fieldlist = ['HIGH'] * 2
        allow_fieldlist = ['LOW'] * 2
        alopen_fieldlist = ['OPEN'] * 2
        alvol_fieldlist = ['VOLUME'] * 2  
        cuclose_fieldlist = ['CLOSE'] * 12
        cuhigh_fieldlist = ['HIGH'] * 12
        culow_fieldlist = ['LOW'] * 12
        cuopen_fieldlist = ['OPEN'] * 12
        cuvol_fieldlist = ['VOLUME'] * 12   
        auclose_fieldlist = ['CLOSE'] * 22
        auhigh_fieldlist = ['HIGH'] * 22
        aulow_fieldlist = ['LOW'] * 22
        auopen_fieldlist = ['OPEN'] * 22
        auvol_fieldlist = ['VOLUME'] * 22
        feclose_fieldlist = ['CLOSE'] * 2
        fehigh_fieldlist = ['HIGH'] * 2
        felow_fieldlist = ['LOW'] * 2
        feopen_fieldlist = ['OPEN'] * 2
        fevol_fieldlist = ['VOLUME'] * 2  
        pbclose_fieldlist = ['CLOSE'] * 2
        pbhigh_fieldlist = ['HIGH'] * 2
        pblow_fieldlist = ['LOW'] * 2
        pbopen_fieldlist = ['OPEN'] * 2
        pbvol_fieldlist = ['VOLUME'] * 2  
        niclose_fieldlist = ['CLOSE'] * 2
        nihigh_fieldlist = ['HIGH'] * 2
        nilow_fieldlist = ['LOW'] * 2
        niopen_fieldlist = ['OPEN'] * 2
        nivol_fieldlist = ['VOLUME'] * 2  
        paclose_fieldlist = ['CLOSE'] * 2
        pahigh_fieldlist = ['HIGH'] * 2
        palow_fieldlist = ['LOW'] * 2
        paopen_fieldlist = ['OPEN'] * 2
        pavol_fieldlist = ['VOLUME'] * 2  
        plclose_fieldlist = ['CLOSE'] * 2
        plhigh_fieldlist = ['HIGH'] * 2
        pllow_fieldlist = ['LOW'] * 2
        plopen_fieldlist = ['OPEN'] * 2
        plvol_fieldlist = ['VOLUME'] * 2   
        agclose_fieldlist = ['CLOSE'] * 7
        aghigh_fieldlist = ['HIGH'] * 7
        aglow_fieldlist = ['LOW'] * 7
        agopen_fieldlist = ['OPEN'] * 7
        agvol_fieldlist = ['VOLUME'] * 7  
        stclose_fieldlist = ['CLOSE'] * 2
        sthigh_fieldlist = ['HIGH'] * 2
        stlow_fieldlist = ['LOW'] * 2
        stopen_fieldlist = ['OPEN'] * 2
        stvol_fieldlist = ['VOLUME'] * 2      
        tnclose_fieldlist = ['CLOSE'] * 2
        tnhigh_fieldlist = ['HIGH'] * 2
        tnlow_fieldlist = ['LOW'] * 2
        tnopen_fieldlist = ['OPEN'] * 2
        tnvol_fieldlist = ['VOLUME'] * 2   
        urclose_fieldlist = ['CLOSE'] * 2
        urhigh_fieldlist = ['HIGH'] * 2
        urlow_fieldlist = ['LOW'] * 2
        uropen_fieldlist = ['OPEN'] * 2
        urvol_fieldlist = ['VOLUME'] * 2 
        znclose_fieldlist = ['CLOSE'] * 2
        znhigh_fieldlist = ['HIGH'] * 2
        znlow_fieldlist = ['LOW'] * 2
        znopen_fieldlist = ['OPEN'] * 2
        znvol_fieldlist = ['VOLUME'] * 2    
        cornclose_fieldlist = ['CLOSE'] * 15
        cornhigh_fieldlist = ['HIGH'] * 15
        cornlow_fieldlist = ['LOW'] * 15
        cornopen_fieldlist = ['OPEN'] * 15
        cornvol_fieldlist = ['VOLUME'] * 15 
        wheatclose_fieldlist = ['CLOSE'] * 15
        wheathigh_fieldlist = ['HIGH'] * 15
        wheatlow_fieldlist = ['LOW'] * 15
        wheatopen_fieldlist = ['OPEN'] * 15
        wheatvol_fieldlist = ['VOLUME'] * 15    
        soyclose_fieldlist = ['CLOSE'] * 15
        soyhigh_fieldlist = ['HIGH'] * 15
        soylow_fieldlist = ['LOW'] * 15
        soyopen_fieldlist = ['OPEN'] * 15
        soyvol_fieldlist = ['VOLUME'] * 15  
        soclose_fieldlist = ['CLOSE'] * 15
        sohigh_fieldlist = ['HIGH'] * 15
        solow_fieldlist = ['LOW'] * 15
        soopen_fieldlist = ['OPEN'] * 15
        sovol_fieldlist = ['VOLUME'] * 15  
        cotclose_fieldlist = ['CLOSE'] * 7
        cothigh_fieldlist = ['HIGH'] * 7
        cotlow_fieldlist = ['LOW'] * 7
        cotopen_fieldlist = ['OPEN'] * 7
        cotvol_fieldlist = ['VOLUME'] * 7    
        sbclose_fieldlist = ['CLOSE'] * 12
        sbhigh_fieldlist = ['HIGH'] * 12
        sblow_fieldlist = ['LOW'] * 12
        sbopen_fieldlist = ['OPEN'] * 12
        sbvol_fieldlist = ['VOLUME'] * 12 
        sincurrency_fieldlist = ['CLOSE'] * 11
        crosscurrency_fieldlist = ['CLOSE'] * 6  
        equity_fieldlist = ['CLOSE','HIGH','LOW','OPEN','VOLUME'] * 3
        sent_fieldlist = (['CLOSE']*4)+['ALLSECURITIES','ALLSECURITIES_AVG21','EQUITY','EQUITY_AVG21','INDEX','INDEX_AVG21','CLOSE','CLOSE','CLOSE']
        imammtot_fieldlist = ['AG-IMPORT_ACT'] * 48
        imamman_fieldlist = ['AG-IMPORT_ACT'] * 47
        imammnittot_fieldlist = ['AG-IMPORT_ACT'] * 51
        imammnitaq_fieldlist = ['AG-IMPORT_ACT'] * 51
        imammsu_fieldlist = ['AG-IMPORT_ACT'] * 42
        imdap_fieldlist = ['AG-IMPORT_ACT'] * 39
        imint_fieldlist = ['AG-IMPORT_ACT'] * 2
        immaptot_fieldlist = ['AG-IMPORT_ACT'] * 47 
        immapmix_fieldlist = ['AG-IMPORT_ACT'] * 21
        imphosac_fieldlist = ['AG-IMPORT_ACT'] * 12
        impot_fieldlist = ['AG-IMPORT_ACT'] * 49
        imtsptot_fieldlist = ['AG-IMPORT_ACT'] * 29
        imtspless_fieldlist = ['AG-IMPORT_ACT'] * 17
        imtspgreat_fieldlist = ['AG-IMPORT_ACT'] * 27
        imuantot_fieldlist = ['AG-IMPORT_ACT'] * 40
        imuanmix_fieldlist = ['AG-IMPORT_ACT'] * 40 
        imureatot_fieldlist = ['AG-IMPORT_ACT'] * 83
        imureadef_fieldlist = ['AG-IMPORT_ACT'] * 8
        imureanesoi_fieldlist = ['AG-IMPORT_ACT'] * 35
        imureasolid_fieldlist = ['AG-IMPORT_ACT'] * 34
        imureaaq_fieldlist = ['AG-IMPORT_ACT'] * 68
        exammtot_fieldlist = ['AG-EXPORT_ACT'] * 72
        examman_fieldlist = ['AG-EXPORT_ACT'] * 62
        exammnittot_fieldlist = ['AG-EXPORT_ACT'] * 44
        exammnitaq_fieldlist = ['AG-EXPORT_ACT'] * 44
        exammsu_fieldlist = ['AG-EXPORT_ACT'] * 90
        exdap_fieldlist = ['AG-EXPORT_ACT'] * 76
        exnpk_fieldlist = ['AG-EXPORT_ACT'] 
        exmaptot_fieldlist = ['AG-EXPORT_ACT'] * 72
        exmapmix_fieldlist = ['AG-EXPORT_ACT'] * 59
        exphosac_fieldlist = ['AG-EXPORT_ACT'] * 12
        expot_fieldlist = ['AG-EXPORT_ACT'] * 161
        extsptot_fieldlist = ['AG-EXPORT_ACT'] * 37 
        extspless_fieldlist = ['AG-EXPORT_ACT'] * 29
        extspgreat_fieldlist = ['AG-EXPORT_ACT'] * 19
        exuantot_fieldlist = ['AG-EXPORT_ACT'] * 34
        exuanmix_fieldlist = ['AG-EXPORT_ACT'] * 34
        exureatot_fieldlist = ['AG-EXPORT_ACT'] * 129
        exureaaq_fieldlist = ['AG-EXPORT_ACT'] * 83
        sdamm_fieldlist = ['FORC_CPC_BASE','FORC_CPC_BEAR','FORC_CPC_BULL','FORC_DMD_BASE','FORC_DMD_BEAR','FORC_DMD_BULL','FORC_UTL_BASE','FORC_UTL_BEAR','FORC_UTL_BULL']
        sddapmapus_fieldlist = ['ALL_END-INVNTRY','ACT_END-INVNTRY','FORC_END-INVNTRY','ALL_PRODUCED','ACT_PRODUCED','FORC_PRODUCED']
        sddapmapall_fieldlist = ['FORC_CPC_BASE','FORC_CPC_BEAR','FORC_CPC_BULL','FORC_DMD_BASE','FORC_DMD_BEAR','FORC_DMD_BULL','FORC_UTL_BASE','FORC_UTL_BEAR','FORC_UTL_BULL']
        sdpotus_fieldlist = ['ALL_END-INVNTRY','ACT_END-INVNTRY','FORC_END-INVNTRY','ALL_PRODUCED','ACT_PRODUCED','FORC_PRODUCED']
        sdpotall_fieldlist = ['FORC_CPC_BASE','FORC_CPC_BEAR','FORC_CPC_BULL','FORC_DMD_BASE','FORC_DMD_BEAR','FORC_DMD_BULL','FORC_UTL_BASE','FORC_UTL_BEAR','FORC_UTL_BULL']        
        sduan_fieldlist = ['ALL_END-INVNTRY','ACT_END-INVNTRY','FORC_END-INVNTRY','ALL_PRODUCED','ACT_PRODUCED','FORC_PRODUCED']
        sdureaus_fieldlist = ['ALL_END-INVNTRY','ACT_END-INVNTRY','FORC_END-INVNTRY','ALL_PRODUCED','ACT_PRODUCED','FORC_PRODUCED']
        sdureaall_fieldlist = ['FORC_CPC_BASE','FORC_CPC_BEAR','FORC_CPC_BULL','FORC_DMD_BASE','FORC_DMD_BEAR','FORC_DMD_BULL','FORC_UTL_BASE','FORC_UTL_BEAR','FORC_UTL_BULL']      
        dapbid_fieldlist = ['FERTILIZER-FRT_DRY_BID'] * 14
        dapoffer_fieldlist = ['FERTILIZER-FRT_DRY_OFFER'] * 14
        dapmid_fieldlist = ['FERTILIZER-FRT_DRY_MID'] * 14
        mopbid_fieldlist = ['FERTILIZER-FRT_DRY_BID'] * 13
        mopoffer_fieldlist = ['FERTILIZER-FRT_DRY_OFFER'] * 13
        mopmid_fieldlist = ['FERTILIZER-FRT_DRY_MID'] * 13     
        phorockbid_fieldlist = ['FERTILIZER-FRT_DRY_BID'] * 2
        phorockoffer_fieldlist = ['FERTILIZER-FRT_DRY_OFFER'] * 2
        phorockmid_fieldlist = ['FERTILIZER-FRT_DRY_MID'] * 2  
        sulfurbid_fieldlist = ['FERTILIZER-FRT_DRY_BID'] * 7
        sulfuroffer_fieldlist = ['FERTILIZER-FRT_DRY_OFFER'] * 7
        sulfurmid_fieldlist = ['FERTILIZER-FRT_DRY_MID'] * 7 
        ureabid_fieldlist = ['FERTILIZER-FRT_DRY_BID'] * 17
        ureaoffer_fieldlist = ['FERTILIZER-FRT_DRY_OFFER'] * 17
        ureamid_fieldlist = ['FERTILIZER-FRT_DRY_MID'] * 17   
        ammbid_fieldlist = ['FERTILIZER-FRT_LQD_BID'] * 10
        ammoffer_fieldlist = ['FERTILIZER-FRT_LQD_OFFER'] * 10
        ammmid_fieldlist = ['FERTILIZER-FRT_LQD_MID'] * 10   
        phoacbid_fieldlist = ['FERTILIZER-FRT_LQD_BID'] * 2
        phoacoffer_fieldlist = ['FERTILIZER-FRT_LQD_OFFER'] * 2
        phoacmid_fieldlist = ['FERTILIZER-FRT_LQD_MID'] * 2    
        sulacbid_fieldlist = ['FERTILIZER-FRT_LQD_BID'] * 6
        sulacoffer_fieldlist = ['FERTILIZER-FRT_LQD_OFFER'] * 6
        sulacmid_fieldlist = ['FERTILIZER-FRT_LQD_MID'] * 6   
        uanbid_fieldlist = ['FERTILIZER-FRT_LQD_BID'] * 2
        uanoffer_fieldlist = ['FERTILIZER-FRT_LQD_OFFER'] * 2
        uanmid_fieldlist = ['FERTILIZER-FRT_LQD_MID'] * 2  
        chsdap_fieldlist = (['FOB_MWEST_PRICE']*13)+(['FOB_NOLA_PRICE']*13)    
        chspot_fieldlist = (['FOB_MWEST_PRICE']*13)+(['FOB_NOLA_PRICE']*13) 
        chsuan_fieldlist = (['FOB_MWEST_PRICE']*13)+(['FOB_NOLA_PRICE']*13) 
        chsurea_fieldlist = (['FOB_MWEST_PRICE']*13)+(['FOB_NOLA_PRICE']*13) 
        buckdap_fieldlist = (['FOB_MWEST_PRICE']*13)+(['FOB_NOLA_PRICE']*13)    
        buckpot_fieldlist = (['FOB_MWEST_PRICE']*13)+(['FOB_NOLA_PRICE']*13) 
        buckuan_fieldlist = (['FOB_MWEST_PRICE']*13)+(['FOB_NOLA_PRICE']*13) 
        buckurea_fieldlist = (['FOB_MWEST_PRICE']*13)+(['FOB_NOLA_PRICE']*13) 
        cru_fieldlist = (['FOB_TAMPA_PRICE']*13)+(['FOB_NOLA_PRICE']*13)
        avgcorn_fieldlist = ['CMD-FORC_AVG'] * 8  
        lowcorn_fieldlist = ['CMD-FORC_LOW'] * 8
        highcorn_fieldlist = ['CMD-FORC_HIGH'] * 8     
        avgsoy_fieldlist = ['CMD-FORC_AVG'] * 8   
        lowsoy_fieldlist = ['CMD-FORC_LOW'] * 8
        highsoy_fieldlist = ['CMD-FORC_HIGH'] * 8      
        avgso_fieldlist = ['CMD-FORC_AVG'] * 8   
        lowso_fieldlist = ['CMD-FORC_LOW'] * 8
        highso_fieldlist = ['CMD-FORC_HIGH'] * 8     
        avgwheat_fieldlist = ['CMD-FORC_AVG'] * 8      
        lowwheat_fieldlist = ['CMD-FORC_LOW'] * 8
        highwheat_fieldlist = ['CMD-FORC_HIGH'] * 8     
        avgwti_fieldlist = ['CMD-FORC_AVG'] * 8  
        lowwti_fieldlist = ['CMD-FORC_LOW'] * 8 
        highwti_fieldlist = ['CMD-FORC_HIGH'] * 8     
        avgng_fieldlist = ['CMD-FORC_AVG'] * 8   
        lowng_fieldlist = ['CMD-FORC_LOW'] * 8 
        highng_fieldlist = ['CMD-FORC_HIGH'] * 8     
        avgcot_fieldlist = ['CMD-FORC_AVG'] * 8   
        lowcot_fieldlist = ['CMD-FORC_LOW'] * 8
        highcot_fieldlist = ['CMD-FORC_HIGH'] * 8    
        avgal_fieldlist = ['CMD-FORC_AVG'] * 8  
        lowal_fieldlist = ['CMD-FORC_LOW'] * 8
        highal_fieldlist = ['CMD-FORC_HIGH'] * 8    
        avgara_fieldlist = ['CMD-FORC_AVG'] * 8   
        lowara_fieldlist = ['CMD-FORC_LOW'] * 8
        highara_fieldlist = ['CMD-FORC_HIGH'] * 8     
        avgrb_fieldlist = ['CMD-FORC_AVG'] * 8  
        lowrb_fieldlist = ['CMD-FORC_LOW'] * 8
        highrb_fieldlist = ['CMD-FORC_HIGH'] * 8    
        avgcu_fieldlist = ['CMD-FORC_AVG'] * 8  
        lowcu_fieldlist = ['CMD-FORC_LOW'] * 8 
        highcu_fieldlist = ['CMD-FORC_HIGH'] * 8    
        avgau_fieldlist = ['CMD-FORC_AVG'] * 8   
        lowau_fieldlist = ['CMD-FORC_LOW'] * 8
        highau_fieldlist = ['CMD-FORC_HIGH'] * 8    
        avgho_fieldlist = ['CMD-FORC_AVG'] * 8  
        lowho_fieldlist = ['CMD-FORC_LOW'] * 8 
        highho_fieldlist = ['CMD-FORC_HIGH'] * 8      
        avgice_fieldlist = ['CMD-FORC_AVG'] * 8   
        lowice_fieldlist = ['CMD-FORC_LOW'] * 8 
        highice_fieldlist = ['CMD-FORC_HIGH'] * 8      
        avgfe_fieldlist = ['CMD-FORC_AVG'] * 8   
        lowfe_fieldlist = ['CMD-FORC_LOW'] * 8
        highfe_fieldlist = ['CMD-FORC_HIGH'] * 8      
        avgpb_fieldlist = ['CMD-FORC_AVG'] * 8  
        lowpb_fieldlist = ['CMD-FORC_LOW'] * 8
        highpb_fieldlist = ['CMD-FORC_HIGH'] * 8     
        avgnbp_fieldlist = ['CMD-FORC_AVG'] * 8   
        lowrnbp_fieldlist = ['CMD-FORC_LOW'] * 8
        highnbp_fieldlist = ['CMD-FORC_HIGH'] * 8     
        avgni_fieldlist = ['CMD-FORC_AVG'] * 8  
        lowni_fieldlist = ['CMD-FORC_LOW'] * 8
        highni_fieldlist = ['CMD-FORC_HIGH'] * 8     
        avgpa_fieldlist = ['CMD-FORC_AVG'] * 8  
        lowpa_fieldlist = ['CMD-FORC_LOW'] * 8
        highpa_fieldlist = ['CMD-FORC_HIGH'] * 8    
        avgpt_fieldlist = ['CMD-FORC_AVG'] * 8 
        lowpt_fieldlist = ['CMD-FORC_LOW'] * 8
        highpt_fieldlist = ['CMD-FORC_HIGH'] * 8    
        avgrbob_fieldlist = ['CMD-FORC_AVG'] * 8  
        lowrbob_fieldlist = ['CMD-FORC_LOW'] * 8
        highrbob_fieldlist = ['CMD-FORC_HIGH'] * 8      
        avgag_fieldlist = ['CMD-FORC_AVG'] * 8  
        lowag_fieldlist = ['CMD-FORC_LOW'] * 8
        highag_fieldlist = ['CMD-FORC_HIGH'] * 8    
        avgst_fieldlist = ['CMD-FORC_AVG'] * 8   
        lowst_fieldlist = ['CMD-FORC_LOW'] * 8
        highst_fieldlist = ['CMD-FORC_HIGH'] * 8     
        avgsb_fieldlist = ['CMD-FORC_AVG'] * 8  
        lowsb_fieldlist = ['CMD-FORC_LOW'] * 8
        highsb_fieldlist = ['CMD-FORC_HIGH'] * 8     
        avgtn_fieldlist = ['CMD-FORC_AVG'] * 8 
        lowtn_fieldlist = ['CMD-FORC_LOW'] * 8 
        hightn_fieldlist = ['CMD-FORC_HIGH'] * 8       
        avgur_fieldlist = ['CMD-FORC_AVG'] * 8 
        lowur_fieldlist = ['CMD-FORC_LOW'] * 8
        highur_fieldlist = ['CMD-FORC_HIGH'] * 8    
        avgzn_fieldlist = ['CMD-FORC_AVG'] * 8  
        lowzn_fieldlist = ['CMD-FORC_LOW'] * 8 
        highzn_fieldlist = ['CMD-FORC_HIGH'] * 8          
#############################################################################################################################################################################
        #corresponding source to text lists
        ureagrancfr_sourcelist = ['ARGUS','FIS','FIS','FIS','FIS','ARGUS','CRU','FIS','FIS','FIS','FIS','ARGUS','FIS','FIS','FIS','FIS','CRU','CRU','CRU']                         
        ureagrandel_sourcelist = ['CRU','CRU','CRU','CRU'] 
        ureagranfca_sourcelist = ['CRU']
        ureagranfob_sourcelist = ['CRU','ARGUS','ARGUS','ARGUS','ARGUS','ARGUS','ARGUS','ARGUS','ARGUS','ARGUS','CRU','ARGUS','ARGUS','CRU','ARGUS','CRU','ARGUS','ARGUS',
                                  'CRU','ARGUS','ARGUS','ARGUS','CRU','ARGUS','CRU','ARGUS','ARGUS','CRU','ARGUS','CRU','CRU','CRU','CRU','GREEN-MARKETS','GREEN-MARKETS',
                                  'GREEN-MARKETS','GREEN-MARKETS','GREEN-MARKETS','GREEN-MARKETS','CRU','GREEN-MARKETS','GREEN-MARKETS','CRU','CRU','CRU','CRU','CRU','CRU',
                                  'ARGUS','ARGUS','ARGUS','CRU','CRU','CRU']
        ureagranfobfis_sourcelist = ['FIS'] * 57
        ureaprillcfr_sourcelist = ['CRU'] * 6
        ureaprillcpt_sourcelist = ['CRU'] * 2
        ureaprillfob_sourcelist = ['CRU'] * 7
        ureaprillfobfis_sourcelist = ['FIS'] * 24
        ureaother_sourcelist = ['CHN-NBS']
        uan2830_sourcelist = ['CRU','CRU']+(['FIS']*12)
        uan32_sourcelist = ['CRU']+(['ARGUS']*5)+['CRU','ARGUS','ARGUS']+(['FIS']*9)+['ARGUS','CRU']+(['FIS']*9)+['ARGUS']+(['FIS']*9)
        uanother_sourcelist = ['CRU','CRU','CRU']+(['GREEN-MARKETS']*6)+['CRU']+['GREEN-MARKETS','GREEN-MARKETS']+(['CRU']*6)
        potgran_sourcelist = ['CRU'] * 11
        potstan_sourcelist = ['CRU'] * 9
        ammspot_sourcelist = ['CRU']
        ammtotcfr_sourcelist = (['CRU']*7)+(['GREEN_MARKETS']*2)+['CRU']+(['GREEN_MARKETS']*2)+(['CRU']*2)
        ammtotdel_sourcelist = ['CRU','CRU']
        ammtotfob_sourcelist = (['CRU']*4)+(['GREEN_MARKETS']*3)+(['CRU']*7)
        ammcontract_sourcelist = ['CRU']
        anbag_sourcelist = ['CRU'] * 2
        anbulk_sourcelist = ['CRU']
        antotcfr_sourcelist = ['CRU'] * 2
        antotfob_sourcelist = ['CRU'] * 6
        asother_sourcelist = ['CRU'] * 2
        asstan_sourcelist = ['CRU']
        aswcfr_sourcelist = ['CRU'] * 2
        aswfob_sourcelist = ['CRU'] * 2
        can_sourcelist = ['CRU'] * 2
        dapfob_sourcelist = (['CRU']*7)+(['FIS']*5)+['CRU']+(['FIS']*10)+(['CRU']*4)+(['ARGUS']*3)+(['CRU']*5)
        dapother_sourcelist = ['CRU'] * 8
        map10_sourcelist = ['CRU'] * 2
        mapother_sourcelist = ['CRU'] * 7
        npk10_sourcelist = ['CRU'] * 2
        npk15_sourcelist = ['CRU'] * 4
        npk16_sourcelist = ['CRU'] * 3
        npk17_sourcelist = ['CRU'] 
        npk20_sourcelist = ['CRU']
        phosrock_sourcelist = ['CRU'] * 7
        phosacid_sourcelist = ['CRU'] * 4
        sopssp_sourcelist = ['CRU'] * 2
        sspot_sourcelist = ['CRU'] * 4
        stot_sourcelist = ['CRU'] * 4
        s6m_sourcelist = ['CRU'] * 3
        sgreat_sourcelist = ['CRU'] * 2
        sliq_sourcelist = ['CRU'] * 3
        smonth_sourcelist = ['CRU'] * 3
        sq_sourcelist = ['CRU'] * 4
        saspot_sourcelist = ['CRU'] * 3
        satot_sourcelist = ['CRU'] * 4
        sacon_sourcelist = ['CRU'] * 3
        tsp_sourcelist = ['CRU'] * 5
        coale_sourcelist = ['EXCH'] * 5
        coalara_sourcelist = ['BLOOMBERG'] * 4
        coalr_sourcelist = ['BLOOMBERG'] * 4
        petrolinv_sourcelist = ['EIA']
        ngnclose_sourcelist = ['EXCH'] * 12
        ngnhigh_sourcelist = ['EXCH'] * 12
        ngnlow_sourcelist = ['EXCH'] * 12
        ngnopen_sourcelist = ['EXCH'] * 12
        ngnvol_sourcelist = ['EXCH'] * 12
        ngnbp_sourcelist = ['BLOOMBERG'] * 4
        wticlose_sourcelist = ['EXCH'] * 12
        wtihigh_sourcelist = ['EXCH'] * 12
        wtilow_sourcelist = ['EXCH'] * 12
        wtiopen_sourcelist = ['EXCH'] * 12
        wtivol_sourcelist = ['EXCH'] * 12
        brentclose_sourcelist = ['EXCH'] * 10
        brenthigh_sourcelist = ['EXCH'] * 10
        brentlow_sourcelist = ['EXCH'] * 10
        brentopen_sourcelist = ['EXCH'] * 10
        brentvol_sourcelist = ['EXCH'] * 10  
        hoclose_sourcelist = ['EXCH'] * 17
        hohigh_sourcelist = ['EXCH'] * 17
        holow_sourcelist = ['EXCH'] * 17
        hoopen_sourcelist = ['EXCH'] * 17
        hovol_sourcelist = ['EXCH'] * 17  
        rbobclose_sourcelist = ['EXCH'] * 12
        rbobhigh_sourcelist = ['EXCH'] * 12
        rboblow_sourcelist = ['EXCH'] * 12
        rbobopen_sourcelist = ['EXCH'] * 12
        rbobvol_sourcelist = ['EXCH'] * 12
        alclose_sourcelist = ['EXCH'] * 2
        alhigh_sourcelist = ['EXCH'] * 2
        allow_sourcelist = ['EXCH'] * 2
        alopen_sourcelist = ['EXCH'] * 2
        alvol_sourcelist = ['EXCH'] * 2
        cuclose_sourcelist = ['EXCH'] * 12
        cuhigh_sourcelist = ['EXCH'] * 12
        culow_sourcelist = ['EXCH'] * 12
        cuopen_sourcelist = ['EXCH'] * 12
        cuvol_sourcelist = ['EXCH'] * 12
        auclose_sourcelist = ['EXCH'] * 22
        auhigh_sourcelist = ['EXCH'] * 22
        aulow_sourcelist = ['EXCH'] * 22
        auopen_sourcelist = ['EXCH'] * 22
        auvol_sourcelist = ['EXCH'] * 22  
        feclose_sourcelist = ['EXCH'] * 2
        fehigh_sourcelist = ['EXCH'] * 2
        felow_sourcelist = ['EXCH'] * 2
        feopen_sourcelist = ['EXCH'] * 2
        fevol_sourcelist = ['EXCH'] * 2 
        pbclose_sourcelist = ['EXCH'] * 2
        pbhigh_sourcelist = ['EXCH'] * 2
        pblow_sourcelist = ['EXCH'] * 2
        pbopen_sourcelist = ['EXCH'] * 2
        pbvol_sourcelist = ['EXCH'] * 2       
        niclose_sourcelist = ['EXCH'] * 2
        nihigh_sourcelist = ['EXCH'] * 2
        nilow_sourcelist = ['EXCH'] * 2
        niopen_sourcelist = ['EXCH'] * 2
        nivol_sourcelist = ['EXCH'] * 2  
        paclose_sourcelist = ['EXCH'] * 2
        pahigh_sourcelist = ['EXCH'] * 2
        palow_sourcelist = ['EXCH'] * 2
        paopen_sourcelist = ['EXCH'] * 2
        pavol_sourcelist = ['EXCH'] * 2    
        plclose_sourcelist = ['EXCH'] * 2
        plhigh_sourcelist = ['EXCH'] * 2
        pllow_sourcelist = ['EXCH'] * 2
        plopen_sourcelist = ['EXCH'] * 2
        plvol_sourcelist = ['EXCH'] * 2   
        agclose_sourcelist = ['EXCH'] * 7
        aghigh_sourcelist = ['EXCH'] * 7
        aglow_sourcelist = ['EXCH'] * 7
        agopen_sourcelist = ['EXCH'] * 7
        agvol_sourcelist = ['EXCH'] * 7  
        stclose_sourcelist = ['EXCH'] * 2
        sthigh_sourcelist = ['EXCH'] * 2
        stlow_sourcelist = ['EXCH'] * 2
        stopen_sourcelist = ['EXCH'] * 2
        stvol_sourcelist = ['EXCH'] * 2  
        tnclose_sourcelist = ['EXCH'] * 2
        tnhigh_sourcelist = ['EXCH'] * 2
        tnlow_sourcelist = ['EXCH'] * 2
        tnopen_sourcelist = ['EXCH'] * 2
        tnvol_sourcelist = ['EXCH'] * 2   
        urclose_sourcelist = ['EXCH'] * 2
        urhigh_sourcelist = ['EXCH'] * 2
        urlow_sourcelist = ['EXCH'] * 2
        uropen_sourcelist = ['EXCH'] * 2
        urvol_sourcelist = ['EXCH'] * 2  
        znclose_sourcelist = ['EXCH'] * 2
        znhigh_sourcelist = ['EXCH'] * 2
        znlow_sourcelist = ['EXCH'] * 2
        znopen_sourcelist = ['EXCH'] * 2
        znvol_sourcelist = ['EXCH'] * 2  
        cornclose_sourcelist = ['EXCH'] *15
        cornhigh_sourcelist = ['EXCH'] * 15
        cornlow_sourcelist = ['EXCH'] * 15
        cornopen_sourcelist = ['EXCH'] * 15
        cornvol_sourcelist = ['EXCH'] * 15  
        wheatclose_sourcelist = ['EXCH'] *15
        wheathigh_sourcelist = ['EXCH'] * 15
        wheatlow_sourcelist = ['EXCH'] * 15
        wheatopen_sourcelist = ['EXCH'] * 15
        wheatvol_sourcelist = ['EXCH'] * 15 
        soyclose_sourcelist = ['EXCH'] *15
        soyhigh_sourcelist = ['EXCH'] * 15
        soylow_sourcelist = ['EXCH'] * 15
        soyopen_sourcelist = ['EXCH'] * 15
        soyvol_sourcelist = ['EXCH'] * 15 
        soclose_sourcelist = ['EXCH'] *15
        sohigh_sourcelist = ['EXCH'] * 15
        solow_sourcelist = ['EXCH'] * 15
        soopen_sourcelist = ['EXCH'] * 15
        sovol_sourcelist = ['EXCH'] * 15   
        cotclose_sourcelist = ['EXCH'] * 7
        cothigh_sourcelist = ['EXCH'] * 7
        cotlow_sourcelist = ['EXCH'] * 7
        cotopen_sourcelist = ['EXCH'] * 7
        cotvol_sourcelist = ['EXCH'] * 7  
        sbclose_sourcelist = ['EXCH'] * 12
        sbhigh_sourcelist = ['EXCH'] * 12
        sblow_sourcelist = ['EXCH'] * 12
        sbopen_sourcelist = ['EXCH'] * 12
        sbvol_sourcelist = ['EXCH'] * 12 
        sincurrency_sourcelist = ['PUB'] * 11
        crosscurrency_sourcelist = ['PUB'] * 6 
        equity_sourcelist = ['EXCH'] * 15
        sent_sourcelist = ['BLOOMBERG','PUB','DTN-RESEARCH','DTN-RESEARCH']+(['ISEE']*6)+['PUB','PUB','PUB']
        imammtot_sourcelist = ['USITC','CHN-GAC']+(['USITC']*46)
        imamman_sourcelist = ['USITC'] * 47
        imammnittot_sourcelist = ['USITC'] * 51
        imammnitaq_sourcelist = ['USITC'] * 51
        imammsu_sourcelist = ['USITC'] * 42
        imdap_sourcelist = ['IFA','IFA','CHN-GAC']+(['IFA']*7)+['USITC','IFA','IFA']+(['USITC']*26)
        imint_sourcelist = ['NAFD','CHN-GAC']
        immaptot_sourcelist = ['IFA','IFA','CHN-GAC']+(['IFA']*7)+['USITC','IFA','IFA','IFA']+(['USITC']*33)
        immapmix_sourcelist = ['USITC'] * 21
        imphosac_sourcelist = ['IFA'] * 12
        impot_sourcelist = ['IFA','IFA','IFA','CHN-GAC']+(['IFA']*7)+ ['USITC','IFA','IFA']+(['USITC']*35)
        imtsptot_sourcelist = ['USITC'] * 29
        imtspless_sourcelist = ['USITC'] * 17
        imtspgreat_sourcelist = ['USITC'] * 27
        imuantot_sourcelist = ['USITC'] * 40
        imuanmix_sourcelist = ['USITC'] * 40
        imureatot_sourcelist = (['IFA']*10)+['USITC','IFA','IFA']+(['USITC']*70)
        imureadef_sourcelist = ['USITC'] * 8
        imureanesoi_sourcelist = ['USITC'] * 35
        imureasolid_sourcelist = ['USITC'] * 34
        imureaaq_sourcelist = ['USITC'] * 68
        exammtot_sourcelist = (['CUSTOMS']*10)+(['USITC']*62)
        examman_sourcelist = ['USITC'] * 62
        exammnittot_sourcelist = ['USITC'] * 44
        exammnitaq_sourcelist = ['USITC'] * 44
        exammsu_sourcelist = (['CUSTOMS']*22)+(['USITC']*68)
        exdap_sourcelist = ['IFA','IFA','CHN-NCI']+(['IFA']*7)+(['USITC']*63)+(['IFA']*3)
        exnpk_sourcelist = ['NAFD']
        exmaptot_sourcelist = ['IFA','IFA','CHN-NCI']+(['IFA']*7)+(['USITC']*59)+(['IFA']*3)
        exmapmix_sourcelist = ['USITC'] * 59
        exphosac_sourcelist = ['IFA'] * 12
        expot_sourcelist = ['IFA','IFA']+(['CUSTOMS']*65)+(['IFA']*8)+(['USITC']*84)+['IFA','IFA']
        extsptot_sourcelist = ['CHN-NCI']+(['USITC']*36)
        extspless_sourcelist = ['USITC'] * 29
        extspgreat_sourcelist = ['USITC'] * 19
        exuantot_sourcelist = ['USITC'] * 34
        exuanmix_sourcelist = ['USITC'] * 34
        exureatot_sourcelist = ['IFA','IFA'] + (['CUSTOMS']*33) + ['IFA','CHN-GAC']+(['IFA']*7)+(['USITC']*83)+['IFA','IFA']
        exureaaq_sourcelist = ['USITC'] * 83
        sdamm_sourcelist = ['GREEN-MARKETS'] * 9
        sddapmapus_sourcelist = ['IFA'] * 6
        sddapmapall_sourcelist = ['GREEN-MARKETS'] * 9
        sdpotus_sourcelist = ['IFA'] * 6
        sdpotall_sourcelist = ['GREEN-MARKETS'] * 9   
        sduan_sourcelist = ['IFA'] * 6
        sdureaus_sourcelist = ['IFA'] * 6
        sdureaall_sourcelist = ['GREEN-MARKETS'] * 9 
        dapbid_sourcelist = ['CRU'] * 14
        dapoffer_sourcelist = ['CRU'] * 14
        dapmid_sourcelist = ['CRU'] * 14
        mopbid_sourcelist = ['CRU'] * 13
        mopoffer_sourcelist = ['CRU'] * 13
        mopmid_sourcelist = ['CRU'] * 13        
        phorockbid_sourcelist = ['CRU'] * 2
        phorockoffer_sourcelist = ['CRU'] * 2
        phorockmid_sourcelist = ['CRU'] * 2  
        sulfurbid_sourcelist = ['CRU'] * 7
        sulfuroffer_sourcelist = ['CRU'] * 7
        sulfurmid_sourcelist = ['CRU'] * 7  
        ureabid_sourcelist = ['CRU'] * 17
        ureaoffer_sourcelist = ['CRU'] * 17
        ureamid_sourcelist = ['CRU'] * 17 
        ammbid_sourcelist = ['CRU'] * 10
        ammoffer_sourcelist = ['CRU'] * 10
        ammmid_sourcelist = ['CRU'] * 10  
        phoacbid_sourcelist = ['CRU'] * 2
        phoacoffer_sourcelist = ['CRU'] * 2
        phoacmid_sourcelist = ['CRU'] * 2  
        sulacbid_sourcelist = ['CRU'] * 6
        sulacoffer_sourcelist = ['CRU'] * 6
        sulacmid_sourcelist = ['CRU'] * 6  
        uanbid_sourcelist = ['CRU'] * 2
        uanoffer_sourcelist = ['CRU'] * 2
        uanmid_sourcelist = ['CRU'] * 2   
        chsdap_sourcelist = ['CHS'] * 26
        chspot_sourcelist = ['CHS'] * 26
        chsuan_sourcelist = ['CHS'] * 26
        chsurea_sourcelist = ['CHS'] * 26
        buckdap_sourcelist = ['BUCKLEY'] * 26
        buckpot_sourcelist = ['BUCKLEY'] * 26
        buckuan_sourcelist = ['BUCKLEY'] * 26
        buckurea_sourcelist = ['BUCKLEY'] * 26  
        cru_sourcelist = ['CRU'] * 26
#############################################################################################################################################################################
        #creating dictionaries so name and ticker, field, source go together
        #print(len(exureaaq_list),len(exureaaq_ticlist),len(exureaaq_fieldlist),len(exureaaq_sourcelist))
        dictTickerureagrancfr = {}
        dictFieldureagrancfr = {}
        dictSourceureagrancfr = {}
        for i in range(0,len(ureagrancfr_list)):
            dictTickerureagrancfr[ureagrancfr_list[i]] = ureagrancfr_ticlist[i]
            dictFieldureagrancfr[ureagrancfr_list[i]] = ureagrancfr_fieldlist[i]
            dictSourceureagrancfr[ureagrancfr_list[i]] = ureagrancfr_sourcelist[i] 
        dictTickerureagrandel = {}
        dictFieldureagrandel = {}
        dictSourceureagrandel = {}
        for i in range(0,len(ureagrandel_list)):
            dictTickerureagrandel[ureagrandel_list[i]] = ureagrandel_ticlist[i]
            dictFieldureagrandel[ureagrandel_list[i]] = ureagrandel_fieldlist[i]
            dictSourceureagrandel[ureagrandel_list[i]] = ureagrandel_sourcelist[i]      
        dictTickerureagranfca = {}
        dictFieldureagranfca = {}
        dictSourceureagranfca = {}
        for i in range(0,len(ureagranfca_list)):
            dictTickerureagranfca[ureagranfca_list[i]] = ureagranfca_ticlist[i]
            dictFieldureagranfca[ureagranfca_list[i]] = ureagranfca_fieldlist[i]
            dictSourceureagranfca[ureagranfca_list[i]] = ureagranfca_sourcelist[i]                               
        dictTickerureagranfob = {}
        dictFieldureagranfob = {}
        dictSourceureagranfob = {}
        for i in range(0,len(ureagranfob_list)):
            dictTickerureagranfob[ureagranfob_list[i]] = ureagranfob_ticlist[i]
            dictFieldureagranfob[ureagranfob_list[i]] = ureagranfob_fieldlist[i]
            dictSourceureagranfob[ureagranfob_list[i]] = ureagranfob_sourcelist[i] 
        dictTickerureagranfobfis = {}
        dictFieldureagranfobfis = {}
        dictSourceureagranfobfis = {}
        for i in range(0,len(ureagranfobfis_list)):
            dictTickerureagranfobfis[ureagranfobfis_list[i]] = ureagranfobfis_ticlist[i]
            dictFieldureagranfobfis[ureagranfobfis_list[i]] = ureagranfobfis_fieldlist[i]
            dictSourceureagranfobfis[ureagranfobfis_list[i]] = ureagranfobfis_sourcelist[i]            
        dictTickerureaprillcfr = {}
        dictFieldureaprillcfr = {}
        dictSourceureaprillcfr = {}
        for i in range(0,len(ureaprillcfr_list)):
            dictTickerureaprillcfr[ureaprillcfr_list[i]] = ureaprillcfr_ticlist[i]
            dictFieldureaprillcfr[ureaprillcfr_list[i]] = ureaprillcfr_fieldlist[i]
            dictSourceureaprillcfr[ureaprillcfr_list[i]] = ureaprillcfr_sourcelist[i] 
        dictTickerureaprillcpt = {}
        dictFieldureaprillcpt = {}
        dictSourceureaprillcpt = {}
        for i in range(0,len(ureaprillcpt_list)):
            dictTickerureaprillcpt[ureaprillcpt_list[i]] = ureaprillcpt_ticlist[i]
            dictFieldureaprillcpt[ureaprillcpt_list[i]] = ureaprillcpt_fieldlist[i]
            dictSourceureaprillcpt[ureaprillcpt_list[i]] = ureaprillcpt_sourcelist[i]    
        dictTickerureaprillfob = {}
        dictFieldureaprillfob = {}
        dictSourceureaprillfob = {}
        for i in range(0,len(ureaprillfob_list)):
            dictTickerureaprillfob[ureaprillfob_list[i]] = ureaprillfob_ticlist[i]
            dictFieldureaprillfob[ureaprillfob_list[i]] = ureaprillfob_fieldlist[i]
            dictSourceureaprillfob[ureaprillfob_list[i]] = ureaprillfob_sourcelist[i]
        dictTickerureaprillfobfis = {}
        dictFieldureaprillfobfis = {}
        dictSourceureaprillfobfis = {}
        for i in range(0,len(ureaprillfobfis_list)):
            dictTickerureaprillfobfis[ureaprillfobfis_list[i]] = ureaprillfobfis_ticlist[i]
            dictFieldureaprillfobfis[ureaprillfobfis_list[i]] = ureaprillfobfis_fieldlist[i]
            dictSourceureaprillfobfis[ureaprillfobfis_list[i]] = ureaprillfobfis_sourcelist[i]    
        dictTickerureaother = {}
        dictFieldureaother = {}
        dictSourceureaother = {}
        for i in range(0,len(ureaother_list)):
            dictTickerureaother[ureaother_list[i]] = ureaother_ticlist[i]
            dictFieldureaother[ureaother_list[i]] = ureaother_fieldlist[i]
            dictSourceureaother[ureaother_list[i]] = ureaother_sourcelist[i]   
        dictTickeruan2830 = {}
        dictFielduan2830 = {}
        dictSourceuan2830 = {}
        for i in range(0,len(uan2830_list)):
            dictTickeruan2830[uan2830_list[i]] = uan2830_ticlist[i]
            dictFielduan2830[uan2830_list[i]] = uan2830_fieldlist[i]
            dictSourceuan2830[uan2830_list[i]] = uan2830_sourcelist[i]  
        dictTickeruan32 = {}
        dictFielduan32 = {}
        dictSourceuan32 = {}
        for i in range(0,len(uan32_list)):
            dictTickeruan32[uan32_list[i]] = uan32_ticlist[i]
            dictFielduan32[uan32_list[i]] = uan32_fieldlist[i]
            dictSourceuan32[uan32_list[i]] = uan32_sourcelist[i]        
        dictTickeruanother = {}
        dictFielduanother = {}
        dictSourceuanother = {}
        for i in range(0,len(uanother_list)):
            dictTickeruanother[uanother_list[i]] = uanother_ticlist[i]
            dictFielduanother[uanother_list[i]] = uanother_fieldlist[i]
            dictSourceuanother[uanother_list[i]] = uanother_sourcelist[i]   
        dictTickerpotgran = {}
        dictFieldpotgran = {}
        dictSourcepotgran = {}
        for i in range(0,len(potgran_list)):
            dictTickerpotgran[potgran_list[i]] = potgran_ticlist[i]
            dictFieldpotgran[potgran_list[i]] = potgran_fieldlist[i]
            dictSourcepotgran[potgran_list[i]] = potgran_sourcelist[i]
        dictTickerpotstan = {}
        dictFieldpotstan = {}
        dictSourcepotstan = {}
        for i in range(0,len(potstan_list)):
            dictTickerpotstan[potstan_list[i]] = potstan_ticlist[i]
            dictFieldpotstan[potstan_list[i]] = potstan_fieldlist[i]
            dictSourcepotstan[potstan_list[i]] = potstan_sourcelist[i]   
        dictTickerammspot = {}
        dictFieldammspot = {}
        dictSourceammspot = {}
        for i in range(0,len(ammspot_list)):
            dictTickerammspot[ammspot_list[i]] = ammspot_ticlist[i]
            dictFieldammspot[ammspot_list[i]] = ammspot_fieldlist[i]
            dictSourceammspot[ammspot_list[i]] = ammspot_sourcelist[i]   
        dictTickerammtotcfr = {}
        dictFieldammtotcfr = {}
        dictSourceammtotcfr = {}
        for i in range(0,len(ammtotcfr_list)):
            dictTickerammtotcfr[ammtotcfr_list[i]] = ammtotcfr_ticlist[i]
            dictFieldammtotcfr[ammtotcfr_list[i]] = ammtotcfr_fieldlist[i]
            dictSourceammtotcfr[ammtotcfr_list[i]] = ammtotcfr_sourcelist[i]    
        dictTickerammtotdel = {}
        dictFieldammtotdel = {}
        dictSourceammtotdel = {}
        for i in range(0,len(ammtotdel_list)):
            dictTickerammtotdel[ammtotdel_list[i]] = ammtotdel_ticlist[i]
            dictFieldammtotdel[ammtotdel_list[i]] = ammtotdel_fieldlist[i]
            dictSourceammtotdel[ammtotdel_list[i]] = ammtotdel_sourcelist[i]   
        dictTickerammtotfob = {}
        dictFieldammtotfob = {}
        dictSourceammtotfob = {}
        for i in range(0,len(ammtotfob_list)):
            dictTickerammtotfob[ammtotfob_list[i]] = ammtotfob_ticlist[i]
            dictFieldammtotfob[ammtotfob_list[i]] = ammtotfob_fieldlist[i]
            dictSourceammtotfob[ammtotfob_list[i]] = ammtotfob_sourcelist[i]  
        dictTickerammcontract = {}
        dictFieldammcontract = {}
        dictSourceammcontract = {}
        for i in range(0,len(ammcontract_list)):
            dictTickerammcontract[ammcontract_list[i]] = ammcontract_ticlist[i]
            dictFieldammcontract[ammcontract_list[i]] = ammcontract_fieldlist[i]
            dictSourceammcontract[ammcontract_list[i]] = ammcontract_sourcelist[i]             
        dictTickeranbag = {}
        dictFieldanbag = {}
        dictSourceanbag = {}
        for i in range(0,len(anbag_list)):
            dictTickeranbag[anbag_list[i]] = anbag_ticlist[i]
            dictFieldanbag[anbag_list[i]] = anbag_fieldlist[i]
            dictSourceanbag[anbag_list[i]] = anbag_sourcelist[i]        
        dictTickeranbulk = {}
        dictFieldanbulk = {}
        dictSourceanbulk = {}
        for i in range(0,len(anbulk_list)):
            dictTickeranbulk[anbulk_list[i]] = anbulk_ticlist[i]
            dictFieldanbulk[anbulk_list[i]] = anbulk_fieldlist[i]
            dictSourceanbulk[anbulk_list[i]] = anbulk_sourcelist[i]   
        dictTickerantotcfr = {}
        dictFieldantotcfr = {}
        dictSourceantotcfr = {}
        for i in range(0,len(antotcfr_list)):
            dictTickerantotcfr[antotcfr_list[i]] = antotcfr_ticlist[i]
            dictFieldantotcfr[antotcfr_list[i]] = antotcfr_fieldlist[i]
            dictSourceantotcfr[antotcfr_list[i]] = antotcfr_sourcelist[i]        
        dictTickerantotfob = {}
        dictFieldantotfob = {}
        dictSourceantotfob = {}
        for i in range(0,len(antotfob_list)):
            dictTickerantotfob[antotfob_list[i]] = antotfob_ticlist[i]
            dictFieldantotfob[antotfob_list[i]] = antotfob_fieldlist[i]
            dictSourceantotfob[antotfob_list[i]] = antotfob_sourcelist[i]    
        dictTickerasother = {}
        dictFieldasother = {}
        dictSourceasother = {}
        for i in range(0,len(asother_list)):
            dictTickerasother[asother_list[i]] = asother_ticlist[i]
            dictFieldasother[asother_list[i]] = asother_fieldlist[i]
            dictSourceasother[asother_list[i]] = asother_sourcelist[i]  
        dictTickerasstan = {}
        dictFieldasstan = {}
        dictSourceasstan = {}
        for i in range(0,len(asstan_list)):
            dictTickerasstan[asstan_list[i]] = asstan_ticlist[i]
            dictFieldasstan[asstan_list[i]] = asstan_fieldlist[i]
            dictSourceasstan[asstan_list[i]] = asstan_sourcelist[i]     
        dictTickeraswcfr = {}
        dictFieldaswcfr = {}
        dictSourceaswcfr = {}
        for i in range(0,len(aswcfr_list)):
            dictTickeraswcfr[aswcfr_list[i]] = aswcfr_ticlist[i]
            dictFieldaswcfr[aswcfr_list[i]] = aswcfr_fieldlist[i]
            dictSourceaswcfr[aswcfr_list[i]] = aswcfr_sourcelist[i]  
        dictTickeraswfob = {}
        dictFieldaswfob = {}
        dictSourceaswfob = {}
        for i in range(0,len(aswfob_list)):
            dictTickeraswfob[aswfob_list[i]] = aswfob_ticlist[i]
            dictFieldaswfob[aswfob_list[i]] = aswfob_fieldlist[i]
            dictSourceaswfob[aswfob_list[i]] = aswfob_sourcelist[i]     
        dictTickercan = {}
        dictFieldcan = {}
        dictSourcecan = {}
        for i in range(0,len(can_list)):
            dictTickercan[can_list[i]] = can_ticlist[i]
            dictFieldcan[can_list[i]] = can_fieldlist[i]
            dictSourcecan[can_list[i]] = can_sourcelist[i] 
        dictTickerdapfob = {}
        dictFielddapfob = {}
        dictSourcedapfob = {}
        for i in range(0,len(dapfob_list)):
            dictTickerdapfob[dapfob_list[i]] = dapfob_ticlist[i]
            dictFielddapfob[dapfob_list[i]] = dapfob_fieldlist[i]
            dictSourcedapfob[dapfob_list[i]] = dapfob_sourcelist[i] 
        dictTickerdapother = {}
        dictFielddapother = {}
        dictSourcedapother = {}
        for i in range(0,len(dapother_list)):
            dictTickerdapother[dapother_list[i]] = dapother_ticlist[i]
            dictFielddapother[dapother_list[i]] = dapother_fieldlist[i]
            dictSourcedapother[dapother_list[i]] = dapother_sourcelist[i]
        dictTickermap10 = {}
        dictFieldmap10 = {}
        dictSourcemap10 = {}
        for i in range(0,len(map10_list)):
            dictTickermap10[map10_list[i]] = map10_ticlist[i]
            dictFieldmap10[map10_list[i]] = map10_fieldlist[i]
            dictSourcemap10[map10_list[i]] = map10_sourcelist[i]            
        dictTickermapother = {}
        dictFieldmapother = {}
        dictSourcemapother = {}
        for i in range(0,len(mapother_list)):
            dictTickermapother[mapother_list[i]] = mapother_ticlist[i]
            dictFieldmapother[mapother_list[i]] = mapother_fieldlist[i]
            dictSourcemapother[mapother_list[i]] = mapother_sourcelist[i]  
        dictTickernpk10 = {}
        dictFieldnpk10 = {}
        dictSourcenpk10 = {}
        for i in range(0,len(npk10_list)):
            dictTickernpk10[npk10_list[i]] = npk10_ticlist[i]
            dictFieldnpk10[npk10_list[i]] = npk10_fieldlist[i]
            dictSourcenpk10[npk10_list[i]] = npk10_sourcelist[i]             
        dictTickernpk15 = {}
        dictFieldnpk15 = {}
        dictSourcenpk15 = {}
        for i in range(0,len(npk15_list)):
            dictTickernpk15[npk15_list[i]] = npk15_ticlist[i]
            dictFieldnpk15[npk15_list[i]] = npk15_fieldlist[i]
            dictSourcenpk15[npk15_list[i]] = npk15_sourcelist[i]  
        dictTickernpk16 = {}
        dictFieldnpk16 = {}
        dictSourcenpk16 = {}
        for i in range(0,len(npk16_list)):
            dictTickernpk16[npk16_list[i]] = npk16_ticlist[i]
            dictFieldnpk16[npk16_list[i]] = npk16_fieldlist[i]
            dictSourcenpk16[npk16_list[i]] = npk16_sourcelist[i]  
        dictTickernpk17 = {}
        dictFieldnpk17 = {}
        dictSourcenpk17 = {}
        for i in range(0,len(npk17_list)):
            dictTickernpk17[npk17_list[i]] = npk17_ticlist[i]
            dictFieldnpk17[npk17_list[i]] = npk17_fieldlist[i]
            dictSourcenpk17[npk17_list[i]] = npk17_sourcelist[i]    
        dictTickernpk20 = {}
        dictFieldnpk20 = {}
        dictSourcenpk20 = {}
        for i in range(0,len(npk20_list)):
            dictTickernpk20[npk20_list[i]] = npk20_ticlist[i]
            dictFieldnpk20[npk20_list[i]] = npk20_fieldlist[i]
            dictSourcenpk20[npk20_list[i]] = npk20_sourcelist[i]     
        dictTickerphosrock = {}
        dictFieldphosrock = {}
        dictSourcephosrock = {}
        for i in range(0,len(phosrock_list)):
            dictTickerphosrock[phosrock_list[i]] = phosrock_ticlist[i]
            dictFieldphosrock[phosrock_list[i]] = phosrock_fieldlist[i]
            dictSourcephosrock[phosrock_list[i]] = phosrock_sourcelist[i]   
        dictTickerphosacid = {}
        dictFieldphosacid = {}
        dictSourcephosacid = {}
        for i in range(0,len(phosacid_list)):
            dictTickerphosacid[phosacid_list[i]] = phosacid_ticlist[i]
            dictFieldphosacid[phosacid_list[i]] = phosacid_fieldlist[i]
            dictSourcephosacid[phosacid_list[i]] = phosacid_sourcelist[i] 
        dictTickersopssp = {}
        dictFieldsopssp = {}
        dictSourcesopssp = {}
        for i in range(0,len(sopssp_list)):
            dictTickersopssp[sopssp_list[i]] = sopssp_ticlist[i]
            dictFieldsopssp[sopssp_list[i]] = sopssp_fieldlist[i]
            dictSourcesopssp[sopssp_list[i]] = sopssp_sourcelist[i]  
        dictTickersspot = {}
        dictFieldsspot = {}
        dictSourcesspot = {}
        for i in range(0,len(sspot_list)):
            dictTickersspot[sspot_list[i]] = sspot_ticlist[i]
            dictFieldsspot[sspot_list[i]] = sspot_fieldlist[i]
            dictSourcesspot[sspot_list[i]] = sspot_sourcelist[i] 
        dictTickerstot = {}
        dictFieldstot = {}
        dictSourcestot = {}
        for i in range(0,len(stot_list)):
            dictTickerstot[stot_list[i]] = stot_ticlist[i]
            dictFieldstot[stot_list[i]] = stot_fieldlist[i]
            dictSourcestot[stot_list[i]] = stot_sourcelist[i]  
        dictTickers6m = {}
        dictFields6m = {}
        dictSources6m = {}
        for i in range(0,len(s6m_list)):
            dictTickers6m[s6m_list[i]] = s6m_ticlist[i]
            dictFields6m[s6m_list[i]] = s6m_fieldlist[i]
            dictSources6m[s6m_list[i]] = s6m_sourcelist[i]     
        dictTickersgreat = {}
        dictFieldsgreat = {}
        dictSourcesgreat = {}
        for i in range(0,len(sgreat_list)):
            dictTickersgreat[sgreat_list[i]] = sgreat_ticlist[i]
            dictFieldsgreat[sgreat_list[i]] = sgreat_fieldlist[i]
            dictSourcesgreat[sgreat_list[i]] = sgreat_sourcelist[i]
        dictTickersliq = {}
        dictFieldsliq = {}
        dictSourcesliq = {}
        for i in range(0,len(sliq_list)):
            dictTickersliq[sliq_list[i]] = sliq_ticlist[i]
            dictFieldsliq[sliq_list[i]] = sliq_fieldlist[i]
            dictSourcesliq[sliq_list[i]] = sliq_sourcelist[i] 
        dictTickersmonth = {}
        dictFieldsmonth = {}
        dictSourcesmonth = {}
        for i in range(0,len(smonth_list)):
            dictTickersmonth[smonth_list[i]] = smonth_ticlist[i]
            dictFieldsmonth[smonth_list[i]] = smonth_fieldlist[i]
            dictSourcesmonth[smonth_list[i]] = smonth_sourcelist[i] 
        dictTickersq = {}
        dictFieldsq = {}
        dictSourcesq = {}
        for i in range(0,len(sq_list)):
            dictTickersq[sq_list[i]] = sq_ticlist[i]
            dictFieldsq[sq_list[i]] = sq_fieldlist[i]
            dictSourcesq[sq_list[i]] = sq_sourcelist[i]      
        dictTickersaspot = {}
        dictFieldsaspot = {}
        dictSourcesaspot = {}
        for i in range(0,len(saspot_list)):
            dictTickersaspot[saspot_list[i]] = saspot_ticlist[i]
            dictFieldsaspot[saspot_list[i]] = saspot_fieldlist[i]
            dictSourcesaspot[saspot_list[i]] = saspot_sourcelist[i] 
        dictTickersatot = {}
        dictFieldsatot = {}
        dictSourcesatot = {}
        for i in range(0,len(satot_list)):
            dictTickersatot[satot_list[i]] = satot_ticlist[i]
            dictFieldsatot[satot_list[i]] = satot_fieldlist[i]
            dictSourcesatot[satot_list[i]] = satot_sourcelist[i] 
        dictTickersacon = {}
        dictFieldsacon = {}
        dictSourcesacon = {}
        for i in range(0,len(sacon_list)):
            dictTickersacon[sacon_list[i]] = sacon_ticlist[i]
            dictFieldsacon[sacon_list[i]] = sacon_fieldlist[i]
            dictSourcesacon[sacon_list[i]] = sacon_sourcelist[i]   
        dictTickertsp = {}
        dictFieldtsp = {}
        dictSourcetsp = {}
        for i in range(0,len(tsp_list)):
            dictTickertsp[tsp_list[i]] = tsp_ticlist[i]
            dictFieldtsp[tsp_list[i]] = tsp_fieldlist[i]
            dictSourcetsp[tsp_list[i]] = tsp_sourcelist[i]    
        dictTickercoale = {}
        dictFieldcoale = {}
        dictSourcecoale = {}
        for i in range(0,len(coale_list)):
            dictTickercoale[coale_list[i]] = coale_ticlist[i]
            dictFieldcoale[coale_list[i]] = coale_fieldlist[i]
            dictSourcecoale[coale_list[i]] = coale_sourcelist[i]   
        dictTickercoalara = {}
        dictFieldcoalara = {}
        dictSourcecoalara = {}
        for i in range(0,len(coalara_list)):
            dictTickercoalara[coalara_list[i]] = coalara_ticlist[i]
            dictFieldcoalara[coalara_list[i]] = coalara_fieldlist[i]
            dictSourcecoalara[coalara_list[i]] = coalara_sourcelist[i]  
        dictTickercoalr = {}
        dictFieldcoalr = {}
        dictSourcecoalr = {}
        for i in range(0,len(coalr_list)):
            dictTickercoalr[coalr_list[i]] = coalr_ticlist[i]
            dictFieldcoalr[coalr_list[i]] = coalr_fieldlist[i]
            dictSourcecoalr[coalr_list[i]] = coalr_sourcelist[i]    
        dictTickerpetrolinv = {}
        dictFieldpetrolinv = {}
        dictSourcepetrolinv = {}
        for i in range(0,len(petrolinv_list)):
            dictTickerpetrolinv[petrolinv_list[i]] = petrolinv_ticlist[i]
            dictFieldpetrolinv[petrolinv_list[i]] = petrolinv_fieldlist[i]
            dictSourcepetrolinv[petrolinv_list[i]] = petrolinv_sourcelist[i]  
        dictTickerngnclose = {}
        dictFieldngnclose = {}
        dictSourcengnclose = {}
        for i in range(0,len(ngnclose_list)):
            dictTickerngnclose[ngnclose_list[i]] = ngnclose_ticlist[i]
            dictFieldngnclose[ngnclose_list[i]] = ngnclose_fieldlist[i]
            dictSourcengnclose[ngnclose_list[i]] = ngnclose_sourcelist[i] 
        dictTickerngnhigh = {}
        dictFieldngnhigh = {}
        dictSourcengnhigh = {}
        for i in range(0,len(ngnhigh_list)):
            dictTickerngnhigh[ngnhigh_list[i]] = ngnhigh_ticlist[i]
            dictFieldngnhigh[ngnhigh_list[i]] = ngnhigh_fieldlist[i]
            dictSourcengnhigh[ngnhigh_list[i]] = ngnhigh_sourcelist[i]
        dictTickerngnlow = {}
        dictFieldngnlow = {}
        dictSourcengnlow = {}
        for i in range(0,len(ngnlow_list)):
            dictTickerngnlow[ngnlow_list[i]] = ngnlow_ticlist[i]
            dictFieldngnlow[ngnlow_list[i]] = ngnlow_fieldlist[i]
            dictSourcengnlow[ngnlow_list[i]] = ngnlow_sourcelist[i] 
        dictTickerngnopen = {}
        dictFieldngnopen = {}
        dictSourcengnopen = {}
        for i in range(0,len(ngnopen_list)):
            dictTickerngnopen[ngnopen_list[i]] = ngnopen_ticlist[i]
            dictFieldngnopen[ngnopen_list[i]] = ngnopen_fieldlist[i]
            dictSourcengnopen[ngnopen_list[i]] = ngnopen_sourcelist[i]             
        dictTickerngnvol = {}
        dictFieldngnvol = {}
        dictSourcengnvol = {}
        for i in range(0,len(ngnvol_list)):
            dictTickerngnvol[ngnvol_list[i]] = ngnvol_ticlist[i]
            dictFieldngnvol[ngnvol_list[i]] = ngnvol_fieldlist[i]
            dictSourcengnvol[ngnvol_list[i]] = ngnvol_sourcelist[i]
        dictTickerngnbp = {}
        dictFieldngnbp = {}
        dictSourcengnbp = {}
        for i in range(0,len(ngnbp_list)):
            dictTickerngnbp[ngnbp_list[i]] = ngnbp_ticlist[i]
            dictFieldngnbp[ngnbp_list[i]] = ngnbp_fieldlist[i]
            dictSourcengnbp[ngnbp_list[i]] = ngnbp_sourcelist[i]             
        dictTickerwticlose = {}
        dictFieldwticlose = {}
        dictSourcewticlose = {}
        for i in range(0,len(wticlose_list)):
            dictTickerwticlose[wticlose_list[i]] = wticlose_ticlist[i]
            dictFieldwticlose[wticlose_list[i]] = wticlose_fieldlist[i]
            dictSourcewticlose[wticlose_list[i]] = wticlose_sourcelist[i] 
        dictTickerwtihigh = {}
        dictFieldwtihigh = {}
        dictSourcewtihigh = {}
        for i in range(0,len(wtihigh_list)):
            dictTickerwtihigh[wtihigh_list[i]] = wtihigh_ticlist[i]
            dictFieldwtihigh[wtihigh_list[i]] = wtihigh_fieldlist[i]
            dictSourcewtihigh[wtihigh_list[i]] = wtihigh_sourcelist[i]
        dictTickerwtilow = {}
        dictFieldwtilow = {}
        dictSourcewtilow = {}
        for i in range(0,len(wtilow_list)):
            dictTickerwtilow[wtilow_list[i]] = wtilow_ticlist[i]
            dictFieldwtilow[wtilow_list[i]] = wtilow_fieldlist[i]
            dictSourcewtilow[wtilow_list[i]] = wtilow_sourcelist[i] 
        dictTickerwtiopen = {}
        dictFieldwtiopen = {}
        dictSourcewtiopen = {}
        for i in range(0,len(wtiopen_list)):
            dictTickerwtiopen[wtiopen_list[i]] = wtiopen_ticlist[i]
            dictFieldwtiopen[wtiopen_list[i]] = wtiopen_fieldlist[i]
            dictSourcewtiopen[wtiopen_list[i]] = wtiopen_sourcelist[i]             
        dictTickerwtivol = {}
        dictFieldwtivol = {}
        dictSourcewtivol = {}
        for i in range(0,len(wtivol_list)):
            dictTickerwtivol[wtivol_list[i]] = wtivol_ticlist[i]
            dictFieldwtivol[wtivol_list[i]] = wtivol_fieldlist[i]
            dictSourcewtivol[wtivol_list[i]] = wtivol_sourcelist[i]             
        dictTickerbrentclose = {}
        dictFieldbrentclose = {}
        dictSourcebrentclose = {}
        for i in range(0,len(brentclose_list)):
            dictTickerbrentclose[brentclose_list[i]] = brentclose_ticlist[i]
            dictFieldbrentclose[brentclose_list[i]] = brentclose_fieldlist[i]
            dictSourcebrentclose[brentclose_list[i]] = brentclose_sourcelist[i] 
        dictTickerbrenthigh = {}
        dictFieldbrenthigh = {}
        dictSourcebrenthigh = {}
        for i in range(0,len(brenthigh_list)):
            dictTickerbrenthigh[brenthigh_list[i]] = brenthigh_ticlist[i]
            dictFieldbrenthigh[brenthigh_list[i]] = brenthigh_fieldlist[i]
            dictSourcebrenthigh[brenthigh_list[i]] = brenthigh_sourcelist[i]
        dictTickerbrentlow = {}
        dictFieldbrentlow = {}
        dictSourcebrentlow = {}
        for i in range(0,len(brentlow_list)):
            dictTickerbrentlow[brentlow_list[i]] = brentlow_ticlist[i]
            dictFieldbrentlow[brentlow_list[i]] = brentlow_fieldlist[i]
            dictSourcebrentlow[brentlow_list[i]] = brentlow_sourcelist[i] 
        dictTickerbrentopen = {}
        dictFieldbrentopen = {}
        dictSourcebrentopen = {}
        for i in range(0,len(brentopen_list)):
            dictTickerbrentopen[brentopen_list[i]] = brentopen_ticlist[i]
            dictFieldbrentopen[brentopen_list[i]] = brentopen_fieldlist[i]
            dictSourcebrentopen[brentopen_list[i]] = brentopen_sourcelist[i]             
        dictTickerbrentvol = {}
        dictFieldbrentvol = {}
        dictSourcebrentvol = {}
        for i in range(0,len(brentvol_list)):
            dictTickerbrentvol[brentvol_list[i]] = brentvol_ticlist[i]
            dictFieldbrentvol[brentvol_list[i]] = brentvol_fieldlist[i]
            dictSourcebrentvol[brentvol_list[i]] = brentvol_sourcelist[i]            
        dictTickerhoclose = {}
        dictFieldhoclose = {}
        dictSourcehoclose = {}
        for i in range(0,len(hoclose_list)):
            dictTickerhoclose[hoclose_list[i]] = hoclose_ticlist[i]
            dictFieldhoclose[hoclose_list[i]] = hoclose_fieldlist[i]
            dictSourcehoclose[hoclose_list[i]] = hoclose_sourcelist[i] 
        dictTickerhohigh = {}
        dictFieldhohigh = {}
        dictSourcehohigh = {}
        for i in range(0,len(hohigh_list)):
            dictTickerhohigh[hohigh_list[i]] = hohigh_ticlist[i]
            dictFieldhohigh[hohigh_list[i]] = hohigh_fieldlist[i]
            dictSourcehohigh[hohigh_list[i]] = hohigh_sourcelist[i]
        dictTickerholow = {}
        dictFieldholow = {}
        dictSourceholow = {}
        for i in range(0,len(holow_list)):
            dictTickerholow[holow_list[i]] = holow_ticlist[i]
            dictFieldholow[holow_list[i]] = holow_fieldlist[i]
            dictSourceholow[holow_list[i]] = holow_sourcelist[i] 
        dictTickerhoopen = {}
        dictFieldhoopen = {}
        dictSourcehoopen = {}
        for i in range(0,len(hoopen_list)):
            dictTickerhoopen[hoopen_list[i]] = hoopen_ticlist[i]
            dictFieldhoopen[hoopen_list[i]] = hoopen_fieldlist[i]
            dictSourcehoopen[hoopen_list[i]] = hoopen_sourcelist[i]             
        dictTickerhovol = {}
        dictFieldhovol = {}
        dictSourcehovol = {}
        for i in range(0,len(hovol_list)):
            dictTickerhovol[hovol_list[i]] = hovol_ticlist[i]
            dictFieldhovol[hovol_list[i]] = hovol_fieldlist[i]
            dictSourcehovol[hovol_list[i]] = hovol_sourcelist[i] 
        dictTickerrbobclose = {}
        dictFieldrbobclose = {}
        dictSourcerbobclose = {}
        for i in range(0,len(rbobclose_list)):
            dictTickerrbobclose[rbobclose_list[i]] = rbobclose_ticlist[i]
            dictFieldrbobclose[rbobclose_list[i]] = rbobclose_fieldlist[i]
            dictSourcerbobclose[rbobclose_list[i]] = rbobclose_sourcelist[i] 
        dictTickerrbobhigh = {}
        dictFieldrbobhigh = {}
        dictSourcerbobhigh = {}
        for i in range(0,len(rbobhigh_list)):
            dictTickerrbobhigh[rbobhigh_list[i]] = rbobhigh_ticlist[i]
            dictFieldrbobhigh[rbobhigh_list[i]] = rbobhigh_fieldlist[i]
            dictSourcerbobhigh[rbobhigh_list[i]] = rbobhigh_sourcelist[i]
        dictTickerrboblow = {}
        dictFieldrboblow = {}
        dictSourcerboblow = {}
        for i in range(0,len(rboblow_list)):
            dictTickerrboblow[rboblow_list[i]] = rboblow_ticlist[i]
            dictFieldrboblow[rboblow_list[i]] = rboblow_fieldlist[i]
            dictSourcerboblow[rboblow_list[i]] = rboblow_sourcelist[i] 
        dictTickerrbobopen = {}
        dictFieldrbobopen = {}
        dictSourcerbobopen = {}
        for i in range(0,len(rbobopen_list)):
            dictTickerrbobopen[rbobopen_list[i]] = rbobopen_ticlist[i]
            dictFieldrbobopen[rbobopen_list[i]] = rbobopen_fieldlist[i]
            dictSourcerbobopen[rbobopen_list[i]] = rbobopen_sourcelist[i]             
        dictTickerrbobvol = {}
        dictFieldrbobvol = {}
        dictSourcerbobvol = {}
        for i in range(0,len(rbobvol_list)):
            dictTickerrbobvol[rbobvol_list[i]] = rbobvol_ticlist[i]
            dictFieldrbobvol[rbobvol_list[i]] = rbobvol_fieldlist[i]
            dictSourcerbobvol[rbobvol_list[i]] = rbobvol_sourcelist[i]
        dictTickeralclose = {}
        dictFieldalclose = {}
        dictSourcealclose = {}
        for i in range(0,len(alclose_list)):
            dictTickeralclose[alclose_list[i]] = alclose_ticlist[i]
            dictFieldalclose[alclose_list[i]] = alclose_fieldlist[i]
            dictSourcealclose[alclose_list[i]] = alclose_sourcelist[i] 
        dictTickeralhigh = {}
        dictFieldalhigh = {}
        dictSourcealhigh = {}
        for i in range(0,len(alhigh_list)):
            dictTickeralhigh[alhigh_list[i]] = alhigh_ticlist[i]
            dictFieldalhigh[alhigh_list[i]] = alhigh_fieldlist[i]
            dictSourcealhigh[alhigh_list[i]] = alhigh_sourcelist[i]
        dictTickerallow = {}
        dictFieldallow = {}
        dictSourceallow = {}
        for i in range(0,len(allow_list)):
            dictTickerallow[allow_list[i]] = allow_ticlist[i]
            dictFieldallow[allow_list[i]] = allow_fieldlist[i]
            dictSourceallow[allow_list[i]] = allow_sourcelist[i] 
        dictTickeralopen = {}
        dictFieldalopen = {}
        dictSourcealopen = {}
        for i in range(0,len(alopen_list)):
            dictTickeralopen[alopen_list[i]] = alopen_ticlist[i]
            dictFieldalopen[alopen_list[i]] = alopen_fieldlist[i]
            dictSourcealopen[alopen_list[i]] = alopen_sourcelist[i]             
        dictTickeralvol = {}
        dictFieldalvol = {}
        dictSourcealvol = {}
        for i in range(0,len(alvol_list)):
            dictTickeralvol[alvol_list[i]] = alvol_ticlist[i]
            dictFieldalvol[alvol_list[i]] = alvol_fieldlist[i]
            dictSourcealvol[alvol_list[i]] = alvol_sourcelist[i]  
        dictTickercuclose = {}
        dictFieldcuclose = {}
        dictSourcecuclose = {}
        for i in range(0,len(cuclose_list)):
            dictTickercuclose[cuclose_list[i]] = cuclose_ticlist[i]
            dictFieldcuclose[cuclose_list[i]] = cuclose_fieldlist[i]
            dictSourcecuclose[cuclose_list[i]] = cuclose_sourcelist[i] 
        dictTickercuhigh = {}
        dictFieldcuhigh = {}
        dictSourcecuhigh = {}
        for i in range(0,len(cuhigh_list)):
            dictTickercuhigh[cuhigh_list[i]] = cuhigh_ticlist[i]
            dictFieldcuhigh[cuhigh_list[i]] = cuhigh_fieldlist[i]
            dictSourcecuhigh[cuhigh_list[i]] = cuhigh_sourcelist[i]
        dictTickerculow = {}
        dictFieldculow = {}
        dictSourceculow = {}
        for i in range(0,len(culow_list)):
            dictTickerculow[culow_list[i]] = culow_ticlist[i]
            dictFieldculow[culow_list[i]] = culow_fieldlist[i]
            dictSourceculow[culow_list[i]] = culow_sourcelist[i] 
        dictTickercuopen = {}
        dictFieldcuopen = {}
        dictSourcecuopen = {}
        for i in range(0,len(cuopen_list)):
            dictTickercuopen[cuopen_list[i]] = cuopen_ticlist[i]
            dictFieldcuopen[cuopen_list[i]] = cuopen_fieldlist[i]
            dictSourcecuopen[cuopen_list[i]] = cuopen_sourcelist[i]             
        dictTickercuvol = {}
        dictFieldcuvol = {}
        dictSourcecuvol = {}
        for i in range(0,len(cuvol_list)):
            dictTickercuvol[cuvol_list[i]] = cuvol_ticlist[i]
            dictFieldcuvol[cuvol_list[i]] = cuvol_fieldlist[i]
            dictSourcecuvol[cuvol_list[i]] = cuvol_sourcelist[i]  
        dictTickerauclose = {}
        dictFieldauclose = {}
        dictSourceauclose = {}
        for i in range(0,len(auclose_list)):
            dictTickerauclose[auclose_list[i]] = auclose_ticlist[i]
            dictFieldauclose[auclose_list[i]] = auclose_fieldlist[i]
            dictSourceauclose[auclose_list[i]] = auclose_sourcelist[i] 
        dictTickerauhigh = {}
        dictFieldauhigh = {}
        dictSourceauhigh = {}
        for i in range(0,len(auhigh_list)):
            dictTickerauhigh[auhigh_list[i]] = auhigh_ticlist[i]
            dictFieldauhigh[auhigh_list[i]] = auhigh_fieldlist[i]
            dictSourceauhigh[auhigh_list[i]] = auhigh_sourcelist[i]
        dictTickeraulow = {}
        dictFieldaulow = {}
        dictSourceaulow = {}
        for i in range(0,len(aulow_list)):
            dictTickeraulow[aulow_list[i]] = aulow_ticlist[i]
            dictFieldaulow[aulow_list[i]] = aulow_fieldlist[i]
            dictSourceaulow[aulow_list[i]] = aulow_sourcelist[i] 
        dictTickerauopen = {}
        dictFieldauopen = {}
        dictSourceauopen = {}
        for i in range(0,len(auopen_list)):
            dictTickerauopen[auopen_list[i]] = auopen_ticlist[i]
            dictFieldauopen[auopen_list[i]] = auopen_fieldlist[i]
            dictSourceauopen[auopen_list[i]] = auopen_sourcelist[i]             
        dictTickerauvol = {}
        dictFieldauvol = {}
        dictSourceauvol = {}
        for i in range(0,len(auvol_list)):
            dictTickerauvol[auvol_list[i]] = auvol_ticlist[i]
            dictFieldauvol[auvol_list[i]] = auvol_fieldlist[i]
            dictSourceauvol[auvol_list[i]] = auvol_sourcelist[i]  
        dictTickerfeclose = {}
        dictFieldfeclose = {}
        dictSourcefeclose = {}
        for i in range(0,len(feclose_list)):
            dictTickerfeclose[feclose_list[i]] = feclose_ticlist[i]
            dictFieldfeclose[feclose_list[i]] = feclose_fieldlist[i]
            dictSourcefeclose[feclose_list[i]] = feclose_sourcelist[i] 
        dictTickerfehigh = {}
        dictFieldfehigh = {}
        dictSourcefehigh = {}
        for i in range(0,len(fehigh_list)):
            dictTickerfehigh[fehigh_list[i]] = fehigh_ticlist[i]
            dictFieldfehigh[fehigh_list[i]] = fehigh_fieldlist[i]
            dictSourcefehigh[fehigh_list[i]] = fehigh_sourcelist[i]
        dictTickerfelow = {}
        dictFieldfelow = {}
        dictSourcefelow = {}
        for i in range(0,len(felow_list)):
            dictTickerfelow[felow_list[i]] = felow_ticlist[i]
            dictFieldfelow[felow_list[i]] = felow_fieldlist[i]
            dictSourcefelow[felow_list[i]] = felow_sourcelist[i] 
        dictTickerfeopen = {}
        dictFieldfeopen = {}
        dictSourcefeopen = {}
        for i in range(0,len(feopen_list)):
            dictTickerfeopen[feopen_list[i]] = feopen_ticlist[i]
            dictFieldfeopen[feopen_list[i]] = feopen_fieldlist[i]
            dictSourcefeopen[feopen_list[i]] = feopen_sourcelist[i]             
        dictTickerfevol = {}
        dictFieldfevol = {}
        dictSourcefevol = {}
        for i in range(0,len(fevol_list)):
            dictTickerfevol[fevol_list[i]] = fevol_ticlist[i]
            dictFieldfevol[fevol_list[i]] = fevol_fieldlist[i]
            dictSourcefevol[fevol_list[i]] = fevol_sourcelist[i]  
        dictTickerpbclose = {}
        dictFieldpbclose = {}
        dictSourcepbclose = {}
        for i in range(0,len(pbclose_list)):
            dictTickerpbclose[pbclose_list[i]] = pbclose_ticlist[i]
            dictFieldpbclose[pbclose_list[i]] = pbclose_fieldlist[i]
            dictSourcepbclose[pbclose_list[i]] = pbclose_sourcelist[i] 
        dictTickerpbhigh = {}
        dictFieldpbhigh = {}
        dictSourcepbhigh = {}
        for i in range(0,len(pbhigh_list)):
            dictTickerpbhigh[pbhigh_list[i]] = pbhigh_ticlist[i]
            dictFieldpbhigh[pbhigh_list[i]] = pbhigh_fieldlist[i]
            dictSourcepbhigh[pbhigh_list[i]] = pbhigh_sourcelist[i]
        dictTickerpblow = {}
        dictFieldpblow = {}
        dictSourcepblow = {}
        for i in range(0,len(pblow_list)):
            dictTickerpblow[pblow_list[i]] = pblow_ticlist[i]
            dictFieldpblow[pblow_list[i]] = pblow_fieldlist[i]
            dictSourcepblow[pblow_list[i]] = pblow_sourcelist[i] 
        dictTickerpbopen = {}
        dictFieldpbopen = {}
        dictSourcepbopen = {}
        for i in range(0,len(pbopen_list)):
            dictTickerpbopen[pbopen_list[i]] = pbopen_ticlist[i]
            dictFieldpbopen[pbopen_list[i]] = pbopen_fieldlist[i]
            dictSourcepbopen[pbopen_list[i]] = pbopen_sourcelist[i]             
        dictTickerpbvol = {}
        dictFieldpbvol = {}
        dictSourcepbvol = {}
        for i in range(0,len(pbvol_list)):
            dictTickerpbvol[pbvol_list[i]] = pbvol_ticlist[i]
            dictFieldpbvol[pbvol_list[i]] = pbvol_fieldlist[i]
            dictSourcepbvol[pbvol_list[i]] = pbvol_sourcelist[i]  
        dictTickerniclose = {}
        dictFieldniclose = {}
        dictSourceniclose = {}
        for i in range(0,len(niclose_list)):
            dictTickerniclose[niclose_list[i]] = niclose_ticlist[i]
            dictFieldniclose[niclose_list[i]] = niclose_fieldlist[i]
            dictSourceniclose[niclose_list[i]] = niclose_sourcelist[i] 
        dictTickernihigh = {}
        dictFieldnihigh = {}
        dictSourcenihigh = {}
        for i in range(0,len(nihigh_list)):
            dictTickernihigh[nihigh_list[i]] = nihigh_ticlist[i]
            dictFieldnihigh[nihigh_list[i]] = nihigh_fieldlist[i]
            dictSourcenihigh[nihigh_list[i]] = nihigh_sourcelist[i]
        dictTickernilow = {}
        dictFieldnilow = {}
        dictSourcenilow = {}
        for i in range(0,len(nilow_list)):
            dictTickernilow[nilow_list[i]] = nilow_ticlist[i]
            dictFieldnilow[nilow_list[i]] = nilow_fieldlist[i]
            dictSourcenilow[nilow_list[i]] = nilow_sourcelist[i] 
        dictTickerniopen = {}
        dictFieldniopen = {}
        dictSourceniopen = {}
        for i in range(0,len(niopen_list)):
            dictTickerniopen[niopen_list[i]] = niopen_ticlist[i]
            dictFieldniopen[niopen_list[i]] = niopen_fieldlist[i]
            dictSourceniopen[niopen_list[i]] = niopen_sourcelist[i]             
        dictTickernivol = {}
        dictFieldnivol = {}
        dictSourcenivol = {}
        for i in range(0,len(nivol_list)):
            dictTickernivol[nivol_list[i]] = nivol_ticlist[i]
            dictFieldnivol[nivol_list[i]] = nivol_fieldlist[i]
            dictSourcenivol[nivol_list[i]] = nivol_sourcelist[i]    
        dictTickerpaclose = {}
        dictFieldpaclose = {}
        dictSourcepaclose = {}
        for i in range(0,len(paclose_list)):
            dictTickerpaclose[paclose_list[i]] = paclose_ticlist[i]
            dictFieldpaclose[paclose_list[i]] = paclose_fieldlist[i]
            dictSourcepaclose[paclose_list[i]] = paclose_sourcelist[i] 
        dictTickerpahigh = {}
        dictFieldpahigh = {}
        dictSourcepahigh = {}
        for i in range(0,len(pahigh_list)):
            dictTickerpahigh[pahigh_list[i]] = pahigh_ticlist[i]
            dictFieldpahigh[pahigh_list[i]] = pahigh_fieldlist[i]
            dictSourcepahigh[pahigh_list[i]] = pahigh_sourcelist[i]
        dictTickerpalow = {}
        dictFieldpalow = {}
        dictSourcepalow = {}
        for i in range(0,len(palow_list)):
            dictTickerpalow[palow_list[i]] = palow_ticlist[i]
            dictFieldpalow[palow_list[i]] = palow_fieldlist[i]
            dictSourcepalow[palow_list[i]] = palow_sourcelist[i] 
        dictTickerpaopen = {}
        dictFieldpaopen = {}
        dictSourcepaopen = {}
        for i in range(0,len(paopen_list)):
            dictTickerpaopen[paopen_list[i]] = paopen_ticlist[i]
            dictFieldpaopen[paopen_list[i]] = paopen_fieldlist[i]
            dictSourcepaopen[paopen_list[i]] = paopen_sourcelist[i]             
        dictTickerpavol = {}
        dictFieldpavol = {}
        dictSourcepavol = {}
        for i in range(0,len(pavol_list)):
            dictTickerpavol[pavol_list[i]] = pavol_ticlist[i]
            dictFieldpavol[pavol_list[i]] = pavol_fieldlist[i]
            dictSourcepavol[pavol_list[i]] = pavol_sourcelist[i] 
        dictTickerplclose = {}
        dictFieldplclose = {}
        dictSourceplclose = {}
        for i in range(0,len(plclose_list)):
            dictTickerplclose[plclose_list[i]] = plclose_ticlist[i]
            dictFieldplclose[plclose_list[i]] = plclose_fieldlist[i]
            dictSourceplclose[plclose_list[i]] = plclose_sourcelist[i] 
        dictTickerplhigh = {}
        dictFieldplhigh = {}
        dictSourceplhigh = {}
        for i in range(0,len(plhigh_list)):
            dictTickerplhigh[plhigh_list[i]] = plhigh_ticlist[i]
            dictFieldplhigh[plhigh_list[i]] = plhigh_fieldlist[i]
            dictSourceplhigh[plhigh_list[i]] = plhigh_sourcelist[i]
        dictTickerpllow = {}
        dictFieldpllow = {}
        dictSourcepllow = {}
        for i in range(0,len(pllow_list)):
            dictTickerpllow[pllow_list[i]] = pllow_ticlist[i]
            dictFieldpllow[pllow_list[i]] = pllow_fieldlist[i]
            dictSourcepllow[pllow_list[i]] = pllow_sourcelist[i] 
        dictTickerplopen = {}
        dictFieldplopen = {}
        dictSourceplopen = {}
        for i in range(0,len(plopen_list)):
            dictTickerplopen[plopen_list[i]] = plopen_ticlist[i]
            dictFieldplopen[plopen_list[i]] = plopen_fieldlist[i]
            dictSourceplopen[plopen_list[i]] = plopen_sourcelist[i]             
        dictTickerplvol = {}
        dictFieldplvol = {}
        dictSourceplvol = {}
        for i in range(0,len(plvol_list)):
            dictTickerplvol[plvol_list[i]] = plvol_ticlist[i]
            dictFieldplvol[plvol_list[i]] = plvol_fieldlist[i]
            dictSourceplvol[plvol_list[i]] = plvol_sourcelist[i] 
        dictTickeragclose = {}
        dictFieldagclose = {}
        dictSourceagclose = {}
        for i in range(0,len(agclose_list)):
            dictTickeragclose[agclose_list[i]] = agclose_ticlist[i]
            dictFieldagclose[agclose_list[i]] = agclose_fieldlist[i]
            dictSourceagclose[agclose_list[i]] = agclose_sourcelist[i] 
        dictTickeraghigh = {}
        dictFieldaghigh = {}
        dictSourceaghigh = {}
        for i in range(0,len(aghigh_list)):
            dictTickeraghigh[aghigh_list[i]] = aghigh_ticlist[i]
            dictFieldaghigh[aghigh_list[i]] = aghigh_fieldlist[i]
            dictSourceaghigh[aghigh_list[i]] = aghigh_sourcelist[i]
        dictTickeraglow = {}
        dictFieldaglow = {}
        dictSourceaglow = {}
        for i in range(0,len(aglow_list)):
            dictTickeraglow[aglow_list[i]] = aglow_ticlist[i]
            dictFieldaglow[aglow_list[i]] = aglow_fieldlist[i]
            dictSourceaglow[aglow_list[i]] = aglow_sourcelist[i] 
        dictTickeragopen = {}
        dictFieldagopen = {}
        dictSourceagopen = {}
        for i in range(0,len(agopen_list)):
            dictTickeragopen[agopen_list[i]] = agopen_ticlist[i]
            dictFieldagopen[agopen_list[i]] = agopen_fieldlist[i]
            dictSourceagopen[agopen_list[i]] = agopen_sourcelist[i]             
        dictTickeragvol = {}
        dictFieldagvol = {}
        dictSourceagvol = {}
        for i in range(0,len(agvol_list)):
            dictTickeragvol[agvol_list[i]] = agvol_ticlist[i]
            dictFieldagvol[agvol_list[i]] = agvol_fieldlist[i]
            dictSourceagvol[agvol_list[i]] = agvol_sourcelist[i]
        dictTickerstclose = {}
        dictFieldstclose = {}
        dictSourcestclose = {}
        for i in range(0,len(stclose_list)):
            dictTickerstclose[stclose_list[i]] = stclose_ticlist[i]
            dictFieldstclose[stclose_list[i]] = stclose_fieldlist[i]
            dictSourcestclose[stclose_list[i]] = stclose_sourcelist[i] 
        dictTickersthigh = {}
        dictFieldsthigh = {}
        dictSourcesthigh = {}
        for i in range(0,len(sthigh_list)):
            dictTickersthigh[sthigh_list[i]] = sthigh_ticlist[i]
            dictFieldsthigh[sthigh_list[i]] = sthigh_fieldlist[i]
            dictSourcesthigh[sthigh_list[i]] = sthigh_sourcelist[i]
        dictTickerstlow = {}
        dictFieldstlow = {}
        dictSourcestlow = {}
        for i in range(0,len(stlow_list)):
            dictTickerstlow[stlow_list[i]] = stlow_ticlist[i]
            dictFieldstlow[stlow_list[i]] = stlow_fieldlist[i]
            dictSourcestlow[stlow_list[i]] = stlow_sourcelist[i] 
        dictTickerstopen = {}
        dictFieldstopen = {}
        dictSourcestopen = {}
        for i in range(0,len(stopen_list)):
            dictTickerstopen[stopen_list[i]] = stopen_ticlist[i]
            dictFieldstopen[stopen_list[i]] = stopen_fieldlist[i]
            dictSourcestopen[stopen_list[i]] = stopen_sourcelist[i]             
        dictTickerstvol = {}
        dictFieldstvol = {}
        dictSourcestvol = {}
        for i in range(0,len(stvol_list)):
            dictTickerstvol[stvol_list[i]] = stvol_ticlist[i]
            dictFieldstvol[stvol_list[i]] = stvol_fieldlist[i]
            dictSourcestvol[stvol_list[i]] = stvol_sourcelist[i] 
        dictTickertnclose = {}
        dictFieldtnclose = {}
        dictSourcetnclose = {}
        for i in range(0,len(tnclose_list)):
            dictTickertnclose[tnclose_list[i]] = tnclose_ticlist[i]
            dictFieldtnclose[tnclose_list[i]] = tnclose_fieldlist[i]
            dictSourcetnclose[tnclose_list[i]] = tnclose_sourcelist[i] 
        dictTickertnhigh = {}
        dictFieldtnhigh = {}
        dictSourcetnhigh = {}
        for i in range(0,len(tnhigh_list)):
            dictTickertnhigh[tnhigh_list[i]] = tnhigh_ticlist[i]
            dictFieldtnhigh[tnhigh_list[i]] = tnhigh_fieldlist[i]
            dictSourcetnhigh[tnhigh_list[i]] = tnhigh_sourcelist[i]
        dictTickertnlow = {}
        dictFieldtnlow = {}
        dictSourcetnlow = {}
        for i in range(0,len(tnlow_list)):
            dictTickertnlow[tnlow_list[i]] = tnlow_ticlist[i]
            dictFieldtnlow[tnlow_list[i]] = tnlow_fieldlist[i]
            dictSourcetnlow[tnlow_list[i]] = tnlow_sourcelist[i] 
        dictTickertnopen = {}
        dictFieldtnopen = {}
        dictSourcetnopen = {}
        for i in range(0,len(tnopen_list)):
            dictTickertnopen[tnopen_list[i]] = tnopen_ticlist[i]
            dictFieldtnopen[tnopen_list[i]] = tnopen_fieldlist[i]
            dictSourcetnopen[tnopen_list[i]] = tnopen_sourcelist[i]             
        dictTickertnvol = {}
        dictFieldtnvol = {}
        dictSourcetnvol = {}
        for i in range(0,len(tnvol_list)):
            dictTickertnvol[tnvol_list[i]] = tnvol_ticlist[i]
            dictFieldtnvol[tnvol_list[i]] = tnvol_fieldlist[i]
            dictSourcetnvol[tnvol_list[i]] = tnvol_sourcelist[i] 
        dictTickerurclose = {}
        dictFieldurclose = {}
        dictSourceurclose = {}
        for i in range(0,len(urclose_list)):
            dictTickerurclose[urclose_list[i]] = urclose_ticlist[i]
            dictFieldurclose[urclose_list[i]] = urclose_fieldlist[i]
            dictSourceurclose[urclose_list[i]] = urclose_sourcelist[i] 
        dictTickerurhigh = {}
        dictFieldurhigh = {}
        dictSourceurhigh = {}
        for i in range(0,len(urhigh_list)):
            dictTickerurhigh[urhigh_list[i]] = urhigh_ticlist[i]
            dictFieldurhigh[urhigh_list[i]] = urhigh_fieldlist[i]
            dictSourceurhigh[urhigh_list[i]] = urhigh_sourcelist[i]
        dictTickerurlow = {}
        dictFieldurlow = {}
        dictSourceurlow = {}
        for i in range(0,len(urlow_list)):
            dictTickerurlow[urlow_list[i]] = urlow_ticlist[i]
            dictFieldurlow[urlow_list[i]] = urlow_fieldlist[i]
            dictSourceurlow[urlow_list[i]] = urlow_sourcelist[i] 
        dictTickeruropen = {}
        dictFielduropen = {}
        dictSourceuropen = {}
        for i in range(0,len(uropen_list)):
            dictTickeruropen[uropen_list[i]] = uropen_ticlist[i]
            dictFielduropen[uropen_list[i]] = uropen_fieldlist[i]
            dictSourceuropen[uropen_list[i]] = uropen_sourcelist[i]             
        dictTickerurvol = {}
        dictFieldurvol = {}
        dictSourceurvol = {}
        for i in range(0,len(urvol_list)):
            dictTickerurvol[urvol_list[i]] = urvol_ticlist[i]
            dictFieldurvol[urvol_list[i]] = urvol_fieldlist[i]
            dictSourceurvol[urvol_list[i]] = urvol_sourcelist[i] 
        dictTickerznclose = {}
        dictFieldznclose = {}
        dictSourceznclose = {}
        for i in range(0,len(znclose_list)):
            dictTickerznclose[znclose_list[i]] = znclose_ticlist[i]
            dictFieldznclose[znclose_list[i]] = znclose_fieldlist[i]
            dictSourceznclose[znclose_list[i]] = znclose_sourcelist[i] 
        dictTickerznhigh = {}
        dictFieldznhigh = {}
        dictSourceznhigh = {}
        for i in range(0,len(znhigh_list)):
            dictTickerznhigh[znhigh_list[i]] = znhigh_ticlist[i]
            dictFieldznhigh[znhigh_list[i]] = znhigh_fieldlist[i]
            dictSourceznhigh[znhigh_list[i]] = znhigh_sourcelist[i]
        dictTickerznlow = {}
        dictFieldznlow = {}
        dictSourceznlow = {}
        for i in range(0,len(znlow_list)):
            dictTickerznlow[znlow_list[i]] = znlow_ticlist[i]
            dictFieldznlow[znlow_list[i]] = znlow_fieldlist[i]
            dictSourceznlow[znlow_list[i]] = znlow_sourcelist[i] 
        dictTickerznopen = {}
        dictFieldznopen = {}
        dictSourceznopen = {}
        for i in range(0,len(znopen_list)):
            dictTickerznopen[znopen_list[i]] = znopen_ticlist[i]
            dictFieldznopen[znopen_list[i]] = znopen_fieldlist[i]
            dictSourceznopen[znopen_list[i]] = znopen_sourcelist[i]             
        dictTickerznvol = {}
        dictFieldznvol = {}
        dictSourceznvol = {}
        for i in range(0,len(znvol_list)):
            dictTickerznvol[znvol_list[i]] = znvol_ticlist[i]
            dictFieldznvol[znvol_list[i]] = znvol_fieldlist[i]
            dictSourceznvol[znvol_list[i]] = znvol_sourcelist[i] 
        dictTickercornclose = {}
        dictFieldcornclose = {}
        dictSourcecornclose = {}
        for i in range(0,len(cornclose_list)):
            dictTickercornclose[cornclose_list[i]] = cornclose_ticlist[i]
            dictFieldcornclose[cornclose_list[i]] = cornclose_fieldlist[i]
            dictSourcecornclose[cornclose_list[i]] = cornclose_sourcelist[i] 
        dictTickercornhigh = {}
        dictFieldcornhigh = {}
        dictSourcecornhigh = {}
        for i in range(0,len(cornhigh_list)):
            dictTickercornhigh[cornhigh_list[i]] = cornhigh_ticlist[i]
            dictFieldcornhigh[cornhigh_list[i]] = cornhigh_fieldlist[i]
            dictSourcecornhigh[cornhigh_list[i]] = cornhigh_sourcelist[i]
        dictTickercornlow = {}
        dictFieldcornlow = {}
        dictSourcecornlow = {}
        for i in range(0,len(cornlow_list)):
            dictTickercornlow[cornlow_list[i]] = cornlow_ticlist[i]
            dictFieldcornlow[cornlow_list[i]] = cornlow_fieldlist[i]
            dictSourcecornlow[cornlow_list[i]] = cornlow_sourcelist[i] 
        dictTickercornopen = {}
        dictFieldcornopen = {}
        dictSourcecornopen = {}
        for i in range(0,len(cornopen_list)):
            dictTickercornopen[cornopen_list[i]] = cornopen_ticlist[i]
            dictFieldcornopen[cornopen_list[i]] = cornopen_fieldlist[i]
            dictSourcecornopen[cornopen_list[i]] = cornopen_sourcelist[i]             
        dictTickercornvol = {}
        dictFieldcornvol = {}
        dictSourcecornvol = {}
        for i in range(0,len(cornvol_list)):
            dictTickercornvol[cornvol_list[i]] = cornvol_ticlist[i]
            dictFieldcornvol[cornvol_list[i]] = cornvol_fieldlist[i]
            dictSourcecornvol[cornvol_list[i]] = cornvol_sourcelist[i]
        dictTickerwheatclose = {}
        dictFieldwheatclose = {}
        dictSourcewheatclose = {}
        for i in range(0,len(wheatclose_list)):
            dictTickerwheatclose[wheatclose_list[i]] = wheatclose_ticlist[i]
            dictFieldwheatclose[wheatclose_list[i]] = wheatclose_fieldlist[i]
            dictSourcewheatclose[wheatclose_list[i]] = wheatclose_sourcelist[i] 
        dictTickerwheathigh = {}
        dictFieldwheathigh = {}
        dictSourcewheathigh = {}
        for i in range(0,len(wheathigh_list)):
            dictTickerwheathigh[wheathigh_list[i]] = wheathigh_ticlist[i]
            dictFieldwheathigh[wheathigh_list[i]] = wheathigh_fieldlist[i]
            dictSourcewheathigh[wheathigh_list[i]] = wheathigh_sourcelist[i]
        dictTickerwheatlow = {}
        dictFieldwheatlow = {}
        dictSourcewheatlow = {}
        for i in range(0,len(wheatlow_list)):
            dictTickerwheatlow[wheatlow_list[i]] = wheatlow_ticlist[i]
            dictFieldwheatlow[wheatlow_list[i]] = wheatlow_fieldlist[i]
            dictSourcewheatlow[wheatlow_list[i]] = wheatlow_sourcelist[i] 
        dictTickerwheatopen = {}
        dictFieldwheatopen = {}
        dictSourcewheatopen = {}
        for i in range(0,len(wheatopen_list)):
            dictTickerwheatopen[wheatopen_list[i]] = wheatopen_ticlist[i]
            dictFieldwheatopen[wheatopen_list[i]] = wheatopen_fieldlist[i]
            dictSourcewheatopen[wheatopen_list[i]] = wheatopen_sourcelist[i]             
        dictTickerwheatvol = {}
        dictFieldwheatvol = {}
        dictSourcewheatvol = {}
        for i in range(0,len(wheatvol_list)):
            dictTickerwheatvol[wheatvol_list[i]] = wheatvol_ticlist[i]
            dictFieldwheatvol[wheatvol_list[i]] = wheatvol_fieldlist[i]
            dictSourcewheatvol[wheatvol_list[i]] = wheatvol_sourcelist[i]   
        dictTickersoyclose = {}
        dictFieldsoyclose = {}
        dictSourcesoyclose = {}
        for i in range(0,len(soyclose_list)):
            dictTickersoyclose[soyclose_list[i]] = soyclose_ticlist[i]
            dictFieldsoyclose[soyclose_list[i]] = soyclose_fieldlist[i]
            dictSourcesoyclose[soyclose_list[i]] = soyclose_sourcelist[i] 
        dictTickersoyhigh = {}
        dictFieldsoyhigh = {}
        dictSourcesoyhigh = {}
        for i in range(0,len(soyhigh_list)):
            dictTickersoyhigh[soyhigh_list[i]] = soyhigh_ticlist[i]
            dictFieldsoyhigh[soyhigh_list[i]] = soyhigh_fieldlist[i]
            dictSourcesoyhigh[soyhigh_list[i]] = soyhigh_sourcelist[i]
        dictTickersoylow = {}
        dictFieldsoylow = {}
        dictSourcesoylow = {}
        for i in range(0,len(soylow_list)):
            dictTickersoylow[soylow_list[i]] = soylow_ticlist[i]
            dictFieldsoylow[soylow_list[i]] = soylow_fieldlist[i]
            dictSourcesoylow[soylow_list[i]] = soylow_sourcelist[i] 
        dictTickersoyopen = {}
        dictFieldsoyopen = {}
        dictSourcesoyopen = {}
        for i in range(0,len(soyopen_list)):
            dictTickersoyopen[soyopen_list[i]] = soyopen_ticlist[i]
            dictFieldsoyopen[soyopen_list[i]] = soyopen_fieldlist[i]
            dictSourcesoyopen[soyopen_list[i]] = soyopen_sourcelist[i]             
        dictTickersoyvol = {}
        dictFieldsoyvol = {}
        dictSourcesoyvol = {}
        for i in range(0,len(soyvol_list)):
            dictTickersoyvol[soyvol_list[i]] = soyvol_ticlist[i]
            dictFieldsoyvol[soyvol_list[i]] = soyvol_fieldlist[i]
            dictSourcesoyvol[soyvol_list[i]] = soyvol_sourcelist[i]   
        dictTickersoclose = {}
        dictFieldsoclose = {}
        dictSourcesoclose = {}
        for i in range(0,len(soclose_list)):
            dictTickersoclose[soclose_list[i]] = soclose_ticlist[i]
            dictFieldsoclose[soclose_list[i]] = soclose_fieldlist[i]
            dictSourcesoclose[soclose_list[i]] = soclose_sourcelist[i] 
        dictTickersohigh = {}
        dictFieldsohigh = {}
        dictSourcesohigh = {}
        for i in range(0,len(sohigh_list)):
            dictTickersohigh[sohigh_list[i]] = sohigh_ticlist[i]
            dictFieldsohigh[sohigh_list[i]] = sohigh_fieldlist[i]
            dictSourcesohigh[sohigh_list[i]] = sohigh_sourcelist[i]
        dictTickersolow = {}
        dictFieldsolow = {}
        dictSourcesolow = {}
        for i in range(0,len(solow_list)):
            dictTickersolow[solow_list[i]] = solow_ticlist[i]
            dictFieldsolow[solow_list[i]] = solow_fieldlist[i]
            dictSourcesolow[solow_list[i]] = solow_sourcelist[i] 
        dictTickersoopen = {}
        dictFieldsoopen = {}
        dictSourcesoopen = {}
        for i in range(0,len(soopen_list)):
            dictTickersoopen[soopen_list[i]] = soopen_ticlist[i]
            dictFieldsoopen[soopen_list[i]] = soopen_fieldlist[i]
            dictSourcesoopen[soopen_list[i]] = soopen_sourcelist[i]             
        dictTickersovol = {}
        dictFieldsovol = {}
        dictSourcesovol = {}
        for i in range(0,len(sovol_list)):
            dictTickersovol[sovol_list[i]] = sovol_ticlist[i]
            dictFieldsovol[sovol_list[i]] = sovol_fieldlist[i]
            dictSourcesovol[sovol_list[i]] = sovol_sourcelist[i] 
        dictTickercotclose = {}
        dictFieldcotclose = {}
        dictSourcecotclose = {}
        for i in range(0,len(cotclose_list)):
            dictTickercotclose[cotclose_list[i]] = cotclose_ticlist[i]
            dictFieldcotclose[cotclose_list[i]] = cotclose_fieldlist[i]
            dictSourcecotclose[cotclose_list[i]] = cotclose_sourcelist[i] 
        dictTickercothigh = {}
        dictFieldcothigh = {}
        dictSourcecothigh = {}
        for i in range(0,len(cothigh_list)):
            dictTickercothigh[cothigh_list[i]] = cothigh_ticlist[i]
            dictFieldcothigh[cothigh_list[i]] = cothigh_fieldlist[i]
            dictSourcecothigh[cothigh_list[i]] = cothigh_sourcelist[i]
        dictTickercotlow = {}
        dictFieldcotlow = {}
        dictSourcecotlow = {}
        for i in range(0,len(cotlow_list)):
            dictTickercotlow[cotlow_list[i]] = cotlow_ticlist[i]
            dictFieldcotlow[cotlow_list[i]] = cotlow_fieldlist[i]
            dictSourcecotlow[cotlow_list[i]] = cotlow_sourcelist[i] 
        dictTickercotopen = {}
        dictFieldcotopen = {}
        dictSourcecotopen = {}
        for i in range(0,len(cotopen_list)):
            dictTickercotopen[cotopen_list[i]] = cotopen_ticlist[i]
            dictFieldcotopen[cotopen_list[i]] = cotopen_fieldlist[i]
            dictSourcecotopen[cotopen_list[i]] = cotopen_sourcelist[i]             
        dictTickercotvol = {}
        dictFieldcotvol = {}
        dictSourcecotvol = {}
        for i in range(0,len(cotvol_list)):
            dictTickercotvol[cotvol_list[i]] = cotvol_ticlist[i]
            dictFieldcotvol[cotvol_list[i]] = cotvol_fieldlist[i]
            dictSourcecotvol[cotvol_list[i]] = cotvol_sourcelist[i]
        dictTickersbclose = {}
        dictFieldsbclose = {}
        dictSourcesbclose = {}
        for i in range(0,len(sbclose_list)):
            dictTickersbclose[sbclose_list[i]] = sbclose_ticlist[i]
            dictFieldsbclose[sbclose_list[i]] = sbclose_fieldlist[i]
            dictSourcesbclose[sbclose_list[i]] = sbclose_sourcelist[i] 
        dictTickersbhigh = {}
        dictFieldsbhigh = {}
        dictSourcesbhigh = {}
        for i in range(0,len(sbhigh_list)):
            dictTickersbhigh[sbhigh_list[i]] = sbhigh_ticlist[i]
            dictFieldsbhigh[sbhigh_list[i]] = sbhigh_fieldlist[i]
            dictSourcesbhigh[sbhigh_list[i]] = sbhigh_sourcelist[i]
        dictTickersblow = {}
        dictFieldsblow = {}
        dictSourcesblow = {}
        for i in range(0,len(sblow_list)):
            dictTickersblow[sblow_list[i]] = sblow_ticlist[i]
            dictFieldsblow[sblow_list[i]] = sblow_fieldlist[i]
            dictSourcesblow[sblow_list[i]] = sblow_sourcelist[i] 
        dictTickersbopen = {}
        dictFieldsbopen = {}
        dictSourcesbopen = {}
        for i in range(0,len(sbopen_list)):
            dictTickersbopen[sbopen_list[i]] = sbopen_ticlist[i]
            dictFieldsbopen[sbopen_list[i]] = sbopen_fieldlist[i]
            dictSourcesbopen[sbopen_list[i]] = sbopen_sourcelist[i]             
        dictTickersbvol = {}
        dictFieldsbvol = {}
        dictSourcesbvol = {}
        for i in range(0,len(sbvol_list)):
            dictTickersbvol[sbvol_list[i]] = sbvol_ticlist[i]
            dictFieldsbvol[sbvol_list[i]] = sbvol_fieldlist[i]
            dictSourcesbvol[sbvol_list[i]] = sbvol_sourcelist[i] 
        dictTickersincurrency = {}
        dictFieldsincurrency = {}
        dictSourcesincurrency = {}
        for i in range(0,len(sincurrency_list)):
            dictTickersincurrency[sincurrency_list[i]] = sincurrency_ticlist[i]
            dictFieldsincurrency[sincurrency_list[i]] = sincurrency_fieldlist[i]
            dictSourcesincurrency[sincurrency_list[i]] = sincurrency_sourcelist[i]     
        dictTickercrosscurrency = {}
        dictFieldcrosscurrency = {}
        dictSourcecrosscurrency = {}
        for i in range(0,len(crosscurrency_list)):
            dictTickercrosscurrency[crosscurrency_list[i]] = crosscurrency_ticlist[i]
            dictFieldcrosscurrency[crosscurrency_list[i]] = crosscurrency_fieldlist[i]
            dictSourcecrosscurrency[crosscurrency_list[i]] = crosscurrency_sourcelist[i]
        dictTickerequity = {}
        dictFieldequity = {}
        dictSourceequity = {}
        for i in range(0,len(equity_list)):
            dictTickerequity[equity_list[i]] = equity_ticlist[i]
            dictFieldequity[equity_list[i]] = equity_fieldlist[i]
            dictSourceequity[equity_list[i]] = equity_sourcelist[i]  
        dictTickersent = {}
        dictFieldsent = {}
        dictSourcesent = {}
        for i in range(0,len(sent_list)):
            dictTickersent[sent_list[i]] = sent_ticlist[i]
            dictFieldsent[sent_list[i]] = sent_fieldlist[i]
            dictSourcesent[sent_list[i]] = sent_sourcelist[i]   
        dictTickerimammtot = {}
        dictFieldimammtot = {}
        dictSourceimammtot = {}
        for i in range(0,len(imammtot_list)):
            dictTickerimammtot[imammtot_list[i]] = imammtot_ticlist[i]
            dictFieldimammtot[imammtot_list[i]] = imammtot_fieldlist[i]
            dictSourceimammtot[imammtot_list[i]] = imammtot_sourcelist[i]  
        dictTickerimamman = {}
        dictFieldimamman = {}
        dictSourceimamman = {}
        for i in range(0,len(imamman_list)):
            dictTickerimamman[imamman_list[i]] = imamman_ticlist[i]
            dictFieldimamman[imamman_list[i]] = imamman_fieldlist[i]
            dictSourceimamman[imamman_list[i]] = imamman_sourcelist[i] 
        dictTickerimammnittot = {}
        dictFieldimammnittot = {}
        dictSourceimammnittot = {}
        for i in range(0,len(imammnittot_list)):
            dictTickerimammnittot[imammnittot_list[i]] = imammnittot_ticlist[i]
            dictFieldimammnittot[imammnittot_list[i]] = imammnittot_fieldlist[i]
            dictSourceimammnittot[imammnittot_list[i]] = imammnittot_sourcelist[i]       
        dictTickerimammnitaq = {}
        dictFieldimammnitaq = {}
        dictSourceimammnitaq = {}
        for i in range(0,len(imammnitaq_list)):
            dictTickerimammnitaq[imammnitaq_list[i]] = imammnitaq_ticlist[i]
            dictFieldimammnitaq[imammnitaq_list[i]] = imammnitaq_fieldlist[i]
            dictSourceimammnitaq[imammnitaq_list[i]] = imammnitaq_sourcelist[i]     
        dictTickerimammsu = {}
        dictFieldimammsu = {}
        dictSourceimammsu = {}
        for i in range(0,len(imammsu_list)):
            dictTickerimammsu[imammsu_list[i]] = imammsu_ticlist[i]
            dictFieldimammsu[imammsu_list[i]] = imammsu_fieldlist[i]
            dictSourceimammsu[imammsu_list[i]] = imammsu_sourcelist[i]   
        dictTickerimdap = {}
        dictFieldimdap = {}
        dictSourceimdap = {}
        for i in range(0,len(imdap_list)):
            dictTickerimdap[imdap_list[i]] = imdap_ticlist[i]
            dictFieldimdap[imdap_list[i]] = imdap_fieldlist[i]
            dictSourceimdap[imdap_list[i]] = imdap_sourcelist[i]     
        dictTickerimint = {}
        dictFieldimint = {}
        dictSourceimint = {}
        for i in range(0,len(imint_list)):
            dictTickerimint[imint_list[i]] = imint_ticlist[i]
            dictFieldimint[imint_list[i]] = imint_fieldlist[i]
            dictSourceimint[imint_list[i]] = imint_sourcelist[i] 
        dictTickerimmaptot = {}
        dictFieldimmaptot = {}
        dictSourceimmaptot = {}
        for i in range(0,len(immaptot_list)):
            dictTickerimmaptot[immaptot_list[i]] = immaptot_ticlist[i]
            dictFieldimmaptot[immaptot_list[i]] = immaptot_fieldlist[i]
            dictSourceimmaptot[immaptot_list[i]] = immaptot_sourcelist[i] 
        dictTickerimmapmix = {}
        dictFieldimmapmix = {}
        dictSourceimmapmix = {}
        for i in range(0,len(immapmix_list)):
            dictTickerimmapmix[immapmix_list[i]] = immapmix_ticlist[i]
            dictFieldimmapmix[immapmix_list[i]] = immapmix_fieldlist[i]
            dictSourceimmapmix[immapmix_list[i]] = immapmix_sourcelist[i]  
        dictTickerimphosac = {}
        dictFieldimphosac = {}
        dictSourceimphosac = {}
        for i in range(0,len(imphosac_list)):
            dictTickerimphosac[imphosac_list[i]] = imphosac_ticlist[i]
            dictFieldimphosac[imphosac_list[i]] = imphosac_fieldlist[i]
            dictSourceimphosac[imphosac_list[i]] = imphosac_sourcelist[i] 
        dictTickerimpot = {}
        dictFieldimpot = {}
        dictSourceimpot = {}
        for i in range(0,len(impot_list)):
            dictTickerimpot[impot_list[i]] = impot_ticlist[i]
            dictFieldimpot[impot_list[i]] = impot_fieldlist[i]
            dictSourceimpot[impot_list[i]] = impot_sourcelist[i]   
        dictTickerimtsptot = {}
        dictFieldimtsptot = {}
        dictSourceimtsptot = {}
        for i in range(0,len(imtsptot_list)):
            dictTickerimtsptot[imtsptot_list[i]] = imtsptot_ticlist[i]
            dictFieldimtsptot[imtsptot_list[i]] = imtsptot_fieldlist[i]
            dictSourceimtsptot[imtsptot_list[i]] = imtsptot_sourcelist[i]   
        dictTickerimtspless = {}
        dictFieldimtspless = {}
        dictSourceimtspless = {}
        for i in range(0,len(imtspless_list)):
            dictTickerimtspless[imtspless_list[i]] = imtspless_ticlist[i]
            dictFieldimtspless[imtspless_list[i]] = imtspless_fieldlist[i]
            dictSourceimtspless[imtspless_list[i]] = imtspless_sourcelist[i]
        dictTickerimtspgreat = {}
        dictFieldimtspgreat = {}
        dictSourceimtspgreat = {}
        for i in range(0,len(imtspgreat_list)):
            dictTickerimtspgreat[imtspgreat_list[i]] = imtspgreat_ticlist[i]
            dictFieldimtspgreat[imtspgreat_list[i]] = imtspgreat_fieldlist[i]
            dictSourceimtspgreat[imtspgreat_list[i]] = imtspgreat_sourcelist[i]  
        dictTickerimuantot = {}
        dictFieldimuantot = {}
        dictSourceimuantot = {}
        for i in range(0,len(imuantot_list)):
            dictTickerimuantot[imuantot_list[i]] = imuantot_ticlist[i]
            dictFieldimuantot[imuantot_list[i]] = imuantot_fieldlist[i]
            dictSourceimuantot[imuantot_list[i]] = imuantot_sourcelist[i]   
        dictTickerimuanmix = {}
        dictFieldimuanmix = {}
        dictSourceimuanmix = {}
        for i in range(0,len(imuanmix_list)):
            dictTickerimuanmix[imuanmix_list[i]] = imuanmix_ticlist[i]
            dictFieldimuanmix[imuanmix_list[i]] = imuanmix_fieldlist[i]
            dictSourceimuanmix[imuanmix_list[i]] = imuanmix_sourcelist[i]  
        dictTickerimureatot = {}
        dictFieldimureatot = {}
        dictSourceimureatot = {}
        for i in range(0,len(imureatot_list)):
            dictTickerimureatot[imureatot_list[i]] = imureatot_ticlist[i]
            dictFieldimureatot[imureatot_list[i]] = imureatot_fieldlist[i]
            dictSourceimureatot[imureatot_list[i]] = imureatot_sourcelist[i]     
        dictTickerimureadef = {}
        dictFieldimureadef = {}
        dictSourceimureadef = {}
        for i in range(0,len(imureadef_list)):
            dictTickerimureadef[imureadef_list[i]] = imureadef_ticlist[i]
            dictFieldimureadef[imureadef_list[i]] = imureadef_fieldlist[i]
            dictSourceimureadef[imureadef_list[i]] = imureadef_sourcelist[i]   
        dictTickerimureanesoi = {}
        dictFieldimureanesoi = {}
        dictSourceimureanesoi = {}
        for i in range(0,len(imureanesoi_list)):
            dictTickerimureanesoi[imureanesoi_list[i]] = imureanesoi_ticlist[i]
            dictFieldimureanesoi[imureanesoi_list[i]] = imureanesoi_fieldlist[i]
            dictSourceimureanesoi[imureanesoi_list[i]] = imureanesoi_sourcelist[i]   
        dictTickerimureasolid = {}
        dictFieldimureasolid = {}
        dictSourceimureasolid = {}
        for i in range(0,len(imureasolid_list)):
            dictTickerimureasolid[imureasolid_list[i]] = imureasolid_ticlist[i]
            dictFieldimureasolid[imureasolid_list[i]] = imureasolid_fieldlist[i]
            dictSourceimureasolid[imureasolid_list[i]] = imureasolid_sourcelist[i]  
        dictTickerimureaaq = {}
        dictFieldimureaaq = {}
        dictSourceimureaaq = {}
        for i in range(0,len(imureaaq_list)):
            dictTickerimureaaq[imureaaq_list[i]] = imureaaq_ticlist[i]
            dictFieldimureaaq[imureaaq_list[i]] = imureaaq_fieldlist[i]
            dictSourceimureaaq[imureaaq_list[i]] = imureaaq_sourcelist[i]  
        dictTickerexammtot = {}
        dictFieldexammtot = {}
        dictSourceexammtot = {}
        for i in range(0,len(exammtot_list)):
            dictTickerexammtot[exammtot_list[i]] = exammtot_ticlist[i]
            dictFieldexammtot[exammtot_list[i]] = exammtot_fieldlist[i]
            dictSourceexammtot[exammtot_list[i]] = exammtot_sourcelist[i] 
        dictTickerexamman = {}
        dictFieldexamman = {}
        dictSourceexamman = {}
        for i in range(0,len(examman_list)):
            dictTickerexamman[examman_list[i]] = examman_ticlist[i]
            dictFieldexamman[examman_list[i]] = examman_fieldlist[i]
            dictSourceexamman[examman_list[i]] = examman_sourcelist[i] 
        dictTickerexammnittot = {}
        dictFieldexammnittot = {}
        dictSourceexammnittot = {}
        for i in range(0,len(exammnittot_list)):
            dictTickerexammnittot[exammnittot_list[i]] = exammnittot_ticlist[i]
            dictFieldexammnittot[exammnittot_list[i]] = exammnittot_fieldlist[i]
            dictSourceexammnittot[exammnittot_list[i]] = exammnittot_sourcelist[i]  
        dictTickerexammnitaq = {}
        dictFieldexammnitaq = {}
        dictSourceexammnitaq = {}
        for i in range(0,len(exammnitaq_list)):
            dictTickerexammnitaq[exammnitaq_list[i]] = exammnitaq_ticlist[i]
            dictFieldexammnitaq[exammnitaq_list[i]] = exammnitaq_fieldlist[i]
            dictSourceexammnitaq[exammnitaq_list[i]] = exammnitaq_sourcelist[i]
        dictTickerexammsu = {}
        dictFieldexammsu = {}
        dictSourceexammsu = {}
        for i in range(0,len(exammsu_list)):
            dictTickerexammsu[exammsu_list[i]] = exammsu_ticlist[i]
            dictFieldexammsu[exammsu_list[i]] = exammsu_fieldlist[i]
            dictSourceexammsu[exammsu_list[i]] = exammsu_sourcelist[i]    
        dictTickerexdap = {}
        dictFieldexdap = {}
        dictSourceexdap = {}
        for i in range(0,len(exdap_list)):
            dictTickerexdap[exdap_list[i]] = exdap_ticlist[i]
            dictFieldexdap[exdap_list[i]] = exdap_fieldlist[i]
            dictSourceexdap[exdap_list[i]] = exdap_sourcelist[i]   
        dictTickerexnpk = {}
        dictFieldexnpk = {}
        dictSourceexnpk = {}
        for i in range(0,len(exnpk_list)):
            dictTickerexnpk[exnpk_list[i]] = exnpk_ticlist[i]
            dictFieldexnpk[exnpk_list[i]] = exnpk_fieldlist[i]
            dictSourceexnpk[exnpk_list[i]] = exnpk_sourcelist[i]  
        dictTickerexmaptot = {}
        dictFieldexmaptot = {}
        dictSourceexmaptot = {}
        for i in range(0,len(exmaptot_list)):
            dictTickerexmaptot[exmaptot_list[i]] = exmaptot_ticlist[i]
            dictFieldexmaptot[exmaptot_list[i]] = exmaptot_fieldlist[i]
            dictSourceexmaptot[exmaptot_list[i]] = exmaptot_sourcelist[i]  
        dictTickerexmapmix = {}
        dictFieldexmapmix = {}
        dictSourceexmapmix = {}
        for i in range(0,len(exmapmix_list)):
            dictTickerexmapmix[exmapmix_list[i]] = exmapmix_ticlist[i]
            dictFieldexmapmix[exmapmix_list[i]] = exmapmix_fieldlist[i]
            dictSourceexmapmix[exmapmix_list[i]] = exmapmix_sourcelist[i]    
        dictTickerexphosac = {}
        dictFieldexphosac = {}
        dictSourceexphosac = {}
        for i in range(0,len(exphosac_list)):
            dictTickerexphosac[exphosac_list[i]] = exphosac_ticlist[i]
            dictFieldexphosac[exphosac_list[i]] = exphosac_fieldlist[i]
            dictSourceexphosac[exphosac_list[i]] = exphosac_sourcelist[i]  
        dictTickerexpot = {}
        dictFieldexpot = {}
        dictSourceexpot = {}
        for i in range(0,len(expot_list)):
            dictTickerexpot[expot_list[i]] = expot_ticlist[i]
            dictFieldexpot[expot_list[i]] = expot_fieldlist[i]
            dictSourceexpot[expot_list[i]] = expot_sourcelist[i]      
        dictTickerextsptot = {}
        dictFieldextsptot = {}
        dictSourceextsptot = {}
        for i in range(0,len(extsptot_list)):
            dictTickerextsptot[extsptot_list[i]] = extsptot_ticlist[i]
            dictFieldextsptot[extsptot_list[i]] = extsptot_fieldlist[i]
            dictSourceextsptot[extsptot_list[i]] = extsptot_sourcelist[i]   
        dictTickerextspless = {}
        dictFieldextspless = {}
        dictSourceextspless = {}
        for i in range(0,len(extspless_list)):
            dictTickerextspless[extspless_list[i]] = extspless_ticlist[i]
            dictFieldextspless[extspless_list[i]] = extspless_fieldlist[i]
            dictSourceextspless[extspless_list[i]] = extspless_sourcelist[i]  
        dictTickerextspgreat = {}
        dictFieldextspgreat = {}
        dictSourceextspgreat = {}
        for i in range(0,len(extspgreat_list)):
            dictTickerextspgreat[extspgreat_list[i]] = extspgreat_ticlist[i]
            dictFieldextspgreat[extspgreat_list[i]] = extspgreat_fieldlist[i]
            dictSourceextspgreat[extspgreat_list[i]] = extspgreat_sourcelist[i]  
        dictTickerexuantot = {}
        dictFieldexuantot = {}
        dictSourceexuantot = {}
        for i in range(0,len(exuantot_list)):
            dictTickerexuantot[exuantot_list[i]] = exuantot_ticlist[i]
            dictFieldexuantot[exuantot_list[i]] = exuantot_fieldlist[i]
            dictSourceexuantot[exuantot_list[i]] = exuantot_sourcelist[i]   
        dictTickerexuanmix = {}
        dictFieldexuanmix = {}
        dictSourceexuanmix = {}
        for i in range(0,len(exuanmix_list)):
            dictTickerexuanmix[exuanmix_list[i]] = exuanmix_ticlist[i]
            dictFieldexuanmix[exuanmix_list[i]] = exuanmix_fieldlist[i]
            dictSourceexuanmix[exuanmix_list[i]] = exuanmix_sourcelist[i]   
        dictTickerexureatot = {}
        dictFieldexureatot = {}
        dictSourceexureatot = {}
        for i in range(0,len(exureatot_list)):
            dictTickerexureatot[exureatot_list[i]] = exureatot_ticlist[i]
            dictFieldexureatot[exureatot_list[i]] = exureatot_fieldlist[i]
            dictSourceexureatot[exureatot_list[i]] = exureatot_sourcelist[i] 
        dictTickerexureaaq = {}
        dictFieldexureaaq = {}
        dictSourceexureaaq = {}
        for i in range(0,len(exureaaq_list)):
            dictTickerexureaaq[exureaaq_list[i]] = exureaaq_ticlist[i]
            dictFieldexureaaq[exureaaq_list[i]] = exureaaq_fieldlist[i]
            dictSourceexureaaq[exureaaq_list[i]] = exureaaq_sourcelist[i]  
        dictTickersdamm = {}
        dictFieldsdamm = {}
        dictSourcesdamm = {}
        for i in range(0,len(sdamm_list)):
            dictTickersdamm[sdamm_list[i]] = sdamm_ticlist[i]
            dictFieldsdamm[sdamm_list[i]] = sdamm_fieldlist[i]
            dictSourcesdamm[sdamm_list[i]] = sdamm_sourcelist[i]     
        dictTickersddapmapus = {}
        dictFieldsddapmapus = {}
        dictSourcesddapmapus = {}
        for i in range(0,len(sddapmapus_list)):
            dictTickersddapmapus[sddapmapus_list[i]] = sddapmapus_ticlist[i]
            dictFieldsddapmapus[sddapmapus_list[i]] = sddapmapus_fieldlist[i]
            dictSourcesddapmapus[sddapmapus_list[i]] = sddapmapus_sourcelist[i] 
        dictTickersddapmapall = {}
        dictFieldsddapmapall = {}
        dictSourcesddapmapall = {}
        for i in range(0,len(sddapmapall_list)):
            dictTickersddapmapall[sddapmapall_list[i]] = sddapmapall_ticlist[i]
            dictFieldsddapmapall[sddapmapall_list[i]] = sddapmapall_fieldlist[i]
            dictSourcesddapmapall[sddapmapall_list[i]] = sddapmapall_sourcelist[i]    
        dictTickersdpotus = {}
        dictFieldsdpotus = {}
        dictSourcesdpotus = {}
        for i in range(0,len(sdpotus_list)):
            dictTickersdpotus[sdpotus_list[i]] = sdpotus_ticlist[i]
            dictFieldsdpotus[sdpotus_list[i]] = sdpotus_fieldlist[i]
            dictSourcesdpotus[sdpotus_list[i]] = sdpotus_sourcelist[i] 
        dictTickersdpotall = {}
        dictFieldsdpotall = {}
        dictSourcesdpotall = {}
        for i in range(0,len(sdpotall_list)):
            dictTickersdpotall[sdpotall_list[i]] = sdpotall_ticlist[i]
            dictFieldsdpotall[sdpotall_list[i]] = sdpotall_fieldlist[i]
            dictSourcesdpotall[sdpotall_list[i]] = sdpotall_sourcelist[i]      
        dictTickersduan = {}
        dictFieldsduan = {}
        dictSourcesduan = {}
        for i in range(0,len(sduan_list)):
            dictTickersduan[sduan_list[i]] = sduan_ticlist[i]
            dictFieldsduan[sduan_list[i]] = sduan_fieldlist[i]
            dictSourcesduan[sduan_list[i]] = sduan_sourcelist[i]
        dictTickersdureaus = {}
        dictFieldsdureaus = {}
        dictSourcesdureaus = {}
        for i in range(0,len(sdureaus_list)):
            dictTickersdureaus[sdureaus_list[i]] = sdureaus_ticlist[i]
            dictFieldsdureaus[sdureaus_list[i]] = sdureaus_fieldlist[i]
            dictSourcesdureaus[sdureaus_list[i]] = sdureaus_sourcelist[i] 
        dictTickersdureaall = {}
        dictFieldsdureaall = {}
        dictSourcesdureaall = {}
        for i in range(0,len(sdureaall_list)):
            dictTickersdureaall[sdureaall_list[i]] = sdureaall_ticlist[i]
            dictFieldsdureaall[sdureaall_list[i]] = sdureaall_fieldlist[i]
            dictSourcesdureaall[sdureaall_list[i]] = sdureaall_sourcelist[i]    
        dictTickerdapbid = {}
        dictFielddapbid = {}
        dictSourcedapbid = {}
        for i in range(0,len(dapbid_list)):
            dictTickerdapbid[dapbid_list[i]] = dapbid_ticlist[i]
            dictFielddapbid[dapbid_list[i]] = dapbid_fieldlist[i]
            dictSourcedapbid[dapbid_list[i]] = dapbid_sourcelist[i]   
        dictTickerdapoffer = {}
        dictFielddapoffer = {}
        dictSourcedapoffer = {}
        for i in range(0,len(dapoffer_list)):
            dictTickerdapoffer[dapoffer_list[i]] = dapoffer_ticlist[i]
            dictFielddapoffer[dapoffer_list[i]] = dapoffer_fieldlist[i]
            dictSourcedapoffer[dapoffer_list[i]] = dapoffer_sourcelist[i]
        dictTickerdapmid = {}
        dictFielddapmid = {}
        dictSourcedapmid = {}
        for i in range(0,len(dapmid_list)):
            dictTickerdapmid[dapmid_list[i]] = dapmid_ticlist[i]
            dictFielddapmid[dapmid_list[i]] = dapmid_fieldlist[i]
            dictSourcedapmid[dapmid_list[i]] = dapmid_sourcelist[i]  
        dictTickermopbid = {}
        dictFieldmopbid = {}
        dictSourcemopbid = {}
        for i in range(0,len(mopbid_list)):
            dictTickermopbid[mopbid_list[i]] = mopbid_ticlist[i]
            dictFieldmopbid[mopbid_list[i]] = mopbid_fieldlist[i]
            dictSourcemopbid[mopbid_list[i]] = mopbid_sourcelist[i]   
        dictTickermopoffer = {}
        dictFieldmopoffer = {}
        dictSourcemopoffer = {}
        for i in range(0,len(mopoffer_list)):
            dictTickermopoffer[mopoffer_list[i]] = mopoffer_ticlist[i]
            dictFieldmopoffer[mopoffer_list[i]] = mopoffer_fieldlist[i]
            dictSourcemopoffer[mopoffer_list[i]] = mopoffer_sourcelist[i]
        dictTickermopmid = {}
        dictFieldmopmid = {}
        dictSourcemopmid = {}
        for i in range(0,len(mopmid_list)):
            dictTickermopmid[mopmid_list[i]] = mopmid_ticlist[i]
            dictFieldmopmid[mopmid_list[i]] = mopmid_fieldlist[i]
            dictSourcemopmid[mopmid_list[i]] = mopmid_sourcelist[i]   
        dictTickerphorockbid = {}
        dictFieldphorockbid = {}
        dictSourcephorockbid = {}
        for i in range(0,len(phorockbid_list)):
            dictTickerphorockbid[phorockbid_list[i]] = phorockbid_ticlist[i]
            dictFieldphorockbid[phorockbid_list[i]] = phorockbid_fieldlist[i]
            dictSourcephorockbid[phorockbid_list[i]] = phorockbid_sourcelist[i]   
        dictTickerphorockoffer = {}
        dictFieldphorockoffer = {}
        dictSourcephorockoffer = {}
        for i in range(0,len(phorockoffer_list)):
            dictTickerphorockoffer[phorockoffer_list[i]] = phorockoffer_ticlist[i]
            dictFieldphorockoffer[phorockoffer_list[i]] = phorockoffer_fieldlist[i]
            dictSourcephorockoffer[phorockoffer_list[i]] = phorockoffer_sourcelist[i]
        dictTickerphorockmid = {}
        dictFieldphorockmid = {}
        dictSourcephorockmid = {}
        for i in range(0,len(phorockmid_list)):
            dictTickerphorockmid[phorockmid_list[i]] = phorockmid_ticlist[i]
            dictFieldphorockmid[phorockmid_list[i]] = phorockmid_fieldlist[i]
            dictSourcephorockmid[phorockmid_list[i]] = phorockmid_sourcelist[i]   
        dictTickersulfurbid = {}
        dictFieldsulfurbid = {}
        dictSourcesulfurbid = {}
        for i in range(0,len(sulfurbid_list)):
            dictTickersulfurbid[sulfurbid_list[i]] = sulfurbid_ticlist[i]
            dictFieldsulfurbid[sulfurbid_list[i]] = sulfurbid_fieldlist[i]
            dictSourcesulfurbid[sulfurbid_list[i]] = sulfurbid_sourcelist[i]   
        dictTickersulfuroffer = {}
        dictFieldsulfuroffer = {}
        dictSourcesulfuroffer = {}
        for i in range(0,len(sulfuroffer_list)):
            dictTickersulfuroffer[sulfuroffer_list[i]] = sulfuroffer_ticlist[i]
            dictFieldsulfuroffer[sulfuroffer_list[i]] = sulfuroffer_fieldlist[i]
            dictSourcesulfuroffer[sulfuroffer_list[i]] = sulfuroffer_sourcelist[i]
        dictTickersulfurmid = {}
        dictFieldsulfurmid = {}
        dictSourcesulfurmid = {}
        for i in range(0,len(sulfurmid_list)):
            dictTickersulfurmid[sulfurmid_list[i]] = sulfurmid_ticlist[i]
            dictFieldsulfurmid[sulfurmid_list[i]] = sulfurmid_fieldlist[i]
            dictSourcesulfurmid[sulfurmid_list[i]] = sulfurmid_sourcelist[i] 
        dictTickerureabid = {}
        dictFieldureabid = {}
        dictSourceureabid = {}
        for i in range(0,len(ureabid_list)):
            dictTickerureabid[ureabid_list[i]] = ureabid_ticlist[i]
            dictFieldureabid[ureabid_list[i]] = ureabid_fieldlist[i]
            dictSourceureabid[ureabid_list[i]] = ureabid_sourcelist[i]   
        dictTickerureaoffer = {}
        dictFieldureaoffer = {}
        dictSourceureaoffer = {}
        for i in range(0,len(ureaoffer_list)):
            dictTickerureaoffer[ureaoffer_list[i]] = ureaoffer_ticlist[i]
            dictFieldureaoffer[ureaoffer_list[i]] = ureaoffer_fieldlist[i]
            dictSourceureaoffer[ureaoffer_list[i]] = ureaoffer_sourcelist[i]
        dictTickerureamid = {}
        dictFieldureamid = {}
        dictSourceureamid = {}
        for i in range(0,len(ureamid_list)):
            dictTickerureamid[ureamid_list[i]] = ureamid_ticlist[i]
            dictFieldureamid[ureamid_list[i]] = ureamid_fieldlist[i]
            dictSourceureamid[ureamid_list[i]] = ureamid_sourcelist[i]  
        dictTickerammbid = {}
        dictFieldammbid = {}
        dictSourceammbid = {}
        for i in range(0,len(ammbid_list)):
            dictTickerammbid[ammbid_list[i]] = ammbid_ticlist[i]
            dictFieldammbid[ammbid_list[i]] = ammbid_fieldlist[i]
            dictSourceammbid[ammbid_list[i]] = ammbid_sourcelist[i]   
        dictTickerammoffer = {}
        dictFieldammoffer = {}
        dictSourceammoffer = {}
        for i in range(0,len(ammoffer_list)):
            dictTickerammoffer[ammoffer_list[i]] = ammoffer_ticlist[i]
            dictFieldammoffer[ammoffer_list[i]] = ammoffer_fieldlist[i]
            dictSourceammoffer[ammoffer_list[i]] = ammoffer_sourcelist[i]
        dictTickerammmid = {}
        dictFieldammmid = {}
        dictSourceammmid = {}
        for i in range(0,len(ammmid_list)):
            dictTickerammmid[ammmid_list[i]] = ammmid_ticlist[i]
            dictFieldammmid[ammmid_list[i]] = ammmid_fieldlist[i]
            dictSourceammmid[ammmid_list[i]] = ammmid_sourcelist[i]   
        dictTickerphoacbid = {}
        dictFieldphoacbid = {}
        dictSourcephoacbid = {}
        for i in range(0,len(phoacbid_list)):
            dictTickerphoacbid[phoacbid_list[i]] = phoacbid_ticlist[i]
            dictFieldphoacbid[phoacbid_list[i]] = phoacbid_fieldlist[i]
            dictSourcephoacbid[phoacbid_list[i]] = phoacbid_sourcelist[i]   
        dictTickerphoacoffer = {}
        dictFieldphoacoffer = {}
        dictSourcephoacoffer = {}
        for i in range(0,len(phoacoffer_list)):
            dictTickerphoacoffer[phoacoffer_list[i]] = phoacoffer_ticlist[i]
            dictFieldphoacoffer[phoacoffer_list[i]] = phoacoffer_fieldlist[i]
            dictSourcephoacoffer[phoacoffer_list[i]] = phoacoffer_sourcelist[i]
        dictTickerphoacmid = {}
        dictFieldphoacmid = {}
        dictSourcephoacmid = {}
        for i in range(0,len(phoacmid_list)):
            dictTickerphoacmid[phoacmid_list[i]] = phoacmid_ticlist[i]
            dictFieldphoacmid[phoacmid_list[i]] = phoacmid_fieldlist[i]
            dictSourcephoacmid[phoacmid_list[i]] = phoacmid_sourcelist[i] 
        dictTickersulacbid = {}
        dictFieldsulacbid = {}
        dictSourcesulacbid = {}
        for i in range(0,len(sulacbid_list)):
            dictTickersulacbid[sulacbid_list[i]] = sulacbid_ticlist[i]
            dictFieldsulacbid[sulacbid_list[i]] = sulacbid_fieldlist[i]
            dictSourcesulacbid[sulacbid_list[i]] = sulacbid_sourcelist[i]   
        dictTickersulacoffer = {}
        dictFieldsulacoffer = {}
        dictSourcesulacoffer = {}
        for i in range(0,len(sulacoffer_list)):
            dictTickersulacoffer[sulacoffer_list[i]] = sulacoffer_ticlist[i]
            dictFieldsulacoffer[sulacoffer_list[i]] = sulacoffer_fieldlist[i]
            dictSourcesulacoffer[sulacoffer_list[i]] = sulacoffer_sourcelist[i]
        dictTickersulacmid = {}
        dictFieldsulacmid = {}
        dictSourcesulacmid = {}
        for i in range(0,len(sulacmid_list)):
            dictTickersulacmid[sulacmid_list[i]] = sulacmid_ticlist[i]
            dictFieldsulacmid[sulacmid_list[i]] = sulacmid_fieldlist[i]
            dictSourcesulacmid[sulacmid_list[i]] = sulacmid_sourcelist[i]  
        dictTickeruanbid = {}
        dictFielduanbid = {}
        dictSourceuanbid = {}
        for i in range(0,len(uanbid_list)):
            dictTickeruanbid[uanbid_list[i]] = uanbid_ticlist[i]
            dictFielduanbid[uanbid_list[i]] = uanbid_fieldlist[i]
            dictSourceuanbid[uanbid_list[i]] = uanbid_sourcelist[i]   
        dictTickeruanoffer = {}
        dictFielduanoffer = {}
        dictSourceuanoffer = {}
        for i in range(0,len(uanoffer_list)):
            dictTickeruanoffer[uanoffer_list[i]] = uanoffer_ticlist[i]
            dictFielduanoffer[uanoffer_list[i]] = uanoffer_fieldlist[i]
            dictSourceuanoffer[uanoffer_list[i]] = uanoffer_sourcelist[i]
        dictTickeruanmid = {}
        dictFielduanmid = {}
        dictSourceuanmid = {}
        for i in range(0,len(uanmid_list)):
            dictTickeruanmid[uanmid_list[i]] = uanmid_ticlist[i]
            dictFielduanmid[uanmid_list[i]] = uanmid_fieldlist[i]
            dictSourceuanmid[uanmid_list[i]] = uanmid_sourcelist[i]  
        dictTickerchsdap = {}
        dictFieldchsdap = {}
        dictSourcechsdap = {}
        for i in range(0,len(chsdap_list)):
            dictTickerchsdap[chsdap_list[i]] = chsdap_ticlist[i]
            dictFieldchsdap[chsdap_list[i]] = chsdap_fieldlist[i]
            dictSourcechsdap[chsdap_list[i]] = chsdap_sourcelist[i]    
        dictTickerchspot = {}
        dictFieldchspot = {}
        dictSourcechspot = {}
        for i in range(0,len(chspot_list)):
            dictTickerchspot[chspot_list[i]] = chspot_ticlist[i]
            dictFieldchspot[chspot_list[i]] = chspot_fieldlist[i]
            dictSourcechspot[chspot_list[i]] = chspot_sourcelist[i] 
        dictTickerchsuan = {}
        dictFieldchsuan = {}
        dictSourcechsuan = {}
        for i in range(0,len(chsuan_list)):
            dictTickerchsuan[chsuan_list[i]] = chsuan_ticlist[i]
            dictFieldchsuan[chsuan_list[i]] = chsuan_fieldlist[i]
            dictSourcechsuan[chsuan_list[i]] = chsuan_sourcelist[i] 
        dictTickerchsurea = {}
        dictFieldchsurea = {}
        dictSourcechsurea = {}
        for i in range(0,len(chsurea_list)):
            dictTickerchsurea[chsurea_list[i]] = chsurea_ticlist[i]
            dictFieldchsurea[chsurea_list[i]] = chsurea_fieldlist[i]
            dictSourcechsurea[chsurea_list[i]] = chsurea_sourcelist[i]           
        dictTickerbuckdap = {}
        dictFieldbuckdap = {}
        dictSourcebuckdap = {}
        for i in range(0,len(buckdap_list)):
            dictTickerbuckdap[buckdap_list[i]] = buckdap_ticlist[i]
            dictFieldbuckdap[buckdap_list[i]] = buckdap_fieldlist[i]
            dictSourcebuckdap[buckdap_list[i]] = buckdap_sourcelist[i]    
        dictTickerbuckpot = {}
        dictFieldbuckpot = {}
        dictSourcebuckpot = {}
        for i in range(0,len(buckpot_list)):
            dictTickerbuckpot[buckpot_list[i]] = buckpot_ticlist[i]
            dictFieldbuckpot[buckpot_list[i]] = buckpot_fieldlist[i]
            dictSourcebuckpot[buckpot_list[i]] = buckpot_sourcelist[i] 
        dictTickerbuckuan = {}
        dictFieldbuckuan = {}
        dictSourcebuckuan = {}
        for i in range(0,len(buckuan_list)):
            dictTickerbuckuan[buckuan_list[i]] = buckuan_ticlist[i]
            dictFieldbuckuan[buckuan_list[i]] = buckuan_fieldlist[i]
            dictSourcebuckuan[buckuan_list[i]] = buckuan_sourcelist[i] 
        dictTickerbuckurea = {}
        dictFieldbuckurea = {}
        dictSourcebuckurea = {}
        for i in range(0,len(buckurea_list)):
            dictTickerbuckurea[buckurea_list[i]] = buckurea_ticlist[i]
            dictFieldbuckurea[buckurea_list[i]] = buckurea_fieldlist[i]
            dictSourcebuckurea[buckurea_list[i]] = buckurea_sourcelist[i]  
        dictTickercru = {}
        dictFieldcru = {}
        dictSourcecru = {}
        for i in range(0,len(cru_list)):
            dictTickercru[cru_list[i]] = cru_ticlist[i]
            dictFieldcru[cru_list[i]] = cru_fieldlist[i]
            dictSourcecru[cru_list[i]] = cru_sourcelist[i]                    
##############################################################################################################################################################################
        #selected items from lists x variables
        ureagrancfr = (self.ureagrancfr_listWidget.selectedItems()) #selected items
        list_ureagrancfr = [] #put in format that is useful for each chosen thing
        for i in list(ureagrancfr):
            list_ureagrancfr.append(str(i.text()))
        ureagrandel = (self.ureagrandel_listWidget.selectedItems()) #selected items
        list_ureagrandel = [] #put in format that is useful for each chosen thing
        for i in list(ureagrandel):
            list_ureagrandel.append(str(i.text()))
        ureagranfca = (self.ureagranfca_listWidget.selectedItems())
        list_ureagranfca = [] #put in format that is useful for each chosen thing
        for i in list(ureagranfca):
            list_ureagranfca.append(str(i.text()))            
        ureagranfob = (self.ureagranfob_listWidget.selectedItems()) #selected items
        list_ureagranfob = [] #put in format that is useful for each chosen thing
        for i in list(ureagranfob):
            list_ureagranfob.append(str(i.text()))
        ureagranfobfis = (self.ureagranfobfis_listWidget.selectedItems()) #selected items
        list_ureagranfobfis = [] #put in format that is useful for each chosen thing
        for i in list(ureagranfobfis):
            list_ureagranfobfis.append(str(i.text()))
        ureaprillcfr = (self.ureaprillcfr_listWidget.selectedItems()) #selected items
        list_ureaprillcfr = [] #put in format that is useful for each chosen thing
        for i in list(ureaprillcfr):
            list_ureaprillcfr.append(str(i.text()))
        ureaprillcpt = (self.ureaprillcpt_listWidget.selectedItems()) #selected items
        list_ureaprillcpt = [] #put in format that is useful for each chosen thing
        for i in list(ureaprillcpt):
            list_ureaprillcpt.append(str(i.text()))
        ureaprillfob = (self.ureaprillfob_listWidget.selectedItems()) #selected items
        list_ureaprillfob = [] #put in format that is useful for each chosen thing
        for i in list(ureaprillfob):
            list_ureaprillfob.append(str(i.text()))
        ureaprillfobfis = (self.ureaprillfobfis_listWidget.selectedItems()) #selected items
        list_ureaprillfobfis = [] #put in format that is useful for each chosen thing
        for i in list(ureaprillfobfis):
            list_ureaprillfobfis.append(str(i.text()))            
        ureaother = (self.ureaother_listWidget.selectedItems()) 
        list_ureaother = [] 
        for i in list(ureaother):
            list_ureaother.append(str(i.text())) 
        uan2830 = (self.uan2830_listWidget.selectedItems()) 
        list_uan2830 = [] 
        for i in list(uan2830):
            list_uan2830.append(str(i.text()))   
        uan32 = (self.uan32_listWidget.selectedItems()) 
        list_uan32 = [] 
        for i in list(uan32):
            list_uan32.append(str(i.text()))              
        uanother = (self.uanother_listWidget.selectedItems()) 
        list_uanother = [] 
        for i in list(uanother):
            list_uanother.append(str(i.text()))
        potgran = (self.potgran_listWidget.selectedItems()) 
        list_potgran = [] 
        for i in list(potgran):
            list_potgran.append(str(i.text()))
        potstan = (self.potstan_listWidget.selectedItems()) 
        list_potstan = [] 
        for i in list(potstan):
            list_potstan.append(str(i.text()))            
        ammspot = (self.ammspot_listWidget.selectedItems()) 
        list_ammspot = [] 
        for i in list(ammspot):
            list_ammspot.append(str(i.text()))  
        ammtotcfr = (self.ammtotcfr_listWidget.selectedItems()) 
        list_ammtotcfr = [] 
        for i in list(ammtotcfr):
            list_ammtotcfr.append(str(i.text()))    
        ammtotdel = (self.ammtotdel_listWidget.selectedItems()) 
        list_ammtotdel = [] 
        for i in list(ammtotdel):
            list_ammtotdel.append(str(i.text()))    
        ammtotfob = (self.ammtotfob_listWidget.selectedItems()) 
        list_ammtotfob = [] 
        for i in list(ammtotfob):
            list_ammtotfob.append(str(i.text())) 
        ammcontract = (self.ammcontract_listWidget.selectedItems()) 
        list_ammcontract = [] 
        for i in list(ammcontract):
            list_ammcontract.append(str(i.text()))             
        anbag = (self.anbag_listWidget.selectedItems()) 
        list_anbag = [] 
        for i in list(anbag):
            list_anbag.append(str(i.text())) 
        anbulk = (self.anbulk_listWidget.selectedItems()) 
        list_anbulk = [] 
        for i in list(anbulk):
            list_anbulk.append(str(i.text()))    
        antotcfr = (self.antotcfr_listWidget.selectedItems()) 
        list_antotcfr = [] 
        for i in list(antotcfr):
            list_antotcfr.append(str(i.text()))    
        antotfob = (self.antotfob_listWidget.selectedItems()) 
        list_antotfob = [] 
        for i in list(antotfob):
            list_antotfob.append(str(i.text()))   
        asother = (self.asother_listWidget.selectedItems()) 
        list_asother = [] 
        for i in list(asother):
            list_asother.append(str(i.text()))     
        asstan = (self.asstan_listWidget.selectedItems()) 
        list_asstan = [] 
        for i in list(asstan):
            list_asstan.append(str(i.text()))    
        aswcfr = (self.aswcfr_listWidget.selectedItems()) 
        list_aswcfr = [] 
        for i in list(aswcfr):
            list_aswcfr.append(str(i.text()))     
        aswfob = (self.aswfob_listWidget.selectedItems()) 
        list_aswfob = [] 
        for i in list(aswfob):
            list_aswfob.append(str(i.text()))  
        can = (self.can_listWidget.selectedItems()) 
        list_can = [] 
        for i in list(can):
            list_can.append(str(i.text()))      
        dapfob = (self.dapfob_listWidget.selectedItems()) 
        list_dapfob = [] 
        for i in list(dapfob):
            list_dapfob.append(str(i.text()))     
        dapother = (self.dapother_listWidget.selectedItems()) 
        list_dapother = [] 
        for i in list(dapother):
            list_dapother.append(str(i.text())) 
        map10 = (self.map10_listWidget.selectedItems()) 
        list_map10 = [] 
        for i in list(map10):
            list_map10.append(str(i.text()))            
        mapother = (self.mapother_listWidget.selectedItems()) 
        list_mapother = [] 
        for i in list(mapother):
            list_mapother.append(str(i.text())) 
        npk10 = (self.npk10_listWidget.selectedItems()) 
        list_npk10 = [] 
        for i in list(npk10):
            list_npk10.append(str(i.text()))             
        npk15 = (self.npk15_listWidget.selectedItems()) 
        list_npk15 = [] 
        for i in list(npk15):
            list_npk15.append(str(i.text()))    
        npk16 = (self.npk16_listWidget.selectedItems()) 
        list_npk16 = [] 
        for i in list(npk16):
            list_npk16.append(str(i.text())) 
        npk17 = (self.npk17_listWidget.selectedItems()) 
        list_npk17 = [] 
        for i in list(npk17):
            list_npk17.append(str(i.text())) 
        npk20 = (self.npk20_listWidget.selectedItems()) 
        list_npk20 = [] 
        for i in list(npk20):
            list_npk20.append(str(i.text()))     
        phosrock = (self.phosrock_listWidget.selectedItems()) 
        list_phosrock = [] 
        for i in list(phosrock):
            list_phosrock.append(str(i.text()))  
        phosacid = (self.phosacid_listWidget.selectedItems()) 
        list_phosacid = [] 
        for i in list(phosacid):
            list_phosacid.append(str(i.text())) 
        sopssp = (self.sopssp_listWidget.selectedItems()) 
        list_sopssp = [] 
        for i in list(sopssp):
            list_sopssp.append(str(i.text()))   
        sspot = (self.sspot_listWidget.selectedItems()) 
        list_sspot = [] 
        for i in list(sspot):
            list_sspot.append(str(i.text()))
        stot = (self.stot_listWidget.selectedItems()) 
        list_stot = [] 
        for i in list(stot):
            list_stot.append(str(i.text())) 
        s6m = (self.s6m_listWidget.selectedItems()) 
        list_s6m = [] 
        for i in list(s6m):
            list_s6m.append(str(i.text())) 
        sgreat = (self.sgreat_listWidget.selectedItems()) 
        list_sgreat = [] 
        for i in list(sgreat):
            list_sgreat.append(str(i.text()))  
        sliq = (self.sliq_listWidget.selectedItems()) 
        list_sliq = [] 
        for i in list(sliq):
            list_sliq.append(str(i.text())) 
        smonth = (self.smonth_listWidget.selectedItems()) 
        list_smonth = [] 
        for i in list(smonth):
            list_smonth.append(str(i.text()))  
        sq = (self.sq_listWidget.selectedItems()) 
        list_sq = [] 
        for i in list(sq):
            list_sq.append(str(i.text()))  
        saspot = (self.saspot_listWidget.selectedItems()) 
        list_saspot = [] 
        for i in list(saspot):
            list_saspot.append(str(i.text()))  
        satot = (self.satot_listWidget.selectedItems()) 
        list_satot = [] 
        for i in list(satot):
            list_satot.append(str(i.text()))  
        sacon = (self.sacon_listWidget.selectedItems()) 
        list_sacon = [] 
        for i in list(sacon):
            list_sacon.append(str(i.text())) 
        tsp = (self.tsp_listWidget.selectedItems()) 
        list_tsp = [] 
        for i in list(tsp):
            list_tsp.append(str(i.text()))    
        coale = (self.coale_listWidget.selectedItems()) 
        list_coale = [] 
        for i in list(coale):
            list_coale.append(str(i.text()))  
        coalara = (self.coalara_listWidget.selectedItems()) 
        list_coalara = [] 
        for i in list(coalara):
            list_coalara.append(str(i.text())) 
        coalr = (self.coalr_listWidget.selectedItems()) 
        list_coalr = [] 
        for i in list(coalr):
            list_coalr.append(str(i.text()))   
        petrolinv = (self.petrolinv_listWidget.selectedItems()) 
        list_petrolinv = [] 
        for i in list(petrolinv):
            list_petrolinv.append(str(i.text()))      
        ngnclose = (self.ngnclose_listWidget.selectedItems()) 
        list_ngnclose = [] 
        for i in list(ngnclose):
            list_ngnclose.append(str(i.text()))     
        ngnhigh = (self.ngnhigh_listWidget.selectedItems()) 
        list_ngnhigh = [] 
        for i in list(ngnhigh):
            list_ngnhigh.append(str(i.text()))  
        ngnlow = (self.ngnlow_listWidget.selectedItems()) 
        list_ngnlow = [] 
        for i in list(ngnlow):
            list_ngnlow.append(str(i.text()))  
        ngnopen = (self.ngnopen_listWidget.selectedItems()) 
        list_ngnopen = [] 
        for i in list(ngnopen):
            list_ngnopen.append(str(i.text())) 
        ngnvol = (self.ngnvol_listWidget.selectedItems()) 
        list_ngnvol = [] 
        for i in list(ngnvol):
            list_ngnvol.append(str(i.text()))  
        ngnbp = (self.ngnbp_listWidget.selectedItems()) 
        list_ngnbp = [] 
        for i in list(ngnbp):
            list_ngnbp.append(str(i.text()))  
        wticlose = (self.wticlose_listWidget.selectedItems()) 
        list_wticlose = [] 
        for i in list(wticlose):
            list_wticlose.append(str(i.text()))     
        wtihigh = (self.wtihigh_listWidget.selectedItems()) 
        list_wtihigh = [] 
        for i in list(wtihigh):
            list_wtihigh.append(str(i.text()))  
        wtilow = (self.wtilow_listWidget.selectedItems()) 
        list_wtilow = [] 
        for i in list(wtilow):
            list_wtilow.append(str(i.text()))  
        wtiopen = (self.wtiopen_listWidget.selectedItems()) 
        list_wtiopen = [] 
        for i in list(wtiopen):
            list_wtiopen.append(str(i.text())) 
        wtivol = (self.wtivol_listWidget.selectedItems()) 
        list_wtivol = [] 
        for i in list(wtivol):
            list_wtivol.append(str(i.text()))    
        brentclose = (self.brentclose_listWidget.selectedItems()) 
        list_brentclose = [] 
        for i in list(brentclose):
            list_brentclose.append(str(i.text()))     
        brenthigh = (self.brenthigh_listWidget.selectedItems()) 
        list_brenthigh = [] 
        for i in list(brenthigh):
            list_brenthigh.append(str(i.text()))  
        brentlow = (self.brentlow_listWidget.selectedItems()) 
        list_brentlow = [] 
        for i in list(brentlow):
            list_brentlow.append(str(i.text()))  
        brentopen = (self.brentopen_listWidget.selectedItems()) 
        list_brentopen = [] 
        for i in list(brentopen):
            list_brentopen.append(str(i.text())) 
        brentvol = (self.brentvol_listWidget.selectedItems()) 
        list_brentvol = [] 
        for i in list(brentvol):
            list_brentvol.append(str(i.text()))   
        hoclose = (self.hoclose_listWidget.selectedItems()) 
        list_hoclose = [] 
        for i in list(hoclose):
            list_hoclose.append(str(i.text()))     
        hohigh = (self.hohigh_listWidget.selectedItems()) 
        list_hohigh = [] 
        for i in list(hohigh):
            list_hohigh.append(str(i.text()))  
        holow = (self.holow_listWidget.selectedItems()) 
        list_holow = [] 
        for i in list(holow):
            list_holow.append(str(i.text()))  
        hoopen = (self.hoopen_listWidget.selectedItems()) 
        list_hoopen = [] 
        for i in list(hoopen):
            list_hoopen.append(str(i.text())) 
        hovol = (self.hovol_listWidget.selectedItems()) 
        list_hovol = [] 
        for i in list(hovol):
            list_hovol.append(str(i.text()))  
        rbobclose = (self.rbobclose_listWidget.selectedItems()) 
        list_rbobclose = [] 
        for i in list(rbobclose):
            list_rbobclose.append(str(i.text()))     
        rbobhigh = (self.rbobhigh_listWidget.selectedItems()) 
        list_rbobhigh = [] 
        for i in list(rbobhigh):
            list_rbobhigh.append(str(i.text()))  
        rboblow = (self.rboblow_listWidget.selectedItems()) 
        list_rboblow = [] 
        for i in list(rboblow):
            list_rboblow.append(str(i.text()))  
        rbobopen = (self.rbobopen_listWidget.selectedItems()) 
        list_rbobopen = [] 
        for i in list(rbobopen):
            list_rbobopen.append(str(i.text())) 
        rbobvol = (self.rbobvol_listWidget.selectedItems()) 
        list_rbobvol = [] 
        for i in list(rbobvol):
            list_rbobvol.append(str(i.text()))          
        alclose = (self.alclose_listWidget.selectedItems()) 
        list_alclose = [] 
        for i in list(alclose):
            list_alclose.append(str(i.text()))     
        alhigh = (self.alhigh_listWidget.selectedItems()) 
        list_alhigh = [] 
        for i in list(alhigh):
            list_alhigh.append(str(i.text()))  
        allow = (self.allow_listWidget.selectedItems()) 
        list_allow = [] 
        for i in list(allow):
            list_allow.append(str(i.text()))  
        alopen = (self.alopen_listWidget.selectedItems()) 
        list_alopen = [] 
        for i in list(alopen):
            list_alopen.append(str(i.text())) 
        alvol = (self.alvol_listWidget.selectedItems()) 
        list_alvol = [] 
        for i in list(alvol):
            list_alvol.append(str(i.text()))  
        cuclose = (self.cuclose_listWidget.selectedItems()) 
        list_cuclose = [] 
        for i in list(cuclose):
            list_cuclose.append(str(i.text()))     
        cuhigh = (self.cuhigh_listWidget.selectedItems()) 
        list_cuhigh = [] 
        for i in list(cuhigh):
            list_cuhigh.append(str(i.text()))  
        culow = (self.culow_listWidget.selectedItems()) 
        list_culow = [] 
        for i in list(culow):
            list_culow.append(str(i.text()))  
        cuopen = (self.cuopen_listWidget.selectedItems()) 
        list_cuopen = [] 
        for i in list(cuopen):
            list_cuopen.append(str(i.text())) 
        cuvol = (self.cuvol_listWidget.selectedItems()) 
        list_cuvol = [] 
        for i in list(cuvol):
            list_cuvol.append(str(i.text()))   
        auclose = (self.auclose_listWidget.selectedItems()) 
        list_auclose = [] 
        for i in list(auclose):
            list_auclose.append(str(i.text()))     
        auhigh = (self.auhigh_listWidget.selectedItems()) 
        list_auhigh = [] 
        for i in list(auhigh):
            list_auhigh.append(str(i.text()))  
        aulow = (self.aulow_listWidget.selectedItems()) 
        list_aulow = [] 
        for i in list(aulow):
            list_aulow.append(str(i.text()))  
        auopen = (self.auopen_listWidget.selectedItems()) 
        list_auopen = [] 
        for i in list(auopen):
            list_auopen.append(str(i.text())) 
        auvol = (self.auvol_listWidget.selectedItems()) 
        list_auvol = [] 
        for i in list(auvol):
            list_auvol.append(str(i.text()))    
        feclose = (self.feclose_listWidget.selectedItems()) 
        list_feclose = [] 
        for i in list(feclose):
            list_feclose.append(str(i.text()))     
        fehigh = (self.fehigh_listWidget.selectedItems()) 
        list_fehigh = [] 
        for i in list(fehigh):
            list_fehigh.append(str(i.text()))  
        felow = (self.felow_listWidget.selectedItems()) 
        list_felow = [] 
        for i in list(felow):
            list_felow.append(str(i.text()))  
        feopen = (self.feopen_listWidget.selectedItems()) 
        list_feopen = [] 
        for i in list(feopen):
            list_feopen.append(str(i.text())) 
        fevol = (self.fevol_listWidget.selectedItems()) 
        list_fevol = [] 
        for i in list(fevol):
            list_fevol.append(str(i.text()))   
        pbclose = (self.pbclose_listWidget.selectedItems()) 
        list_pbclose = [] 
        for i in list(pbclose):
            list_pbclose.append(str(i.text()))     
        pbhigh = (self.pbhigh_listWidget.selectedItems()) 
        list_pbhigh = [] 
        for i in list(pbhigh):
            list_pbhigh.append(str(i.text()))  
        pblow = (self.pblow_listWidget.selectedItems()) 
        list_pblow = [] 
        for i in list(pblow):
            list_pblow.append(str(i.text()))  
        pbopen = (self.pbopen_listWidget.selectedItems()) 
        list_pbopen = [] 
        for i in list(pbopen):
            list_pbopen.append(str(i.text())) 
        pbvol = (self.pbvol_listWidget.selectedItems()) 
        list_pbvol = [] 
        for i in list(pbvol):
            list_pbvol.append(str(i.text())) 
        niclose = (self.niclose_listWidget.selectedItems()) 
        list_niclose = [] 
        for i in list(niclose):
            list_niclose.append(str(i.text()))     
        nihigh = (self.nihigh_listWidget.selectedItems()) 
        list_nihigh = [] 
        for i in list(nihigh):
            list_nihigh.append(str(i.text()))  
        nilow = (self.nilow_listWidget.selectedItems()) 
        list_nilow = [] 
        for i in list(nilow):
            list_nilow.append(str(i.text()))  
        niopen = (self.niopen_listWidget.selectedItems()) 
        list_niopen = [] 
        for i in list(niopen):
            list_niopen.append(str(i.text())) 
        nivol = (self.nivol_listWidget.selectedItems()) 
        list_nivol = [] 
        for i in list(nivol):
            list_nivol.append(str(i.text()))  
        paclose = (self.paclose_listWidget.selectedItems()) 
        list_paclose = [] 
        for i in list(paclose):
            list_paclose.append(str(i.text()))     
        pahigh = (self.pahigh_listWidget.selectedItems()) 
        list_pahigh = [] 
        for i in list(pahigh):
            list_pahigh.append(str(i.text()))  
        palow = (self.palow_listWidget.selectedItems()) 
        list_palow = [] 
        for i in list(palow):
            list_palow.append(str(i.text()))  
        paopen = (self.paopen_listWidget.selectedItems()) 
        list_paopen = [] 
        for i in list(paopen):
            list_paopen.append(str(i.text())) 
        pavol = (self.pavol_listWidget.selectedItems()) 
        list_pavol = [] 
        for i in list(pavol):
            list_pavol.append(str(i.text())) 
        plclose = (self.plclose_listWidget.selectedItems()) 
        list_plclose = [] 
        for i in list(plclose):
            list_plclose.append(str(i.text()))     
        plhigh = (self.plhigh_listWidget.selectedItems()) 
        list_plhigh = [] 
        for i in list(plhigh):
            list_plhigh.append(str(i.text()))  
        pllow = (self.pllow_listWidget.selectedItems()) 
        list_pllow = [] 
        for i in list(pllow):
            list_pllow.append(str(i.text()))  
        plopen = (self.plopen_listWidget.selectedItems()) 
        list_plopen = [] 
        for i in list(plopen):
            list_plopen.append(str(i.text())) 
        plvol = (self.plvol_listWidget.selectedItems()) 
        list_plvol = [] 
        for i in list(plvol):
            list_plvol.append(str(i.text())) 
        agclose = (self.agclose_listWidget.selectedItems()) 
        list_agclose = [] 
        for i in list(agclose):
            list_agclose.append(str(i.text()))     
        aghigh = (self.aghigh_listWidget.selectedItems()) 
        list_aghigh = [] 
        for i in list(aghigh):
            list_aghigh.append(str(i.text()))  
        aglow = (self.aglow_listWidget.selectedItems()) 
        list_aglow = [] 
        for i in list(aglow):
            list_aglow.append(str(i.text()))  
        agopen = (self.agopen_listWidget.selectedItems()) 
        list_agopen = [] 
        for i in list(agopen):
            list_agopen.append(str(i.text())) 
        agvol = (self.agvol_listWidget.selectedItems()) 
        list_agvol = [] 
        for i in list(agvol):
            list_agvol.append(str(i.text())) 
        stclose = (self.stclose_listWidget.selectedItems()) 
        list_stclose = [] 
        for i in list(stclose):
            list_stclose.append(str(i.text()))     
        sthigh = (self.sthigh_listWidget.selectedItems()) 
        list_sthigh = [] 
        for i in list(sthigh):
            list_sthigh.append(str(i.text()))  
        stlow = (self.stlow_listWidget.selectedItems()) 
        list_stlow = [] 
        for i in list(stlow):
            list_stlow.append(str(i.text()))  
        stopen = (self.stopen_listWidget.selectedItems()) 
        list_stopen = [] 
        for i in list(stopen):
            list_stopen.append(str(i.text())) 
        stvol = (self.stvol_listWidget.selectedItems()) 
        list_stvol = [] 
        for i in list(stvol):
            list_stvol.append(str(i.text()))  
        tnclose = (self.tnclose_listWidget.selectedItems()) 
        list_tnclose = [] 
        for i in list(tnclose):
            list_tnclose.append(str(i.text()))     
        tnhigh = (self.tnhigh_listWidget.selectedItems()) 
        list_tnhigh = [] 
        for i in list(tnhigh):
            list_tnhigh.append(str(i.text()))  
        tnlow = (self.tnlow_listWidget.selectedItems()) 
        list_tnlow = [] 
        for i in list(tnlow):
            list_tnlow.append(str(i.text()))  
        tnopen = (self.tnopen_listWidget.selectedItems()) 
        list_tnopen = [] 
        for i in list(tnopen):
            list_tnopen.append(str(i.text())) 
        tnvol = (self.tnvol_listWidget.selectedItems()) 
        list_tnvol = [] 
        for i in list(tnvol):
            list_tnvol.append(str(i.text())) 
        urclose = (self.urclose_listWidget.selectedItems()) 
        list_urclose = [] 
        for i in list(urclose):
            list_urclose.append(str(i.text()))     
        urhigh = (self.urhigh_listWidget.selectedItems()) 
        list_urhigh = [] 
        for i in list(urhigh):
            list_urhigh.append(str(i.text()))  
        urlow = (self.urlow_listWidget.selectedItems()) 
        list_urlow = [] 
        for i in list(urlow):
            list_urlow.append(str(i.text()))  
        uropen = (self.uropen_listWidget.selectedItems()) 
        list_uropen = [] 
        for i in list(uropen):
            list_uropen.append(str(i.text())) 
        urvol = (self.urvol_listWidget.selectedItems()) 
        list_urvol = [] 
        for i in list(urvol):
            list_urvol.append(str(i.text()))  
        znclose = (self.znclose_listWidget.selectedItems()) 
        list_znclose = [] 
        for i in list(znclose):
            list_znclose.append(str(i.text()))     
        znhigh = (self.znhigh_listWidget.selectedItems()) 
        list_znhigh = [] 
        for i in list(znhigh):
            list_znhigh.append(str(i.text()))  
        znlow = (self.znlow_listWidget.selectedItems()) 
        list_znlow = [] 
        for i in list(znlow):
            list_znlow.append(str(i.text()))  
        znopen = (self.znopen_listWidget.selectedItems()) 
        list_znopen = [] 
        for i in list(znopen):
            list_znopen.append(str(i.text())) 
        znvol = (self.znvol_listWidget.selectedItems()) 
        list_znvol = [] 
        for i in list(znvol):
            list_znvol.append(str(i.text()))  
        cornclose = (self.cornclose_listWidget.selectedItems()) 
        list_cornclose = [] 
        for i in list(cornclose):
            list_cornclose.append(str(i.text()))     
        cornhigh = (self.cornhigh_listWidget.selectedItems()) 
        list_cornhigh = [] 
        for i in list(cornhigh):
            list_cornhigh.append(str(i.text()))  
        cornlow = (self.cornlow_listWidget.selectedItems()) 
        list_cornlow = [] 
        for i in list(cornlow):
            list_cornlow.append(str(i.text()))  
        cornopen = (self.cornopen_listWidget.selectedItems()) 
        list_cornopen = [] 
        for i in list(cornopen):
            list_cornopen.append(str(i.text())) 
        cornvol = (self.cornvol_listWidget.selectedItems()) 
        list_cornvol = [] 
        for i in list(cornvol):
            list_cornvol.append(str(i.text()))  
        wheatclose = (self.wheatclose_listWidget.selectedItems()) 
        list_wheatclose = [] 
        for i in list(wheatclose):
            list_wheatclose.append(str(i.text()))     
        wheathigh = (self.wheathigh_listWidget.selectedItems()) 
        list_wheathigh = [] 
        for i in list(wheathigh):
            list_wheathigh.append(str(i.text()))  
        wheatlow = (self.wheatlow_listWidget.selectedItems()) 
        list_wheatlow = [] 
        for i in list(wheatlow):
            list_wheatlow.append(str(i.text()))  
        wheatopen = (self.wheatopen_listWidget.selectedItems()) 
        list_wheatopen = [] 
        for i in list(wheatopen):
            list_wheatopen.append(str(i.text())) 
        wheatvol = (self.wheatvol_listWidget.selectedItems()) 
        list_wheatvol = [] 
        for i in list(wheatvol):
            list_wheatvol.append(str(i.text())) 
        soyclose = (self.soyclose_listWidget.selectedItems()) 
        list_soyclose = [] 
        for i in list(soyclose):
            list_soyclose.append(str(i.text()))     
        soyhigh = (self.soyhigh_listWidget.selectedItems()) 
        list_soyhigh = [] 
        for i in list(soyhigh):
            list_soyhigh.append(str(i.text()))  
        soylow = (self.soylow_listWidget.selectedItems()) 
        list_soylow = [] 
        for i in list(soylow):
            list_soylow.append(str(i.text()))  
        soyopen = (self.soyopen_listWidget.selectedItems()) 
        list_soyopen = [] 
        for i in list(soyopen):
            list_soyopen.append(str(i.text())) 
        soyvol = (self.soyvol_listWidget.selectedItems()) 
        list_soyvol = [] 
        for i in list(soyvol):
            list_soyvol.append(str(i.text()))
        soclose = (self.soclose_listWidget.selectedItems()) 
        list_soclose = [] 
        for i in list(soclose):
            list_soclose.append(str(i.text()))     
        sohigh = (self.sohigh_listWidget.selectedItems()) 
        list_sohigh = [] 
        for i in list(sohigh):
            list_sohigh.append(str(i.text()))  
        solow = (self.solow_listWidget.selectedItems()) 
        list_solow = [] 
        for i in list(solow):
            list_solow.append(str(i.text()))  
        soopen = (self.soopen_listWidget.selectedItems()) 
        list_soopen = [] 
        for i in list(soopen):
            list_soopen.append(str(i.text())) 
        sovol = (self.sovol_listWidget.selectedItems()) 
        list_sovol = [] 
        for i in list(sovol):
            list_sovol.append(str(i.text())) 
        cotclose = (self.cotclose_listWidget.selectedItems()) 
        list_cotclose = [] 
        for i in list(cotclose):
            list_cotclose.append(str(i.text()))     
        cothigh = (self.cothigh_listWidget.selectedItems()) 
        list_cothigh = [] 
        for i in list(cothigh):
            list_cothigh.append(str(i.text()))  
        cotlow = (self.cotlow_listWidget.selectedItems()) 
        list_cotlow = [] 
        for i in list(cotlow):
            list_cotlow.append(str(i.text()))  
        cotopen = (self.cotopen_listWidget.selectedItems()) 
        list_cotopen = [] 
        for i in list(cotopen):
            list_cotopen.append(str(i.text())) 
        cotvol = (self.cotvol_listWidget.selectedItems()) 
        list_cotvol = [] 
        for i in list(cotvol):
            list_cotvol.append(str(i.text())) 
        sbclose = (self.sbclose_listWidget.selectedItems()) 
        list_sbclose = [] 
        for i in list(sbclose):
            list_sbclose.append(str(i.text()))     
        sbhigh = (self.sbhigh_listWidget.selectedItems()) 
        list_sbhigh = [] 
        for i in list(sbhigh):
            list_sbhigh.append(str(i.text()))  
        sblow = (self.sblow_listWidget.selectedItems()) 
        list_sblow = [] 
        for i in list(sblow):
            list_sblow.append(str(i.text()))  
        sbopen = (self.sbopen_listWidget.selectedItems()) 
        list_sbopen = [] 
        for i in list(sbopen):
            list_sbopen.append(str(i.text())) 
        sbvol = (self.sbvol_listWidget.selectedItems()) 
        list_sbvol = [] 
        for i in list(sbvol):
            list_sbvol.append(str(i.text())) 
        sbopen = (self.sbopen_listWidget.selectedItems()) 
        list_sbopen = [] 
        for i in list(sbopen):
            list_sbopen.append(str(i.text())) 
        sincurrency = (self.sincurrency_listWidget.selectedItems()) 
        list_sincurrency = [] 
        for i in list(sincurrency):
            list_sincurrency.append(str(i.text()))   
        crosscurrency = (self.crosscurrency_listWidget.selectedItems()) 
        list_crosscurrency = [] 
        for i in list(crosscurrency):
            list_crosscurrency.append(str(i.text())) 
        equity = (self.equity_listWidget.selectedItems()) 
        list_equity = [] 
        for i in list(equity):
            list_equity.append(str(i.text()))  
        sent = (self.sent_listWidget.selectedItems()) 
        list_sent = [] 
        for i in list(sent):
            list_sent.append(str(i.text()))     
        imammtot = (self.imammtot_listWidget.selectedItems()) 
        list_imammtot = [] 
        for i in list(imammtot):
            list_imammtot.append(str(i.text()))      
        imamman = (self.imamman_listWidget.selectedItems()) 
        list_imamman = [] 
        for i in list(imamman):
            list_imamman.append(str(i.text()))
        imammnittot = (self.imammnittot_listWidget.selectedItems()) 
        list_imammnittot = [] 
        for i in list(imammnittot):
            list_imammnittot.append(str(i.text()))  
        imammnitaq = (self.imammnitaq_listWidget.selectedItems()) 
        list_imammnitaq = [] 
        for i in list(imammnitaq):
            list_imammnitaq.append(str(i.text()))    
        imammsu = (self.imammsu_listWidget.selectedItems()) 
        list_imammsu = [] 
        for i in list(imammsu):
            list_imammsu.append(str(i.text()))  
        imdap = (self.imdap_listWidget.selectedItems()) 
        list_imdap = [] 
        for i in list(imdap):
            list_imdap.append(str(i.text()))   
        imint = (self.imint_listWidget.selectedItems()) 
        list_imint = [] 
        for i in list(imint):
            list_imint.append(str(i.text())) 
        immaptot = (self.immaptot_listWidget.selectedItems()) 
        list_immaptot = [] 
        for i in list(immaptot):
            list_immaptot.append(str(i.text()))
        immapmix = (self.immapmix_listWidget.selectedItems()) 
        list_immapmix = [] 
        for i in list(immapmix):
            list_immapmix.append(str(i.text())) 
        imphosac = (self.imphosac_listWidget.selectedItems()) 
        list_imphosac = [] 
        for i in list(imphosac):
            list_imphosac.append(str(i.text()))   
        impot = (self.impot_listWidget.selectedItems()) 
        list_impot = [] 
        for i in list(impot):
            list_impot.append(str(i.text()))   
        imtsptot = (self.imtsptot_listWidget.selectedItems()) 
        list_imtsptot = [] 
        for i in list(imtsptot):
            list_imtsptot.append(str(i.text()))     
        imtspless = (self.imtspless_listWidget.selectedItems()) 
        list_imtspless = [] 
        for i in list(imtspless):
            list_imtspless.append(str(i.text()))   
        imtspgreat = (self.imtspgreat_listWidget.selectedItems()) 
        list_imtspgreat = [] 
        for i in list(imtspgreat):
            list_imtspgreat.append(str(i.text()))   
        imuantot = (self.imuantot_listWidget.selectedItems()) 
        list_imuantot = [] 
        for i in list(imuantot):
            list_imuantot.append(str(i.text()))
        imuanmix = (self.imuanmix_listWidget.selectedItems()) 
        list_imuanmix = [] 
        for i in list(imuanmix):
            list_imuanmix.append(str(i.text()))      
        imureatot = (self.imureatot_listWidget.selectedItems()) 
        list_imureatot = [] 
        for i in list(imureatot):
            list_imureatot.append(str(i.text()))    
        imureadef = (self.imureadef_listWidget.selectedItems()) 
        list_imureadef = [] 
        for i in list(imureadef):
            list_imureadef.append(str(i.text()))     
        imureanesoi = (self.imureanesoi_listWidget.selectedItems()) 
        list_imureanesoi = [] 
        for i in list(imureanesoi):
            list_imureanesoi.append(str(i.text()))     
        imureasolid = (self.imureasolid_listWidget.selectedItems()) 
        list_imureasolid = [] 
        for i in list(imureasolid):
            list_imureasolid.append(str(i.text()))     
        imureaaq = (self.imureaaq_listWidget.selectedItems()) 
        list_imureaaq = [] 
        for i in list(imureaaq):
            list_imureaaq.append(str(i.text()))  
        exammtot = (self.exammtot_listWidget.selectedItems()) 
        list_exammtot = [] 
        for i in list(exammtot):
            list_exammtot.append(str(i.text()))  
        examman = (self.examman_listWidget.selectedItems()) 
        list_examman = [] 
        for i in list(examman):
            list_examman.append(str(i.text())) 
        exammnittot = (self.exammnittot_listWidget.selectedItems()) 
        list_exammnittot = [] 
        for i in list(exammnittot):
            list_exammnittot.append(str(i.text()))  
        exammnitaq = (self.exammnitaq_listWidget.selectedItems()) 
        list_exammnitaq = [] 
        for i in list(exammnitaq):
            list_exammnitaq.append(str(i.text()))      
        exammsu = (self.exammsu_listWidget.selectedItems()) 
        list_exammsu = [] 
        for i in list(exammsu):
            list_exammsu.append(str(i.text()))     
        exdap = (self.exdap_listWidget.selectedItems()) 
        list_exdap = [] 
        for i in list(exdap):
            list_exdap.append(str(i.text()))     
        exnpk = (self.exnpk_listWidget.selectedItems()) 
        list_exnpk = [] 
        for i in list(exnpk):
            list_exnpk.append(str(i.text()))     
        exmaptot = (self.exmaptot_listWidget.selectedItems()) 
        list_exmaptot = [] 
        for i in list(exmaptot):
            list_exmaptot.append(str(i.text()))    
        exmapmix = (self.exmapmix_listWidget.selectedItems()) 
        list_exmapmix = [] 
        for i in list(exmapmix):
            list_exmapmix.append(str(i.text()))         
        exphosac = (self.exphosac_listWidget.selectedItems()) 
        list_exphosac = [] 
        for i in list(exphosac):
            list_exphosac.append(str(i.text()))   
        expot = (self.expot_listWidget.selectedItems()) 
        list_expot = [] 
        for i in list(expot):
            list_expot.append(str(i.text()))     
        extsptot = (self.extsptot_listWidget.selectedItems()) 
        list_extsptot = [] 
        for i in list(extsptot):
            list_extsptot.append(str(i.text()))          
        extspless = (self.extspless_listWidget.selectedItems()) 
        list_extspless = [] 
        for i in list(extspless):
            list_extspless.append(str(i.text())) 
        extspgreat = (self.extspgreat_listWidget.selectedItems()) 
        list_extspgreat = [] 
        for i in list(extspgreat):
            list_extspgreat.append(str(i.text()))     
        exuantot = (self.exuantot_listWidget.selectedItems()) 
        list_exuantot = [] 
        for i in list(exuantot):
            list_exuantot.append(str(i.text())) 
        exuanmix = (self.exuanmix_listWidget.selectedItems()) 
        list_exuanmix = [] 
        for i in list(exuanmix):
            list_exuanmix.append(str(i.text()))      
        exureatot = (self.exureatot_listWidget.selectedItems()) 
        list_exureatot = [] 
        for i in list(exureatot):
            list_exureatot.append(str(i.text()))     
        exureaaq = (self.exureaaq_listWidget.selectedItems()) 
        list_exureaaq = [] 
        for i in list(exureaaq):
            list_exureaaq.append(str(i.text()))    
        sdamm = (self.sdamm_listWidget.selectedItems()) 
        list_sdamm = [] 
        for i in list(sdamm):
            list_sdamm.append(str(i.text()))    
        sddapmapus = (self.sddapmapus_listWidget.selectedItems()) 
        list_sddapmapus = [] 
        for i in list(sddapmapus):
            list_sddapmapus.append(str(i.text()))    
        sddapmapall = (self.sddapmapall_listWidget.selectedItems()) 
        list_sddapmapall = [] 
        for i in list(sddapmapall):
            list_sddapmapall.append(str(i.text()))   
        sdpotus = (self.sdpotus_listWidget.selectedItems()) 
        list_sdpotus = [] 
        for i in list(sdpotus):
            list_sdpotus.append(str(i.text()))    
        sdpotall = (self.sdpotall_listWidget.selectedItems()) 
        list_sdpotall = [] 
        for i in list(sdpotall):
            list_sdpotall.append(str(i.text()))   
        sduan = (self.sduan_listWidget.selectedItems()) 
        list_sduan = [] 
        for i in list(sduan):
            list_sduan.append(str(i.text()))     
        sdureaus = (self.sdureaus_listWidget.selectedItems()) 
        list_sdureaus = [] 
        for i in list(sdureaus):
            list_sdureaus.append(str(i.text()))    
        sdureaall = (self.sdureaall_listWidget.selectedItems()) 
        list_sdureaall = [] 
        for i in list(sdureaall):
            list_sdureaall.append(str(i.text()))  
        dapbid = (self.dapbid_listWidget.selectedItems()) 
        list_dapbid = [] 
        for i in list(dapbid):
            list_dapbid.append(str(i.text()))  
        dapoffer = (self.dapoffer_listWidget.selectedItems()) 
        list_dapoffer = [] 
        for i in list(dapoffer):
            list_dapoffer.append(str(i.text())) 
        dapmid = (self.dapmid_listWidget.selectedItems()) 
        list_dapmid = [] 
        for i in list(dapmid):
            list_dapmid.append(str(i.text()))   
        mopbid = (self.mopbid_listWidget.selectedItems()) 
        list_mopbid = [] 
        for i in list(mopbid):
            list_mopbid.append(str(i.text()))  
        mopoffer = (self.mopoffer_listWidget.selectedItems()) 
        list_mopoffer = [] 
        for i in list(mopoffer):
            list_mopoffer.append(str(i.text())) 
        mopmid = (self.mopmid_listWidget.selectedItems()) 
        list_mopmid = [] 
        for i in list(mopmid):
            list_mopmid.append(str(i.text()))  
        phorockbid = (self.phorockbid_listWidget.selectedItems()) 
        list_phorockbid = [] 
        for i in list(phorockbid):
            list_phorockbid.append(str(i.text()))  
        phorockoffer = (self.phorockoffer_listWidget.selectedItems()) 
        list_phorockoffer = [] 
        for i in list(phorockoffer):
            list_phorockoffer.append(str(i.text())) 
        phorockmid = (self.phorockmid_listWidget.selectedItems()) 
        list_phorockmid = [] 
        for i in list(phorockmid):
            list_phorockmid.append(str(i.text()))    
        sulfurbid = (self.sulfurbid_listWidget.selectedItems()) 
        list_sulfurbid = [] 
        for i in list(sulfurbid):
            list_sulfurbid.append(str(i.text()))  
        sulfuroffer = (self.sulfuroffer_listWidget.selectedItems()) 
        list_sulfuroffer = [] 
        for i in list(sulfuroffer):
            list_sulfuroffer.append(str(i.text())) 
        sulfurmid = (self.sulfurmid_listWidget.selectedItems()) 
        list_sulfurmid = [] 
        for i in list(sulfurmid):
            list_sulfurmid.append(str(i.text()))      
        ureabid = (self.ureabid_listWidget.selectedItems()) 
        list_ureabid = [] 
        for i in list(ureabid):
            list_ureabid.append(str(i.text()))  
        ureaoffer = (self.ureaoffer_listWidget.selectedItems()) 
        list_ureaoffer = [] 
        for i in list(ureaoffer):
            list_ureaoffer.append(str(i.text())) 
        ureamid = (self.ureamid_listWidget.selectedItems()) 
        list_ureamid = [] 
        for i in list(ureamid):
            list_ureamid.append(str(i.text()))  
        ammbid = (self.ammbid_listWidget.selectedItems()) 
        list_ammbid = [] 
        for i in list(ammbid):
            list_ammbid.append(str(i.text()))  
        ammoffer = (self.ammoffer_listWidget.selectedItems()) 
        list_ammoffer = [] 
        for i in list(ammoffer):
            list_ammoffer.append(str(i.text())) 
        ammmid = (self.ammmid_listWidget.selectedItems()) 
        list_ammmid = [] 
        for i in list(ammmid):
            list_ammmid.append(str(i.text()))  
        phoacbid = (self.phoacbid_listWidget.selectedItems()) 
        list_phoacbid = [] 
        for i in list(phoacbid):
            list_phoacbid.append(str(i.text()))  
        phoacoffer = (self.phoacoffer_listWidget.selectedItems()) 
        list_phoacoffer = [] 
        for i in list(phoacoffer):
            list_phoacoffer.append(str(i.text())) 
        phoacmid = (self.phoacmid_listWidget.selectedItems()) 
        list_phoacmid = [] 
        for i in list(phoacmid):
            list_phoacmid.append(str(i.text()))    
        sulacbid = (self.sulacbid_listWidget.selectedItems()) 
        list_sulacbid = [] 
        for i in list(sulacbid):
            list_sulacbid.append(str(i.text()))  
        sulacoffer = (self.sulacoffer_listWidget.selectedItems()) 
        list_sulacoffer = [] 
        for i in list(sulacoffer):
            list_sulacoffer.append(str(i.text())) 
        sulacmid = (self.sulacmid_listWidget.selectedItems()) 
        list_sulacmid = [] 
        for i in list(sulacmid):
            list_sulacmid.append(str(i.text()))    
        uanbid = (self.uanbid_listWidget.selectedItems()) 
        list_uanbid = [] 
        for i in list(uanbid):
            list_uanbid.append(str(i.text()))  
        uanoffer = (self.uanoffer_listWidget.selectedItems()) 
        list_uanoffer = [] 
        for i in list(uanoffer):
            list_uanoffer.append(str(i.text())) 
        uanmid = (self.uanmid_listWidget.selectedItems()) 
        list_uanmid = [] 
        for i in list(uanmid):
            list_uanmid.append(str(i.text()))     
        chsdap = (self.chsdap_listWidget.selectedItems()) 
        list_chsdap = [] 
        for i in list(chsdap):
            list_chsdap.append(str(i.text()))         
        chspot = (self.chspot_listWidget.selectedItems()) 
        list_chspot = [] 
        for i in list(chspot):
            list_chspot.append(str(i.text()))   
        chsuan = (self.chsuan_listWidget.selectedItems()) 
        list_chsuan = [] 
        for i in list(chsuan):
            list_chsuan.append(str(i.text()))   
        chsurea = (self.chsurea_listWidget.selectedItems()) 
        list_chsurea = [] 
        for i in list(chsurea):
            list_chsurea.append(str(i.text()))      
        buckdap = (self.buckdap_listWidget.selectedItems()) 
        list_buckdap = [] 
        for i in list(buckdap):
            list_buckdap.append(str(i.text()))         
        buckpot = (self.buckpot_listWidget.selectedItems()) 
        list_buckpot = [] 
        for i in list(buckpot):
            list_buckpot.append(str(i.text()))   
        buckuan = (self.buckuan_listWidget.selectedItems()) 
        list_buckuan = [] 
        for i in list(buckuan):
            list_buckuan.append(str(i.text()))   
        buckurea = (self.buckurea_listWidget.selectedItems()) 
        list_buckurea = [] 
        for i in list(buckurea):
            list_buckurea.append(str(i.text()))   
        cru = (self.cru_listWidget.selectedItems()) 
        list_cru = [] 
        for i in list(cru):
            list_cru.append(str(i.text()))             
############################################################################################################################################################################
        ureagrancfrfinal_ticker = []
        ureagrancfrfinal_field = []
        ureagrancfrfinal_source = []
        for i in (list_ureagrancfr):
            ureagrancfrfinal_ticker.append(dictTickerureagrancfr.get(i))
            ureagrancfrfinal_field.append(dictFieldureagrancfr.get(i))
            ureagrancfrfinal_source.append(dictSourceureagrancfr.get(i))  
        ureagrandelfinal_ticker = []
        ureagrandelfinal_field = []
        ureagrandelfinal_source = []
        for i in (list_ureagrandel):
            ureagrandelfinal_ticker.append(dictTickerureagrandel.get(i))
            ureagrandelfinal_field.append(dictFieldureagrandel.get(i))
            ureagrandelfinal_source.append(dictSourceureagrandel.get(i))  
        ureagranfcafinal_ticker = []
        ureagranfcafinal_field = []
        ureagranfcafinal_source = []
        for i in (list_ureagranfca):
            ureagranfcafinal_ticker.append(dictTickerureagranfca.get(i))
            ureagranfcafinal_field.append(dictFieldureagranfca.get(i))
            ureagranfcafinal_source.append(dictSourceureagranfca.get(i)) 
        ureagranfobfinal_ticker = []
        ureagranfobfinal_field = []
        ureagranfobfinal_source = []
        for i in (list_ureagranfob):
            ureagranfobfinal_ticker.append(dictTickerureagranfob.get(i))
            ureagranfobfinal_field.append(dictFieldureagranfob.get(i))
            ureagranfobfinal_source.append(dictSourceureagranfob.get(i))
        ureagranfobfisfinal_ticker = []
        ureagranfobfisfinal_field = []
        ureagranfobfisfinal_source = []
        for i in (list_ureagranfobfis):
            ureagranfobfisfinal_ticker.append(dictTickerureagranfobfis.get(i))
            ureagranfobfisfinal_field.append(dictFieldureagranfobfis.get(i))
            ureagranfobfisfinal_source.append(dictSourceureagranfobfis.get(i))
        ureaprillcfrfinal_ticker = []
        ureaprillcfrfinal_field = []
        ureaprillcfrfinal_source = []
        for i in (list_ureaprillcfr):
            ureaprillcfrfinal_ticker.append(dictTickerureaprillcfr.get(i))
            ureaprillcfrfinal_field.append(dictFieldureaprillcfr.get(i))
            ureaprillcfrfinal_source.append(dictSourceureaprillcfr.get(i))    
        ureaprillcptfinal_ticker = []
        ureaprillcptfinal_field = []
        ureaprillcptfinal_source = []
        for i in (list_ureaprillcpt):
            ureaprillcptfinal_ticker.append(dictTickerureaprillcpt.get(i))
            ureaprillcptfinal_field.append(dictFieldureaprillcpt.get(i))
            ureaprillcptfinal_source.append(dictSourceureaprillcpt.get(i)) 
        ureaprillfobfinal_ticker = []
        ureaprillfobfinal_field = []
        ureaprillfobfinal_source = []
        for i in (list_ureaprillfob):
            ureaprillfobfinal_ticker.append(dictTickerureaprillfob.get(i))
            ureaprillfobfinal_field.append(dictFieldureaprillfob.get(i))
            ureaprillfobfinal_source.append(dictSourceureaprillfob.get(i))    
        ureaprillfobfisfinal_ticker = []
        ureaprillfobfisfinal_field = []
        ureaprillfobfisfinal_source = []
        for i in (list_ureaprillfobfis):
            ureaprillfobfisfinal_ticker.append(dictTickerureaprillfobfis.get(i))
            ureaprillfobfisfinal_field.append(dictFieldureaprillfobfis.get(i))
            ureaprillfobfisfinal_source.append(dictSourceureaprillfobfis.get(i))  
        ureaotherfinal_ticker = []
        ureaotherfinal_field = []
        ureaotherfinal_source = []
        for i in (list_ureaother):
            ureaotherfinal_ticker.append(dictTickerureaother.get(i))
            ureaotherfinal_field.append(dictFieldureaother.get(i))
            ureaotherfinal_source.append(dictSourceureaother.get(i)) 
        uan2830final_ticker = []
        uan2830final_field = []
        uan2830final_source = []
        for i in (list_uan2830):
            uan2830final_ticker.append(dictTickeruan2830.get(i))
            uan2830final_field.append(dictFielduan2830.get(i))
            uan2830final_source.append(dictSourceuan2830.get(i)) 
        uan32final_ticker = []
        uan32final_field = []
        uan32final_source = []
        for i in (list_uan32):
            uan32final_ticker.append(dictTickeruan32.get(i))
            uan32final_field.append(dictFielduan32.get(i))
            uan32final_source.append(dictSourceuan32.get(i))    
        uanotherfinal_ticker = []
        uanotherfinal_field = []
        uanotherfinal_source = []
        for i in (list_uanother):
            uanotherfinal_ticker.append(dictTickeruanother.get(i))
            uanotherfinal_field.append(dictFielduanother.get(i))
            uanotherfinal_source.append(dictSourceuanother.get(i))  
        potgranfinal_ticker = []
        potgranfinal_field = []
        potgranfinal_source = []
        for i in (list_potgran):
            potgranfinal_ticker.append(dictTickerpotgran.get(i))
            potgranfinal_field.append(dictFieldpotgran.get(i))
            potgranfinal_source.append(dictSourcepotgran.get(i))
        potstanfinal_ticker = []
        potstanfinal_field = []
        potstanfinal_source = []
        for i in (list_potstan):
            potstanfinal_ticker.append(dictTickerpotstan.get(i))
            potstanfinal_field.append(dictFieldpotstan.get(i))
            potstanfinal_source.append(dictSourcepotstan.get(i)) 
        ammspotfinal_ticker = []
        ammspotfinal_field = []
        ammspotfinal_source = []
        for i in (list_ammspot):
            ammspotfinal_ticker.append(dictTickerammspot.get(i))
            ammspotfinal_field.append(dictFieldammspot.get(i))
            ammspotfinal_source.append(dictSourceammspot.get(i))     
        ammtotcfrfinal_ticker = []
        ammtotcfrfinal_field = []
        ammtotcfrfinal_source = []
        for i in (list_ammtotcfr):
            ammtotcfrfinal_ticker.append(dictTickerammtotcfr.get(i))
            ammtotcfrfinal_field.append(dictFieldammtotcfr.get(i))
            ammtotcfrfinal_source.append(dictSourceammtotcfr.get(i)) 
        ammtotdelfinal_ticker = []
        ammtotdelfinal_field = []
        ammtotdelfinal_source = []
        for i in (list_ammtotdel):
            ammtotdelfinal_ticker.append(dictTickerammtotdel.get(i))
            ammtotdelfinal_field.append(dictFieldammtotdel.get(i))
            ammtotdelfinal_source.append(dictSourceammtotdel.get(i))    
        ammtotfobfinal_ticker = []
        ammtotfobfinal_field = []
        ammtotfobfinal_source = []
        for i in (list_ammtotfob):
            ammtotfobfinal_ticker.append(dictTickerammtotfob.get(i))
            ammtotfobfinal_field.append(dictFieldammtotfob.get(i))
            ammtotfobfinal_source.append(dictSourceammtotfob.get(i)) 
        ammcontractfinal_ticker = []
        ammcontractfinal_field = []
        ammcontractfinal_source = []
        for i in (list_ammcontract):
            ammcontractfinal_ticker.append(dictTickerammcontract.get(i))
            ammcontractfinal_field.append(dictFieldammcontract.get(i))
            ammcontractfinal_source.append(dictSourceammcontract.get(i))             
        anbagfinal_ticker = []
        anbagfinal_field = []
        anbagfinal_source = []
        for i in (list_anbag):
            anbagfinal_ticker.append(dictTickeranbag.get(i))
            anbagfinal_field.append(dictFieldanbag.get(i))
            anbagfinal_source.append(dictSourceanbag.get(i))   
        anbulkfinal_ticker = []
        anbulkfinal_field = []
        anbulkfinal_source = []
        for i in (list_anbulk):
            anbulkfinal_ticker.append(dictTickeranbulk.get(i))
            anbulkfinal_field.append(dictFieldanbulk.get(i))
            anbulkfinal_source.append(dictSourceanbulk.get(i))   
        antotcfrfinal_ticker = []
        antotcfrfinal_field = []
        antotcfrfinal_source = []
        for i in (list_antotcfr):
            antotcfrfinal_ticker.append(dictTickerantotcfr.get(i))
            antotcfrfinal_field.append(dictFieldantotcfr.get(i))
            antotcfrfinal_source.append(dictSourceantotcfr.get(i))   
        antotfobfinal_ticker = []
        antotfobfinal_field = []
        antotfobfinal_source = []
        for i in (list_antotfob):
            antotfobfinal_ticker.append(dictTickerantotfob.get(i))
            antotfobfinal_field.append(dictFieldantotfob.get(i))
            antotfobfinal_source.append(dictSourceantotfob.get(i))  
        asotherfinal_ticker = []
        asotherfinal_field = []
        asotherfinal_source = []
        for i in (list_asother):
            asotherfinal_ticker.append(dictTickerasother.get(i))
            asotherfinal_field.append(dictFieldasother.get(i))
            asotherfinal_source.append(dictSourceasother.get(i))      
        asstanfinal_ticker = []
        asstanfinal_field = []
        asstanfinal_source = []
        for i in (list_asstan):
            asstanfinal_ticker.append(dictTickerasstan.get(i))
            asstanfinal_field.append(dictFieldasstan.get(i))
            asstanfinal_source.append(dictSourceasstan.get(i))        
        aswcfrfinal_ticker = []
        aswcfrfinal_field = []
        aswcfrfinal_source = []
        for i in (list_aswcfr):
            aswcfrfinal_ticker.append(dictTickeraswcfr.get(i))
            aswcfrfinal_field.append(dictFieldaswcfr.get(i))
            aswcfrfinal_source.append(dictSourceaswcfr.get(i))    
        aswfobfinal_ticker = []
        aswfobfinal_field = []
        aswfobfinal_source = []
        for i in (list_aswfob):
            aswfobfinal_ticker.append(dictTickeraswfob.get(i))
            aswfobfinal_field.append(dictFieldaswfob.get(i))
            aswfobfinal_source.append(dictSourceaswfob.get(i))     
        canfinal_ticker = []
        canfinal_field = []
        canfinal_source = []
        for i in (list_can):
            canfinal_ticker.append(dictTickercan.get(i))
            canfinal_field.append(dictFieldcan.get(i))
            canfinal_source.append(dictSourcecan.get(i))  
        dapfobfinal_ticker = []
        dapfobfinal_field = []
        dapfobfinal_source = []
        for i in (list_dapfob):
            dapfobfinal_ticker.append(dictTickerdapfob.get(i))
            dapfobfinal_field.append(dictFielddapfob.get(i))
            dapfobfinal_source.append(dictSourcedapfob.get(i))  
        dapotherfinal_ticker = []
        dapotherfinal_field = []
        dapotherfinal_source = []
        for i in (list_dapother):
            dapotherfinal_ticker.append(dictTickerdapother.get(i))
            dapotherfinal_field.append(dictFielddapother.get(i))
            dapotherfinal_source.append(dictSourcedapother.get(i)) 
        map10final_ticker = []
        map10final_field = []
        map10final_source = []
        for i in (list_map10):
            map10final_ticker.append(dictTickermap10.get(i))
            map10final_field.append(dictFieldmap10.get(i))
            map10final_source.append(dictSourcemap10.get(i))            
        mapotherfinal_ticker = []
        mapotherfinal_field = []
        mapotherfinal_source = []
        for i in (list_mapother):
            mapotherfinal_ticker.append(dictTickermapother.get(i))
            mapotherfinal_field.append(dictFieldmapother.get(i))
            mapotherfinal_source.append(dictSourcemapother.get(i))
        npk10final_ticker = []
        npk10final_field = []
        npk10final_source = []
        for i in (list_npk10):
            npk10final_ticker.append(dictTickernpk10.get(i))
            npk10final_field.append(dictFieldnpk10.get(i))
            npk10final_source.append(dictSourcenpk10.get(i))              
        npk15final_ticker = []
        npk15final_field = []
        npk15final_source = []
        for i in (list_npk15):
            npk15final_ticker.append(dictTickernpk15.get(i))
            npk15final_field.append(dictFieldnpk15.get(i))
            npk15final_source.append(dictSourcenpk15.get(i))   
        npk16final_ticker = []
        npk16final_field = []
        npk16final_source = []
        for i in (list_npk16):
            npk16final_ticker.append(dictTickernpk16.get(i))
            npk16final_field.append(dictFieldnpk16.get(i))
            npk16final_source.append(dictSourcenpk16.get(i))
        npk17final_ticker = []
        npk17final_field = []
        npk17final_source = []
        for i in (list_npk17):
            npk17final_ticker.append(dictTickernpk17.get(i))
            npk17final_field.append(dictFieldnpk17.get(i))
            npk17final_source.append(dictSourcenpk17.get(i))  
        npk20final_ticker = []
        npk20final_field = []
        npk20final_source = []
        for i in (list_npk20):
            npk20final_ticker.append(dictTickernpk20.get(i))
            npk20final_field.append(dictFieldnpk20.get(i))
            npk20final_source.append(dictSourcenpk20.get(i))
        phosrockfinal_ticker = []
        phosrockfinal_field = []
        phosrockfinal_source = []
        for i in (list_phosrock):
            phosrockfinal_ticker.append(dictTickerphosrock.get(i))
            phosrockfinal_field.append(dictFieldphosrock.get(i))
            phosrockfinal_source.append(dictSourcephosrock.get(i))    
        phosacidfinal_ticker = []
        phosacidfinal_field = []
        phosacidfinal_source = []
        for i in (list_phosacid):
            phosacidfinal_ticker.append(dictTickerphosacid.get(i))
            phosacidfinal_field.append(dictFieldphosacid.get(i))
            phosacidfinal_source.append(dictSourcephosacid.get(i)) 
        sopsspfinal_ticker = []
        sopsspfinal_field = []
        sopsspfinal_source = []
        for i in (list_sopssp):
            sopsspfinal_ticker.append(dictTickersopssp.get(i))
            sopsspfinal_field.append(dictFieldsopssp.get(i))
            sopsspfinal_source.append(dictSourcesopssp.get(i))   
        sspotfinal_ticker = []
        sspotfinal_field = []
        sspotfinal_source = []
        for i in (list_sspot):
            sspotfinal_ticker.append(dictTickersspot.get(i))
            sspotfinal_field.append(dictFieldsspot.get(i))
            sspotfinal_source.append(dictSourcesspot.get(i))  
        stotfinal_ticker = []
        stotfinal_field = []
        stotfinal_source = []
        for i in (list_stot):
            stotfinal_ticker.append(dictTickerstot.get(i))
            stotfinal_field.append(dictFieldstot.get(i))
            stotfinal_source.append(dictSourcestot.get(i))   
        s6mfinal_ticker = []
        s6mfinal_field = []
        s6mfinal_source = []
        for i in (list_s6m):
            s6mfinal_ticker.append(dictTickers6m.get(i))
            s6mfinal_field.append(dictFields6m.get(i))
            s6mfinal_source.append(dictSources6m.get(i))
        sgreatfinal_ticker = []
        sgreatfinal_field = []
        sgreatfinal_source = []
        for i in (list_sgreat):
            sgreatfinal_ticker.append(dictTickersgreat.get(i))
            sgreatfinal_field.append(dictFieldsgreat.get(i))
            sgreatfinal_source.append(dictSourcesgreat.get(i)) 
        sliqfinal_ticker = []
        sliqfinal_field = []
        sliqfinal_source = []
        for i in (list_sliq):
            sliqfinal_ticker.append(dictTickersliq.get(i))
            sliqfinal_field.append(dictFieldsliq.get(i))
            sliqfinal_source.append(dictSourcesliq.get(i))
        smonthfinal_ticker = []
        smonthfinal_field = []
        smonthfinal_source = []
        for i in (list_smonth):
            smonthfinal_ticker.append(dictTickersmonth.get(i))
            smonthfinal_field.append(dictFieldsmonth.get(i))
            smonthfinal_source.append(dictSourcesmonth.get(i)) 
        sqfinal_ticker = []
        sqfinal_field = []
        sqfinal_source = []
        for i in (list_sq):
            sqfinal_ticker.append(dictTickersq.get(i))
            sqfinal_field.append(dictFieldsq.get(i))
            sqfinal_source.append(dictSourcesq.get(i)) 
        saspotfinal_ticker = []
        saspotfinal_field = []
        saspotfinal_source = []
        for i in (list_saspot):
            saspotfinal_ticker.append(dictTickersaspot.get(i))
            saspotfinal_field.append(dictFieldsaspot.get(i))
            saspotfinal_source.append(dictSourcesaspot.get(i))    
        satotfinal_ticker = []
        satotfinal_field = []
        satotfinal_source = []
        for i in (list_satot):
            satotfinal_ticker.append(dictTickersatot.get(i))
            satotfinal_field.append(dictFieldsatot.get(i))
            satotfinal_source.append(dictSourcesatot.get(i)) 
        saconfinal_ticker = []
        saconfinal_field = []
        saconfinal_source = []
        for i in (list_sacon):
            saconfinal_ticker.append(dictTickersacon.get(i))
            saconfinal_field.append(dictFieldsacon.get(i))
            saconfinal_source.append(dictSourcesacon.get(i))   
        tspfinal_ticker = []
        tspfinal_field = []
        tspfinal_source = []
        for i in (list_tsp):
            tspfinal_ticker.append(dictTickertsp.get(i))
            tspfinal_field.append(dictFieldtsp.get(i))
            tspfinal_source.append(dictSourcetsp.get(i))    
        coalefinal_ticker = []
        coalefinal_field = []
        coalefinal_source = []
        for i in (list_coale):
            coalefinal_ticker.append(dictTickercoale.get(i))
            coalefinal_field.append(dictFieldcoale.get(i))
            coalefinal_source.append(dictSourcecoale.get(i))     
        coalarafinal_ticker = []
        coalarafinal_field = []
        coalarafinal_source = []
        for i in (list_coalara):
            coalarafinal_ticker.append(dictTickercoalara.get(i))
            coalarafinal_field.append(dictFieldcoalara.get(i))
            coalarafinal_source.append(dictSourcecoalara.get(i))
        coalrfinal_ticker = []
        coalrfinal_field = []
        coalrfinal_source = []
        for i in (list_coalr):
            coalrfinal_ticker.append(dictTickercoalr.get(i))
            coalrfinal_field.append(dictFieldcoalr.get(i))
            coalrfinal_source.append(dictSourcecoalr.get(i))  
        petrolinvfinal_ticker = []
        petrolinvfinal_field = []
        petrolinvfinal_source = []
        for i in (list_petrolinv):
            petrolinvfinal_ticker.append(dictTickerpetrolinv.get(i))
            petrolinvfinal_field.append(dictFieldpetrolinv.get(i))
            petrolinvfinal_source.append(dictSourcepetrolinv.get(i)) 
        ngnclosefinal_ticker = []
        ngnclosefinal_field = []
        ngnclosefinal_source = []
        for i in (list_ngnclose):
            ngnclosefinal_ticker.append(dictTickerngnclose.get(i))
            ngnclosefinal_field.append(dictFieldngnclose.get(i))
            ngnclosefinal_source.append(dictSourcengnclose.get(i)) 
        ngnhighfinal_ticker = []
        ngnhighfinal_field = []
        ngnhighfinal_source = []
        for i in (list_ngnhigh):
            ngnhighfinal_ticker.append(dictTickerngnhigh.get(i))
            ngnhighfinal_field.append(dictFieldngnhigh.get(i))
            ngnhighfinal_source.append(dictSourcengnhigh.get(i))
        ngnlowfinal_ticker = []
        ngnlowfinal_field = []
        ngnlowfinal_source = []
        for i in (list_ngnlow):
            ngnlowfinal_ticker.append(dictTickerngnlow.get(i))
            ngnlowfinal_field.append(dictFieldngnlow.get(i))
            ngnlowfinal_source.append(dictSourcengnlow.get(i)) 
        ngnopenfinal_ticker = []
        ngnopenfinal_field = []
        ngnopenfinal_source = []
        for i in (list_ngnopen):
            ngnopenfinal_ticker.append(dictTickerngnopen.get(i))
            ngnopenfinal_field.append(dictFieldngnopen.get(i))
            ngnopenfinal_source.append(dictSourcengnopen.get(i)) 
        ngnvolfinal_ticker = []
        ngnvolfinal_field = []
        ngnvolfinal_source = []
        for i in (list_ngnvol):
            ngnvolfinal_ticker.append(dictTickerngnvol.get(i))
            ngnvolfinal_field.append(dictFieldngnvol.get(i))
            ngnvolfinal_source.append(dictSourcengnvol.get(i))    
        ngnbpfinal_ticker = []
        ngnbpfinal_field = []
        ngnbpfinal_source = []
        for i in (list_ngnbp):
            ngnbpfinal_ticker.append(dictTickerngnbp.get(i))
            ngnbpfinal_field.append(dictFieldngnbp.get(i))
            ngnbpfinal_source.append(dictSourcengnbp.get(i))     
        wticlosefinal_ticker = []
        wticlosefinal_field = []
        wticlosefinal_source = []
        for i in (list_wticlose):
            wticlosefinal_ticker.append(dictTickerwticlose.get(i))
            wticlosefinal_field.append(dictFieldwticlose.get(i))
            wticlosefinal_source.append(dictSourcewticlose.get(i)) 
        wtihighfinal_ticker = []
        wtihighfinal_field = []
        wtihighfinal_source = []
        for i in (list_wtihigh):
            wtihighfinal_ticker.append(dictTickerwtihigh.get(i))
            wtihighfinal_field.append(dictFieldwtihigh.get(i))
            wtihighfinal_source.append(dictSourcewtihigh.get(i))
        wtilowfinal_ticker = []
        wtilowfinal_field = []
        wtilowfinal_source = []
        for i in (list_wtilow):
            wtilowfinal_ticker.append(dictTickerwtilow.get(i))
            wtilowfinal_field.append(dictFieldwtilow.get(i))
            wtilowfinal_source.append(dictSourcewtilow.get(i)) 
        wtiopenfinal_ticker = []
        wtiopenfinal_field = []
        wtiopenfinal_source = []
        for i in (list_wtiopen):
            wtiopenfinal_ticker.append(dictTickerwtiopen.get(i))
            wtiopenfinal_field.append(dictFieldwtiopen.get(i))
            wtiopenfinal_source.append(dictSourcewtiopen.get(i)) 
        wtivolfinal_ticker = []
        wtivolfinal_field = []
        wtivolfinal_source = []
        for i in (list_wtivol):
            wtivolfinal_ticker.append(dictTickerwtivol.get(i))
            wtivolfinal_field.append(dictFieldwtivol.get(i))
            wtivolfinal_source.append(dictSourcewtivol.get(i))   
        brentclosefinal_ticker = []
        brentclosefinal_field = []
        brentclosefinal_source = []
        for i in (list_brentclose):
            brentclosefinal_ticker.append(dictTickerbrentclose.get(i))
            brentclosefinal_field.append(dictFieldbrentclose.get(i))
            brentclosefinal_source.append(dictSourcebrentclose.get(i)) 
        brenthighfinal_ticker = []
        brenthighfinal_field = []
        brenthighfinal_source = []
        for i in (list_brenthigh):
            brenthighfinal_ticker.append(dictTickerbrenthigh.get(i))
            brenthighfinal_field.append(dictFieldbrenthigh.get(i))
            brenthighfinal_source.append(dictSourcebrenthigh.get(i))
        brentlowfinal_ticker = []
        brentlowfinal_field = []
        brentlowfinal_source = []
        for i in (list_brentlow):
            brentlowfinal_ticker.append(dictTickerbrentlow.get(i))
            brentlowfinal_field.append(dictFieldbrentlow.get(i))
            brentlowfinal_source.append(dictSourcebrentlow.get(i)) 
        brentopenfinal_ticker = []
        brentopenfinal_field = []
        brentopenfinal_source = []
        for i in (list_brentopen):
            brentopenfinal_ticker.append(dictTickerbrentopen.get(i))
            brentopenfinal_field.append(dictFieldbrentopen.get(i))
            brentopenfinal_source.append(dictSourcebrentopen.get(i)) 
        brentvolfinal_ticker = []
        brentvolfinal_field = []
        brentvolfinal_source = []
        for i in (list_brentvol):
            brentvolfinal_ticker.append(dictTickerbrentvol.get(i))
            brentvolfinal_field.append(dictFieldbrentvol.get(i))
            brentvolfinal_source.append(dictSourcebrentvol.get(i)) 
        hoclosefinal_ticker = []
        hoclosefinal_field = []
        hoclosefinal_source = []
        for i in (list_hoclose):
            hoclosefinal_ticker.append(dictTickerhoclose.get(i))
            hoclosefinal_field.append(dictFieldhoclose.get(i))
            hoclosefinal_source.append(dictSourcehoclose.get(i)) 
        hohighfinal_ticker = []
        hohighfinal_field = []
        hohighfinal_source = []
        for i in (list_hohigh):
            hohighfinal_ticker.append(dictTickerhohigh.get(i))
            hohighfinal_field.append(dictFieldhohigh.get(i))
            hohighfinal_source.append(dictSourcehohigh.get(i))
        holowfinal_ticker = []
        holowfinal_field = []
        holowfinal_source = []
        for i in (list_holow):
            holowfinal_ticker.append(dictTickerholow.get(i))
            holowfinal_field.append(dictFieldholow.get(i))
            holowfinal_source.append(dictSourceholow.get(i)) 
        hoopenfinal_ticker = []
        hoopenfinal_field = []
        hoopenfinal_source = []
        for i in (list_hoopen):
            hoopenfinal_ticker.append(dictTickerhoopen.get(i))
            hoopenfinal_field.append(dictFieldhoopen.get(i))
            hoopenfinal_source.append(dictSourcehoopen.get(i)) 
        hovolfinal_ticker = []
        hovolfinal_field = []
        hovolfinal_source = []
        for i in (list_hovol):
            hovolfinal_ticker.append(dictTickerhovol.get(i))
            hovolfinal_field.append(dictFieldhovol.get(i))
            hovolfinal_source.append(dictSourcehovol.get(i)) 
        rbobclosefinal_ticker = []
        rbobclosefinal_field = []
        rbobclosefinal_source = []
        for i in (list_rbobclose):
            rbobclosefinal_ticker.append(dictTickerrbobclose.get(i))
            rbobclosefinal_field.append(dictFieldrbobclose.get(i))
            rbobclosefinal_source.append(dictSourcerbobclose.get(i)) 
        rbobhighfinal_ticker = []
        rbobhighfinal_field = []
        rbobhighfinal_source = []
        for i in (list_rbobhigh):
            rbobhighfinal_ticker.append(dictTickerrbobhigh.get(i))
            rbobhighfinal_field.append(dictFieldrbobhigh.get(i))
            rbobhighfinal_source.append(dictSourcerbobhigh.get(i))
        rboblowfinal_ticker = []
        rboblowfinal_field = []
        rboblowfinal_source = []
        for i in (list_rboblow):
            rboblowfinal_ticker.append(dictTickerrboblow.get(i))
            rboblowfinal_field.append(dictFieldrboblow.get(i))
            rboblowfinal_source.append(dictSourcerboblow.get(i)) 
        rbobopenfinal_ticker = []
        rbobopenfinal_field = []
        rbobopenfinal_source = []
        for i in (list_rbobopen):
            rbobopenfinal_ticker.append(dictTickerrbobopen.get(i))
            rbobopenfinal_field.append(dictFieldrbobopen.get(i))
            rbobopenfinal_source.append(dictSourcerbobopen.get(i)) 
        rbobvolfinal_ticker = []
        rbobvolfinal_field = []
        rbobvolfinal_source = []
        for i in (list_rbobvol):
            rbobvolfinal_ticker.append(dictTickerrbobvol.get(i))
            rbobvolfinal_field.append(dictFieldrbobvol.get(i))
            rbobvolfinal_source.append(dictSourcerbobvol.get(i)) 
        alclosefinal_ticker = []
        alclosefinal_field = []
        alclosefinal_source = []
        for i in (list_alclose):
            alclosefinal_ticker.append(dictTickeralclose.get(i))
            alclosefinal_field.append(dictFieldalclose.get(i))
            alclosefinal_source.append(dictSourcealclose.get(i)) 
        alhighfinal_ticker = []
        alhighfinal_field = []
        alhighfinal_source = []
        for i in (list_alhigh):
            alhighfinal_ticker.append(dictTickeralhigh.get(i))
            alhighfinal_field.append(dictFieldalhigh.get(i))
            alhighfinal_source.append(dictSourcealhigh.get(i))
        allowfinal_ticker = []
        allowfinal_field = []
        allowfinal_source = []
        for i in (list_allow):
            allowfinal_ticker.append(dictTickerallow.get(i))
            allowfinal_field.append(dictFieldallow.get(i))
            allowfinal_source.append(dictSourceallow.get(i)) 
        alopenfinal_ticker = []
        alopenfinal_field = []
        alopenfinal_source = []
        for i in (list_alopen):
            alopenfinal_ticker.append(dictTickeralopen.get(i))
            alopenfinal_field.append(dictFieldalopen.get(i))
            alopenfinal_source.append(dictSourcealopen.get(i)) 
        alvolfinal_ticker = []
        alvolfinal_field = []
        alvolfinal_source = []
        for i in (list_alvol):
            alvolfinal_ticker.append(dictTickeralvol.get(i))
            alvolfinal_field.append(dictFieldalvol.get(i))
            alvolfinal_source.append(dictSourcealvol.get(i))  
        cuclosefinal_ticker = []
        cuclosefinal_field = []
        cuclosefinal_source = []
        for i in (list_cuclose):
            cuclosefinal_ticker.append(dictTickercuclose.get(i))
            cuclosefinal_field.append(dictFieldcuclose.get(i))
            cuclosefinal_source.append(dictSourcecuclose.get(i)) 
        cuhighfinal_ticker = []
        cuhighfinal_field = []
        cuhighfinal_source = []
        for i in (list_cuhigh):
            cuhighfinal_ticker.append(dictTickercuhigh.get(i))
            cuhighfinal_field.append(dictFieldcuhigh.get(i))
            cuhighfinal_source.append(dictSourcecuhigh.get(i))
        culowfinal_ticker = []
        culowfinal_field = []
        culowfinal_source = []
        for i in (list_culow):
            culowfinal_ticker.append(dictTickerculow.get(i))
            culowfinal_field.append(dictFieldculow.get(i))
            culowfinal_source.append(dictSourceculow.get(i)) 
        cuopenfinal_ticker = []
        cuopenfinal_field = []
        cuopenfinal_source = []
        for i in (list_cuopen):
            cuopenfinal_ticker.append(dictTickercuopen.get(i))
            cuopenfinal_field.append(dictFieldcuopen.get(i))
            cuopenfinal_source.append(dictSourcecuopen.get(i)) 
        cuvolfinal_ticker = []
        cuvolfinal_field = []
        cuvolfinal_source = []
        for i in (list_cuvol):
            cuvolfinal_ticker.append(dictTickercuvol.get(i))
            cuvolfinal_field.append(dictFieldcuvol.get(i))
            cuvolfinal_source.append(dictSourcecuvol.get(i))  
        auclosefinal_ticker = []
        auclosefinal_field = []
        auclosefinal_source = []
        for i in (list_auclose):
            auclosefinal_ticker.append(dictTickerauclose.get(i))
            auclosefinal_field.append(dictFieldauclose.get(i))
            auclosefinal_source.append(dictSourceauclose.get(i)) 
        auhighfinal_ticker = []
        auhighfinal_field = []
        auhighfinal_source = []
        for i in (list_auhigh):
            auhighfinal_ticker.append(dictTickerauhigh.get(i))
            auhighfinal_field.append(dictFieldauhigh.get(i))
            auhighfinal_source.append(dictSourceauhigh.get(i))
        aulowfinal_ticker = []
        aulowfinal_field = []
        aulowfinal_source = []
        for i in (list_aulow):
            aulowfinal_ticker.append(dictTickeraulow.get(i))
            aulowfinal_field.append(dictFieldaulow.get(i))
            aulowfinal_source.append(dictSourceaulow.get(i)) 
        auopenfinal_ticker = []
        auopenfinal_field = []
        auopenfinal_source = []
        for i in (list_auopen):
            auopenfinal_ticker.append(dictTickerauopen.get(i))
            auopenfinal_field.append(dictFieldauopen.get(i))
            auopenfinal_source.append(dictSourceauopen.get(i)) 
        auvolfinal_ticker = []
        auvolfinal_field = []
        auvolfinal_source = []
        for i in (list_auvol):
            auvolfinal_ticker.append(dictTickerauvol.get(i))
            auvolfinal_field.append(dictFieldauvol.get(i))
            auvolfinal_source.append(dictSourceauvol.get(i))             
        feclosefinal_ticker = []
        feclosefinal_field = []
        feclosefinal_source = []
        for i in (list_feclose):
            feclosefinal_ticker.append(dictTickerfeclose.get(i))
            feclosefinal_field.append(dictFieldfeclose.get(i))
            feclosefinal_source.append(dictSourcefeclose.get(i)) 
        fehighfinal_ticker = []
        fehighfinal_field = []
        fehighfinal_source = []
        for i in (list_fehigh):
            fehighfinal_ticker.append(dictTickerfehigh.get(i))
            fehighfinal_field.append(dictFieldfehigh.get(i))
            fehighfinal_source.append(dictSourcefehigh.get(i))
        felowfinal_ticker = []
        felowfinal_field = []
        felowfinal_source = []
        for i in (list_felow):
            felowfinal_ticker.append(dictTickerfelow.get(i))
            felowfinal_field.append(dictFieldfelow.get(i))
            felowfinal_source.append(dictSourcefelow.get(i)) 
        feopenfinal_ticker = []
        feopenfinal_field = []
        feopenfinal_source = []
        for i in (list_feopen):
            feopenfinal_ticker.append(dictTickerfeopen.get(i))
            feopenfinal_field.append(dictFieldfeopen.get(i))
            feopenfinal_source.append(dictSourcefeopen.get(i)) 
        fevolfinal_ticker = []
        fevolfinal_field = []
        fevolfinal_source = []
        for i in (list_fevol):
            fevolfinal_ticker.append(dictTickerfevol.get(i))
            fevolfinal_field.append(dictFieldfevol.get(i))
            fevolfinal_source.append(dictSourcefevol.get(i))  
        pbclosefinal_ticker = []
        pbclosefinal_field = []
        pbclosefinal_source = []
        for i in (list_pbclose):
            pbclosefinal_ticker.append(dictTickerpbclose.get(i))
            pbclosefinal_field.append(dictFieldpbclose.get(i))
            pbclosefinal_source.append(dictSourcepbclose.get(i)) 
        pbhighfinal_ticker = []
        pbhighfinal_field = []
        pbhighfinal_source = []
        for i in (list_pbhigh):
            pbhighfinal_ticker.append(dictTickerpbhigh.get(i))
            pbhighfinal_field.append(dictFieldpbhigh.get(i))
            pbhighfinal_source.append(dictSourcepbhigh.get(i))
        pblowfinal_ticker = []
        pblowfinal_field = []
        pblowfinal_source = []
        for i in (list_pblow):
            pblowfinal_ticker.append(dictTickerpblow.get(i))
            pblowfinal_field.append(dictFieldpblow.get(i))
            pblowfinal_source.append(dictSourcepblow.get(i)) 
        pbopenfinal_ticker = []
        pbopenfinal_field = []
        pbopenfinal_source = []
        for i in (list_pbopen):
            pbopenfinal_ticker.append(dictTickerpbopen.get(i))
            pbopenfinal_field.append(dictFieldpbopen.get(i))
            pbopenfinal_source.append(dictSourcepbopen.get(i)) 
        pbvolfinal_ticker = []
        pbvolfinal_field = []
        pbvolfinal_source = []
        for i in (list_pbvol):
            pbvolfinal_ticker.append(dictTickerpbvol.get(i))
            pbvolfinal_field.append(dictFieldpbvol.get(i))
            pbvolfinal_source.append(dictSourcepbvol.get(i))
        niclosefinal_ticker = []
        niclosefinal_field = []
        niclosefinal_source = []
        for i in (list_niclose):
            niclosefinal_ticker.append(dictTickerniclose.get(i))
            niclosefinal_field.append(dictFieldniclose.get(i))
            niclosefinal_source.append(dictSourceniclose.get(i)) 
        nihighfinal_ticker = []
        nihighfinal_field = []
        nihighfinal_source = []
        for i in (list_nihigh):
            nihighfinal_ticker.append(dictTickernihigh.get(i))
            nihighfinal_field.append(dictFieldnihigh.get(i))
            nihighfinal_source.append(dictSourcenihigh.get(i))
        nilowfinal_ticker = []
        nilowfinal_field = []
        nilowfinal_source = []
        for i in (list_nilow):
            nilowfinal_ticker.append(dictTickernilow.get(i))
            nilowfinal_field.append(dictFieldnilow.get(i))
            nilowfinal_source.append(dictSourcenilow.get(i)) 
        niopenfinal_ticker = []
        niopenfinal_field = []
        niopenfinal_source = []
        for i in (list_niopen):
            niopenfinal_ticker.append(dictTickerniopen.get(i))
            niopenfinal_field.append(dictFieldniopen.get(i))
            niopenfinal_source.append(dictSourceniopen.get(i)) 
        nivolfinal_ticker = []
        nivolfinal_field = []
        nivolfinal_source = []
        for i in (list_nivol):
            nivolfinal_ticker.append(dictTickernivol.get(i))
            nivolfinal_field.append(dictFieldnivol.get(i))
            nivolfinal_source.append(dictSourcenivol.get(i)) 
        paclosefinal_ticker = []
        paclosefinal_field = []
        paclosefinal_source = []
        for i in (list_paclose):
            paclosefinal_ticker.append(dictTickerpaclose.get(i))
            paclosefinal_field.append(dictFieldpaclose.get(i))
            paclosefinal_source.append(dictSourcepaclose.get(i)) 
        pahighfinal_ticker = []
        pahighfinal_field = []
        pahighfinal_source = []
        for i in (list_pahigh):
            pahighfinal_ticker.append(dictTickerpahigh.get(i))
            pahighfinal_field.append(dictFieldpahigh.get(i))
            pahighfinal_source.append(dictSourcepahigh.get(i))
        palowfinal_ticker = []
        palowfinal_field = []
        palowfinal_source = []
        for i in (list_palow):
            palowfinal_ticker.append(dictTickerpalow.get(i))
            palowfinal_field.append(dictFieldpalow.get(i))
            palowfinal_source.append(dictSourcepalow.get(i)) 
        paopenfinal_ticker = []
        paopenfinal_field = []
        paopenfinal_source = []
        for i in (list_paopen):
            paopenfinal_ticker.append(dictTickerpaopen.get(i))
            paopenfinal_field.append(dictFieldpaopen.get(i))
            paopenfinal_source.append(dictSourcepaopen.get(i)) 
        pavolfinal_ticker = []
        pavolfinal_field = []
        pavolfinal_source = []
        for i in (list_pavol):
            pavolfinal_ticker.append(dictTickerpavol.get(i))
            pavolfinal_field.append(dictFieldpavol.get(i))
            pavolfinal_source.append(dictSourcepavol.get(i)) 
        plclosefinal_ticker = []
        plclosefinal_field = []
        plclosefinal_source = []
        for i in (list_plclose):
            plclosefinal_ticker.append(dictTickerplclose.get(i))
            plclosefinal_field.append(dictFieldplclose.get(i))
            plclosefinal_source.append(dictSourceplclose.get(i)) 
        plhighfinal_ticker = []
        plhighfinal_field = []
        plhighfinal_source = []
        for i in (list_plhigh):
            plhighfinal_ticker.append(dictTickerplhigh.get(i))
            plhighfinal_field.append(dictFieldplhigh.get(i))
            plhighfinal_source.append(dictSourceplhigh.get(i))
        pllowfinal_ticker = []
        pllowfinal_field = []
        pllowfinal_source = []
        for i in (list_pllow):
            pllowfinal_ticker.append(dictTickerpllow.get(i))
            pllowfinal_field.append(dictFieldpllow.get(i))
            pllowfinal_source.append(dictSourcepllow.get(i)) 
        plopenfinal_ticker = []
        plopenfinal_field = []
        plopenfinal_source = []
        for i in (list_plopen):
            plopenfinal_ticker.append(dictTickerplopen.get(i))
            plopenfinal_field.append(dictFieldplopen.get(i))
            plopenfinal_source.append(dictSourceplopen.get(i)) 
        plvolfinal_ticker = []
        plvolfinal_field = []
        plvolfinal_source = []
        for i in (list_plvol):
            plvolfinal_ticker.append(dictTickerplvol.get(i))
            plvolfinal_field.append(dictFieldplvol.get(i))
            plvolfinal_source.append(dictSourceplvol.get(i)) 
        agclosefinal_ticker = []
        agclosefinal_field = []
        agclosefinal_source = []
        for i in (list_agclose):
            agclosefinal_ticker.append(dictTickeragclose.get(i))
            agclosefinal_field.append(dictFieldagclose.get(i))
            agclosefinal_source.append(dictSourceagclose.get(i)) 
        aghighfinal_ticker = []
        aghighfinal_field = []
        aghighfinal_source = []
        for i in (list_aghigh):
            aghighfinal_ticker.append(dictTickeraghigh.get(i))
            aghighfinal_field.append(dictFieldaghigh.get(i))
            aghighfinal_source.append(dictSourceaghigh.get(i))
        aglowfinal_ticker = []
        aglowfinal_field = []
        aglowfinal_source = []
        for i in (list_aglow):
            aglowfinal_ticker.append(dictTickeraglow.get(i))
            aglowfinal_field.append(dictFieldaglow.get(i))
            aglowfinal_source.append(dictSourceaglow.get(i)) 
        agopenfinal_ticker = []
        agopenfinal_field = []
        agopenfinal_source = []
        for i in (list_agopen):
            agopenfinal_ticker.append(dictTickeragopen.get(i))
            agopenfinal_field.append(dictFieldagopen.get(i))
            agopenfinal_source.append(dictSourceagopen.get(i)) 
        agvolfinal_ticker = []
        agvolfinal_field = []
        agvolfinal_source = []
        for i in (list_agvol):
            agvolfinal_ticker.append(dictTickeragvol.get(i))
            agvolfinal_field.append(dictFieldagvol.get(i))
            agvolfinal_source.append(dictSourceagvol.get(i))  
        stclosefinal_ticker = []
        stclosefinal_field = []
        stclosefinal_source = []
        for i in (list_stclose):
            stclosefinal_ticker.append(dictTickerstclose.get(i))
            stclosefinal_field.append(dictFieldstclose.get(i))
            stclosefinal_source.append(dictSourcestclose.get(i)) 
        sthighfinal_ticker = []
        sthighfinal_field = []
        sthighfinal_source = []
        for i in (list_sthigh):
            sthighfinal_ticker.append(dictTickersthigh.get(i))
            sthighfinal_field.append(dictFieldsthigh.get(i))
            sthighfinal_source.append(dictSourcesthigh.get(i))
        stlowfinal_ticker = []
        stlowfinal_field = []
        stlowfinal_source = []
        for i in (list_stlow):
            stlowfinal_ticker.append(dictTickerstlow.get(i))
            stlowfinal_field.append(dictFieldstlow.get(i))
            stlowfinal_source.append(dictSourcestlow.get(i)) 
        stopenfinal_ticker = []
        stopenfinal_field = []
        stopenfinal_source = []
        for i in (list_stopen):
            stopenfinal_ticker.append(dictTickerstopen.get(i))
            stopenfinal_field.append(dictFieldstopen.get(i))
            stopenfinal_source.append(dictSourcestopen.get(i)) 
        stvolfinal_ticker = []
        stvolfinal_field = []
        stvolfinal_source = []
        for i in (list_stvol):
            stvolfinal_ticker.append(dictTickerstvol.get(i))
            stvolfinal_field.append(dictFieldstvol.get(i))
            stvolfinal_source.append(dictSourcestvol.get(i)) 
        tnclosefinal_ticker = []
        tnclosefinal_field = []
        tnclosefinal_source = []
        for i in (list_tnclose):
            tnclosefinal_ticker.append(dictTickertnclose.get(i))
            tnclosefinal_field.append(dictFieldtnclose.get(i))
            tnclosefinal_source.append(dictSourcetnclose.get(i)) 
        tnhighfinal_ticker = []
        tnhighfinal_field = []
        tnhighfinal_source = []
        for i in (list_tnhigh):
            tnhighfinal_ticker.append(dictTickertnhigh.get(i))
            tnhighfinal_field.append(dictFieldtnhigh.get(i))
            tnhighfinal_source.append(dictSourcetnhigh.get(i))
        tnlowfinal_ticker = []
        tnlowfinal_field = []
        tnlowfinal_source = []
        for i in (list_tnlow):
            tnlowfinal_ticker.append(dictTickertnlow.get(i))
            tnlowfinal_field.append(dictFieldtnlow.get(i))
            tnlowfinal_source.append(dictSourcetnlow.get(i)) 
        tnopenfinal_ticker = []
        tnopenfinal_field = []
        tnopenfinal_source = []
        for i in (list_tnopen):
            tnopenfinal_ticker.append(dictTickertnopen.get(i))
            tnopenfinal_field.append(dictFieldtnopen.get(i))
            tnopenfinal_source.append(dictSourcetnopen.get(i)) 
        tnvolfinal_ticker = []
        tnvolfinal_field = []
        tnvolfinal_source = []
        for i in (list_tnvol):
            tnvolfinal_ticker.append(dictTickertnvol.get(i))
            tnvolfinal_field.append(dictFieldtnvol.get(i))
            tnvolfinal_source.append(dictSourcetnvol.get(i))  
        urclosefinal_ticker = []
        urclosefinal_field = []
        urclosefinal_source = []
        for i in (list_urclose):
            urclosefinal_ticker.append(dictTickerurclose.get(i))
            urclosefinal_field.append(dictFieldurclose.get(i))
            urclosefinal_source.append(dictSourceurclose.get(i)) 
        urhighfinal_ticker = []
        urhighfinal_field = []
        urhighfinal_source = []
        for i in (list_urhigh):
            urhighfinal_ticker.append(dictTickerurhigh.get(i))
            urhighfinal_field.append(dictFieldurhigh.get(i))
            urhighfinal_source.append(dictSourceurhigh.get(i))
        urlowfinal_ticker = []
        urlowfinal_field = []
        urlowfinal_source = []
        for i in (list_urlow):
            urlowfinal_ticker.append(dictTickerurlow.get(i))
            urlowfinal_field.append(dictFieldurlow.get(i))
            urlowfinal_source.append(dictSourceurlow.get(i)) 
        uropenfinal_ticker = []
        uropenfinal_field = []
        uropenfinal_source = []
        for i in (list_uropen):
            uropenfinal_ticker.append(dictTickeruropen.get(i))
            uropenfinal_field.append(dictFielduropen.get(i))
            uropenfinal_source.append(dictSourceuropen.get(i)) 
        urvolfinal_ticker = []
        urvolfinal_field = []
        urvolfinal_source = []
        for i in (list_urvol):
            urvolfinal_ticker.append(dictTickerurvol.get(i))
            urvolfinal_field.append(dictFieldurvol.get(i))
            urvolfinal_source.append(dictSourceurvol.get(i))
        znclosefinal_ticker = []
        znclosefinal_field = []
        znclosefinal_source = []
        for i in (list_znclose):
            znclosefinal_ticker.append(dictTickerznclose.get(i))
            znclosefinal_field.append(dictFieldznclose.get(i))
            znclosefinal_source.append(dictSourceznclose.get(i)) 
        znhighfinal_ticker = []
        znhighfinal_field = []
        znhighfinal_source = []
        for i in (list_znhigh):
            znhighfinal_ticker.append(dictTickerznhigh.get(i))
            znhighfinal_field.append(dictFieldznhigh.get(i))
            znhighfinal_source.append(dictSourceznhigh.get(i))
        znlowfinal_ticker = []
        znlowfinal_field = []
        znlowfinal_source = []
        for i in (list_znlow):
            znlowfinal_ticker.append(dictTickerznlow.get(i))
            znlowfinal_field.append(dictFieldznlow.get(i))
            znlowfinal_source.append(dictSourceznlow.get(i)) 
        znopenfinal_ticker = []
        znopenfinal_field = []
        znopenfinal_source = []
        for i in (list_znopen):
            znopenfinal_ticker.append(dictTickerznopen.get(i))
            znopenfinal_field.append(dictFieldznopen.get(i))
            znopenfinal_source.append(dictSourceznopen.get(i)) 
        znvolfinal_ticker = []
        znvolfinal_field = []
        znvolfinal_source = []
        for i in (list_znvol):
            znvolfinal_ticker.append(dictTickerznvol.get(i))
            znvolfinal_field.append(dictFieldznvol.get(i))
            znvolfinal_source.append(dictSourceznvol.get(i)) 
        cornclosefinal_ticker = []
        cornclosefinal_field = []
        cornclosefinal_source = []
        for i in (list_cornclose):
            cornclosefinal_ticker.append(dictTickercornclose.get(i))
            cornclosefinal_field.append(dictFieldcornclose.get(i))
            cornclosefinal_source.append(dictSourcecornclose.get(i)) 
        cornhighfinal_ticker = []
        cornhighfinal_field = []
        cornhighfinal_source = []
        for i in (list_cornhigh):
            cornhighfinal_ticker.append(dictTickercornhigh.get(i))
            cornhighfinal_field.append(dictFieldcornhigh.get(i))
            cornhighfinal_source.append(dictSourcecornhigh.get(i))
        cornlowfinal_ticker = []
        cornlowfinal_field = []
        cornlowfinal_source = []
        for i in (list_cornlow):
            cornlowfinal_ticker.append(dictTickercornlow.get(i))
            cornlowfinal_field.append(dictFieldcornlow.get(i))
            cornlowfinal_source.append(dictSourcecornlow.get(i)) 
        cornopenfinal_ticker = []
        cornopenfinal_field = []
        cornopenfinal_source = []
        for i in (list_cornopen):
            cornopenfinal_ticker.append(dictTickercornopen.get(i))
            cornopenfinal_field.append(dictFieldcornopen.get(i))
            cornopenfinal_source.append(dictSourcecornopen.get(i)) 
        cornvolfinal_ticker = []
        cornvolfinal_field = []
        cornvolfinal_source = []
        for i in (list_cornvol):
            cornvolfinal_ticker.append(dictTickercornvol.get(i))
            cornvolfinal_field.append(dictFieldcornvol.get(i))
            cornvolfinal_source.append(dictSourcecornvol.get(i)) 
        wheatclosefinal_ticker = []
        wheatclosefinal_field = []
        wheatclosefinal_source = []
        for i in (list_wheatclose):
            wheatclosefinal_ticker.append(dictTickerwheatclose.get(i))
            wheatclosefinal_field.append(dictFieldwheatclose.get(i))
            wheatclosefinal_source.append(dictSourcewheatclose.get(i)) 
        wheathighfinal_ticker = []
        wheathighfinal_field = []
        wheathighfinal_source = []
        for i in (list_wheathigh):
            wheathighfinal_ticker.append(dictTickerwheathigh.get(i))
            wheathighfinal_field.append(dictFieldwheathigh.get(i))
            wheathighfinal_source.append(dictSourcewheathigh.get(i))
        wheatlowfinal_ticker = []
        wheatlowfinal_field = []
        wheatlowfinal_source = []
        for i in (list_wheatlow):
            wheatlowfinal_ticker.append(dictTickerwheatlow.get(i))
            wheatlowfinal_field.append(dictFieldwheatlow.get(i))
            wheatlowfinal_source.append(dictSourcewheatlow.get(i)) 
        wheatopenfinal_ticker = []
        wheatopenfinal_field = []
        wheatopenfinal_source = []
        for i in (list_wheatopen):
            wheatopenfinal_ticker.append(dictTickerwheatopen.get(i))
            wheatopenfinal_field.append(dictFieldwheatopen.get(i))
            wheatopenfinal_source.append(dictSourcewheatopen.get(i)) 
        wheatvolfinal_ticker = []
        wheatvolfinal_field = []
        wheatvolfinal_source = []
        for i in (list_wheatvol):
            wheatvolfinal_ticker.append(dictTickerwheatvol.get(i))
            wheatvolfinal_field.append(dictFieldwheatvol.get(i))
            wheatvolfinal_source.append(dictSourcewheatvol.get(i))
        soyclosefinal_ticker = []
        soyclosefinal_field = []
        soyclosefinal_source = []
        for i in (list_soyclose):
            soyclosefinal_ticker.append(dictTickersoyclose.get(i))
            soyclosefinal_field.append(dictFieldsoyclose.get(i))
            soyclosefinal_source.append(dictSourcesoyclose.get(i)) 
        soyhighfinal_ticker = []
        soyhighfinal_field = []
        soyhighfinal_source = []
        for i in (list_soyhigh):
            soyhighfinal_ticker.append(dictTickersoyhigh.get(i))
            soyhighfinal_field.append(dictFieldsoyhigh.get(i))
            soyhighfinal_source.append(dictSourcesoyhigh.get(i))
        soylowfinal_ticker = []
        soylowfinal_field = []
        soylowfinal_source = []
        for i in (list_soylow):
            soylowfinal_ticker.append(dictTickersoylow.get(i))
            soylowfinal_field.append(dictFieldsoylow.get(i))
            soylowfinal_source.append(dictSourcesoylow.get(i)) 
        soyopenfinal_ticker = []
        soyopenfinal_field = []
        soyopenfinal_source = []
        for i in (list_soyopen):
            soyopenfinal_ticker.append(dictTickersoyopen.get(i))
            soyopenfinal_field.append(dictFieldsoyopen.get(i))
            soyopenfinal_source.append(dictSourcesoyopen.get(i)) 
        soyvolfinal_ticker = []
        soyvolfinal_field = []
        soyvolfinal_source = []
        for i in (list_soyvol):
            soyvolfinal_ticker.append(dictTickersoyvol.get(i))
            soyvolfinal_field.append(dictFieldsoyvol.get(i))
            soyvolfinal_source.append(dictSourcesoyvol.get(i))
        soclosefinal_ticker = []
        soclosefinal_field = []
        soclosefinal_source = []
        for i in (list_soclose):
            soclosefinal_ticker.append(dictTickersoclose.get(i))
            soclosefinal_field.append(dictFieldsoclose.get(i))
            soclosefinal_source.append(dictSourcesoclose.get(i)) 
        sohighfinal_ticker = []
        sohighfinal_field = []
        sohighfinal_source = []
        for i in (list_sohigh):
            sohighfinal_ticker.append(dictTickersohigh.get(i))
            sohighfinal_field.append(dictFieldsohigh.get(i))
            sohighfinal_source.append(dictSourcesohigh.get(i))
        solowfinal_ticker = []
        solowfinal_field = []
        solowfinal_source = []
        for i in (list_solow):
            solowfinal_ticker.append(dictTickersolow.get(i))
            solowfinal_field.append(dictFieldsolow.get(i))
            solowfinal_source.append(dictSourcesolow.get(i)) 
        soopenfinal_ticker = []
        soopenfinal_field = []
        soopenfinal_source = []
        for i in (list_soopen):
            soopenfinal_ticker.append(dictTickersoopen.get(i))
            soopenfinal_field.append(dictFieldsoopen.get(i))
            soopenfinal_source.append(dictSourcesoopen.get(i)) 
        sovolfinal_ticker = []
        sovolfinal_field = []
        sovolfinal_source = []
        for i in (list_sovol):
            sovolfinal_ticker.append(dictTickersovol.get(i))
            sovolfinal_field.append(dictFieldsovol.get(i))
            sovolfinal_source.append(dictSourcesovol.get(i))  
        cotclosefinal_ticker = []
        cotclosefinal_field = []
        cotclosefinal_source = []
        for i in (list_cotclose):
            cotclosefinal_ticker.append(dictTickercotclose.get(i))
            cotclosefinal_field.append(dictFieldcotclose.get(i))
            cotclosefinal_source.append(dictSourcecotclose.get(i)) 
        cothighfinal_ticker = []
        cothighfinal_field = []
        cothighfinal_source = []
        for i in (list_cothigh):
            cothighfinal_ticker.append(dictTickercothigh.get(i))
            cothighfinal_field.append(dictFieldcothigh.get(i))
            cothighfinal_source.append(dictSourcecothigh.get(i))
        cotlowfinal_ticker = []
        cotlowfinal_field = []
        cotlowfinal_source = []
        for i in (list_cotlow):
            cotlowfinal_ticker.append(dictTickercotlow.get(i))
            cotlowfinal_field.append(dictFieldcotlow.get(i))
            cotlowfinal_source.append(dictSourcecotlow.get(i)) 
        cotopenfinal_ticker = []
        cotopenfinal_field = []
        cotopenfinal_source = []
        for i in (list_cotopen):
            cotopenfinal_ticker.append(dictTickercotopen.get(i))
            cotopenfinal_field.append(dictFieldcotopen.get(i))
            cotopenfinal_source.append(dictSourcecotopen.get(i)) 
        cotvolfinal_ticker = []
        cotvolfinal_field = []
        cotvolfinal_source = []
        for i in (list_cotvol):
            cotvolfinal_ticker.append(dictTickercotvol.get(i))
            cotvolfinal_field.append(dictFieldcotvol.get(i))
            cotvolfinal_source.append(dictSourcecotvol.get(i))
        sbclosefinal_ticker = []
        sbclosefinal_field = []
        sbclosefinal_source = []
        for i in (list_sbclose):
            sbclosefinal_ticker.append(dictTickersbclose.get(i))
            sbclosefinal_field.append(dictFieldsbclose.get(i))
            sbclosefinal_source.append(dictSourcesbclose.get(i)) 
        sbhighfinal_ticker = []
        sbhighfinal_field = []
        sbhighfinal_source = []
        for i in (list_sbhigh):
            sbhighfinal_ticker.append(dictTickersbhigh.get(i))
            sbhighfinal_field.append(dictFieldsbhigh.get(i))
            sbhighfinal_source.append(dictSourcesbhigh.get(i))
        sblowfinal_ticker = []
        sblowfinal_field = []
        sblowfinal_source = []
        for i in (list_sblow):
            sblowfinal_ticker.append(dictTickersblow.get(i))
            sblowfinal_field.append(dictFieldsblow.get(i))
            sblowfinal_source.append(dictSourcesblow.get(i)) 
        sbopenfinal_ticker = []
        sbopenfinal_field = []
        sbopenfinal_source = []
        for i in (list_sbopen):
            sbopenfinal_ticker.append(dictTickersbopen.get(i))
            sbopenfinal_field.append(dictFieldsbopen.get(i))
            sbopenfinal_source.append(dictSourcesbopen.get(i)) 
        sbvolfinal_ticker = []
        sbvolfinal_field = []
        sbvolfinal_source = []
        for i in (list_sbvol):
            sbvolfinal_ticker.append(dictTickersbvol.get(i))
            sbvolfinal_field.append(dictFieldsbvol.get(i))
            sbvolfinal_source.append(dictSourcesbvol.get(i)) 
        sincurrencyfinal_ticker = []
        sincurrencyfinal_field = []
        sincurrencyfinal_source = []
        for i in (list_sincurrency):
            sincurrencyfinal_ticker.append(dictTickersincurrency.get(i))
            sincurrencyfinal_field.append(dictFieldsincurrency.get(i))
            sincurrencyfinal_source.append(dictSourcesincurrency.get(i))   
        crosscurrencyfinal_ticker = []
        crosscurrencyfinal_field = []
        crosscurrencyfinal_source = []
        for i in (list_crosscurrency):
            crosscurrencyfinal_ticker.append(dictTickercrosscurrency.get(i))
            crosscurrencyfinal_field.append(dictFieldcrosscurrency.get(i))
            crosscurrencyfinal_source.append(dictSourcecrosscurrency.get(i))  
        equityfinal_ticker = []
        equityfinal_field = []
        equityfinal_source = []
        for i in (list_equity):
            equityfinal_ticker.append(dictTickerequity.get(i))
            equityfinal_field.append(dictFieldequity.get(i))
            equityfinal_source.append(dictSourceequity.get(i))   
        sentfinal_ticker = []
        sentfinal_field = []
        sentfinal_source = []
        for i in (list_sent):
            sentfinal_ticker.append(dictTickersent.get(i))
            sentfinal_field.append(dictFieldsent.get(i))
            sentfinal_source.append(dictSourcesent.get(i))   
        imammtotfinal_ticker = []
        imammtotfinal_field = []
        imammtotfinal_source = []
        for i in (list_imammtot):
            imammtotfinal_ticker.append(dictTickerimammtot.get(i))
            imammtotfinal_field.append(dictFieldimammtot.get(i))
            imammtotfinal_source.append(dictSourceimammtot.get(i)) 
        imammanfinal_ticker = []
        imammanfinal_field = []
        imammanfinal_source = []
        for i in (list_imamman):
            imammanfinal_ticker.append(dictTickerimamman.get(i))
            imammanfinal_field.append(dictFieldimamman.get(i))
            imammanfinal_source.append(dictSourceimamman.get(i)) 
        imammnittotfinal_ticker = []
        imammnittotfinal_field = []
        imammnittotfinal_source = []
        for i in (list_imammnittot):
            imammnittotfinal_ticker.append(dictTickerimammnittot.get(i))
            imammnittotfinal_field.append(dictFieldimammnittot.get(i))
            imammnittotfinal_source.append(dictSourceimammnittot.get(i))   
        imammnitaqfinal_ticker = []
        imammnitaqfinal_field = []
        imammnitaqfinal_source = []
        for i in (list_imammnitaq):
            imammnitaqfinal_ticker.append(dictTickerimammnitaq.get(i))
            imammnitaqfinal_field.append(dictFieldimammnitaq.get(i))
            imammnitaqfinal_source.append(dictSourceimammnitaq.get(i))  
        imammsufinal_ticker = []
        imammsufinal_field = []
        imammsufinal_source = []
        for i in (list_imammsu):
            imammsufinal_ticker.append(dictTickerimammsu.get(i))
            imammsufinal_field.append(dictFieldimammsu.get(i))
            imammsufinal_source.append(dictSourceimammsu.get(i))   
        imdapfinal_ticker = []
        imdapfinal_field = []
        imdapfinal_source = []
        for i in (list_imdap):
            imdapfinal_ticker.append(dictTickerimdap.get(i))
            imdapfinal_field.append(dictFieldimdap.get(i))
            imdapfinal_source.append(dictSourceimdap.get(i))   
        imintfinal_ticker = []
        imintfinal_field = []
        imintfinal_source = []
        for i in (list_imint):
            imintfinal_ticker.append(dictTickerimint.get(i))
            imintfinal_field.append(dictFieldimint.get(i))
            imintfinal_source.append(dictSourceimint.get(i))  
        immaptotfinal_ticker = []
        immaptotfinal_field = []
        immaptotfinal_source = []
        for i in (list_immaptot):
            immaptotfinal_ticker.append(dictTickerimmaptot.get(i))
            immaptotfinal_field.append(dictFieldimmaptot.get(i))
            immaptotfinal_source.append(dictSourceimmaptot.get(i))  
        immapmixfinal_ticker = []
        immapmixfinal_field = []
        immapmixfinal_source = []
        for i in (list_immapmix):
            immapmixfinal_ticker.append(dictTickerimmapmix.get(i))
            immapmixfinal_field.append(dictFieldimmapmix.get(i))
            immapmixfinal_source.append(dictSourceimmapmix.get(i)) 
        imphosacfinal_ticker = []
        imphosacfinal_field = []
        imphosacfinal_source = []
        for i in (list_imphosac):
            imphosacfinal_ticker.append(dictTickerimphosac.get(i))
            imphosacfinal_field.append(dictFieldimphosac.get(i))
            imphosacfinal_source.append(dictSourceimphosac.get(i))     
        impotfinal_ticker = []
        impotfinal_field = []
        impotfinal_source = []
        for i in (list_impot):
            impotfinal_ticker.append(dictTickerimpot.get(i))
            impotfinal_field.append(dictFieldimpot.get(i))
            impotfinal_source.append(dictSourceimpot.get(i)) 
        imtsptotfinal_ticker = []
        imtsptotfinal_field = []
        imtsptotfinal_source = []
        for i in (list_imtsptot):
            imtsptotfinal_ticker.append(dictTickerimtsptot.get(i))
            imtsptotfinal_field.append(dictFieldimtsptot.get(i))
            imtsptotfinal_source.append(dictSourceimtsptot.get(i))    
        imtsplessfinal_ticker = []
        imtsplessfinal_field = []
        imtsplessfinal_source = []
        for i in (list_imtspless):
            imtsplessfinal_ticker.append(dictTickerimtspless.get(i))
            imtsplessfinal_field.append(dictFieldimtspless.get(i))
            imtsplessfinal_source.append(dictSourceimtspless.get(i)) 
        imtspgreatfinal_ticker = []
        imtspgreatfinal_field = []
        imtspgreatfinal_source = []
        for i in (list_imtspgreat):
            imtspgreatfinal_ticker.append(dictTickerimtspgreat.get(i))
            imtspgreatfinal_field.append(dictFieldimtspgreat.get(i))
            imtspgreatfinal_source.append(dictSourceimtspgreat.get(i)) 
        imuantotfinal_ticker = []
        imuantotfinal_field = []
        imuantotfinal_source = []
        for i in (list_imuantot):
            imuantotfinal_ticker.append(dictTickerimuantot.get(i))
            imuantotfinal_field.append(dictFieldimuantot.get(i))
            imuantotfinal_source.append(dictSourceimuantot.get(i))    
        imuanmixfinal_ticker = []
        imuanmixfinal_field = []
        imuanmixfinal_source = []
        for i in (list_imuanmix):
            imuanmixfinal_ticker.append(dictTickerimuanmix.get(i))
            imuanmixfinal_field.append(dictFieldimuanmix.get(i))
            imuanmixfinal_source.append(dictSourceimuanmix.get(i)) 
        imureatotfinal_ticker = []
        imureatotfinal_field = []
        imureatotfinal_source = []
        for i in (list_imureatot):
            imureatotfinal_ticker.append(dictTickerimureatot.get(i))
            imureatotfinal_field.append(dictFieldimureatot.get(i))
            imureatotfinal_source.append(dictSourceimureatot.get(i))   
        imureadeffinal_ticker = []
        imureadeffinal_field = []
        imureadeffinal_source = []
        for i in (list_imureadef):
            imureadeffinal_ticker.append(dictTickerimureadef.get(i))
            imureadeffinal_field.append(dictFieldimureadef.get(i))
            imureadeffinal_source.append(dictSourceimureadef.get(i)) 
        imureanesoifinal_ticker = []
        imureanesoifinal_field = []
        imureanesoifinal_source = []
        for i in (list_imureanesoi):
            imureanesoifinal_ticker.append(dictTickerimureanesoi.get(i))
            imureanesoifinal_field.append(dictFieldimureanesoi.get(i))
            imureanesoifinal_source.append(dictSourceimureanesoi.get(i))  
        imureasolidfinal_ticker = []
        imureasolidfinal_field = []
        imureasolidfinal_source = []
        for i in (list_imureasolid):
            imureasolidfinal_ticker.append(dictTickerimureasolid.get(i))
            imureasolidfinal_field.append(dictFieldimureasolid.get(i))
            imureasolidfinal_source.append(dictSourceimureasolid.get(i))  
        imureaaqfinal_ticker = []
        imureaaqfinal_field = []
        imureaaqfinal_source = []
        for i in (list_imureaaq):
            imureaaqfinal_ticker.append(dictTickerimureaaq.get(i))
            imureaaqfinal_field.append(dictFieldimureaaq.get(i))
            imureaaqfinal_source.append(dictSourceimureaaq.get(i))   
        exammtotfinal_ticker = []
        exammtotfinal_field = []
        exammtotfinal_source = []
        for i in (list_exammtot):
            exammtotfinal_ticker.append(dictTickerexammtot.get(i))
            exammtotfinal_field.append(dictFieldexammtot.get(i))
            exammtotfinal_source.append(dictSourceexammtot.get(i)) 
        exammanfinal_ticker = []
        exammanfinal_field = []
        exammanfinal_source = []
        for i in (list_examman):
            exammanfinal_ticker.append(dictTickerexamman.get(i))
            exammanfinal_field.append(dictFieldexamman.get(i))
            exammanfinal_source.append(dictSourceexamman.get(i))
        exammnittotfinal_ticker = []
        exammnittotfinal_field = []
        exammnittotfinal_source = []
        for i in (list_exammnittot):
            exammnittotfinal_ticker.append(dictTickerexammnittot.get(i))
            exammnittotfinal_field.append(dictFieldexammnittot.get(i))
            exammnittotfinal_source.append(dictSourceexammnittot.get(i))    
        exammnitaqfinal_ticker = []
        exammnitaqfinal_field = []
        exammnitaqfinal_source = []
        for i in (list_exammnitaq):
            exammnitaqfinal_ticker.append(dictTickerexammnitaq.get(i))
            exammnitaqfinal_field.append(dictFieldexammnitaq.get(i))
            exammnitaqfinal_source.append(dictSourceexammnitaq.get(i))   
        exammsufinal_ticker = []
        exammsufinal_field = []
        exammsufinal_source = []
        for i in (list_exammsu):
            exammsufinal_ticker.append(dictTickerexammsu.get(i))
            exammsufinal_field.append(dictFieldexammsu.get(i))
            exammsufinal_source.append(dictSourceexammsu.get(i))    
        exdapfinal_ticker = []
        exdapfinal_field = []
        exdapfinal_source = []
        for i in (list_exdap):
            exdapfinal_ticker.append(dictTickerexdap.get(i))
            exdapfinal_field.append(dictFieldexdap.get(i))
            exdapfinal_source.append(dictSourceexdap.get(i))       
        exnpkfinal_ticker = []
        exnpkfinal_field = []
        exnpkfinal_source = []
        for i in (list_exnpk):
            exnpkfinal_ticker.append(dictTickerexnpk.get(i))
            exnpkfinal_field.append(dictFieldexnpk.get(i))
            exnpkfinal_source.append(dictSourceexnpk.get(i))   
        exmaptotfinal_ticker = []
        exmaptotfinal_field = []
        exmaptotfinal_source = []
        for i in (list_exmaptot):
            exmaptotfinal_ticker.append(dictTickerexmaptot.get(i))
            exmaptotfinal_field.append(dictFieldexmaptot.get(i))
            exmaptotfinal_source.append(dictSourceexmaptot.get(i))   
        exmapmixfinal_ticker = []
        exmapmixfinal_field = []
        exmapmixfinal_source = []
        for i in (list_exmapmix):
            exmapmixfinal_ticker.append(dictTickerexmapmix.get(i))
            exmapmixfinal_field.append(dictFieldexmapmix.get(i))
            exmapmixfinal_source.append(dictSourceexmapmix.get(i))  
        exphosacfinal_ticker = []
        exphosacfinal_field = []
        exphosacfinal_source = []
        for i in (list_exphosac):
            exphosacfinal_ticker.append(dictTickerexphosac.get(i))
            exphosacfinal_field.append(dictFieldexphosac.get(i))
            exphosacfinal_source.append(dictSourceexphosac.get(i))   
        expotfinal_ticker = []
        expotfinal_field = []
        expotfinal_source = []
        for i in (list_expot):
            expotfinal_ticker.append(dictTickerexpot.get(i))
            expotfinal_field.append(dictFieldexpot.get(i))
            expotfinal_source.append(dictSourceexpot.get(i)) 
        extsptotfinal_ticker = []
        extsptotfinal_field = []
        extsptotfinal_source = []
        for i in (list_extsptot):
            extsptotfinal_ticker.append(dictTickerextsptot.get(i))
            extsptotfinal_field.append(dictFieldextsptot.get(i))
            extsptotfinal_source.append(dictSourceextsptot.get(i))    
        extsplessfinal_ticker = []
        extsplessfinal_field = []
        extsplessfinal_source = []
        for i in (list_extspless):
            extsplessfinal_ticker.append(dictTickerextspless.get(i))
            extsplessfinal_field.append(dictFieldextspless.get(i))
            extsplessfinal_source.append(dictSourceextspless.get(i))  
        extspgreatfinal_ticker = []
        extspgreatfinal_field = []
        extspgreatfinal_source = []
        for i in (list_extspgreat):
            extspgreatfinal_ticker.append(dictTickerextspgreat.get(i))
            extspgreatfinal_field.append(dictFieldextspgreat.get(i))
            extspgreatfinal_source.append(dictSourceextspgreat.get(i))  
        exuantotfinal_ticker = []
        exuantotfinal_field = []
        exuantotfinal_source = []
        for i in (list_exuantot):
            exuantotfinal_ticker.append(dictTickerexuantot.get(i))
            exuantotfinal_field.append(dictFieldexuantot.get(i))
            exuantotfinal_source.append(dictSourceexuantot.get(i))    
        exuanmixfinal_ticker = []
        exuanmixfinal_field = []
        exuanmixfinal_source = []
        for i in (list_exuanmix):
            exuanmixfinal_ticker.append(dictTickerexuanmix.get(i))
            exuanmixfinal_field.append(dictFieldexuanmix.get(i))
            exuanmixfinal_source.append(dictSourceexuanmix.get(i)) 
        exureatotfinal_ticker = []
        exureatotfinal_field = []
        exureatotfinal_source = []
        for i in (list_exureatot):
            exureatotfinal_ticker.append(dictTickerexureatot.get(i))
            exureatotfinal_field.append(dictFieldexureatot.get(i))
            exureatotfinal_source.append(dictSourceexureatot.get(i))   
        exureaaqfinal_ticker = []
        exureaaqfinal_field = []
        exureaaqfinal_source = []
        for i in (list_exureaaq):
            exureaaqfinal_ticker.append(dictTickerexureaaq.get(i))
            exureaaqfinal_field.append(dictFieldexureaaq.get(i))
            exureaaqfinal_source.append(dictSourceexureaaq.get(i))       
        sdammfinal_ticker = []
        sdammfinal_field = []
        sdammfinal_source = []
        for i in (list_sdamm):
            sdammfinal_ticker.append(dictTickersdamm.get(i))
            sdammfinal_field.append(dictFieldsdamm.get(i))
            sdammfinal_source.append(dictSourcesdamm.get(i))   
        sddapmapusfinal_ticker = []
        sddapmapusfinal_field = []
        sddapmapusfinal_source = []
        for i in (list_sddapmapus):
            sddapmapusfinal_ticker.append(dictTickersddapmapus.get(i))
            sddapmapusfinal_field.append(dictFieldsddapmapus.get(i))
            sddapmapusfinal_source.append(dictSourcesddapmapus.get(i))    
        sddapmapallfinal_ticker = []
        sddapmapallfinal_field = []
        sddapmapallfinal_source = []
        for i in (list_sddapmapall):
            sddapmapallfinal_ticker.append(dictTickersddapmapall.get(i))
            sddapmapallfinal_field.append(dictFieldsddapmapall.get(i))
            sddapmapallfinal_source.append(dictSourcesddapmapall.get(i))  
        sdpotusfinal_ticker = []
        sdpotusfinal_field = []
        sdpotusfinal_source = []
        for i in (list_sdpotus):
            sdpotusfinal_ticker.append(dictTickersdpotus.get(i))
            sdpotusfinal_field.append(dictFieldsdpotus.get(i))
            sdpotusfinal_source.append(dictSourcesdpotus.get(i))    
        sdpotallfinal_ticker = []
        sdpotallfinal_field = []
        sdpotallfinal_source = []
        for i in (list_sdpotall):
            sdpotallfinal_ticker.append(dictTickersdpotall.get(i))
            sdpotallfinal_field.append(dictFieldsdpotall.get(i))
            sdpotallfinal_source.append(dictSourcesdpotall.get(i))         
        sduanfinal_ticker = []
        sduanfinal_field = []
        sduanfinal_source = []
        for i in (list_sduan):
            sduanfinal_ticker.append(dictTickersduan.get(i))
            sduanfinal_field.append(dictFieldsduan.get(i))
            sduanfinal_source.append(dictSourcesduan.get(i))   
        sdureausfinal_ticker = []
        sdureausfinal_field = []
        sdureausfinal_source = []
        for i in (list_sdureaus):
            sdureausfinal_ticker.append(dictTickersdureaus.get(i))
            sdureausfinal_field.append(dictFieldsdureaus.get(i))
            sdureausfinal_source.append(dictSourcesdureaus.get(i))    
        sdureaallfinal_ticker = []
        sdureaallfinal_field = []
        sdureaallfinal_source = []
        for i in (list_sdureaall):
            sdureaallfinal_ticker.append(dictTickersdureaall.get(i))
            sdureaallfinal_field.append(dictFieldsdureaall.get(i))
            sdureaallfinal_source.append(dictSourcesdureaall.get(i))    
        dapbidfinal_ticker = []
        dapbidfinal_field = []
        dapbidfinal_source = []
        for i in (list_dapbid):
            dapbidfinal_ticker.append(dictTickerdapbid.get(i))
            dapbidfinal_field.append(dictFielddapbid.get(i))
            dapbidfinal_source.append(dictSourcedapbid.get(i))     
        dapofferfinal_ticker = []
        dapofferfinal_field = []
        dapofferfinal_source = []
        for i in (list_dapoffer):
            dapofferfinal_ticker.append(dictTickerdapoffer.get(i))
            dapofferfinal_field.append(dictFielddapoffer.get(i))
            dapofferfinal_source.append(dictSourcedapoffer.get(i))      
        dapmidfinal_ticker = []
        dapmidfinal_field = []
        dapmidfinal_source = []
        for i in (list_dapmid):
            dapmidfinal_ticker.append(dictTickerdapmid.get(i))
            dapmidfinal_field.append(dictFielddapmid.get(i))
            dapmidfinal_source.append(dictSourcedapmid.get(i))  
        mopbidfinal_ticker = []
        mopbidfinal_field = []
        mopbidfinal_source = []
        for i in (list_mopbid):
            mopbidfinal_ticker.append(dictTickermopbid.get(i))
            mopbidfinal_field.append(dictFieldmopbid.get(i))
            mopbidfinal_source.append(dictSourcemopbid.get(i))     
        mopofferfinal_ticker = []
        mopofferfinal_field = []
        mopofferfinal_source = []
        for i in (list_mopoffer):
            mopofferfinal_ticker.append(dictTickermopoffer.get(i))
            mopofferfinal_field.append(dictFieldmopoffer.get(i))
            mopofferfinal_source.append(dictSourcemopoffer.get(i))      
        mopmidfinal_ticker = []
        mopmidfinal_field = []
        mopmidfinal_source = []
        for i in (list_mopmid):
            mopmidfinal_ticker.append(dictTickermopmid.get(i))
            mopmidfinal_field.append(dictFieldmopmid.get(i))
            mopmidfinal_source.append(dictSourcemopmid.get(i))    
        phorockbidfinal_ticker = []
        phorockbidfinal_field = []
        phorockbidfinal_source = []
        for i in (list_phorockbid):
            phorockbidfinal_ticker.append(dictTickerphorockbid.get(i))
            phorockbidfinal_field.append(dictFieldphorockbid.get(i))
            phorockbidfinal_source.append(dictSourcephorockbid.get(i))     
        phorockofferfinal_ticker = []
        phorockofferfinal_field = []
        phorockofferfinal_source = []
        for i in (list_phorockoffer):
            phorockofferfinal_ticker.append(dictTickerphorockoffer.get(i))
            phorockofferfinal_field.append(dictFieldphorockoffer.get(i))
            phorockofferfinal_source.append(dictSourcephorockoffer.get(i))      
        phorockmidfinal_ticker = []
        phorockmidfinal_field = []
        phorockmidfinal_source = []
        for i in (list_phorockmid):
            phorockmidfinal_ticker.append(dictTickerphorockmid.get(i))
            phorockmidfinal_field.append(dictFieldphorockmid.get(i))
            phorockmidfinal_source.append(dictSourcephorockmid.get(i)) 
        sulfurbidfinal_ticker = []
        sulfurbidfinal_field = []
        sulfurbidfinal_source = []
        for i in (list_sulfurbid):
            sulfurbidfinal_ticker.append(dictTickersulfurbid.get(i))
            sulfurbidfinal_field.append(dictFieldsulfurbid.get(i))
            sulfurbidfinal_source.append(dictSourcesulfurbid.get(i))     
        sulfurofferfinal_ticker = []
        sulfurofferfinal_field = []
        sulfurofferfinal_source = []
        for i in (list_sulfuroffer):
            sulfurofferfinal_ticker.append(dictTickersulfuroffer.get(i))
            sulfurofferfinal_field.append(dictFieldsulfuroffer.get(i))
            sulfurofferfinal_source.append(dictSourcesulfuroffer.get(i))      
        sulfurmidfinal_ticker = []
        sulfurmidfinal_field = []
        sulfurmidfinal_source = []
        for i in (list_sulfurmid):
            sulfurmidfinal_ticker.append(dictTickersulfurmid.get(i))
            sulfurmidfinal_field.append(dictFieldsulfurmid.get(i))
            sulfurmidfinal_source.append(dictSourcesulfurmid.get(i))    
        ureabidfinal_ticker = []
        ureabidfinal_field = []
        ureabidfinal_source = []
        for i in (list_ureabid):
            ureabidfinal_ticker.append(dictTickerureabid.get(i))
            ureabidfinal_field.append(dictFieldureabid.get(i))
            ureabidfinal_source.append(dictSourceureabid.get(i))     
        ureaofferfinal_ticker = []
        ureaofferfinal_field = []
        ureaofferfinal_source = []
        for i in (list_ureaoffer):
            ureaofferfinal_ticker.append(dictTickerureaoffer.get(i))
            ureaofferfinal_field.append(dictFieldureaoffer.get(i))
            ureaofferfinal_source.append(dictSourceureaoffer.get(i))      
        ureamidfinal_ticker = []
        ureamidfinal_field = []
        ureamidfinal_source = []
        for i in (list_ureamid):
            ureamidfinal_ticker.append(dictTickerureamid.get(i))
            ureamidfinal_field.append(dictFieldureamid.get(i))
            ureamidfinal_source.append(dictSourceureamid.get(i))  
        ammbidfinal_ticker = []
        ammbidfinal_field = []
        ammbidfinal_source = []
        for i in (list_ammbid):
            ammbidfinal_ticker.append(dictTickerammbid.get(i))
            ammbidfinal_field.append(dictFieldammbid.get(i))
            ammbidfinal_source.append(dictSourceammbid.get(i))     
        ammofferfinal_ticker = []
        ammofferfinal_field = []
        ammofferfinal_source = []
        for i in (list_ammoffer):
            ammofferfinal_ticker.append(dictTickerammoffer.get(i))
            ammofferfinal_field.append(dictFieldammoffer.get(i))
            ammofferfinal_source.append(dictSourceammoffer.get(i))      
        ammmidfinal_ticker = []
        ammmidfinal_field = []
        ammmidfinal_source = []
        for i in (list_ammmid):
            ammmidfinal_ticker.append(dictTickerammmid.get(i))
            ammmidfinal_field.append(dictFieldammmid.get(i))
            ammmidfinal_source.append(dictSourceammmid.get(i))   
        phoacbidfinal_ticker = []
        phoacbidfinal_field = []
        phoacbidfinal_source = []
        for i in (list_phoacbid):
            phoacbidfinal_ticker.append(dictTickerphoacbid.get(i))
            phoacbidfinal_field.append(dictFieldphoacbid.get(i))
            phoacbidfinal_source.append(dictSourcephoacbid.get(i))     
        phoacofferfinal_ticker = []
        phoacofferfinal_field = []
        phoacofferfinal_source = []
        for i in (list_phoacoffer):
            phoacofferfinal_ticker.append(dictTickerphoacoffer.get(i))
            phoacofferfinal_field.append(dictFieldphoacoffer.get(i))
            phoacofferfinal_source.append(dictSourcephoacoffer.get(i))      
        phoacmidfinal_ticker = []
        phoacmidfinal_field = []
        phoacmidfinal_source = []
        for i in (list_phoacmid):
            phoacmidfinal_ticker.append(dictTickerphoacmid.get(i))
            phoacmidfinal_field.append(dictFieldphoacmid.get(i))
            phoacmidfinal_source.append(dictSourcephoacmid.get(i))     
        sulacbidfinal_ticker = []
        sulacbidfinal_field = []
        sulacbidfinal_source = []
        for i in (list_sulacbid):
            sulacbidfinal_ticker.append(dictTickersulacbid.get(i))
            sulacbidfinal_field.append(dictFieldsulacbid.get(i))
            sulacbidfinal_source.append(dictSourcesulacbid.get(i))     
        sulacofferfinal_ticker = []
        sulacofferfinal_field = []
        sulacofferfinal_source = []
        for i in (list_sulacoffer):
            sulacofferfinal_ticker.append(dictTickersulacoffer.get(i))
            sulacofferfinal_field.append(dictFieldsulacoffer.get(i))
            sulacofferfinal_source.append(dictSourcesulacoffer.get(i))      
        sulacmidfinal_ticker = []
        sulacmidfinal_field = []
        sulacmidfinal_source = []
        for i in (list_sulacmid):
            sulacmidfinal_ticker.append(dictTickersulacmid.get(i))
            sulacmidfinal_field.append(dictFieldsulacmid.get(i))
            sulacmidfinal_source.append(dictSourcesulacmid.get(i))    
        uanbidfinal_ticker = []
        uanbidfinal_field = []
        uanbidfinal_source = []
        for i in (list_uanbid):
            uanbidfinal_ticker.append(dictTickeruanbid.get(i))
            uanbidfinal_field.append(dictFielduanbid.get(i))
            uanbidfinal_source.append(dictSourceuanbid.get(i))     
        uanofferfinal_ticker = []
        uanofferfinal_field = []
        uanofferfinal_source = []
        for i in (list_uanoffer):
            uanofferfinal_ticker.append(dictTickeruanoffer.get(i))
            uanofferfinal_field.append(dictFielduanoffer.get(i))
            uanofferfinal_source.append(dictSourceuanoffer.get(i))      
        uanmidfinal_ticker = []
        uanmidfinal_field = []
        uanmidfinal_source = []
        for i in (list_uanmid):
            uanmidfinal_ticker.append(dictTickeruanmid.get(i))
            uanmidfinal_field.append(dictFielduanmid.get(i))
            uanmidfinal_source.append(dictSourceuanmid.get(i))   
        chsdapfinal_ticker = []
        chsdapfinal_field = []
        chsdapfinal_source = []
        for i in (list_chsdap):
            chsdapfinal_ticker.append(dictTickerchsdap.get(i))
            chsdapfinal_field.append(dictFieldchsdap.get(i))
            chsdapfinal_source.append(dictSourcechsdap.get(i))  
        chspotfinal_ticker = []
        chspotfinal_field = []
        chspotfinal_source = []
        for i in (list_chspot):
            chspotfinal_ticker.append(dictTickerchspot.get(i))
            chspotfinal_field.append(dictFieldchspot.get(i))
            chspotfinal_source.append(dictSourcechspot.get(i)) 
        chsuanfinal_ticker = []
        chsuanfinal_field = []
        chsuanfinal_source = []
        for i in (list_chsuan):
            chsuanfinal_ticker.append(dictTickerchsuan.get(i))
            chsuanfinal_field.append(dictFieldchsuan.get(i))
            chsuanfinal_source.append(dictSourcechsuan.get(i)) 
        chsureafinal_ticker = []
        chsureafinal_field = []
        chsureafinal_source = []
        for i in (list_chsurea):
            chsureafinal_ticker.append(dictTickerchsurea.get(i))
            chsureafinal_field.append(dictFieldchsurea.get(i))
            chsureafinal_source.append(dictSourcechsurea.get(i))    
        buckdapfinal_ticker = []
        buckdapfinal_field = []
        buckdapfinal_source = []
        for i in (list_buckdap):
            buckdapfinal_ticker.append(dictTickerbuckdap.get(i))
            buckdapfinal_field.append(dictFieldbuckdap.get(i))
            buckdapfinal_source.append(dictSourcebuckdap.get(i))  
        buckpotfinal_ticker = []
        buckpotfinal_field = []
        buckpotfinal_source = []
        for i in (list_buckpot):
            buckpotfinal_ticker.append(dictTickerbuckpot.get(i))
            buckpotfinal_field.append(dictFieldbuckpot.get(i))
            buckpotfinal_source.append(dictSourcebuckpot.get(i)) 
        buckuanfinal_ticker = []
        buckuanfinal_field = []
        buckuanfinal_source = []
        for i in (list_buckuan):
            buckuanfinal_ticker.append(dictTickerbuckuan.get(i))
            buckuanfinal_field.append(dictFieldbuckuan.get(i))
            buckuanfinal_source.append(dictSourcebuckuan.get(i)) 
        buckureafinal_ticker = []
        buckureafinal_field = []
        buckureafinal_source = []
        for i in (list_buckurea):
            buckureafinal_ticker.append(dictTickerbuckurea.get(i))
            buckureafinal_field.append(dictFieldbuckurea.get(i))
            buckureafinal_source.append(dictSourcebuckurea.get(i))   
        crufinal_ticker = []
        crufinal_field = []
        crufinal_source = []
        for i in (list_cru):
            crufinal_ticker.append(dictTickercru.get(i))
            crufinal_field.append(dictFieldcru.get(i))
            crufinal_source.append(dictSourcecru.get(i))             
##############################################################################################################################################################################
        ticker = ureagrancfrfinal_ticker + ureagrandelfinal_ticker + ureagranfcafinal_ticker + ureagranfobfinal_ticker + ureagranfobfisfinal_ticker + ureaprillcfrfinal_ticker + ureaprillcptfinal_ticker + ureaprillfobfinal_ticker + ureaprillfobfisfinal_ticker + ureaotherfinal_ticker + uan2830final_ticker + uan32final_ticker + uanotherfinal_ticker + potgranfinal_ticker + potstanfinal_ticker + ammspotfinal_ticker + ammtotcfrfinal_ticker + ammtotdelfinal_ticker + ammtotfobfinal_ticker + ammcontractfinal_ticker + anbagfinal_ticker + anbulkfinal_ticker + antotcfrfinal_ticker + antotfobfinal_ticker + asotherfinal_ticker +  asstanfinal_ticker + aswcfrfinal_ticker + aswfobfinal_ticker + canfinal_ticker + dapfobfinal_ticker + dapotherfinal_ticker + map10final_ticker + mapotherfinal_ticker + npk10final_ticker + npk15final_ticker + npk16final_ticker + npk17final_ticker + npk20final_ticker + phosrockfinal_ticker + phosacidfinal_ticker + \
        sopsspfinal_ticker + sspotfinal_ticker + stotfinal_ticker + s6mfinal_ticker + sgreatfinal_ticker + sliqfinal_ticker + smonthfinal_ticker + sqfinal_ticker + saspotfinal_ticker + satotfinal_ticker + saconfinal_ticker + tspfinal_ticker + coalefinal_ticker + coalarafinal_ticker + coalrfinal_ticker + \
        petrolinvfinal_ticker + ngnclosefinal_ticker + ngnhighfinal_ticker + ngnlowfinal_ticker + ngnopenfinal_ticker + ngnvolfinal_ticker + ngnbpfinal_ticker + wticlosefinal_ticker + wtihighfinal_ticker + wtilowfinal_ticker + wtiopenfinal_ticker + wtivolfinal_ticker + \
        brentclosefinal_ticker + brenthighfinal_ticker + brentlowfinal_ticker + brentopenfinal_ticker + brentvolfinal_ticker + hoclosefinal_ticker + hohighfinal_ticker + holowfinal_ticker + hoopenfinal_ticker + hovolfinal_ticker + rbobclosefinal_ticker + rbobhighfinal_ticker + rboblowfinal_ticker + rbobopenfinal_ticker + rbobvolfinal_ticker + \
        alclosefinal_ticker + alhighfinal_ticker + allowfinal_ticker + alopenfinal_ticker + alvolfinal_ticker + cuclosefinal_ticker + cuhighfinal_ticker + culowfinal_ticker + cuopenfinal_ticker + cuvolfinal_ticker + \
        auclosefinal_ticker + auhighfinal_ticker + aulowfinal_ticker + auopenfinal_ticker + auvolfinal_ticker + feclosefinal_ticker + fehighfinal_ticker + felowfinal_ticker + feopenfinal_ticker + fevolfinal_ticker + pbclosefinal_ticker + pbhighfinal_ticker + pblowfinal_ticker + pbopenfinal_ticker + pbvolfinal_ticker + \
        niclosefinal_ticker + nihighfinal_ticker + nilowfinal_ticker + niopenfinal_ticker + nivolfinal_ticker + paclosefinal_ticker + pahighfinal_ticker + palowfinal_ticker + paopenfinal_ticker + pavolfinal_ticker + plclosefinal_ticker + plhighfinal_ticker + pllowfinal_ticker + plopenfinal_ticker + plvolfinal_ticker + \
        agclosefinal_ticker + aghighfinal_ticker + aglowfinal_ticker + agopenfinal_ticker + agvolfinal_ticker + stclosefinal_ticker + sthighfinal_ticker + stlowfinal_ticker + stopenfinal_ticker + stvolfinal_ticker + tnclosefinal_ticker + tnhighfinal_ticker + tnlowfinal_ticker + tnopenfinal_ticker + tnvolfinal_ticker + \
        urclosefinal_ticker + urhighfinal_ticker + urlowfinal_ticker + uropenfinal_ticker + urvolfinal_ticker + znclosefinal_ticker + znhighfinal_ticker + znlowfinal_ticker + znopenfinal_ticker + znvolfinal_ticker + cornclosefinal_ticker + cornhighfinal_ticker + cornlowfinal_ticker + cornopenfinal_ticker + cornvolfinal_ticker + \
        wheatclosefinal_ticker + wheathighfinal_ticker + wheatlowfinal_ticker + wheatopenfinal_ticker + wheatvolfinal_ticker + soyclosefinal_ticker + soyhighfinal_ticker + soylowfinal_ticker + soyopenfinal_ticker + soyvolfinal_ticker + soclosefinal_ticker + sohighfinal_ticker + solowfinal_ticker + soopenfinal_ticker + sovolfinal_ticker + \
        cotclosefinal_ticker + cothighfinal_ticker + cotlowfinal_ticker + cotopenfinal_ticker + cotvolfinal_ticker + sbclosefinal_ticker + sbhighfinal_ticker + sblowfinal_ticker + sbopenfinal_ticker + sbvolfinal_ticker + sincurrencyfinal_ticker + crosscurrencyfinal_ticker + equityfinal_ticker + sentfinal_ticker + imammtotfinal_ticker + \
        imammanfinal_ticker + imammnittotfinal_ticker + imammnitaqfinal_ticker + imammsufinal_ticker + imdapfinal_ticker + imintfinal_ticker + immaptotfinal_ticker + immapmixfinal_ticker + imphosacfinal_ticker + impotfinal_ticker + imtsptotfinal_ticker + imtsplessfinal_ticker + imtspgreatfinal_ticker + imuantotfinal_ticker + \
        imuanmixfinal_ticker + imureatotfinal_ticker + imureadeffinal_ticker + imureanesoifinal_ticker + imureasolidfinal_ticker + imureaaqfinal_ticker + exammtotfinal_ticker + exammanfinal_ticker + exammnittotfinal_ticker + exammnitaqfinal_ticker + exammsufinal_ticker + exdapfinal_ticker + exnpkfinal_ticker + exmaptotfinal_ticker + \
        exmapmixfinal_ticker + exphosacfinal_ticker + expotfinal_ticker + extsptotfinal_ticker + extsplessfinal_ticker + extspgreatfinal_ticker + exuantotfinal_ticker + exuanmixfinal_ticker + exureatotfinal_ticker + exureaaqfinal_ticker + sdammfinal_ticker + sddapmapusfinal_ticker + sddapmapallfinal_ticker + sdpotusfinal_ticker + sdpotallfinal_ticker + \
        sduanfinal_ticker + sdureausfinal_ticker + sdureaallfinal_ticker + dapbidfinal_ticker + dapofferfinal_ticker + dapmidfinal_ticker + mopbidfinal_ticker + mopofferfinal_ticker + mopmidfinal_ticker + phorockbidfinal_ticker + phorockofferfinal_ticker + phorockmidfinal_ticker + sulfurbidfinal_ticker + sulfurofferfinal_ticker + sulfurmidfinal_ticker + \
        ureabidfinal_ticker + ureaofferfinal_ticker + ureamidfinal_ticker + ammbidfinal_ticker + ammofferfinal_ticker + ammmidfinal_ticker + phoacbidfinal_ticker + phoacofferfinal_ticker + phoacmidfinal_ticker + sulacbidfinal_ticker + sulacofferfinal_ticker + sulacmidfinal_ticker + uanbidfinal_ticker + uanofferfinal_ticker + uanmidfinal_ticker + \
        chsdapfinal_ticker + chspotfinal_ticker + chsuanfinal_ticker + chsureafinal_ticker + buckdapfinal_ticker + buckpotfinal_ticker + buckuanfinal_ticker + buckureafinal_ticker + crufinal_ticker
        field_name = ureagrancfrfinal_field + ureagrandelfinal_field + ureagranfcafinal_field + ureagranfobfinal_field + ureagranfobfisfinal_field + ureaprillcfrfinal_field + ureaprillcptfinal_field + ureaprillfobfinal_field + ureaprillfobfisfinal_field + ureaotherfinal_field + uan2830final_field + \
                    uan32final_field + uanotherfinal_field + potgranfinal_field + potstanfinal_field + ammspotfinal_field + ammtotcfrfinal_field + ammtotdelfinal_field + ammtotfobfinal_field + ammcontractfinal_field + anbagfinal_field + anbulkfinal_field + antotcfrfinal_field + antotfobfinal_field + asotherfinal_field + \
                     asstanfinal_field + aswcfrfinal_field + aswfobfinal_field + canfinal_field + dapfobfinal_field + dapotherfinal_field + map10final_field + mapotherfinal_field + npk10final_field + npk15final_field + npk16final_field + npk17final_field + npk20final_field + phosrockfinal_field + \
                     phosacidfinal_field + sopsspfinal_field + sspotfinal_field + stotfinal_field + s6mfinal_field + sgreatfinal_field + sliqfinal_field + smonthfinal_field + sqfinal_field + saspotfinal_field + satotfinal_field + saconfinal_field + tspfinal_field + coalefinal_field + coalarafinal_field + coalrfinal_field + \
                     petrolinvfinal_field + ngnclosefinal_field + ngnhighfinal_field + ngnlowfinal_field + ngnopenfinal_field + ngnvolfinal_field + ngnbpfinal_field + wticlosefinal_field + wtihighfinal_field + wtilowfinal_field + wtiopenfinal_field + wtivolfinal_field + \
                     brentclosefinal_field + brenthighfinal_field + brentlowfinal_field + brentopenfinal_field + brentvolfinal_field + hoclosefinal_field + hohighfinal_field + holowfinal_field + hoopenfinal_field + hovolfinal_field + rbobclosefinal_field + rbobhighfinal_field + rboblowfinal_field + rbobopenfinal_field + rbobvolfinal_field + \
                     alclosefinal_field + alhighfinal_field + allowfinal_field + alopenfinal_field + alvolfinal_field + cuclosefinal_field + cuhighfinal_field + culowfinal_field + cuopenfinal_field + cuvolfinal_field + \
                     auclosefinal_field + auhighfinal_field + aulowfinal_field + auopenfinal_field + auvolfinal_field + feclosefinal_field + fehighfinal_field + felowfinal_field + feopenfinal_field + fevolfinal_field + pbclosefinal_field + pbhighfinal_field + pblowfinal_field + pbopenfinal_field + pbvolfinal_field + \
                     niclosefinal_field + nihighfinal_field + nilowfinal_field + niopenfinal_field + nivolfinal_field + paclosefinal_field + pahighfinal_field + palowfinal_field + paopenfinal_field + pavolfinal_field + plclosefinal_field + plhighfinal_field + pllowfinal_field + plopenfinal_field + plvolfinal_field + \
                     agclosefinal_field + aghighfinal_field + aglowfinal_field + agopenfinal_field + agvolfinal_field + stclosefinal_field + sthighfinal_field + stlowfinal_field + stopenfinal_field + stvolfinal_field + tnclosefinal_field + tnhighfinal_field + tnlowfinal_field + tnopenfinal_field + tnvolfinal_field + \
                     urclosefinal_field + urhighfinal_field + urlowfinal_field + uropenfinal_field + urvolfinal_field + znclosefinal_field + znhighfinal_field + znlowfinal_field + znopenfinal_field + znvolfinal_field + cornclosefinal_field + cornhighfinal_field + cornlowfinal_field + cornopenfinal_field + cornvolfinal_field + \
                     wheatclosefinal_field + wheathighfinal_field + wheatlowfinal_field + wheatopenfinal_field + wheatvolfinal_field + soyclosefinal_field + soyhighfinal_field + soylowfinal_field + soyopenfinal_field + soyvolfinal_field + soclosefinal_field + sohighfinal_field + solowfinal_field + soopenfinal_field + sovolfinal_field + \
                     cotclosefinal_field + cothighfinal_field + cotlowfinal_field + cotopenfinal_field + cotvolfinal_field + sbclosefinal_field + sbhighfinal_field + sblowfinal_field + sbopenfinal_field + sbvolfinal_field + sincurrencyfinal_field + crosscurrencyfinal_field + equityfinal_field + sentfinal_field + imammtotfinal_field + \
                     imammanfinal_field + imammnittotfinal_field + imammnitaqfinal_field + imammsufinal_field + imdapfinal_field + imintfinal_field + immaptotfinal_field + immapmixfinal_field + imphosacfinal_field + impotfinal_field + imtsptotfinal_field + imtsplessfinal_field + imtspgreatfinal_field + imuantotfinal_field + \
                     imuanmixfinal_field + imureatotfinal_field + imureadeffinal_field + imureanesoifinal_field + imureasolidfinal_field + imureaaqfinal_field + exammtotfinal_field + exammanfinal_field + exammnittotfinal_field + exammnitaqfinal_field + exammsufinal_field + exdapfinal_field + exnpkfinal_field + exmaptotfinal_field + \
                     exmapmixfinal_field + exphosacfinal_field + expotfinal_field + extsptotfinal_field + extsplessfinal_field + extspgreatfinal_field + exuantotfinal_field + exuanmixfinal_field + exureatotfinal_field + exureaaqfinal_field + sdammfinal_field + sddapmapusfinal_field + sddapmapallfinal_field + sdpotusfinal_field + sdpotallfinal_field + \
                     sduanfinal_field + sdureausfinal_field + sdureaallfinal_field + dapbidfinal_field + dapofferfinal_field + dapmidfinal_field + mopbidfinal_field + mopofferfinal_field + mopmidfinal_field + phorockbidfinal_field + phorockofferfinal_field + phorockmidfinal_field + sulfurbidfinal_field + sulfurofferfinal_field + sulfurmidfinal_field + \
                     ureabidfinal_field + ureaofferfinal_field + ureamidfinal_field + ammbidfinal_field + ammofferfinal_field + ammmidfinal_field + phoacbidfinal_field + phoacofferfinal_field + phoacmidfinal_field + sulacbidfinal_field + sulacofferfinal_field + sulacmidfinal_field + uanbidfinal_field + uanofferfinal_field + uanmidfinal_field + \
                     chsdapfinal_field + chspotfinal_field + chsuanfinal_field + chsureafinal_field + buckdapfinal_field + buckpotfinal_field + buckuanfinal_field + buckureafinal_field + crufinal_field
        source = ureagrancfrfinal_source + ureagrandelfinal_source + ureagranfcafinal_source + ureagranfobfinal_source + ureagranfobfisfinal_source + ureaprillcfrfinal_source + ureaprillcptfinal_source + ureaprillfobfinal_source + ureaprillfobfisfinal_source + ureaotherfinal_source + \
                 uan2830final_source + uan32final_source + uanotherfinal_source + potgranfinal_source + potstanfinal_source + ammspotfinal_source + ammtotcfrfinal_source + ammtotdelfinal_source + ammtotfobfinal_source + ammcontractfinal_source + anbagfinal_source + anbulkfinal_source + antotcfrfinal_source + \
                 antotfobfinal_source + asotherfinal_source + asstanfinal_source + aswcfrfinal_source + aswfobfinal_source + canfinal_source + dapfobfinal_source + dapotherfinal_source + map10final_source + mapotherfinal_source + npk10final_source + npk15final_source + npk16final_source + npk17final_source + npk20final_source + \
                 phosrockfinal_source + phosacidfinal_source + sopsspfinal_source + sspotfinal_source + stotfinal_source + s6mfinal_source + sgreatfinal_source + sliqfinal_source + smonthfinal_source + sqfinal_source + saspotfinal_source + satotfinal_source + saconfinal_source + \
                 tspfinal_source + coalefinal_source + coalarafinal_source + coalrfinal_source + petrolinvfinal_source + ngnclosefinal_source + ngnhighfinal_source + ngnlowfinal_source + ngnopenfinal_source + ngnvolfinal_source + ngnbpfinal_source + \
                 wticlosefinal_source + wtihighfinal_source + wtilowfinal_source + wtiopenfinal_source + wtivolfinal_source + brentclosefinal_source + brenthighfinal_source + brentlowfinal_source + brentopenfinal_source + brentvolfinal_source + hoclosefinal_source + hohighfinal_source + holowfinal_source + hoopenfinal_source + hovolfinal_source + \
                 rbobclosefinal_source + rbobhighfinal_source + rboblowfinal_source + rbobopenfinal_source + rbobvolfinal_source + alclosefinal_source + alhighfinal_source + allowfinal_source + alopenfinal_source + alvolfinal_source + cuclosefinal_source + cuhighfinal_source + culowfinal_source + cuopenfinal_source + cuvolfinal_source + \
                 auclosefinal_source + auhighfinal_source + aulowfinal_source + auopenfinal_source + auvolfinal_source + feclosefinal_source + fehighfinal_source + felowfinal_source + feopenfinal_source + fevolfinal_source + pbclosefinal_source + pbhighfinal_source + pblowfinal_source + pbopenfinal_source + pbvolfinal_source + \
                 niclosefinal_source + nihighfinal_source + nilowfinal_source + niopenfinal_source + nivolfinal_source + paclosefinal_source + pahighfinal_source + palowfinal_source + paopenfinal_source + pavolfinal_source + plclosefinal_source + plhighfinal_source + pllowfinal_source + plopenfinal_source + plvolfinal_source + \
                 agclosefinal_source + aghighfinal_source + aglowfinal_source + agopenfinal_source + agvolfinal_source + stclosefinal_source + sthighfinal_source + stlowfinal_source + stopenfinal_source + stvolfinal_source + tnclosefinal_source + tnhighfinal_source + tnlowfinal_source + tnopenfinal_source + tnvolfinal_source + \
                 urclosefinal_source + urhighfinal_source + urlowfinal_source + uropenfinal_source + urvolfinal_source + znclosefinal_source + znhighfinal_source + znlowfinal_source + znopenfinal_source + znvolfinal_source + cornclosefinal_source + cornhighfinal_source + cornlowfinal_source + cornopenfinal_source + cornvolfinal_source + \
                 wheatclosefinal_source + wheathighfinal_source + wheatlowfinal_source + wheatopenfinal_source + wheatvolfinal_source + soyclosefinal_source + soyhighfinal_source + soylowfinal_source + soyopenfinal_source + soyvolfinal_source + soclosefinal_source + sohighfinal_source + solowfinal_source + soopenfinal_source + sovolfinal_source + \
                 cotclosefinal_source + cothighfinal_source + cotlowfinal_source + cotopenfinal_source + cotvolfinal_source + sbclosefinal_source + sbhighfinal_source + sblowfinal_source + sbopenfinal_source + sbvolfinal_source + sincurrencyfinal_source + crosscurrencyfinal_source + equityfinal_source + sentfinal_source + imammtotfinal_source + \
                 imammanfinal_source + imammnittotfinal_source + imammnitaqfinal_source + imammsufinal_source + imdapfinal_source + imintfinal_source + immaptotfinal_source + immapmixfinal_source + imphosacfinal_source + impotfinal_source + imtsptotfinal_source + imtsplessfinal_source + imtspgreatfinal_source + imuantotfinal_source + \
                 imuanmixfinal_source + imureatotfinal_source + imureadeffinal_source + imureanesoifinal_source + imureasolidfinal_source + imureaaqfinal_source + exammtotfinal_source + exammanfinal_source + exammnittotfinal_source + exammnitaqfinal_source + exammsufinal_source + exdapfinal_source + exnpkfinal_source + exmaptotfinal_source + \
                 exmapmixfinal_source + exphosacfinal_source + expotfinal_source + extsptotfinal_source + extsplessfinal_source + extspgreatfinal_source + exuantotfinal_source + exuanmixfinal_source + exureatotfinal_source + exureaaqfinal_source + sdammfinal_source + sddapmapusfinal_source + sddapmapallfinal_source + sdpotusfinal_source + sdpotallfinal_source + \
                 sduanfinal_source + sdureausfinal_source + sdureaallfinal_source + dapbidfinal_source + dapofferfinal_source + dapmidfinal_source + mopbidfinal_source + mopofferfinal_source + mopmidfinal_source + phorockbidfinal_source + phorockofferfinal_source + phorockmidfinal_source + sulfurbidfinal_source + sulfurofferfinal_source + sulfurmidfinal_source + \
                 ureabidfinal_source + ureaofferfinal_source + ureamidfinal_source + ammbidfinal_source + ammofferfinal_source + ammmidfinal_source + phoacbidfinal_source + phoacofferfinal_source + phoacmidfinal_source + sulacbidfinal_source + sulacofferfinal_source + sulacmidfinal_source + uanbidfinal_source + uanofferfinal_source + uanmidfinal_source + \
                 chsdapfinal_source + chspotfinal_source + chsuanfinal_source + chsureafinal_source + buckdapfinal_source + buckpotfinal_source + buckuanfinal_source + buckureafinal_source + crufinal_source
        
        crtConn = crtDbOpen()
        df = pd.DataFrame()
        whole_dataframes = {}
    
        for i in range(0,len(ticker)):
            
            period_series_dict = {}
                    
            statement ="Select * FROM dbo.CRTGetPeriodSeries('" + start_date + "' , '" + end_date + "' , '" + ticker[i] + "' , '" + field_name[i] + "' , '" + source[i] + "','" + cal_type + "')"
            get_period_series_list = crt_gen_sel (crtConn, statement, None,case="same")
        
            for row in get_period_series_list:
                dt = str(row[0])
                tmpDate = dt.split(' ')
                dt = tmpDate[0]
           
                dt = datetime.datetime.strptime(dt,'%Y-%m-%d')
                t_year = dt.year
            
                dbDate = str(dt).split(' ')
                dbDate = dbDate[0]
                dbDate = str(dbDate[:len(dbDate)-2] + str(t_year))
           
                period_series_dict[dt] = row[1]
            
            statement = " TICKER like '" + ticker[i] + "' AND FIELDNAME = '" + field_name[i] + "' AND DATASOURCE = '" + source[i] + "'"
            TableName = 'CRTTICKERNAME'
            IdColName = 'tickerid'
            
            get_id = crt_select_multiple_value(crtConn,TableName, IdColName, statement)
            
            statement = " tickerid = " + get_id.get(1)
            statement = statement.replace(',','')
            statement = statement.strip()
            
            TableName = 'CRTTICKERVALUE'
            IdColName = 'tickerValueDate,tickerValue'
            PP = crt_select_multiple_value(crtConn,TableName, IdColName, statement)
        
            date_list = []
            value_list = []
            
            for key, value in iter(PP.items()):
                temp_value = PP.get(key)
                temp_value = temp_value.split(',')
        
                dbValue = float(temp_value[1])
                dbDate = str(temp_value[0])
                dbDate = dbDate.split(' ')
                dbDate = dbDate[0]
        
                tmpDate = datetime.datetime.strptime(dbDate,'%Y-%m-%d')
               
                t_year = tmpDate.year
                
                dbDate = str(dbDate[:len(dbDate)-2] + str(t_year))
                
                if period_series_dict.get(tmpDate):
                    period_series_dict[tmpDate] = dbValue
        
            date_list = []
            value_list = [] 
            for key in sorted(period_series_dict.keys()):
                
                dbDate = key
                dbValue = period_series_dict.get(key)
                
                date_list.append(dbDate)
                value_list.append(dbValue)
                whole_dataframes[i] =  pd.DataFrame()
        
            s_PP = pd.Series(date_list)
            s_PP2 = pd.Series(value_list)
           
            whole_dataframes[i]['Date'] = s_PP
            whole_dataframes[i]['Date'] = pd.to_datetime(whole_dataframes[i]['Date']) #run
            whole_dataframes[i][ticker[i]+'_'+field_name[i]+'_'+source[i]] = s_PP2
            
        whole_dataframes[0].index = whole_dataframes[0]['Date'].values  
        whole_dataframes[0] = whole_dataframes[0].drop(['Date'],axis=1)
          
        for i in range(1,len(ticker)):
            whole_dataframes[i].index = whole_dataframes[i]['Date'].values
            whole_dataframes[i] = whole_dataframes[i].drop(['Date'],axis=1)
            
            whole_dataframes[0] = whole_dataframes[0].join(whole_dataframes[i])
        df = whole_dataframes[0] 

        #adding date column instead of as in an index        
        date = df.index
        df['Date'] = date
        cols = df.columns.tolist()
        cols = cols[-1:] + cols[:-1]
        df = df[cols]
        
        #cols = df.columns
        self.data_tableWidget.clear()
        self.data_tableWidget.setRowCount(0)
        self.data_tableWidget.setColumnCount(0)
        self.data_tableWidget.setColumnCount(len(df.columns))
        self.data_tableWidget.setRowCount(len(df.index))
        self.data_tableWidget.setHorizontalHeaderLabels(cols)
        for i in range(len(df.index)):
            for j in range(len(df.columns)):
                self.data_tableWidget.setItem(i,j,QtGui.QTableWidgetItem(str(df.iat[i, j]))) 
        
        #adding variables to x,y comboboxes
        #self.scatx_comboBox.clear()
        #self.scaty_comboBox.clear()
        #self.corx_comboBox.clear()
        #self.cory2_comboBox.clear()
        #self.fitx_comboBox.clear()
        #self.fity_comboBox.clear()
        self.scatx_comboBox.addItems(df.columns[1:])
        self.scaty_comboBox.addItems(df.columns[1:])
        self.corx_comboBox.addItems(df.columns[1:])
        self.cory2_comboBox.addItems(df.columns[1:])
        self.fitx_comboBox.addItems(df.columns[1:])
        self.fity_comboBox.addItems(df.columns[1:])  
       
      
        def forecast_save():
            self.textEdit.setText(QFileDialog.getSaveFileName())
            save_file = (self.textEdit.toPlainText()) 
            dfnew = df.drop(['Date'],axis=1)
            dfnew.to_csv(save_file)
        self.save_pushButton.clicked.connect(forecast_save) 
        return df
        
    def clearselection(self):
        def clear(listwidget):
            for i in range(listwidget.count()):
                item = listwidget.item(i)
                listwidget.setItemSelected(item, False) 
        clear(self.ureagrancfr_listWidget)
        clear(self.ureagrandel_listWidget)
        clear(self.ureagranfobfis_listWidget)
        clear(self.ureagranfobfis_listWidget)
        clear(self.ureaother_listWidget)
        clear(self.uan2830_listWidget)
        clear(self.uan32_listWidget)
        clear(self.uanother_listWidget)
        clear(self.potgran_listWidget)
        clear(self.potstan_listWidget)
        clear(self.ammspot_listWidget)
        clear(self.ammtotcfr_listWidget)
        clear(self.ammtotdel_listWidget)
        clear(self.ammtotfob_listWidget)
        clear(self.ammcontract_listWidget)
        clear(self.anbag_listWidget)
        clear(self.anbulk_listWidget)
        clear(self.antotcfr_listWidget)
        clear(self.antotfob_listWidget)
        clear(self.asother_listWidget)
        clear(self.asstan_listWidget)
        clear(self.aswcfr_listWidget)
        clear(self.aswfob_listWidget)
        clear(self.can_listWidget)
        clear(self.dapfob_listWidget)
        clear(self.dapother_listWidget)
        clear(self.map10_listWidget)
        clear(self.mapother_listWidget)
        clear(self.npk10_listWidget)
        clear(self.npk15_listWidget)
        clear(self.npk16_listWidget)
        clear(self.npk17_listWidget)
        clear(self.npk20_listWidget)
        clear(self.phosrock_listWidget)
        clear(self.phosacid_listWidget)
        clear(self.sopssp_listWidget)
        clear(self.sspot_listWidget)
        clear(self.stot_listWidget)
        clear(self.s6m_listWidget)
        clear(self.sgreat_listWidget)
        clear(self.sliq_listWidget)
        clear(self.smonth_listWidget)
        clear(self.sq_listWidget)
        clear(self.saspot_listWidget)
        clear(self.satot_listWidget)
        clear(self.sacon_listWidget) 
        clear(self.tsp_listWidget)
        clear(self.coalcom_listWidget)
        clear(self.coale_listWidget)
        clear(self.coalara_listWidget)
        clear(self.coalr_listWidget)
        clear(self.petrolinv_listWidget)
        clear(self.ngnclose_listWidget)
        clear(self.ngnhigh_listWidget)
        clear(self.ngnlow_listWidget)
        clear(self.ngnopen_listWidget)
        clear(self.ngnvol_listWidget)
        clear(self.ngnbp_listWidget)
        clear(self.wticlose_listWidget)
        clear(self.wtihigh_listWidget)
        clear(self.wtilow_listWidget)
        clear(self.wtiopen_listWidget)
        clear(self.wtivol_listWidget)
        clear(self.brentclose_listWidget)
        clear(self.brenthigh_listWidget)
        clear(self.brentlow_listWidget)
        clear(self.brentopen_listWidget)
        clear(self.brentvol_listWidget)        
        
    def Graphs(self):
        print("all default graphs")

    def pie(self):
        #slices = [7,2,2,13]
        #activities = ['sleeping','eating','working','playing']
        #cols = ['g','m','r','b']
        #plt.pie(slices,labels=activities,colors=cols,startangle=90,shadow= True,explode=(0,0.1,0,0),autopct='%1.1f%%')
        #plt.title('Interesting Graph\nCheck it out')
        #plt.show()
        dd = self.execute()
        dd = dd.drop(['Date'],axis=1)
        dd = dd.dropna()
        #dd['Sum'] = dd.sum(axis=1)
        cols = dd.columns
        sum_list = []
        for i in range(0,len(cols)):
            sum_list.append(dd[[i]].values.sum())
        slices = sum_list
        activities = cols
        plt.pie(slices,labels=activities,startangle=90,shadow= True,autopct='%1.1f%%')
        plt.title('Pie\nChart')
        plt.show()       
    
    def line(self):
        dd = self.execute()
        dd = dd.drop(['Date'],axis=1)
        cols = dd.columns
        style_input = (self.linechartlinestyle_comboBox.currentText())
        gap_input = (self.linechartgap_comboBox.currentText())
        color_input = (self.linechartcolor_comboBox.currentText())
        if style_input == "Lines":
            linestyle2 = 'solid'
        elif style_input == "Dash":
            linestyle2 = 'dashed'
        elif style_input == "Dotted":
            linestyle2 = 'dotted'
        else:
            linestyle2 = 'dashdot'
        ax1 = dd.plot(linestyle = linestyle2)
        lines,labels = ax1.get_legend_handles_labels()
        ax1.legend(lines[:(len(cols))],labels[:(len(cols))],loc='best')
        plt.show()
    
    def timeseries(self):
        print("time series")
    
    def histogram(self):
        #next create overlap histogram option and one that displays all
        dd = self.execute()
        dd = dd.drop(['Date'],axis=1)
        cols = dd.columns
        dd = dd.dropna()
        color_input = (self.histcolor_comboBox.currentText())
        plt.figure(figsize=(10,5))
        plt.hist(dd[cols[0]],bins=(int(math.sqrt(len(dd.index)))), color=color_input) #bins should=sqrt(#obs) 
        plt.title('Histogram' +str(' ') + str(cols[0]))
        plt.show()

    def bar(self):
        #need to know how to sort by month
        dd = self.execute()
        dd = dd.drop(['Date'],axis=1)
        stack_input = (self.barstack_comboBox.currentText())
        or_input = (self.barorientation_comboBox.currentText())
        group_input = (self.bargroup_comboBox.currentText())
        months = {"Jan":1, "Feb":2, "Mar":3, "Apr":4, "May":5, "Jun":6, "Jul":7, "Aug":8, "Sep":9, "Oct":10, "Nov":11, "Dec":12} 
        if group_input == "Ticker":
            if stack_input == "Yes" and or_input == "Vertical":
                plt.show(dd.plot(kind="bar",stacked=True))
            elif stack_input == "No" and or_input == "Vertical":
                plt.show(dd.plot(kind="bar",stacked=False))
            elif stack_input == "Yes" and or_input == "Horizontal":
                plt.show(dd.plot(kind="barh",stacked=True))
            else:
                plt.show(dd.plot(kind="barh",stacked=False))
        elif group_input == "Monthly":
            dd['Date'] = dd.index
            dd = dd.reset_index(drop=True)
            dd['Year'] = dd['Date'].dt.year
            dd['Month'] = dd['Date'].dt.month
            #dd['Month'] = dd['Month'].apply(lambda x: calendar.month_abbr[x])
            dd = dd.drop(['Date'],axis=1)
            cols = dd.columns
            datamonth = dd[cols[0:-2]].groupby(dd['Month']).mean()
            datamonth = datamonth.round(2)
            if stack_input == "Yes" and or_input == "Vertical":
                plt.show(datamonth.plot(kind="bar",stacked=True))
            elif stack_input == "No" and or_input == "Vertical":
                plt.show(datamonth.plot(kind="bar",stacked=False))
            elif stack_input == "Yes" and or_input == "Horizontal":
                plt.show(datamonth.plot(kind="barh",stacked=True))
            else:
                plt.show(datamonth.plot(kind="barh",stacked=False))
        else:
            dd['Date'] = dd.index
            dd = dd.reset_index(drop=True)
            dd['Year'] = dd['Date'].dt.year
            dd['Month'] = dd['Date'].dt.month
            dd = dd.drop(['Date'],axis=1)
            cols = dd.columns
            datayear = dd[cols[0:-2]].groupby(dd['Year']).mean()
            datayear = datayear.round(2)
            if stack_input == "Yes" and or_input == "Vertical":
                plt.show(datayear.plot(kind="bar",stacked=True))
            elif stack_input == "No" and or_input == "Vertical":
                plt.show(datayear.plot(kind="bar",stacked=False))
            elif stack_input == "Yes" and or_input == "Horizontal":
                plt.show(datayear.plot(kind="barh",stacked=True))
            else:
                plt.show(datayear.plot(kind="barh",stacked=False))
            
    def scatter(self):
        dd = self.execute()
        dd = dd.drop(['Date'],axis=1)
        cols = dd.columns
        color_input = (self.scatcolor_comboBox.currentText())
        x_input = (self.scatx_comboBox.currentText())
        y_input = (self.scaty_comboBox.currentText())
        plt.figure(figsize=(10,5))
        plt.xlabel(x_input)
        plt.ylabel(y_input)
        plt.scatter(dd[x_input],dd[y_input], color = color_input)
        plt.show() 
        
    def scattermatrix(self):
        dd = self.execute()
        dd = dd.drop(['Date'],axis=1)
        dd = dd.dropna()
        sns.set(style='whitegrid', context='notebook')
        corrPlots = sns.PairGrid(dd,size=4)
        corrPlots = corrPlots.map_diag(plt.hist)
        corrPlots = corrPlots.map_lower(sns.kdeplot,cmap="gist_rainbow")
        corrPlots = corrPlots.map_upper(sns.regplot,line_kws={"color":"r","alpha":0.4,"lw":3}) 
        for ax in corrPlots.axes.flat:
            _ = plt.setp(ax.get_yticklabels(), visible=False)
            _ = plt.setp(ax.get_xticklabels(), visible=False)
        plt.show()  
    
    def boxplot(self):
        dd = self.execute()
        dd = dd.drop(['Date'],axis=1)
        #fig = plt.figure(1, figsize=(9, 6))
        #ax = fig.add_subplot(111)
        #bp = ax.boxplot(dd, patch_artist=True)

        #for box in bp['boxes']:
        #    box.set( color='#7570b3', linewidth=2)
        #    box.set( facecolor = '#1b9e77' )
        #for whisker in bp['whiskers']:
        #    whisker.set(color='#7570b3', linewidth=2)
        #for cap in bp['caps']:
        #    cap.set(color='#7570b3', linewidth=2)
        #for median in bp['medians']:
        #    median.set(color='#b2df8a', linewidth=2)
        #for flier in bp['fliers']:
        #    flier.set(marker='o', color='#e7298a', alpha=0.5)
        #plt.show()
        plt.show(dd.plot(kind='box',figsize=(8,8),title=('BoxPlot')))
    
    def corrheat(self):
        color_input = (self.corheatcolor_comboBox.currentText())
        if color_input == "Multicolor":
            color = "Spectral"
        elif color_input == "Blues/Greens":
            color = "BuGn"
        else:
            color = "YlOrRd"
        dd = self.execute()
        dd = dd.drop(['Date'],axis=1)
        corrmat = dd.corr()
        fig, ax = plt.subplots(figsize=(10,8))
        sns.heatmap(corrmat,cmap=color,annot=True,square=True,cbar=True, fmt='.2f',annot_kws={'size':10},ax=ax)  
        plt.yticks(rotation=0) 
        plt.xticks(rotation=0)
        ax.tick_params(labelsize=8)
        ax.set_xticklabels(ax.xaxis.get_majorticklabels(), rotation=60)
        plt.show()
    
    def corrgraph(self):
        #not getting the right values from combobox
        date_start_old = (self.start_calendarWidget.selectedDate())
        qdatestart = QDateTime(date_start_old)
        date_start = qdatestart.toPyDateTime() #putting in datetime format
        start_date = str(date_start)
        date_end_old = (self.end_calendarWidget.selectedDate())
        qdateend = QDateTime(date_end_old)
        date_end = qdateend.toPyDateTime() #putting in datetime format 
        end_date = str(date_end)
        dd = self.execute()
        dd = dd.drop(['Date'],axis=1)
        #dd = dd.dropna()
        x_input = self.corx_comboBox.currentText()
        y_input = self.cory2_comboBox.currentText()
        
        window1 = int(self.corrwindow_textEdit.toPlainText())
        x1new = dd[x_input]
        x2new = dd[y_input]
        dd['roll_corr'] = pd.rolling_corr(x1new,x2new,window = window1)
        roll_corr = dd['roll_corr']
        textsize = 6
        left, width = 0.1, 0.6
        rect1 = [left, 0.3, width, 0.6]
        rect2 = [left, 0.08, width, 0.2]
        fig = plt.figure(facecolor='white',figsize=(16,8))
        axescolor = '#f6f6f6'  # the axes background color
        #making subplot size
        ax1 = fig.add_axes(rect1, axisbg=axescolor)  # left, bottom, width, height
        ax1t = ax1.twinx()
        ax2 = fig.add_axes(rect2, axisbg=axescolor)
        ax2t = ax2.twinx()
        #top subplot
        ax1.set_title(x_input+' '+'vs. '+ y_input+' '+'('+str(window1)+' '+'Week Correlation)',size=15)
        ax1.tick_params(axis='y', which='major', labelsize=10,colors='blue')
        ax1t.tick_params(axis='y', which='major', labelsize=10)
        ax1.xaxis.set_ticklabels([])
        ax1.plot(x1new,color='b',lw=1.5, label = x_input)
        ax1t.plot(x2new,color='g',lw=1.5,label= y_input)
        #bottom subplot
        ax2.plot (roll_corr,'r')
        ax2.axhline(0.5, color='gray',linestyle = '--')
        ax2.axhline(-0.5, color='gray',linestyle = '--')
        ax2.yaxis.set_ticks([-1.0,-0.75,-0.5,-0.25,0,0.25,0.5,0.75,1.0])
        ax2.tick_params(axis='y', which='major', labelsize=10,colors='r')
        ax2.tick_params(axis='x', which='major', labelsize=10)
        ax2.set_xlim([start_date,end_date])
        ax2t.yaxis.set_ticks([-1.0,-0.75,-0.5,-0.25,0,0.25,0.5,0.75,1.0])
        ax2t.tick_params(axis='y', which='major', labelsize=10)
        year = mdates.YearLocator()
        timeFmt = mdates.DateFormatter('%Y')
        ax2.xaxis.set_major_locator(year)
        ax2.xaxis.set_major_formatter(timeFmt)
        ax1.legend(loc='upper left',prop={'size':10})
        ax1t.legend(bbox_to_anchor=(0.32,0.965),prop={'size':10})
        plt.show()
    
    def fitplot(self):
        dd = self.execute()
        dd = dd.drop(['Date'],axis=1)
        dd = dd.dropna()
        x_input = (self.fitx_comboBox.currentText())
        y_input = (self.fity_comboBox.currentText())
        sns.jointplot(x=x_input,y=y_input,data=dd,kind='reg',size=4)
        plt.show() 
    
    def qqplot(self):
        dd = self.execute()
        dd = dd.drop(['Date'],axis=1)
        cols = dd.columns
        fig = sm.qqplot(dd[cols[0]], line='s')
        plt.grid(True)
        plt.title('QQ Plot')
        plt.xlabel('theoretical quantiles')
        plt.ylabel('sample quantiles')
        plt.show()
    
       
        
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        