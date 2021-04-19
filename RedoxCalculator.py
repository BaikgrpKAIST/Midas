import math
import os
import sys

from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QMessageBox

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

form = resource_path("gui/RedoxCalculator.ui")
form_class = uic.loadUiType(form)[0]

class RedoxCalculatorMainWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        #Setup icon
        self.setWindowIcon(QIcon(resource_path('gui\icons\RedoxPotential.png')))

        self.btnCalculate.pressed.connect(self.btnCalculateClicked)
        self.btnClear.pressed.connect(self.btnClearClicked)

    @pyqtSlot()
    def btnCalculateClicked(self):
        try:
            energy1 = float(self.txtEnergy1.text())
            energy2 = float(self.txtEnergy2.text())
            G_sol = energy2 - energy1
            SHE = 0.0
            if self.radio1.isChecked():
                SHE = 4.28
            elif self.radio2.isChecked():
                SHE = 4.43

            if G_sol > 0:
                QMessageBox.question(self, "Notice", "G(Sol) for A should be larger than G(Sol) for A(-1).", QMessageBox.Ok)
            else:
                Correction = float(self.comboRefElectrode.currentText().split()[3])
                RedPot = (-1*G_sol) - SHE - Correction
                self.txtRedoxPot.setText(str(round(RedPot,2)))

        except:
            QMessageBox.question(self, "Notice", "Please enter proper values.", QMessageBox.Ok)

    def btnClearClicked(self):
        self.txtEnergy1.setText("")
        self.txtEnergy2.setText("")
        self.txtRedoxPot.setText("")

