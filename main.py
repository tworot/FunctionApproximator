# FunkcjoAproksymator by Tomasz Worotnicki

import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QSizePolicy, QPushButton, QLineEdit, QLabel, QGroupBox, \
    QComboBox, QCheckBox
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from numpy import polyfit, arange, log, sqrt, exp, sin


class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.left = 100
        self.top = 100
        self.title = 'FunkcjoAproksymator by Tomasz Worotnicki'
        self.width = 640
        self.height = 400
        # inicjalizacje elementów z initUI
        self.manual_insert = QGroupBox('Wprowadzenie ręczne:', self)
        self.manual_insert_x_label = QLabel(self.manual_insert)
        self.manual_insert_x = QLineEdit(self.manual_insert)
        self.manual_insert_y_label = QLabel(self.manual_insert)
        self.manual_insert_y = QLineEdit(self.manual_insert)
        self.manual_insert_button = QPushButton(self.manual_insert)
        self.data = [[i, sin(i)] for i in range(-10, 10, 1)]
        self.grid_on = QCheckBox(self)
        self.grid_label = QLabel('Siatka', self)

        self.interp_box1 = QGroupBox('Metoda aproksymacji (z):', self)
        self.interp_combo1 = QComboBox(self.interp_box1)

        self.interp_box2 = QGroupBox('Metoda aproksymacji (n):', self)
        self.interp_combo2 = QComboBox(self.interp_box2)

        self.select_point_box = QGroupBox('Wybierz punkt:', self)
        self.select_point_combo = QComboBox(self.select_point_box)

        self.plot = PlotCanvas(parent=self)
        self.refresh_plot()
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.manual_insert.move(500, 60)
        self.manual_insert.resize(140, 85)

        self.manual_insert_x_label.setText('x:')
        self.manual_insert_x_label.move(10, 20)

        self.manual_insert_x.placeholderText = 'Podaj wartość x'
        self.manual_insert_x.setToolTip('Punkt, który dodasz będzie miał następującą współrzędną y')
        self.manual_insert_x.move(20, 20)
        self.manual_insert_x.resize(100, 16)
        # self.manual_insert_x.setText('20')

        self.manual_insert_y_label = QLabel(self.manual_insert)
        self.manual_insert_y_label.setText('y:')
        self.manual_insert_y_label.move(10, 40)

        self.manual_insert_y.placeholderText = 'Podaj wartość y'
        self.manual_insert_y.setToolTip('Punkt, który dodasz będzie miał następującą współrzędną y')
        self.manual_insert_y.move(20, 40)
        self.manual_insert_y.resize(100, 16)
        # self.manual_insert_y.setText('10')

        self.manual_insert_button.setText('Dodaj punkt')
        self.manual_insert_button.move(40, 60)
        self.manual_insert_button.resize(81, 24)

        self.manual_insert_button.clicked.connect(self.min_button_clicked)
        self.refresh_plot()

        self.addToolBar(NavigationToolbar2QT(self.plot, self))

        self.interp_box1.move(500, 145)
        self.interp_box1.resize(140, 50)
        self.interp_combo1.addItems(
            ['Brak', 'Liniowa', 'Kwadratowa', 'Wielomianowa (10)', 'Wielomianowa', 'Logarytmiczna', 'Wykładnicza'])
        self.interp_combo1.move(10, 20)
        self.interp_combo1.resize(120, 20)
        self.interp_combo1.activated[int].connect(self.interp_combo_activated1)

        self.interp_box2.move(500, 195)
        self.interp_box2.resize(140, 50)
        self.interp_combo2.addItems(
            ['Brak', 'Liniowa', 'Kwadratowa', 'Wielomianowa (10)', 'Wielomianowa', 'Logarytmiczna', 'Wykładnicza'])
        self.interp_combo2.move(10, 20)
        self.interp_combo2.resize(120, 20)
        self.interp_combo2.activated[int].connect(self.interp_combo_activated2)

        self.select_point_box.move(500, 245)
        self.select_point_box.resize(140, 50)
        self.select_point_combo.move(10, 20)
        self.select_point_combo.resize(120, 20)
        self.select_point_combo.activated[int].connect(self.select_point_combo_activated)

        self.grid_on.move(515, 291)
        self.grid_on.setChecked(False)
        self.grid_on.stateChanged.connect(self.grid_on_changed)

        self.grid_label.move(533, 290)


        # self.refresh_button = QLabel(self)
        # self.refresh_button.move(510, 280)
        # self.refresh_button.resize(81, 24)
        self.show()

    def grid_on_changed(self):
        if self.grid_on.isChecked():
            self.plot.grid = True
        else:
            self.plot.grid = False
        self.plot.draw()

    def interp_combo_activated1(self, text):
        self.plot.interp_type1 = text
        self.plot.draw()

    def interp_combo_activated2(self, text):
        self.plot.interp_type2 = text
        self.plot.draw()

    def select_point_combo_activated(self, text):
        self.plot.select_point = text
        self.plot.draw()

    def min_button_clicked(self):
        self.plot.add_point([float(self.manual_insert_x.text()), float(self.manual_insert_y.text())])
        self.refresh_plot()

    def refresh_plot(self):
        self.plot.draw()

    def refresh_select_point_combo(self):
        self.select_point_combo.clear()
        self.select_point_combo.addItems([''])
        self.select_point_combo.addItems(['{:6.4f}; {:6.4f}'.format(x[0], x[1]) for x in self.plot.data])


class PlotCanvas(FigureCanvas):
    dot_size = 10
    point_size = 10
    data = []
    interp_data1 = []
    interp_data2 = []
    interp_type1 = 0
    interp_type2 = 0
    select_point = 0
    grid = False

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        super(PlotCanvas, self).__init__(fig)
        # self.axes = fig.add_subplot(111)
        # self.move(0, 0)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.ax = self.figure.add_subplot(111)
        self.figure.canvas.mpl_connect('button_press_event', self.mouse_clicked)

    def draw(self):
        self.interp(self.ax.viewLim.x0, self.ax.viewLim.x1)
        x0, y0, x1, y1 = self.ax.viewLim.extents
        self.ax.cla()
        self.ax.autoscale(False)
        self.ax.axis([x0, x1, y0, y1])
        self.ax.grid(self.grid)
        if self.interp_type1 == 5 or self.interp_type2 == 5:
            self.ax.fill_betweenx([y0, y1], x0, hatch='//', edgecolor='#000000', facecolor='#E0E0E0')
        if self.interp_type1 == 6 or self.interp_type2 == 6:
            self.ax.fill_between([x0, x1], y0,  hatch='//', edgecolor='#000000', facecolor='#E0E0E0')
        self.ax.plot([x[0] for x in self.interp_data1], [x[1] for x in self.interp_data1], '-', color='#00B000')
        self.ax.plot([x[0] for x in self.interp_data2], [x[1] for x in self.interp_data2], '-', color='#0000B0')
        if self.select_point > 0:
            self.ax.plot(self.data[self.select_point-1][0], self.data[self.select_point-1][1],
                         'o', ms=12, color='#E00000')
        self.ax.plot([x[0] for x in self.data], [x[1] for x in self.data], 'ko')
        self.ax.set_title('   ')
        super(PlotCanvas, self).draw()

    def mouse_clicked(self, event):
        if not self.toolbar.mode:
            if event.button == 1:
                self.add_point([event.xdata, event.ydata])
            if event.button == 3:
                self.remove_point([event.xdata, event.ydata])

    def remove_point(self, point):
        if not point[0] or not point[1]:
            return
        if not self.data:
            return
        candidate = []
        x0, y0, x1, y1 = self.ax.viewLim.extents
        xmod = (80/(x1-x0)) ** 2
        ymod = (64/(y1-y0)) ** 2
        for index in range(len(self.data)):
            row = self.data[index]
            distance = ((row[0]-point[0]) ** 2) * xmod + ((row[1]-point[1]) ** 2) * ymod
            if not candidate and distance <= 1:
                candidate = [index, distance]
            if candidate and distance < candidate[1]:
                candidate = [index, distance]
        if candidate:
            del self.data[candidate[0]]
            self.select_point = 0
            self.parent().refresh_select_point_combo()
        self.draw()

    def add_point(self, point):
        #if not point[0] or not point[1]:
        #    return
        self.data.append(point)
        self.data.sort(key=lambda p: p[0])
        # x0, y0, x1, y1 = self.ax.viewLim.extents
        # self.ax.cla()
        # self.ax.autoscale(False)
        # self.ax.axis([x0, x1, y0, y1])
        self.select_point = 0
        self.parent().refresh_select_point_combo()
        self.draw()

    def interp(self, data_begin, data_end):
        self.interp_data1 = []
        self.interp_data2 = []

        if self.interp_type1 == 0:
            pass
        elif self.interp_type1 == 1:
            self.interp_linear(data_begin, data_end, self.interp_data1)
        elif self.interp_type1 == 2:
            self.interp_quadratic(data_begin, data_end, self.interp_data1)
        elif self.interp_type1 == 3:
            self.interp_polynomial(data_begin, data_end, self.interp_data1)
        elif self.interp_type1 == 4:
            self.interp_polynomial_limitless(data_begin, data_end, self.interp_data1)
        elif self.interp_type1 == 5:
            self.interp_logarithmic(data_begin, data_end, self.interp_data1)
        elif self.interp_type1 == 6:
            self.interp_exponential(data_begin, data_end, self.interp_data1)
        elif self.interp_type1 == 7:
            self.interp_sine(data_begin, data_end, self.interp_data1)

        if self.interp_type2 == 0:
            pass
        elif self.interp_type2 == 1:
            self.interp_linear(data_begin, data_end, self.interp_data2)
        elif self.interp_type2 == 2:
            self.interp_quadratic(data_begin, data_end, self.interp_data2)
        elif self.interp_type2 == 3:
            self.interp_polynomial(data_begin, data_end, self.interp_data2)
        elif self.interp_type2 == 4:
            self.interp_polynomial_limitless(data_begin, data_end, self.interp_data2)
        elif self.interp_type2 == 5:
            self.interp_logarithmic(data_begin, data_end, self.interp_data2)
        elif self.interp_type2 == 6:
            self.interp_exponential(data_begin, data_end, self.interp_data2)
        elif self.interp_type2 == 7:
            self.interp_sine(data_begin, data_end, self.interp_data2)

    def data_parser(self, data_begin, data_end):
        avg = (data_end - data_begin) / 400
        x0 = []
        x1 = []
        for i in range(len(self.data)):
            x0.append(self.data[i][0])
            x1.append(self.data[i][1])
        return avg, x0, x1

    #def interp_sine(self,data_begin,data_end):


    # def interp_sine(self, data_begin, data_end):
    #     # tutaj ma być dedykowana funkcja parsująca dane!
    #     avg = (data_end - data_begin) / 400
    #     x0 = []
    #     x1 = []
    #     for i in range(len(self.data)):
    #             x0.append(self.data[i][0])
    #             x1.append(self.data[i][1])
    #     print([x0, x1])
    #     try:
    #         poly = rfft(x1)
    #         # print(self.data)
    #         # print(poly)
    #         print(data_begin, data_end)
    #         #for i in arange(data_begin, data_end + avg, avg):
    #         temp = irfft(poly[0:3])
    #         print(temp)
    #             # self.interp_data.append([i, temp])
    #
    #     except ValueError:
    #         return

    # def interp_sine(self, data_begin, data_end):
    #     # tutaj ma być dedykowana funkcja parsująca dane!
    #     avg = (data_end - data_begin) / 400
    #     x0 = []
    #     x1 = []
    #     for i in range(len(self.data)):
    #         x0.append(arcsin(((self.data[i][0] + 1) % 2) - 1))
    #         x1.append(self.data[i][1])
    #     print([x0, x1])
    #     try:
    #         poly = polyfit(x0, x1, min(len(self.data) - 1, 1))
    #         # print(data_begin, data_end)
    #         for i in arange(data_begin, data_end + avg, avg):
    #             temp = poly[0] * sin(i) + poly[1]
    #             self.interp_data.append([i, temp])
    #
    #     except ValueError:
    #         return

    def interp_exponential(self, data_begin, data_end, tab):
        # tutaj ma być dedykowana funkcja parsująca dane!
        avg = (data_end - data_begin) / 400
        x0 = []
        x1 = []
        for i in range(len(self.data)):
            if self.data[i][1] > 0:
                x0.append(self.data[i][0])
                x1.append(self.data[i][1])
        try:
            poly = polyfit(x0, log(x1), min(len(self.data) - 1, 1), w=sqrt(x1))
            # print(data_begin, data_end)
            for i in arange(data_begin, data_end + avg, avg):
                temp = exp(poly[1]) * exp(poly[0]*i)
                tab.append([i, temp])
        except ValueError:
            return

        except IndexError:
            return

        except TypeError:
            return

    def interp_logarithmic(self, data_begin, data_end, tab):
        # tutaj ma być dedykowana funkcja parsująca dane!
        avg = (data_end - data_begin) / 400
        x0 = []
        x1 = []
        for i in range(len(self.data)):
            if self.data[i][0] > 0:
                x0.append(self.data[i][0])
                x1.append(self.data[i][1])
        try:
            poly = polyfit(log(x0), x1, min(len(self.data) - 1, 1))
            # print(data_begin, data_end)
            for i in arange(data_begin, data_end + avg, avg):
                if i > 0:
                    temp = poly[0] * log(i) + poly[1]
                    tab.append([i, temp])

        except ValueError:
            return

        except IndexError:
            return

        except TypeError:
            return

    def interp_polynomial(self, data_begin, data_end, tab):
        avg, x0, x1 = self.data_parser(data_begin, data_end)
        try:
            poly = polyfit(x0, x1, min(len(self.data) - 1, 10))
            poly = poly[::-1]
            # print(data_begin, data_end)
            for i in arange(data_begin, data_end + avg, avg):
                temp = 0
                for j in range(len(poly)):
                    temp += poly[j] * (i ** j)
                tab.append([i, temp])

        except ValueError:
            return

    def interp_polynomial_limitless(self, data_begin, data_end, tab):
        avg, x0, x1 = self.data_parser(data_begin, data_end)
        try:
            poly = polyfit(x0, x1, len(self.data) - 1)
            poly = poly[::-1]
            # print(data_begin, data_end)
            for i in arange(data_begin, data_end + avg, avg):
                temp = 0
                for j in range(len(poly)):
                    temp += poly[j] * (i ** j)
                tab.append([i, temp])

        except ValueError:
            return

    def interp_linear(self, data_begin, data_end, tab):
        avg, x0, x1 = self.data_parser(data_begin, data_end)
        try:
            poly = polyfit(x0, x1, min(len(self.data) - 1, 1))
            poly = poly[::-1]
            # print(data_begin, data_end)
            for i in arange(data_begin, data_end + avg, avg):
                temp = 0
                for j in range(len(poly)):
                    temp += poly[j] * (i ** j)
                tab.append([i, temp])

        except ValueError:
            return

    def interp_quadratic(self, data_begin, data_end, tab):
        avg, x0, x1 = self.data_parser(data_begin, data_end)
        try:
            poly = polyfit(x0, x1, min(len(self.data) - 1, 2))
            poly = poly[::-1]
            # print(data_begin, data_end)
            for i in arange(data_begin, data_end + avg, avg):
                temp = 0
                for j in range(len(poly)):
                    temp += poly[j] * (i ** j)
                tab.append([i, temp])

        except ValueError:
            return

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
