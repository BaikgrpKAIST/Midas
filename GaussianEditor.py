import math
import os
import shutil
import sys

from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox

import PeriodicTable


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

form = resource_path(resource_path("gui/GaussianEditor.ui"))
form_class = uic.loadUiType(form)[0]


class GaussianEditorMainWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        #Enable DnD
        self.setAcceptDrops(True)

        #button click action
        self.btnClear.pressed.connect(self.btnClearClicked)
        self.btnRefresh.pressed.connect(self.btnRefreshClicked)
        self.btnSave.pressed.connect(self.btnSaveClicked)

        #MiscActions --> btnRefreshClicked
        self.checkBoxCurrentFolder.stateChanged.connect(self.btnRefreshClicked)
        self.checkBoxChk.stateChanged.connect(self.btnRefreshClicked)
        self.checkBoxUnrestricted.stateChanged.connect(self.btnRefreshClicked)
        self.chkBoxCopyChk.stateChanged.connect(self.btnRefreshClicked)

        self.comboBoxCalcType.currentTextChanged.connect(self.btnRefreshClicked)

        self.txtJobName.textChanged.connect(self.btnRefreshClicked)
        self.txtNumProc.textChanged.connect(self.btnRefreshClicked)
        self.txtMemory.textChanged.connect(self.btnRefreshClicked)
        self.txtFunctional.textChanged.connect(self.btnRefreshClicked)
        #self.txtBasisSetMain.textChanged.connect(self.btnRefreshClicked)
        #self.txtBasisSetSub.textChanged.connect(self.btnRefreshClicked)
        self.txtCharge.textChanged.connect(self.btnRefreshClicked)
        self.txtMultiplicity.textChanged.connect(self.btnRefreshClicked)
        self.txtAdditionalKeywords.textChanged.connect(self.btnRefreshClicked)
        self.txtSolvationModel.textChanged.connect(self.btnRefreshClicked)
        self.txtSolvent.textChanged.connect(self.btnRefreshClicked)
        self.txtScanParam.textChanged.connect(self.btnRefreshClicked)

        #Setup icon
        #self.setWindowIcon(QIcon('gui\icons\Selectivity.png'))

    @pyqtSlot()
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        for f in files:
            if (os.path.splitext(f)[-1] == '.xyz'):
                try:
                    self.txtXYZPath.setText(f)
                    self.txtSavePath.setText(os.path.splitext(f)[0]+".dat")
                    self.txtJobName.setText(os.path.basename(f).split('.')[0])
                except:
                    pass
            if (os.path.splitext(f)[-1] == '.chk'):
                try:
                    self.txtCHKPath.setText(f)
                except:
                    pass

        self.btnRefreshClicked()

    def btnClearClicked(self):
        try:
            self.txtXYZPath.setText("")
            self.txtCHKPath.setText("")
            self.txtSavePath.setText("")
            self.txtJobName.setText("")
        except:
            pass

    def btnRefreshClicked(self):
        #General setting
        self.txtInputPreview.clear()
        self.txtInputPreview.appendPlainText("%nproc="+self.txtNumProc.text())
        self.txtInputPreview.appendPlainText("%mem="+self.txtMemory.text())
        if self.checkBoxChk.isChecked():
            self.txtInputPreview.appendPlainText("%chk=" + self.txtJobName.text() + ".chk")

        #Calctype setting
        try:
            self.txtInputPreview.appendPlainText("#p")
            if self.comboBoxCalcType.currentText() == "GO+Freq":
                self.txtInputPreview.appendPlainText("opt")
                self.txtInputPreview.appendPlainText("freq=noraman")
                if not self.chkBoxFixBasisSet.isChecked():
                    self.txtBasisSetMain.setText("6-31G**")
                    self.txtBasisSetSub.setText("LANL2DZ")

            elif self.comboBoxCalcType.currentText() == "TS+Freq":
                self.txtInputPreview.appendPlainText("opt=(ts, calcfc, noeigen)")
                self.txtInputPreview.appendPlainText("freq=noraman")
                if not self.chkBoxFixBasisSet.isChecked():
                    self.txtBasisSetMain.setText("6-31G**")
                    self.txtBasisSetSub.setText("LANL2DZ")

            elif self.comboBoxCalcType.currentText() == "SP Solv":
                if self.txtSolvent.text().isalpha():
                    self.txtInputPreview.appendPlainText("scrf=("+self.txtSolvationModel.text()+", solvent="+self.txtSolvent.text()+")")
                else:
                    self.txtInputPreview.appendPlainText("scrf=("+self.txtSolvationModel.text()+", read)")

                self.txtInputPreview.appendPlainText("pop=(nbo,full)")
                if not self.chkBoxFixBasisSet.isChecked():
                    self.txtBasisSetMain.setText("6-311+G**")
                    self.txtBasisSetSub.setText("SDD")

            elif self.comboBoxCalcType.currentText() == "IRC":
                self.txtInputPreview.appendPlainText("irc= (rcfc, LQA, maxpoints=40)")
                if not self.chkBoxFixBasisSet.isChecked():
                    self.txtBasisSetMain.setText("6-31G**")
                    self.txtBasisSetSub.setText("LANL2DZ")

            elif self.comboBoxCalcType.currentText() == "Scan":
                self.txtInputPreview.appendPlainText("opt=modredundant")
                if not self.chkBoxFixBasisSet.isChecked():
                    self.txtBasisSetMain.setText("6-31G**")
                    self.txtBasisSetSub.setText("LANL2DZ")

            elif self.comboBoxCalcType.currentText() == "GO Opt":
                self.txtInputPreview.appendPlainText("opt")
                if not self.chkBoxFixBasisSet.isChecked():
                    self.txtBasisSetMain.setText("6-31G**")
                    self.txtBasisSetSub.setText("LANL2DZ")

            elif self.comboBoxCalcType.currentText() == "TS Opt":
                self.txtInputPreview.appendPlainText("opt=(ts, calcfc, noeigen)")
                if not self.chkBoxFixBasisSet.isChecked():
                    self.txtBasisSetMain.setText("6-31G**")
                    self.txtBasisSetSub.setText("LANL2DZ")

            elif self.comboBoxCalcType.currentText() == "Freq":
                self.txtInputPreview.appendPlainText("freq=noraman")
                if not self.chkBoxFixBasisSet.isChecked():
                    self.txtBasisSetMain.setText("6-31G**")
                    self.txtBasisSetSub.setText("LANL2DZ")

            elif self.comboBoxCalcType.currentText() == "SP":
                self.txtInputPreview.appendPlainText("pop=(nbo,full)")
                if not self.chkBoxFixBasisSet.isChecked():
                    self.txtBasisSetMain.setText("6-311+G**")
                    self.txtBasisSetSub.setText("SDD")

        except:
            pass


        #Functional & basis set
        try:
            self.functional = ""

            if self.checkBoxUnrestricted.isChecked():
                self.functional = self.functional + "u"

            if (self.txtFunctional.text().endswith("-D3")):
                self.functional = self.functional + self.txtFunctional.text().split("-D3")[0]
                self.txtInputPreview.appendPlainText(self.functional + "/gen")
                self.txtInputPreview.appendPlainText("EmpiricalDispersion=GD3")

            else:
                self.functional = self.functional + self.txtFunctional.text()
                self.txtInputPreview.appendPlainText(self.functional + "/gen")
        except:
            pass

        #ECP check
        try:
            self.AllAtoms = getAtoms(self.txtXYZPath.text())
            self.NormalAtoms, self.ECPAtoms = classifyAtoms(self.AllAtoms)

            if (len(self.ECPAtoms)>0):
                self.txtInputPreview.appendPlainText("pseudo=read")

        except:
            pass

        #Guess =  read
        try:
            if self.chkBoxCopyChk.isChecked():
                self.txtInputPreview.appendPlainText("guess=read")
        except:
            pass

        #Other general settings
        try:
            self.txtInputPreview.appendPlainText("scf=(maxcycle=300)")
            self.txtInputPreview.appendPlainText("nosym")
            self.txtInputPreview.appendPlainText("int=ultrafine")
        except:
            pass

        #Additional Keywords
        try:
            self.additionalKeys = self.txtAdditionalKeywords.text()
            if not self.additionalKeys == "":
                for self.keys in self.additionalKeys.split():
                    self.txtInputPreview.appendPlainText(self.keys)
        except:
            pass

        #Title Charge Multiplicity
        try:
            self.txtInputPreview.appendPlainText("\n"+self.txtJobName.text()+"\n")
            self.txtInputPreview.appendPlainText(self.txtCharge.text()+" "+self.txtMultiplicity.text())
        except:
            pass

        #Print coordinates
        try:
            if os.path.isfile(self.txtXYZPath.text()):
                self.XYZFile = open (self.txtXYZPath.text(), 'r')
                while True:
                    self.line = self.XYZFile.readline()
                    if not self.line: break

                    if (len(self.line.split()) == 4):
                        self.txtInputPreview.appendPlainText(self.line.strip())

                self.XYZFile.close()
        except:
            pass

        #Scan input
        try:
            if self.comboBoxCalcType.currentText() == "Scan":
                self.txtInputPreview.appendPlainText("\n"+self.txtScanParam.text())
        except:
            pass

        #Print basis set
        try:
            self.AllAtoms = getAtoms(self.txtXYZPath.text())
            self.NormalAtoms, self.ECPAtoms = classifyAtoms(self.AllAtoms)

            self.txtInputPreview.appendPlainText("")

            #print main basis set
            if len(self.NormalAtoms) > 0:
                self.atom_list = ""
                for self.atom in self.NormalAtoms:
                    self.atom_list = self.atom_list + self.atom + " "
                self.txtInputPreview.appendPlainText(self.atom_list + "0")
                self.txtInputPreview.appendPlainText(self.txtBasisSetMain.text())
                self.txtInputPreview.appendPlainText("****")

            #print sub basis set
            if len(self.ECPAtoms) > 0:
                self.atom_list = ""
                for self.atom in self.ECPAtoms:
                    self.atom_list = self.atom_list + self.atom + " "
                self.txtInputPreview.appendPlainText(self.atom_list + "0")
                self.txtInputPreview.appendPlainText(self.txtBasisSetMain.text())
                self.txtInputPreview.appendPlainText("****\n")

                self.txtInputPreview.appendPlainText(self.atom_list + "0")
                self.txtInputPreview.appendPlainText(self.txtBasisSetMain.text())
                self.txtInputPreview.appendPlainText("****")

        except:
            pass

        #Solvation additional input
        try:
            if self.comboBoxCalcType.currentText() == "SP Solv":
                if not self.txtSolvent.text().isalpha():
                    self.txtInputPreview.appendPlainText("\neps="+self.txtSolvent.text()+"\n")
        except:
            pass

        #Dummy lines
        try:
            self.txtInputPreview.appendPlainText("\n")
        except:
            pass

        #Refresh save path
        try:
            if self.checkBoxCurrentFolder.isChecked():
                self.parent_path = os.path.dirname(self.txtXYZPath.text())
                self.txtSavePath.setText(self.parent_path+"/"+self.txtJobName.text()+".dat")
            else:
                self.parent_path = os.path.dirname(self.txtXYZPath.text())
                self.project_path = os.path.dirname(self.parent_path)
                self.txtSavePath.setText(self.project_path+"/"+self.txtJobName.text()+"/"+self.txtJobName.text()+".dat")

        except:
            pass

    def btnSaveClicked(self):
        try:
            self.write_input = False
            if os.path.exists(self.txtSavePath.text()):
                self.reply = QMessageBox.information(self,"Notice", "Do you want to overwrite file?", QMessageBox.Yes | QMessageBox.No)
                if self.reply == QMessageBox.Yes:
                    self.write_input = True

            else:
                if os.path.isdir(os.path.dirname(self.txtSavePath.text())):
                    self.write_input = True
                else:
                    os.makedirs(os.path.dirname(self.txtSavePath.text()))
                    self.write_input = True

            if self.write_input == True:
                self.DatFile = open(self.txtSavePath.text(), 'w')
                self.DatFile.write(self.txtInputPreview.toPlainText())
                self.DatFile.close()

                if not os.path.isfile(os.path.splitext(self.txtSavePath.text())[0]+".xyz"):
                    shutil.copyfile(self.txtXYZPath.text(), os.path.splitext(self.txtSavePath.text())[0] + ".xyz")

                if self.chkBoxCopyChk.isChecked():
                    if os.path.isfile(self.txtCHKPath.text()):
                        shutil.copyfile(self.txtCHKPath.text(), os.path.splitext(self.txtSavePath.text())[0]+".chk")

                QMessageBox.information(self, "Notice", "Saved.", QMessageBox.Ok)
                os.startfile(os.path.dirname(self.txtSavePath.text()))
        except:
            pass

def getAtoms(xyz_path):
    atoms = []
    if os.path.isfile(xyz_path):
        XYZFile = open(xyz_path, 'r')
        while True:
            line = XYZFile.readline()
            if not line: break

            if (len(line.strip().split()) > 3):
                atom_tmp = line.strip().split()[0]
                c = list(filter(str.isalpha, atom_tmp))
                atom_tmp = ''.join(c)

                if not atom_tmp in atoms:
                    atoms.append(atom_tmp)
        XYZFile.close()

    return atoms

def classifyAtoms(AllAtoms):
    NormalAtoms = []
    ECPAtoms = []

    for atom in AllAtoms:
        if (PeriodicTable.getNumber(atom) > 20):
            ECPAtoms.append(atom)
        else:
            NormalAtoms.append(atom)

    return NormalAtoms, ECPAtoms