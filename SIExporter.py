import os
import sys
import re

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
        self.setWindowIcon(QIcon('gui\icons\SI_Convertor.png'))

        self.btnPath.pressed.connect(self.btnPathClicked)
        self.btnConvert.pressed.connect(self.btnConvertClicked)

    @pyqtSlot()
    def btnPathClicked(self):
        fname = QFileDialog.getExistingDirectory(self, "Select Root Directory")
        self.txtRootPath.setText(fname)

    def btnConvertClicked(self):
        try:
            if (not self.txtRootPath.text()) or (not os.path.isdir(self.txtRootPath.text())):
                QMessageBox.question(self, "Notice", "Please enter root path properly!", QMessageBox.Ok)

            else:
                toConvert = self.txtAreatoConvert.toPlainText().split("\n")
                rootPath = self.txtRootPath.text()
                coordPath = self.txtCoordinatesPath.text()
                freqPath = self.txtFrequenciesPath.text()

                if not (os.path.isdir(Path(coordPath).parent)):
                    os.makedirs(Path(coordPath).parent)
                if not (os.path.isdir(Path(freqPath).parent)):
                    os.makedirs(Path(freqPath).parent)

                for list in toConvert:
                    CalcPath = ""
                    if (os.path.isdir(rootPath + "/" + list.split()[0])):
                        CalcPath = rootPath + "/" + list.split()[0]
                    else:
                        if(os.path.isfile(rootPath+"/"+list.split()[0]+".out")):
                            CalcPath = rootPath
                        else:
                            QMessageBox.question(self, "Error", "Your calculation "+rootPath+"/"+list.split()[0]+".out does not exist!", QMessageBox.Ok)
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
                        QMessageBox.question(self, "Notice",
                                             "Your calculation ID " + list.split[0] + "cannot be classified.",
                                             QMessageBox.Ok)

        except:
            QMessageBox.question(self, "Notice", "Please enter root path, filenames and labels properly!",
                                 QMessageBox.Ok)


def get_program(CalcPath, outname):
    outpath = CalcPath + "/" + outname + ".out"
    outFile = open(outpath, 'r')
    line = ""
    program_determined = False
    program = ""
    while (not program_determined):
        line = outFile.readline()
        if "Jaguar version " in line:
            program = "Jaguar"
            program_determined = True
            break
        elif "Q-Chem version" in line:
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

    line = ""
    while True:
        line = outFile.readline()
        if not line: break

        if line.startswith("  frequencies"):
            line = line.strip()
            freq = ""
            for i in range(len(line.split()) - 1):
                freq = freq + "%8s" % line.split()[i+1]
            freq_txt.write(freq+"\n")

        elif line.startswith(" Input geometry:"):
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

    coord_txt.close()
    coord_xyz.close()
    freq_txt.close()
    outFile.close()


def SI_Gaussian(CalcPath, list, coordPath, freqPath):
    CalcID = list.split()[0]
    outpath = CalcPath + "/" + CalcID + ".out"
    outFile = open(outpath, 'r')
    label = list.split()[1]
    coord_txt = open(coordPath, 'a')
    coord_xyz = open(coordPath.replace('.txt', '.xyz'), 'a')
    freq_txt = open(freqPath, 'a')

    coord_txt.write("===============================\n"+label+"\n===============================\n")
    freq_txt.write("===============================\n"+label+"\n===============================\n")

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

    coord_txt.close()
    coord_xyz.close()
    freq_txt.close()
    outFile.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = SIExporterMainWindow()
    w.show()
    app.exec()
