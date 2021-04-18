import math
import os
import sys

from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

form = resource_path("gui/SelectivityCalculator.ui")
form_class = uic.loadUiType(form)[0]


def getSelectivity(energy, temperature):
    kelvin = float(temperature) + 273.15
    energyVal = float(energy)
    calc = (energyVal * 4.18 * 1000) / (8.3145 * kelvin)
    selectivity = math.exp(-1 * calc)
    return selectivity

def getEnergy(selectivity, temperature):
    kelvin = float(temperature) + 273.15
    calc = math.log(1/float(selectivity))
    energy = (-1 * calc * 8.3145 * kelvin) / (4.18 * 1000)
    return energy

class SelectivityCalculatorMainWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.btnCalculate.pressed.connect(self.btnCalculateClicked)
        self.btnClear.pressed.connect(self.btnClearClicked)

    @pyqtSlot()
    def btnCalculateClicked(self):
        temperature = self.txtTemperature.text()
        energy = self.txtEnergy.text()
        selectivity = self.txtSelectivity.text()

        if energy != "":
            computed_selectivity = "%.2f" %(1/getSelectivity(energy, temperature))
            self.txtSelectivity.setText(computed_selectivity)

        elif selectivity != "" and energy == "":
            computed_energy = "%.2f" %(getEnergy(selectivity, temperature))
            self.txtEnergy.setText(computed_energy)

        else:
            QMessageBox.question(self, "Notice", "Please enter energy or selectivity value.", QMessageBox.Ok)

    def btnClearClicked(self):
        self.txtEnergy.setText("")
        self.txtSelectivity.setText("")

