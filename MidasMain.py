import math
import os
import sys

import GaussianEditor
import SelectivityCalculator, RedoxCalculator, SIExporter, EProfilePlotter

from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtGui import QIcon


def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

form_MidasMain = uic.loadUiType(resource_path("gui/MidasMain.ui"))[0]

class MidasMainWindow(QMainWindow, form_MidasMain):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.statusBar.showMessage("Copyright(C) 2021. Baikgroup @ KAIST. All rights reserved.")

        #Setup icons
        self.setWindowIcon(QIcon('gui\icons\Main.png'))
        self.btnSelectivity.setIcon(QIcon(resource_path("gui\icons\Selectivity.png")))
        self.btnRedox.setIcon(QIcon(resource_path("gui\icons\RedoxPotential.png")))
        self.btnSIExporter.setIcon(QIcon(resource_path("gui\icons\SI_Convertor.png")))
        self.btnEProfile.setIcon(QIcon(resource_path("gui\icons\Chemdraw48.png")))

        #Button clicked events
        self.btnSelectivity.pressed.connect(self.openSelectivityCalculator)
        self.btnRedox.pressed.connect(self.openRedoxCalculator)
        self.btnSIExporter.pressed.connect(self.openSIExporter)
        self.btnEProfile.pressed.connect(self.openEProfilePlotter)
        #self.btnTDPlot.pressed.connect(self.openTDPlotter)
        self.btnG09.pressed.connect(self.openG09Editor)

    @pyqtSlot()
    def openSelectivityCalculator(self):
        self.a = SelectivityCalculator.SelectivityCalculatorMainWindow()
        self.a.show()

    def openRedoxCalculator(self):
        self.a = RedoxCalculator.RedoxCalculatorMainWindow()
        self.a.show()

    def openSIExporter(self):
        self.a = SIExporter.SIExporterMainWindow()
        self.a.show()

    def openEProfilePlotter(self):
        self.a = EProfilePlotter.EProfilePlotterMainWindow()
        self.a.show()


    #def openTDPlotter(self):
    #    self.a = TDUVplot.TDUVPlotMainWindow()
    #    self.a.show()


    def openG09Editor(self):
        self.a = GaussianEditor.GaussianEditorMainWindow()
        self.a.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MidasMainWindow()
    w.show()
    app.exec()