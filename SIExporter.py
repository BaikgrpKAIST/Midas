import os
import sys
import re
import PeriodicTable

from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QFileDialog, QApplication
from PyQt5.QtGui import QIcon
from pathlib import Path


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


form = resource_path("gui/SIExporter.ui")
form_class = uic.loadUiType(form)[0]


class SIExporterMainWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # Setup icon
        self.setWindowIcon(QIcon(resource_path('gui\icons\SI_Convertor.png')))

        self.btnPath.pressed.connect(self.btnPathClicked)
        self.btnConvert.pressed.connect(self.btnConvertClicked)

    @pyqtSlot()
    def btnPathClicked(self):
        fname = QFileDialog.getExistingDirectory(self, "Select Root Directory")
        self.txtRootPath.setText(fname)

    def btnConvertClicked(self):
        try:
            if (not self.txtRootPath.text()) or (not os.path.isdir(self.txtRootPath.text())):
                QMessageBox.information(self, "Notice", "Please enter root path properly!", QMessageBox.Ok)

            else:
                toConvert = self.txtAreatoConvert.toPlainText().split("\n")
                rootPath = self.txtRootPath.text()
                coordPath = self.txtCoordinatesPath.text()
                freqPath = self.txtFrequenciesPath.text()

                if not (os.path.isdir(Path(coordPath).parent)):
                    os.makedirs(Path(coordPath).parent)
                if not (os.path.isdir(Path(freqPath).parent)):
                    os.makedirs(Path(freqPath).parent)

                self.progressBar.setValue(0)
                steps = len(toConvert)
                current_step = 0
                error_list = []

                for list in toConvert:
                    current_step += 1

                    if list.strip() == "":
                        self.progressBar.setValue(int(100 * (current_step / steps)))
                        continue

                    CalcPath = ""
                    if (os.path.isdir(rootPath + "/" + list.split()[0])):
                        CalcPath = rootPath + "/" + list.split()[0]
                    else:
                        if(os.path.isfile(rootPath+"/"+list.split()[0]+".out") or os.path.isfile(rootPath+"/"+list.split()[0]+".log")):
                            CalcPath = rootPath
                        else:
                            QMessageBox.information(self, "Error", "Your calculation "+rootPath+"/"+list.split()[0]+".out does not exist!", QMessageBox.Ok)
                            error_list.append(list.split()[0])
                            continue
                    program_used = get_program(CalcPath, list.split()[0])

                    if program_used == "Jaguar":
                        SI_Jaguar(CalcPath, list, coordPath, freqPath)
                    elif program_used == "Qchem":
                        SI_Qchem(CalcPath, list, coordPath, freqPath)
                    elif program_used == "Gaussian":
                        SI_Gaussian(CalcPath, list, coordPath, freqPath)
                    elif program_used == "orca":
                        SI_ORCA(CalcPath, list, coordPath, freqPath)
                    else:
                        QMessageBox.information(self, "Notice",
                                             "Your calculation ID " + list.split[0] + "cannot be classified.",
                                             QMessageBox.Ok)

                    self.progressBar.setValue(int(100 * (current_step/steps)))

                QMessageBox.information(self, "Notice", "Finished Exportation!", QMessageBox.Ok)
                if len(error_list) > 0:
                    error_message = "Following calculation(s) did not exported:\n"
                    for i in range(len(error_list)):
                        error_message = error_message + error_list[i] + "\n"
                    QMessageBox.information(self, "Error", error_message, QMessageBox.Ok)

                os.startfile(Path(coordPath).parent)
                if coordPath != freqPath:
                    os.startfile(Path(freqPath).parent)

        except:
            QMessageBox.information(self, "Notice", "Please enter root path, filenames and labels properly!",
                                 QMessageBox.Ok)


def get_program(CalcPath, outname):
    outpath = CalcPath + "/" + outname + ".out"
    logpath = CalcPath + "/" + outname + ".log"

    #open outfile. If not, read logfile.
    outFile = None
    if os.path.isfile(outpath):
        outFile = open(outpath, 'r')
    elif os.path.isfile(logpath):
        outFile = open(logpath, 'r')

    line = ""
    program_determined = False
    program = ""
    while (not program_determined):
        line = outFile.readline()
        if "Jaguar version " in line:
            program = "Jaguar"
            program_determined = True
            break
        elif "Q-Chem" in line:
            program = "Qchem"
            program_determined = True
            break
        elif "Entering Gaussian System," in line:
            program = "Gaussian"
            program_determined = True
            break
        elif "O   R   C   A" in line:
            program = "orca"
            program_determined = True
            break
        else:
            pass
    outFile.close()
    return program


def SI_Jaguar(CalcPath, list, coordPath, freqPath):
    CalcID = list.split()[0]
    outpath = CalcPath + "/" + CalcID + ".out"
    outFile = open(outpath, 'r')
    label = list.split()[1]
    coord_txt = open(coordPath, 'a')
    coord_xyz = open(coordPath.replace('.txt', '.xyz'), 'a')
    freq_txt = open(freqPath, 'a')

    coord_txt.write("===============================\n"+label+"\n===============================\n")
    freq_txt.write("===============================\n"+label+"\n===============================\n")

    frequencies = ""
    coordinates = ""
    numatom = 0

    while True:
        line = outFile.readline()
        if not line: break

        #get freqencies
        if line.startswith("  frequencies"):
            freq = ""
            line = line.strip()
            for i in range(len(line.split()) - 1):
                freq = freq + "%8s" % line.split()[i+1]
            frequencies = frequencies + freq + "\n"

        #get coordinates
        elif line.startswith(" Input geometry:") or line.startswith("  final geometry:") or line.startswith("  new geometry:"):
            coordinates = ""
            numatom = 0

            outFile.readline()
            outFile.readline()
            line = outFile.readline().strip()
            while line.strip() != "":
                numatom += 1
                coord = "%4s" % re.sub('[0-9]+', '', line.strip().split()[0])
                for i in range(len(line.strip().split()) - 1):
                    coord = coord + ("%14.9f"% float(line.strip().split()[i+1]))
                line = outFile.readline()
                coordinates = coordinates + coord + "\n"

    #write files
    freq_txt.write(frequencies+"\n")
    coord_txt.write(coordinates + "\n")
    coord_xyz.write(str(numatom)+"\n")
    coord_xyz.write(label+"\n")
    coord_xyz.write(coordinates)

    coord_txt.close()
    coord_xyz.close()
    freq_txt.close()
    outFile.close()


def SI_Qchem(CalcPath, list, coordPath, freqPath):
    CalcID = list.split()[0]
    outpath = CalcPath + "/" + CalcID + ".out"
    outFile = open(outpath, 'r')
    label = list.split()[1]
    coord_txt = open(coordPath, 'a')
    coord_xyz = open(coordPath.replace('.txt', '.xyz'), 'a')
    freq_txt = open(freqPath, 'a')

    coord_txt.write("===============================\n"+label+"\n===============================\n")
    freq_txt.write("===============================\n"+label+"\n===============================\n")

    frequencies = ""
    coordinates = ""
    numatom = 0
    freq_count = 0

    while True:
        line = outFile.readline()
        if not line: break

        #get freqencies
        if "Frequency:" in line:
            freq_count += 1
            freq = ""
            line = line.strip()
            for i in range(len(line.split()) - 1):
                freq = freq + "%8s" % line.split()[i+1]

            frequencies = frequencies + freq
            if freq_count%2 == 0 : frequencies = frequencies + "\n"

        #get coordinates
        elif "Standard Nuclear Orientation (Angstroms)" in line:
            coordinates = ""
            numatom = 0

            outFile.readline()
            outFile.readline()
            line = outFile.readline().strip()
            while not ("----------" in line):
                numatom += 1
                coord = "%4s" % re.sub('[0-9]+', '', line.strip().split()[1])
                for i in range(len(line.strip().split()) - 2):
                    coord = coord + ("%14.9f"% float(line.strip().split()[i+2]))
                line = outFile.readline()
                coordinates = coordinates + coord + "\n"

    #write files
    freq_txt.write(frequencies+"\n")
    coord_txt.write(coordinates + "\n")
    coord_xyz.write(str(numatom)+"\n")
    coord_xyz.write(label+"\n")
    coord_xyz.write(coordinates)

    coord_txt.close()
    coord_xyz.close()
    freq_txt.close()
    outFile.close()



def SI_Gaussian(CalcPath, list, coordPath, freqPath):
    CalcID = list.split()[0]
    outpath = CalcPath + "/" + CalcID + ".out"
    logpath = CalcPath + "/" + CalcID + ".log"

    #open outfile. If not, read logfile.
    outFile = None
    if os.path.isfile(outpath):
        outFile = open(outpath, 'r')
    elif os.path.isfile(logpath):
        outFile = open(logpath, 'r')

    label = list.split()[1]
    coord_txt = open(coordPath, 'a')
    coord_xyz = open(coordPath.replace('.txt', '.xyz'), 'a')
    freq_txt = open(freqPath, 'a')

    coord_txt.write("===============================\n"+label+"\n===============================\n")
    freq_txt.write("===============================\n"+label+"\n===============================\n")

    frequencies = ""
    coordinates = ""
    numatom = 0
    freq_count = 0

    while True:
        line = outFile.readline()
        if not line: break

        #get freqencies
        if "Frequencies --" in line:
            freq_count += 1
            freq = ""
            line = line.strip()
            for i in range(len(line.split()) - 2):
                freq = freq + "%8s" % str(format(float(line.split()[i+2]),".2f"))

            frequencies = frequencies + freq
            if freq_count%2 == 0 : frequencies = frequencies + "\n"

        #get coordinates
        elif "Input orientation:" in line:
            coordinates = ""
            numatom = 0

            outFile.readline()
            outFile.readline()
            outFile.readline()
            outFile.readline()
            line = outFile.readline().strip()
            while not ("----------" in line.strip()):
                numatom += 1
                atom = PeriodicTable.getAtom(line.strip().split()[1])
                coord = "%4s" % atom
                for i in range(len(line.strip().split()) - 3):
                    coord = coord + ("%14.6f"% float(line.strip().split()[i+3]))
                line = outFile.readline()
                coordinates = coordinates + coord + "\n"

        elif "Standard orientation:" in line:
            coordinates = ""
            numatom = 0

            outFile.readline()
            outFile.readline()
            outFile.readline()
            outFile.readline()
            line = outFile.readline().strip()
            while not ("----------" in line.strip()):
                numatom += 1
                atom = PeriodicTable.getAtom(line.strip().split()[1])
                coord = "%4s" % atom
                for i in range(len(line.strip().split()) - 3):
                    coord = coord + ("%14.6f"% float(line.strip().split()[i+3]))
                line = outFile.readline()
                coordinates = coordinates + coord + "\n"

    #write files
    freq_txt.write(frequencies+"\n")
    coord_txt.write(coordinates + "\n")
    coord_xyz.write(str(numatom)+"\n")
    coord_xyz.write(label+"\n")
    coord_xyz.write(coordinates)

    coord_txt.close()
    coord_xyz.close()
    freq_txt.close()
    outFile.close()


def SI_ORCA(CalcPath, list, coordPath, freqPath):
    CalcID = list.split()[0]
    outpath = CalcPath + "/" + CalcID + ".out"
    outFile = open(outpath, 'r')
    label = list.split()[1]
    coord_txt = open(coordPath, 'a')
    coord_xyz = open(coordPath.replace('.txt', '.xyz'), 'a')
    freq_txt = open(freqPath, 'a')

    coord_txt.write("===============================\n"+label+"\n===============================\n")
    freq_txt.write("===============================\n"+label+"\n===============================\n")

    frequencies = ""
    coordinates = ""
    numatom = 0
    freq_count = 0

    while True:
        line = outFile.readline()
        if not line: break

        #get freqencies
        if "VIBRATIONAL FREQUENCIES" in line:
            freq = ""
            outFile.readline()
            outFile.readline()
            line = outFile.readline().strip()
            if "Scaling factor" in line:
                outFile.readline()
                line = outFile.readline().strip()
            while line.strip() != "":
                freq_count += 1
                freq = freq + "%8s" % line.strip().split()[1]
                if freq_count % 6 == 0: freq = freq + "\n"
                line = outFile.readline()

            frequencies = frequencies + freq

        #get coordinates
        elif "CARTESIAN COORDINATES (ANGSTROEM)" in line:
            coordinates = ""
            numatom = 0

            outFile.readline()
            line = outFile.readline().strip()
            while line.strip() != "":
                numatom += 1
                coord = "%4s" % re.sub('[0-9]+', '', line.strip().split()[0])
                for i in range(len(line.strip().split())-1):
                    coord = coord + ("%14.6f"% float(line.strip().split()[i+1]))
                line = outFile.readline()
                coordinates = coordinates + coord + "\n"

    #write files
    freq_txt.write(frequencies+"\n")
    coord_txt.write(coordinates + "\n")
    coord_xyz.write(str(numatom)+"\n")
    coord_xyz.write(label+"\n")
    coord_xyz.write(coordinates)

    coord_txt.close()
    coord_xyz.close()
    freq_txt.close()
    outFile.close()

