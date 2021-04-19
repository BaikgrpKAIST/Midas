import sys

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot


form_class = uic.loadUiType("TD-UVPlot.ui")[0]

class MainWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.btnConvert.pressed.connect(self.ConvertAction)

    @pyqtSlot()
    def ConvertAction(self):
        Exp_data_path = self.txtDataDir.text()
        TD_out_path = self.txtOutDir.text()
        #print(Exp_data_path + "\n" + TD_out_path)
        read_files(Exp_data_path, TD_out_path)


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
            if ' Excited State   ' in line:
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

    y_uv = df['HJ10-051']
    x_uv = df["Wavelength"]
    ax1.plot(x_uv, y_uv, color='r', label='Experimental')
    ax1.set_ylabel('Absorbance')
    ax1.legend()
    # ax1.tick_params(axis='x', labelbottom=False, bottom=False)
    ax1.set_xlim(200, 700)

    ax2.plot(freq, Abs, color='b', label="Computed")
    ax2.vlines(poles, [0], osc, label="Computed transitions")
    # ax2.invert_xaxis()  # sometimes helpful to invert axis if using nm
    ax2.set_ylabel('Relative Stength')
    ax2.legend()
    ax2.set_xlim(200, 700)

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
        if 'Entering Gaussian System,' in line:
            program = "Gaussian"
            break
        if 'O   R   C   A' in line:
            program = "ORCA"
            break
    searchfile.close()

    return program

def read_files(uvpath, outpath):
    # designate TD-DFT calculation and UV-Vis spectrum
    """
    outpath = 'TDDFT-output/HJ_tutorial_012_orca.out'
    uvdata = pd.read_csv("UV-master.csv")
    """
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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    app.exec()



