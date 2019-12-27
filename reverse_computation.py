# -*- coding: utf-8 -*-

# Author: Christian Winkler
# Date: 27-12-2019

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QProcess
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar

import os
import pandas as pd
import numpy as np

from scipy import interpolate
from scipy.stats import truncnorm
from scipy.optimize import minimize
import scipy.stats as st
import sys
import shutil

#from helprefcurv import *


class Reverese_Comp(QtGui.QMainWindow):    
    def __init__(self, parent=None):
        super(Reverese_Comp, self).__init__() 
        self.program_path = os.path.dirname(sys.argv[0])
        
        self.filename = ""
        self.lms_chart_exists  = False
        
        self.mainWidget = QtGui.QWidget(self)
        self.setCentralWidget(self.mainWidget)
        self.mainLayout = QtGui.QVBoxLayout()
        self.mainWidget.setLayout(self.mainLayout)
        
        self.setWindowTitle('RefCurv - Reverse Computation')
        self.setWindowIcon(QIcon(self.program_path +'/logo/refcurv_logo.png'))
        
        pal = QtGui.QPalette()
        role = QtGui.QPalette.Background
        pal.setColor(role, QtGui.QColor(255, 255, 255))
        self.setPalette(pal)

        self.vLayout = QtGui.QVBoxLayout()
        self.mainLayout.insertLayout(1, self.vLayout)
        
        self.setGeometry(50, 50, 500, 500)
        self.center_window()
                
        self.figure_perc = Figure()
        self.canvas = FigureCanvas(self.figure_perc)
        
        self.figure_LMS = Figure()
        self.canvas_LMS = FigureCanvas(self.figure_LMS)
        
        
        self.vLayout.addWidget(self.canvas)
        self.vLayout.addWidget(self.canvas_LMS)

        self.widget_btns = QtGui.QDialogButtonBox()
        self.widget_btns.addButton('Ok', QtGui.QDialogButtonBox.AcceptRole)
        
        self.widget_btns.accepted.connect(self.reverse_comp)
        

        self.mainLayout.addWidget(self.widget_btns)
        
        
        # buttons
        loadRefButton = QtGui.QAction("&Load reference curves", self)
        loadRefButton.setStatusTip('Load reference curves')
        loadRefButton.triggered.connect(self.open_loadRefcurves)
        
        
        loadResultsButton = QtGui.QAction("&Save results", self)
        loadResultsButton.setStatusTip('Save results')
        loadResultsButton.triggered.connect(self.open_saveResultsDialog)
        
        # menu        
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&Reference curves')
        fileMenu.addAction(loadRefButton)
        fileMenu.addSeparator()
        fileMenu.addAction(loadResultsButton)
 

        
    def center_window(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
#    def z_score(self, L, M, S, y):
##        if L == 0:
##            z = (1/S)*np.log(y/M)
##        else:
#        z = (1/(S*L))*(((y/M)**L)-1)
#        return z
        
    def y_value(self, L, M, S, z):
        if L == 0:
            y = M*np.exp(S * z)
        else:
            y = M*(1 + L * S * z)**(1/L)
        return y
    
    def p2z(self, value):
        return st.norm.ppf(value)
        
    def error_func(self, para, y, cent):
        L = para[0]
        M = para[1]
        S = para[2]
        
        if L == 0:
            error = np.inf
        else:
                
            z_values = self.p2z(cent)
            #z_values = self.p2z(np.array([0.03, 0.1, 0.25, 0.5, 0.75, 0.9, 0.97]))
            try:
                y_comp = self.y_value(L, M, S, z_values)
                error = np.sum(np.abs(y - y_comp))
            except:
                error = np.inf
        print(error)
        return error

    def reverse_comp(self):
        if self.lms_chart_exists == True:
            print(self.lms_chart.columns)

            centiles = [z for z in self.lms_chart.columns if "C" in z]
            print(centiles)
            centiles_num = np.array([float(z[1:])/100 for z in centiles])
            print(centiles_num)
            
            try:
                M_array = []
                L_array = []
                S_array = []
                error_array = []
                
                y_0 = np.array([self.lms_chart[i].values[0] for i in centiles])
                para_start = [-0.4, y_0[3], 0.35]
                for j in range(0, len(self.lms_chart["x"].values)):
                    x = self.lms_chart["x"].values[j]
                    y = np.array([self.lms_chart[i].values[j] for i in centiles])
                        
                    res = minimize(self.error_func, para_start, args = (y, centiles_num), method='nelder-mead') 
                    
                    M_array.append(res.x[1])
                    L_array.append(res.x[0])
                    S_array.append(res.x[2])
                    error_array.append(res.fun)
                    para_start = [res.x[0], res.x[1], res.x[2]]
                
                self.ax_L = self.figure_LMS.add_subplot(311)
                self.ax_M = self.figure_LMS.add_subplot(312)
                self.ax_S = self.figure_LMS.add_subplot(313)
                
                self.ax_L.plot(self.lms_chart["x"].values, L_array, 'b')
                self.ax_M.plot(self.lms_chart["x"].values, M_array, 'b')
                self.ax_S.plot(self.lms_chart["x"].values, S_array, 'b')

                
                self.figure_LMS.tight_layout()
                self.canvas_LMS.draw()
                
                
                self.lms_chart["mu"] = pd.DataFrame(M_array)
                self.lms_chart["sigma"] = pd.DataFrame(S_array)
                self.lms_chart["nu"] = pd.DataFrame(L_array)
                self.lms_chart["error"] = pd.DataFrame(error_array)
                
                self.lms_chart.to_csv(self.program_path + "/tmp/results_reverse.csv", sep = ',', encoding = "ISO-8859-1", index = False)
                
                print("DONE.")
            except:
                print("computation error")
        else:
            print("no charts")
            
        
    def open_loadRefcurves(self):
        self.filename = QtGui.QFileDialog.getOpenFileName(self,'Open File', ' ','*.csv')
        if self.filename:
            try:
                self.lms_chart = pd.read_csv(self.filename,sep =',', encoding = "ISO-8859-1")
                self.plot_refcurv()
                self.canvas.draw()
                self.lms_chart_exists = True

            except:
                print("reading error")

            
    # Save results dialog
    def open_saveResultsDialog(self):
        if os.path.isfile(self.program_path +"/tmp/results_reverse.csv"):
            try:
                filename_chart = QtGui.QFileDialog.getSaveFileName(self,'Save File', ' ','*.csv')
                if filename_chart:
                    shutil.copy2(self.program_path +"/tmp/results_reverse.csv", filename_chart)
            except:
                print("copy error")
        else:
            print("no reference curves")

            
    def plot_refcurv(self):
            self.ax_perc = self.figure_perc.add_subplot(111)
            self.ax_perc.clear()
            for col_name in self.lms_chart.columns:
                if "C" in col_name:
                    self.ax_perc.plot(self.lms_chart["x"].values, self.lms_chart[col_name].values, "k")
                    self.ax_perc.text(self.lms_chart["x"].values[-1]*1.01, self.lms_chart[col_name].values[-1], col_name, size = 8)
                    
            
            self.ax_perc.set_xlim([0, self.lms_chart["x"].values[-1]* 1.2])
            
            self.ax_perc.grid()
            
if __name__ == "__main__":
    
    # create an application and an instance "MainWindow"    
    app = QtGui.QApplication(sys.argv)
    Reverse_MainWindow = Reverese_Comp()
    # define the version

    Reverse_MainWindow.show()
    sys.exit(app.exec_())
        
            
            
        

        


