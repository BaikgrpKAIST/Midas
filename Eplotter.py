import sys, os, re
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QToolTip, QDesktopWidget, QLabel, \
    QGridLayout, QLineEdit, QTextEdit, QVBoxLayout, QCheckBox, QComboBox, QAction, QFileDialog, QMainWindow, \
    QInputDialog, QScrollArea, QMessageBox
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import QCoreApplication, Qt


def writing_file(filename, contents, type):
    f = open(filename, type)
    f.write(contents)
    f.close()

def template(page_H, page_W):
    temp = '<?xml version="1.0" encoding="UTF-8" ?>\n\
 <!DOCTYPE CDXML SYSTEM "http://www.cambridgesoft.com/xml/cdxml.dtd" >\n\
 <CDXML\n\
 ><page\n\
 id="6"\n\
 BoundingBox="0 0 523.20 769.68"\n\
 HeaderPosition="36"\n\
 FooterPosition="36"\n\
 PrintTrimMarks="yes"\n\
 HeightPages="{0}"\n\
 WidthPages="{1}"\n\
>\n'.format(page_H, page_W)
    return temp

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

def make_curve(filename, curve_points):
    f = open(filename, "a")
    f.write('<curve\n id="4"\n Z="1"\n ArrowheadType="Solid"\n CurvePoints="%s"\n/>\n' % (curve_points))
    f.close()

def make_dots(filename, points_Eprofile):
    f = open(filename, "a")
    for xy in points_Eprofile:
        f.write('<graphic\n BoundingBox="%s %s %s %s"\n GraphicType="Symbol"\n SymbolType="Electron"\n/>\n' % (
        xy[0], xy[1], xy[0], xy[1] + 15))
    f.close()

def make_labels(filename, values, labels, points_Eprofile, font_size):
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
        f.write('<s font="3" size="{0}" color="0" face="1">{1}\n</s>'.format(font_size, labels[i]))
        if float(values[i]) < 0:  # make en-dash
            num = str(values[i]).split("-")[1]
            f.write('<s font="3" size="{0}" color="0">(</s>'.format(font_size))
            f.write('<s font="7" size="{0}" color="0">-</s><s font="3" size="{1}" color="0">{2:0.2f})</s></t>\n'.format(font_size,font_size,float(num)))
        else:
            f.write('<s font="3" size="{0}" color="0">({1:0.2f})</s></t>\n'.format(font_size, float(values[i])))
    f.close()

class ScrollLabel(QScrollArea):
    def __init__(self, *args, **kwargs):
        QScrollArea.__init__(self, *args, **kwargs)
        self.setWidgetResizable(True)
        content = QWidget(self)
        self.setWidget(content)
        lay = QVBoxLayout(content)
        self.label = QLabel(content)
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.label.setWordWrap(True)
        lay.addWidget(self.label)

    def setText(self, text):
        self.label.setText(text)

    def text(self):
        get_text = self.label.text()
        return get_text

class Plotter(QWidget):

    def __init__(self):
        super().__init__()  # bring all init settings from upper-class (QWidget)
        # Variables
        self.starting_point= [0, 0]
        self.width_get = "1.0"
        self.curve_get = "4"
        self.font_size_get = "10"
        self.page_H = 1
        self.page_W = 1
        self.directory_get = "C:\Temp"
        self.filename_get = "E_profile.cdxml"
        self.curr_energy = [0]
        self.curr_labels = []

        self.initUI()

    def center(self):
        frameGeo = self.frameGeometry()  # size info. of app
        cp = QDesktopWidget().availableGeometry().center()  # size info. of monitor
        frameGeo.moveCenter(cp)
        self.move(frameGeo.topLeft())

    def showMore(self, state):
        if state == Qt.Checked:
            pass
        else:
            pass

    def onActivated_font(self, text):
        self.font_size_get = text

    def onActivated_width(self, text2):
        self.width_get = text2

    def onActivated_curve(self, text3):
        self.curve_get = text3

    def show_directory(self):
        direc, ok = QInputDialog.getText(self, 'Input Dialog', 'Enter saving directory')
        if ok:
            if os.path.isdir(direc):
                self.directory_get = direc
                self.curr_dir.setText(str(direc))
                self.curr_dir.adjustSize()
            else:
                QMessageBox.information(self,"Warning","Entered directory that doesn't exist.")

    def show_filename(self):
        fn, ok = QInputDialog.getText(self, 'Input Dialog', 'Enter filename')
        if ok:
            self.filename_get = fn
            self.curr_file.setText(str(fn))
            self.curr_file.adjustSize()

    def show_history(self):
        QMessageBox.information(self, "Update history", 'This program is made by JJ.\nPlease contact him if problems found.\n\
\nVer. 1.0.\nmade in 21/02/04.\n\nVer. 1.1.\n1. "-" symbol is replaced by en-dash.\n2. Bolding lables.')

    def give_energy(self):
        en, ok = QInputDialog.getText(self, 'Relative energy', 'Enter relative energies. e.g. 0 10 -5 20 -30')
        if ok:
            self.energy_get = en
            try:
                self.curr_energy = list(map(float, en.split()))
                if len(self.curr_energy) > 1:
                    self.curr_labels = []
                    for i in range(len(self.curr_energy)):
                        if i % 2 == 0:
                            temp_lb = "%d" % (i//2 + 1)
                        else:
                            temp_lb = "%d-TS" % (i//2 + 1)
                        self.curr_labels.append(temp_lb)
                new_Einfo = " ".join(list(map(str,self.curr_energy)))
                self.Einfo.setText(str(new_Einfo))
                self.Einfo.adjustSize()

            except:
                QMessageBox.information(self, "Warning", "Warning: please enter float numbers.")

    def create_file(self):
        if len(self.curr_energy) > 1:
            rel_dx = float(self.width_get)
            rel_curv = float(self.curve_get) / 4
            font_size = int(self.font_size_get)

            # starting point
            max_val, min_val = max(self.curr_energy), min(self.curr_energy)
            diff_val = max_val - min_val
            starting_point = [70, 70 + (max_val - self.curr_energy[0]) * 5]

            # setting for pages
            if (len(self.curr_energy) - 1) * 20 * rel_dx > 440: self.page_W = 2
            if diff_val * 5 + 70 > 750: self.page_H = 2
            temp = template(self.page_H, self.page_W)

            # writing CDXML file
            filename = self.directory_get + "\\" + self.filename_get
            writing_file(filename, temp, "w")
            points_Eprofile = make_points_Eprofile(self.curr_energy, starting_point, rel_dx)
            curve_points = make_curve_points(points_Eprofile, rel_curv)
            make_dots(filename, points_Eprofile)
            make_curve(filename, curve_points)
            make_labels(filename, self.curr_energy, self.curr_labels, points_Eprofile, font_size)
            writing_file(filename, "</page></CDXML>","a")

    def initUI(self):
        self.setWindowTitle("Eplotter")
        self.move(300, 300)
        self.resize(400, 300)  # or self.setGeometry(300,300,400,400)
        # self.center()
        self.setWindowIcon(QIcon("Application_images/E-profile_for_icon.jpg"))
        # self.textEdit = QTextEdit()

        # for layout
        grid = QGridLayout()
        self.setLayout(grid)

        # directory
        self.btn_dir = QPushButton('Directory', self)
        self.btn_dir.setGeometry(20, 10, 70, 25)
        self.btn_dir.clicked.connect(self.show_directory)
        self.curr_dir = QLabel(r'C:\Temp', self)
        self.curr_dir.adjustSize()
        self.curr_dir.move(100, 17)

        # filename
        self.btn_file = QPushButton('Filename', self)
        self.btn_file.setGeometry(20, 40, 70, 25)
        self.btn_file.clicked.connect(self.show_filename)
        self.curr_file = QLabel(self.filename_get, self)
        self.curr_file.adjustSize()
        self.curr_file.move(100, 47)

        # check for additional infos
        #cb = QCheckBox('more profiles', self)
        #cb.move(200, 150)
        #cb.stateChanged.connect(self.showMore)
        #

        # Choose font size
        self.lb = QLabel('font size', self)
        self.lb.move(300, 65)
        CB = QComboBox(self)
        for x in range(6, 15): CB.addItem('%d' % (x))
        CB.move(280, 90)
        CB.setCurrentIndex(4)
        CB.activated[str].connect(self.onActivated_font)

        # Choose width ratio
        self.lb2 = QLabel('width ratio', self)
        self.lb2.move(170, 65)
        CB2 = QComboBox(self)
        for x in range(4, 31): CB2.addItem('{0:0.1f}'.format(x / 10))
        CB2.move(150, 90)
        CB2.setCurrentIndex(6)
        CB2.activated[str].connect(self.onActivated_width)

        # Choose curve level
        self.lb3 = QLabel('curve level', self)
        self.lb3.move(40, 65)
        CB3 = QComboBox(self)
        for x in range(1, 11): CB3.addItem('%s' % (x))
        CB3.move(20, 90)
        CB3.setCurrentIndex(3)
        CB3.activated[str].connect(self.onActivated_curve)

        # Energy Info
        self.btn_energy = QPushButton('Energy', self)
        self.btn_energy.setGeometry(125, 135, 150, 30)
        self.btn_energy.clicked.connect(self.give_energy)
        self.relE = QLabel('Current E-info', self)
        self.relE.move(30, 170)
        self.Einfo = QLabel('-', self)
        self.Einfo.adjustSize()
        self.Einfo.move(30, 205)

        # Create button
        self.btn_create = QPushButton('&Create', self)
        self.btn_create.setGeometry(125, 225, 150, 50)
        self.btn_create.clicked.connect(self.create_file)

        # Copyright
        self.copy = QLabel('Ver. 1.1.', self)
        self.copy.adjustSize()
        self.copy.move(335, 285)

        # Update history
        self.btn_upd = QPushButton('History', self)
        self.btn_upd.setGeometry(330, 10, 55, 20)
        self.btn_upd.clicked.connect(self.show_history)

        # Scroll area
        #new_layer = ScrollLabel(self)
        #new_layer.setGeometry(20,200,170,70)
        #new_layer.setText("%s" % (self.curr_energy))

        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Plotter()
    sys.exit(app.exec_())
