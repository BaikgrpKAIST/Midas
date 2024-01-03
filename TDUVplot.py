import os
import sys

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

form = resource_path(resource_path("gui/TDUVplot.ui"))
form_class = uic.loadUiType(form)[0]

class TDUVPlotMainWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.btnReadExpData.pressed.connect(self.ReadExpDataAction)
        self.btnExpDataPath.pressed.connect(self.ReadExpDataPath)

        self.btnTDPath.pressed.connect(self.ReadTDPath)

        self.btnConvert.pressed.connect(self.ConvertAction)

    @pyqtSlot()
    def ReadExpDataPath(self):
        try:
            fname = QFileDialog.getOpenFileName(self, "Select Exp. Data File.")
            self.txtExpDataDir.setText(fname[0])
            self.ReadExpDataAction()

        except:
            pass

    def ReadTDPath(self):
        try:
            fname = QFileDialog.getOpenFileName(self, "Select TDDFT output File.")
            self.txtTDDir.setText(fname[0])

        except:
            pass

    def ReadExpDataAction(self):
        filepath = self.txtExpDataDir.text()
        if (os.path.isfile(filepath)):
            self.uvdata = pd.read_csv(filepath)
            self.df_UV = pd.DataFrame(self.uvdata)
            self.df_UV.head()

            self.df_rows = self.df_UV.shape[0]
            self.df_cols = self.df_UV.shape[1]
            self.tblExpData.setRowCount(self.df_rows)
            self.tblExpData.setColumnCount(self.df_cols)
            for i in range(self.df_rows):
                for j in range(self.df_cols):
                    try:
                        x = self.df_UV.iloc[i, j]
                        self.tblExpData.setItem(i, j, QTableWidgetItem(str(x)))
                    except:
                        pass


    def ConvertAction(self):

        self.num_row = self.tblExpData.rowCount()
        self.num_col = self.tblExpData.columnCount()
        self.tmp_df = pd.DataFrame(
            #columns=['Wavelength', 'Absorbance'],
            #ndex=range(self.num_row)
        )
        for i in range(self.num_row):
            for j in range(self.num_col):
                try:
                    self.tmp_df.loc[i,j] = float(self.tblExpData.item(i,j).text())
                except:
                    pass

        self.outpath = self.txtTDDir.text()

        self.broaden, self.sigma, self.units = 'lorentz', 60, 'nm'
        self.osc, self.poles = combine_calculations(self.outpath, 'Gaussian', self.units)
        self.Abs, self.freqs = broaden_spectrum(self.osc, self.poles, self.broaden, self.sigma)

        plot_spectrum(self.Abs, self.freqs, self.osc, self.poles, self.units, self.tmp_df)
        plt.show()



def search_file(f_name, program, units):
    ''' Grabs all the oscillator strengths and excitation energies '''

    # grab poles/oscillator strengths
    osc, poles = [], []
    searchfile = open(f_name, "r")

    if program == 'Jaguar':
        for line in searchfile:
            if 'Oscillator strength,' in line:
                contents = line.split()
                osc.append(float(contents[3]))
            if 'Excitation energy' in line:
                contents = line.split()
                if units == 'eV':
                    poles.append(float(contents[5]))
                elif units == 'nm':
                    poles.append(float(contents[7]))
                else:
                    print('Units: %s not available' % units)

    if program == 'QChem':
        for line in searchfile:
            if 'Strength' in line:
                contents = line.split()
                osc.append(float(contents[2]))
            if 'excitation energy' in line:
                contents = line.split()
                if units == 'eV':
                    poles.append(float(contents[7]))
                elif units == 'nm':
                    poles.append(1240 / float(contents[7]))
                else:
                    print('Units: %s not available' % units)

    if program == 'Gaussian':
        for line in searchfile:
            if ' Excited State  ' in line:
                contents = line.split()
                osc.append(float(contents[8].split("=")[1]))

                if units == 'eV':
                    poles.append(float(contents[4]))
                elif units == 'nm':
                    poles.append(float(contents[6]))
                else:
                    print('Units: %s not available' % units)

    if program == 'ORCA':
        for line in searchfile:
            if 'STATE ' in line and units == 'eV':
                poles.append(float(contents[5]))

            if 'ABSORPTION SPECTRUM VIA TRANSITION ELECTRIC DIPOLE MOMENTS' in line:
                searchfile.readline()
                searchfile.readline()
                searchfile.readline()
                searchfile.readline()
                temp = searchfile.readline()
                while len(temp.split()) > 0:
                    contents = temp.split()
                    if units == 'nm':
                        poles.append(float(contents[2]))
                    osc.append(float(contents[3]))
                    temp = searchfile.readline()

    searchfile.close()

    osc.append(0)
    poles.append(700)

    return osc, poles

def combine_calculations(f_names, program, units):
    ''' Finds all the oscillator strengths and excitation energies (poles)
        from a list of Gaussian output files
    '''

    # search each file and combine the oscillator strengths
    # and poles into a single list
    combined_osc, combined_poles = [], []
    osc, poles = search_file(f_names, program, units)
    combined_poles += poles
    combined_osc += osc

    return combined_osc, combined_poles

def broaden_spectrum(osc, poles, b_type, sigma):
    ''' Broaden poles to have a particular line shape '''

    npnts = 3000

    # define the range of frequencies
    pole_min, pole_max = min(poles) - 4, max(poles) + 4
    freq_step = (pole_max - pole_min) / npnts
    freq = [pole_min + i * freq_step for i in range(npnts)]

    # Build absorption spectrum by brodening each pole
    Abs = np.zeros([npnts])
    for i in range(len(osc)):
        #       print 'Energy = %.4f, Osc = %.4f' % (poles[i], osc[i])
        for j in range(npnts):
            if b_type == 'lorentz':
                x = (poles[i] - freq[j]) / (sigma / 2)
                Abs[j] += osc[i] / (1 + x ** 2)
            else:
                print('Broadening Scheme %s NYI' % b_type)

    return Abs, freq

def plot_spectrum(Abs, freq, osc, poles, units, df):
    fig = plt.figure()
    ax1 = fig.add_subplot(211)  # .gca()
    ax2 = fig.add_subplot(212)

    y_uv = df[1]
    x_uv = df[0]
    ax1.plot(x_uv, y_uv, color='r', label='Experimental')
    ax1.set_ylabel('Absorbance')
    ax1.legend()
    # ax1.tick_params(axis='x', labelbottom=False, bottom=False)
    ax1.set_xlim(250, 600)

    ax2.plot(freq, Abs, color='b', label="Computed")
    ax2.vlines(poles, [0], osc, label="Computed transitions")
    # ax2.invert_xaxis()  # sometimes helpful to invert axis if using nm
    ax2.set_ylabel('Relative Stength')
    ax2.legend()
    ax2.set_xlim(250, 600)

    plt.xlabel('Wavelength (%s)' % units)

def plot_spectrum_TD(Abs, freqs, osc, poles, units):
    fig = plt.figure()
    ax2 = fig.add_subplot(111)
    ax2.plot(freqs, Abs, color='b', label="Computed")
    ax2.vlines(poles, [0], osc, label="Computed transitions")
    # ax2.invert_xaxis()  # sometimes helpful to invert axis if using nm
    ax2.set_ylabel('Relative Stength')
    ax2.legend()
    ax2.set_xlim(200, 700)

    plt.xlabel('Wavelength (%s)' % units)

def get_program(outpath):
    searchfile = open(outpath, "r")
    program = ""
    for line in searchfile:
        if 'Jaguar version ' in line:
            program = "Jaguar"
            break
        if 'Q-Chem version' in line:
            program = "QChem"
            break
        if 'Entering Gaussian System' in line:
            program = "Gaussian"
            break
        if 'O   R   C   A' in line:
            program = "ORCA"
            break
    searchfile.close()

    return program

def read_files(uvpath, outpath):
    # designate TD-DFT calculation and UV-Vis spectrum
    #uvdata = pd.read_csv(uvpath)
    #df = pd.DataFrame(uvdata)

    # identify program
    program = get_program(outpath)

    # grab oscillators and poles and broaden
    broaden, sigma, units = 'lorentz', 10, 'nm'
    osc, poles = combine_calculations(outpath, program, units)
    Abs, freqs = broaden_spectrum(osc, poles, broaden, sigma)

    # shift spectrum and plot
    shift = 0.0  # eV
    freqs = [freq + shift for freq in freqs]
    poles = [pole + shift for pole in poles]

    # plot_spectrum(Abs, freqs, osc, poles, units, df)
    plot_spectrum_TD(Abs, freqs, osc, poles, units)

    plt.show()
