import os
import sys
import re

from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QFileDialog, QApplication, QColorDialog
from PyQt5.QtGui import QIcon, QColor
from pathlib import Path

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


form = resource_path("gui/EProfilePlotter.ui")
form_class = uic.loadUiType(form)[0]


class EProfilePlotterMainWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Setup icon
        self.setWindowIcon(QIcon(resource_path('gui\icons\Chemdraw48.png')))

        self.btnPath.pressed.connect(self.btnPathClicked)
        self.btnInfo.pressed.connect(self.btnInfoClicked)
        self.btnAdd.pressed.connect(self.btnAddClicked)
        self.btnClear.pressed.connect(self.btnClearClicked)
        self.btnColor.pressed.connect(self.btnColorClicked)

    @pyqtSlot()
    def btnPathClicked(self):
        fname = QFileDialog.getExistingDirectory(self, "Select Root Directory")
        self.txtPath.setText(fname)

    def btnInfoClicked(self):
        QMessageBox.information(self, "About energy profile plotter", "Initial code by Dr. Florian Mulks (Google colab).\nRewritten in Python by Dr. Jinhoon Jeong.\nModified by Hoimin Jung and Mina Son @ Baikgroup KAIST", QMessageBox.Ok)

    def btnAddClicked(self):
        self.txtToConvert.appendPlainText("["+self.txtEnergySequence.text()+"] "+self.comboFontSize.currentText()+" "+self.comboCurveLevel.currentText()+" "+self.comboWidthRatio.currentText())

    def btnClearClicked(self):
        self.txtToConvert.setPlainText("")

    def btnColorClicked(self):
        col = QColorDialog.getColor()
        col_comp = QColor(255-col.getRgb()[0], 255-col.getRgb()[1], 255-col.getRgb()[2])
        self.btnColor.setStyleSheet('QWidget{color: '+col_comp.name()+'; background-color: '+col.name()+';}')
        #print(self.btnColor.styleSheet().split(':')[-1].strip()[0:7])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = EProfilePlotterMainWindow()
    ex.show()
    sys.exit(app.exec_())
