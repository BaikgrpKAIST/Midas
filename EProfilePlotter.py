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

        # Actions
        self.btnPath.pressed.connect(self.btnPathClicked)
        self.btnInfo.pressed.connect(self.btnInfoClicked)
        self.btnAdd.pressed.connect(self.btnAddClicked)
        self.btnClear.pressed.connect(self.btnClearClicked)
        self.btnColor.pressed.connect(self.btnColorClicked)
        self.btnConvert.pressed.connect(self.btnConvertedClicked)

    @pyqtSlot()
    def btnPathClicked(self):
        fname = QFileDialog.getExistingDirectory(self, "Select Root Directory")
        self.txtPath.setText(fname)

    def btnInfoClicked(self):
        QMessageBox.information(self, "About energy profile plotter",
                                "Initial code by Dr. Florian Mulks (Google colab).\nRewritten in Python by Dr. Jinhoon Jeong.\nModified by Hoimin Jung and Mina Son @ Baikgroup KAIST",
                                QMessageBox.Ok)

    def btnAddClicked(self):
        energy_seq = self.txtEnergySequence.text()
        font_size = self.comboFontSize.currentText()
        color_code = self.btnColor.styleSheet().split(':')[-1].strip()[0:7]
        curve_level = self.comboCurveLevel.currentText()
        width_ratio = self.comboWidthRatio.currentText()

        self.txtToConvert.appendPlainText(
            "[" + energy_seq + "] " + font_size + " " + color_code + " " + curve_level + " " + width_ratio)

    def btnClearClicked(self):
        self.txtToConvert.setPlainText("")

    def btnColorClicked(self):
        col = QColorDialog.getColor()
        col_comp = QColor(255 - col.getRgb()[0], 255 - col.getRgb()[1], 255 - col.getRgb()[2])
        self.btnColor.setStyleSheet('QWidget{color: ' + col_comp.name() + '; background-color: ' + col.name() + ';}')

    def btnConvertedClicked(self):
        toConvert = self.txtToConvert.toPlainText().split("\n")
        rootPath = self.txtPath.text()
        filename = self.txtFileName.text()
        filePath = rootPath + "/" + filename + ".cdxml"

        if not (os.path.isdir(Path(rootPath))):
            os.makedirs(Path(rootPath))

        #Get colors
        colortable = []
        for line in toConvert:
            colortable.append(line.split("]")[1].split()[1])

        initialize_file(filePath, colortable)

        #Write cdxml file
        for line in toConvert:
            curr_energy = line.split("]")[0].split("[")[1]
            width = line.split("]")[1].split()[3]
            curve = line.split("]")[1].split()[2]
            font_size = line.split()[1]

            generate_curve(filePath, curr_energy, width, curve, colortable, font_size)

        finalize_file(filePath)

def initialize_file(filePath, colortable):
    cdxml_file = open(filePath, 'w')

    #General info write
    cdxml_file.write("<?xml version=\"1.0\" encoding=\"UTF-8\" ?>\n"
                    + " <!DOCTYPE CDXML SYSTEM \"http://www.cambridgesoft.com/xml/cdxml.dtd\" >\n"
                    + " <CDXML><fonttable>\n" + "<font id=\"3\" charset=\"iso-8859-1\" name=\"Arial\"/>\n<font id=\"7\" charset=\"Unknown\" name=\"Symbol\"/>\n"
                    + "</fonttable>\n")

    #color info
    cdxml_file.write("<colortable>\n<color r=\"1\" g=\"1\" b=\"1\"/>\n<color r=\"0\" g=\"0\" b=\"0\"/>\n")
    for color in colortable:
        col = QColor(color)
        col_r = int(col.getRgb()[0])
        col_g = int(col.getRgb()[1])
        col_b = int(col.getRgb()[2])
        cdxml_file.write("<color r=\"" + str(round(col_r / 255, 2)) + "\" g=\"" + str(round(col_g / 255,2)) + "\" b=\"" + str(round(col_b / 255, 2)) + "\"/>\n")
    cdxml_file.write("</colortable>")

    # Page setup
    cdxml_file.write("<page\n"
                     + " id=\"6\"\n"
                     + " BoundingBox=\"0 0 523.20 769.68\"\n"
                     + " HeaderPosition=\"36\"\n"
                     + " FooterPosition=\"36\"\n"
                     + " PrintTrimMarks=\"yes\"\n"
                     + " HeightPages=\"1\"\n"
                     + " WidthPages=\"1\"\n"
                     + ">\n")

    Arrow = "<arrow\n" + " id=\"13\"\n" + " BoundingBox=\"13.87 13.84 18.63 60\"\n" + " Z=\"6\"\n" + " LineWidth=\"0.85\"\n" + " FillType=\"None\"\n" + " ArrowheadHead=\"Full\"\n" + " ArrowheadType=\"Solid\"\n" + " HeadSize=\"1000\"\n" + " ArrowheadCenterSize=\"875\"\n" + " ArrowheadWidth=\"250\"\n" + " Head3D=\"16.50 13.84 0\"\n" + " Tail3D=\"16.50 64 0\"\n" + " Center3D=\"21.75 45.59 0\"\n" + " MajorAxisEnd3D=\"71.91 45.59 0\"\n" + " MinorAxisEnd3D=\"21.75 95.75 0\"\n" + "/>"

    G_sol = "<t\n" + " id=\"11\"\n" + " p=\"40.50 24.50\"\n" + " BoundingBox=\"20.99 15.45 60.01 37.65\"\n" + " Z=\"7\"\n" + " CaptionJustification=\"Center\"\n" + " Justification=\"Center\"\n" + " LineHeight=\"auto\"\n" + " LineStarts=\"8 18\"\n" + "><s font=\"7\" size=\"9\" color=\"0\" face=\"1\">D</s><s font=\"3\" size=\"9\" color=\"0\" face=\"1\">G(sol)\n" + "</s><s font=\"3\" size=\"9\" color=\"0\">(kcal/mol)</s></t>"

    cdxml_file.write(Arrow)
    cdxml_file.write(G_sol)

    cdxml_file.close()

def generate_curve(filePath, curr_energy, width, curve, colortable, font_size):
    cdxml_file = open(filePath, 'a')

    energy_arr = curr_energy.split()
    firstitem = float(energy_arr[0])

    inc_x = 0
    inc_y = 0
    start_x = 50
    start_y = 50 # + size
    horizontal = 212.8
    vertical = 770
    maxen = 0.0
    minen = 0.0
    curvature = float(curve)

    for item in energy_arr:
        if float(item) > maxen:
            maxen = float(item)
        if float(item) < minen:
            minen = float(item)

    x_spacing = float(horizontal/(len(energy_arr)))
    y_spacing = 5

    if (int(maxen) - int(minen)) > 100:
        y_spacing = 500/(int(maxen) - int(minen))

    points_list_x = []
    points_list_y = []

    for item in energy_arr:
        inc_y = float(item) - firstitem
        points_list_x.append(start_x + inc_x)
        points_list_y.append(start_y - inc_y * y_spacing)
        inc_x += x_spacing

    # Make the sequence for drawing the curves //
    curvepoints = ""
    minval = min(points_list_y)
    maxval = max(points_list_y)
    y_shift = points_list_y[0] - minval
    fix_y = float(font_size) + 3.0

    for i in range(len(points_list_x)):
        curvepoints = curvepoints + (" %.2f" % (points_list_x[i] - 3 * curvature)) + (" %.2f" % (points_list_y[i] + y_shift))
        curvepoints = curvepoints + (" %.2f" % points_list_x[i]) + (" %.2f" % (points_list_y[i] + y_shift))
        curvepoints = curvepoints + (" %.2f" % (points_list_x[i] + 3 * curvature)) + (" %.2f" % (points_list_y[i] + y_shift))
        dot = "<graphic\n BoundingBox=\"" + ("%.2f"% points_list_x[i]) + (" %.2f" % (points_list_y[i] + y_shift)) + " "
        dot = dot + ("%.2f" % points_list_x[i]) + (" %.2f" % (points_list_y[i] + 15 + y_shift)) + "\"\n color=\"4\"\n GraphicType=\"Symbol\"\n SymbolType=\"Electron\"\n/>\n"
        cdxml_file.write(dot)

        label_before = "<t\n" + " id=\"18\"\n" + " p=\"" + ("%.2f" % points_list_x[i]) + (" %.2f" % (points_list_y[i] + y_shift + fix_y)) + "\"\n" + " BoundingBox=\"" + ("%.2f" % points_list_x[i]) + (" %.2f" % (points_list_y[i] + y_shift)) + (" %.2f" % (points_list_x[i] + 25)) + (" %.2f" % (points_list_y[i] + 24 + y_shift)) + "\"\n" + " Z=\"13\"\n color=\"4\"\n" + " Warning=\"Chemical Interpretation is not possible for this label\"\n" + " CaptionJustification=\"Center\"\n" + " Justification=\"Center\"\n" + " LineHeight=\"auto\"\n" + " LineStarts=\"5 11\"\n" + "><s font=\"3\" size=\"" + font_size + "\" color=\"4\" face=\"1\">"
        label_middle = "</s><s font=\"4\" size=\"" + font_size + "\" color=\"4\">"
        label_end = "</s></t>"

        if (i % 2 == 0): # for intermediate
            label = str(int((i + 2) / 2))
            cdxml_file.write(label_before + label + "\n")
            energyval = "%.02f" % float(energy_arr[i])
            cdxml_file.write(label_middle + "(" + energyval + ")") # minus to en dash
            cdxml_file.write(label_end)
            fix_y = -1 * float(font_size) - 6

        else: # for TS
            label = str(int((i + 1) / 2)) + "-TS"
            cdxml_file.write(label_before + label + "\n")
            energyval = "%.02f" % float(energy_arr[i])
            cdxml_file.write(label_middle + "(" + energyval + ")")
            cdxml_file.write(label_end)
            fix_y = float(font_size) + 3

    cdxml_file.write("<curve\n id=\"4\"\n Z=\"1\"\n color=\"4\"\n LineWidth=\"" + width + "\"\n ArrowheadType=\"Solid\"\n CurvePoints=\"" + curvepoints)
    cdxml_file.write("\"\n/>\n")

    cdxml_file.close()

def finalize_file(filePath):
    cdxml_file = open(filePath, 'a')
    cdxml_file.write("</page></CDXML>")
    cdxml_file.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = EProfilePlotterMainWindow()
    ex.show()
    sys.exit(app.exec_())
