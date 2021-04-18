import math
import os
import sys


from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow
from qtconsole.qt import QtGui


def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

form_MidasMain = uic.loadUiType(resource_path("gui/MidasMain.ui"))[0]

class MidasMain(QMainWindow, form_MidasMain):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        #Setup icons
        self.btnSelectivity.setIcon(QtGui.QIcon("gui\icons\Selectivity.png"))
        self.btnRedox.setIcon(QtGui.QIcon("gui\icons\RedoxPotential.png"))
        self.btnSIExporter.setIcon(QtGui.QIcon("gui\icons\SI_Convertor.png"))
        self.btnEProfile.setIcon(QtGui.QIcon("gui\icons\Chemdraw48.png"))

        #Button clicked events
        self.btnSelectivity.setIcon(QtGui.QIcon("gui\icons\Selectivity.png"))
        self.btnRedox.setIcon(QtGui.QIcon("gui\icons\RedoxPotential.png"))
        self.btnSIExporter.setIcon(QtGui.QIcon("gui\icons\SI_Convertor.png"))
        self.btnEProfile.setIcon(QtGui.QIcon("gui\icons\Chemdraw48.png"))


    @pyqtSlot()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MidasMain()
    w.show()
    app.exec()