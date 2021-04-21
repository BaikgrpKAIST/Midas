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
        self.btnDefault.pressed.connect(self.btnDefaultClicked)
        self.btnConvert.pressed.connect(self.btnConvertedClicked)
        self.sliderCurveLevel.valueChanged.connect(self.changeValueCurveLevel)
        self.sliderLineWidth.valueChanged.connect(self.changeValueLineWidth)

    @pyqtSlot()
    def btnPathClicked(self):
        fname = QFileDialog.getExistingDirectory(self, "Select Root Directory")
        self.txtPath.setText(fname)

    def btnInfoClicked(self):
        QMessageBox.information(self, "About energy profile plotter",
                                "Initial code by Dr. Florian Mulks (Google colab).\nRewritten in Python by Dr. Jinhoon Jeong.\nModified by Hoimin Jung and Mina Son @ Baikgroup KAIST",
                                QMessageBox.Ok)

    def changeValueCurveLevel(self):
        value = int(self.sliderCurveLevel.value())
        self.txtCurveLevel.setText(str(value))

    def changeValueLineWidth(self):
        value = int(self.sliderLineWidth.value())
        self.txtLineWidth.setText(str(float(value/10)))

    def btnClearClicked(self):
        self.txtToConvert.setPlainText("")

    def btnColorClicked(self):
        col = QColorDialog.getColor()
        col_comp = QColor(255 - col.getRgb()[0], 255 - col.getRgb()[1], 255 - col.getRgb()[2])
        self.btnColor.setStyleSheet('QWidget{color: ' + col_comp.name() + '; background-color: ' + col.name() + ';}')

    def btnDefaultClicked(self):
        self.sliderCurveLevel.setValue(4)
        self.sliderLineWidth.setValue(10)
        self.comboFontSize.setCurrentIndex(3)
        self.btnColor.setStyleSheet('QWidget{color:#ffffff;\nbackground-color: #000000;}')

    def btnAddClicked(self):
        energy_seq = self.txtEnergySequence.text()
        font_size = self.comboFontSize.currentText()
        color_code = self.btnColor.styleSheet().split(':')[-1].strip()[0:7]
        curve_level = self.txtCurveLevel.text()
        width_ratio = self.txtLineWidth.text()

        #Energy sequence validity check
        temp = energy_seq.replace("-", "")
        temp = temp.replace(".", "")
        temp = "".join(temp.strip().split())
        if temp.isdigit():
            self.txtToConvert.appendPlainText(
                "[" + energy_seq + "] " + font_size + " " + color_code + " " + curve_level + " " + width_ratio)
        else:
            QMessageBox.information(self,"Notice", "Invalid energy sequence\nPlease write down numbers only.", QMessageBox.Ok)

    def btnConvertedClicked(self):
        if self.txtToConvert.toPlainText() == "":
            QMessageBox.information(self, "Notice", "Please add energy sequences.", QMessageBox.Ok)

        else:
            toConvert = self.txtToConvert.toPlainText().split("\n")
            rootPath = self.txtPath.text()
            filename = self.txtFileName.text()
            filePath = rootPath + "/" + filename + ".cdxml"

            if not (os.path.isdir(Path(rootPath))):
                os.makedirs(Path(rootPath))

            #File_exist check
            if os.path.isfile(Path(filePath)):
                reply = QMessageBox.question(self, "Notice", "Do you want to overwrite file "+filename+".cdxml?", QMessageBox.Yes|QMessageBox.No)
                if reply == QMessageBox.Yes:
                    pass
                elif reply == QMessageBox.No:
                    while True:
                        temp = 1
                        filename = filename.replace(filename, filename+"_"+str(temp))
                        filePath = rootPath + "/" + filename + ".cdxml"
                        if not os.path.isfile(Path(filePath)):
                            break

            #Get colors
            colortable = []
            for line in toConvert:
                colortable.append(line.split("]")[1].split()[1])

            #Initiate cdxml_file & write header
            writing_file(filePath, header(1,1, colortable), "w")

            y_size_list = 0.0
            #Write cdxml file
            for i in range(len(toConvert)):
                line = toConvert[i]
                try:
                    curr_energy = list(map(float, line.split("]")[0].split("[")[1].split()))
                    width = line.split("]")[1].split()[3]
                    curve = line.split("]")[1].split()[2]
                    font_size = int(line.split("]")[1].split()[0])
                    rel_dx = float(width)
                    rel_curv = float(curve) / 4

                    # starting point
                    max_val, min_val = max(curr_energy), min(curr_energy)
                    starting_point = [70, 50 + ((max_val - curr_energy[0] + y_size_list) * 5) + y_size_list]
                    y_size_list += (max_val - min_val) + 10

                    # setting for pages
                    #if (len(curr_energy) - 1) * 20 * rel_dx > 440: page_W = 2
                    #if diff_val * 5 + 70 > 750: page_H = 2

                    #make labels
                    curr_labels = []
                    for j in range(len(curr_energy)):
                        if j % 2 == 0:
                            temp_lb = "%d" % (j // 2 + 1)
                        else:
                            temp_lb = "%d-TS" % (j // 2 + 1)
                        curr_labels.append(temp_lb)

                    color_index = i+4
                    points_Eprofile = make_points_Eprofile(curr_energy, starting_point, rel_dx)
                    curve_points = make_curve_points(points_Eprofile, rel_curv)
                    make_dots(filePath, points_Eprofile, color_index)
                    make_curve(filePath, curve_points, color_index)
                    make_labels(filePath, curr_energy, curr_labels, points_Eprofile, font_size, color_index)

                except:
                    continue

            #Close file
            writing_file(filePath, "</page></CDXML>", "a")

            QMessageBox.information(self, "Notice", "Finished!", QMessageBox.Ok)

            #Open folfer
            os.startfile(Path(filePath).parent)

def writing_file(filePath, contents, type):
    f = open(filePath, type)
    f.write(contents)
    f.close()

def header(page_H, page_W, colortable):
    #Header
    header_setup = '<?xml version="1.0" encoding="UTF-8" ?>\n' \
            '<!DOCTYPE CDXML SYSTEM "http://www.cambridgesoft.com/xml/cdxml.dtd" >\n' \
            '<CDXML\n' \
            '><fonttable>\n' \
            '<font id="3" charset="iso-8859-1" name="Arial"/>\n' \
            '<font id="7" charset="Unknown" name="Symbol"/>\n' \
            '</fonttable>\n'

    #Color setup
    color_setup = '<colortable>\n' \
            '<color r=\"1\" g=\"1\" b=\"1\"/>\n' \
            '<color r=\"0\" g=\"0\" b=\"0\"/>\n'

    for color in colortable:
        col = QColor(color)
        col_r = int(col.getRgb()[0])
        col_g = int(col.getRgb()[1])
        col_b = int(col.getRgb()[2])
        color_setup += "<color r=\"" + str(round(col_r / 255, 2)) + "\" g=\"" + str(round(col_g / 255,2)) + "\" b=\"" + str(round(col_b / 255, 2)) + "\"/>\n"

    color_setup += "</colortable>"

    #Page setup
    page_setup = '<page\n' \
            'id="6"\n ' \
            'BoundingBox="0 0 523.20 769.68"\n ' \
            'HeaderPosition="36"\n ' \
            'FooterPosition="36"\n ' \
            'PrintTrimMarks="yes"\n ' \
            'HeightPages="{0}"\n ' \
            'WidthPages="{1}"\n>\n'.format(page_H, page_W)

    Arrow = "<arrow\n" + " id=\"13\"\n" + " BoundingBox=\"13.87 13.84 18.63 60\"\n" + " Z=\"6\"\n" + " LineWidth=\"0.85\"\n" + " FillType=\"None\"\n" + " ArrowheadHead=\"Full\"\n" + " ArrowheadType=\"Solid\"\n" + " HeadSize=\"1000\"\n" + " ArrowheadCenterSize=\"875\"\n" + " ArrowheadWidth=\"250\"\n" + " Head3D=\"16.50 13.84 0\"\n" + " Tail3D=\"16.50 64 0\"\n" + " Center3D=\"21.75 45.59 0\"\n" + " MajorAxisEnd3D=\"71.91 45.59 0\"\n" + " MinorAxisEnd3D=\"21.75 95.75 0\"\n" + "/>"

    G_sol = "<t\n" + " id=\"11\"\n" + " p=\"40.50 24.50\"\n" + " BoundingBox=\"20.99 15.45 60.01 37.65\"\n" + " Z=\"7\"\n" + " CaptionJustification=\"Center\"\n" + " Justification=\"Center\"\n" + " LineHeight=\"auto\"\n" + " LineStarts=\"8 18\"\n" + "><s font=\"7\" size=\"9\" color=\"0\" face=\"1\">D</s><s font=\"3\" size=\"9\" color=\"0\" face=\"1\">G(sol)\n" + "</s><s font=\"3\" size=\"9\" color=\"0\">(kcal/mol)</s></t>"


    general_info = header_setup + color_setup + page_setup + Arrow + G_sol
    return general_info


def make_points_Eprofile(values, starting_point, rel_dx):
    ref_x, ref_y = starting_point[0], starting_point[1]
    points_Eprofile = []
    inc_x, inc_y = 0, 0
    for i in range(len(values)):
        points_Eprofile.append([ref_x + inc_x, ref_y - inc_y * 5])
        inc_x += 30 * rel_dx
        if i < len(values) - 1: inc_y = values[i + 1] - values[0]
    return points_Eprofile

def make_curve_points(points_Eprofile, rel_curv):
    curve_points = []
    for xy in points_Eprofile:
        curve_points = curve_points + [xy[0] - 15 * rel_curv, xy[1], xy[0], xy[1], xy[0] + 15 * rel_curv, xy[1]]
    return " ".join(str(item) for item in curve_points)

def make_curve(filename, curve_points, color_index):
    f = open(filename, "a")
    f.write('<curve\n id="4"\n Z="1"\n color=\"%s\"\nArrowheadType="Solid"\n CurvePoints="%s"\n/>\n' % (str(color_index), curve_points))
    f.close()

def make_dots(filename, points_Eprofile, color_index):
    f = open(filename, "a")
    for xy in points_Eprofile:
        f.write('<graphic\n BoundingBox="%s %s %s %s"\n color=\"%s\"\nGraphicType="Symbol"\n SymbolType="Electron"\n/>\n' % (
        xy[0], xy[1], xy[0], xy[1] + 15, str(color_index)))
    f.close()

def make_labels(filename, values, labels, points_Eprofile, font_size, color_index):
    f = open(filename, "a")
    if font_size > 9:
        alpha = font_size / 4
    else:
        alpha = 0
    for i, xy in enumerate(points_Eprofile):
        if re.search("TS", labels[i]):
            y_inc = -13.5 - alpha
        else:
            y_inc = 12 + alpha
        f.write('<t\n p="%s %s"\n CaptionJustification="Center"\n Justification="Center"\n LineHeight="auto"\n>' % (
        xy[0], xy[1] + y_inc))
        f.write('<s font="3" size="{0}" color="{1}" face="1">{2}\n</s>'.format(font_size, str(color_index), labels[i]))
        if float(values[i]) < 0:  # make en-dash
            num = str(values[i]).split("-")[1]
            f.write('<s font="3" size="{0}" color="{1}">(</s>'.format(font_size, str(color_index)))
            f.write('<s font="7" size="{0}" color="{1}">-</s><s font="3" size="{2}" color="{1}">{3:0.2f})</s></t>\n'.format(font_size,str(color_index),font_size,float(num)))
        else:
            f.write('<s font="3" size="{0}" color="{1}">({2:0.2f})</s></t>\n'.format(font_size, str(color_index), float(values[i])))
    f.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = EProfilePlotterMainWindow()
    ex.show()
    sys.exit(app.exec_())
