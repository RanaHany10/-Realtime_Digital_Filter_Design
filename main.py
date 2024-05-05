import PyQt5
import numpy as np
import pandas as pd
from scipy import signal
from PyQt5 import QtWidgets, uic, QtMultimedia, QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QGraphicsScene, QGraphicsPixmapItem, QCheckBox, QVBoxLayout, \
    QLabel, QStyle, QGraphicsView
import sys
from unit_circle import UnitCircle
from digital_filter import DigitalFilter
from phaseCorrection import PhaseCorrectionWindow
from padding_area import PaddingArea
from scipy.signal import zpk2tf, lfilter
import os
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from pyqtgraph import PlotWidget, mkPen
import logging
from PyQt5.QtCore import QTimer

logging.basicConfig(filename="logging_file.log",
                    filemode="w",
                    format="(%(asctime)s) | %(name)s | %(levelname)s => '%(message)s'",
                    datefmt="%d - %B - %Y, %H:%M:%S")

my_logger = logging.getLogger("name")  # i can change the name as i want

my_logger.warning("This Is Warning Message")  # this line i will write each time i want to make logging


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # Load the UI Page
        uic.loadUi(r'filter.ui', self)
        self.setWindowTitle('Filters')

        self.zeros = []  # list to store zeros
        self.poles = []  # list to store poles
        self.conjugate_enabled = False  # flag to enable/disable adding conjugates

        # Frequency Response
        self.magnitude_response = []  # list to store magnitude response
        self.phase_response = []  # list to store phase response

        # Real-Time Signal
        self.input_signal = []  # list to store the input signal
        self.filtered_signal = []  # list to store the filtered signal

        # All-Pass Filters that user will add Each all-pass filter will have its own zeros and poles so we will store them in a list of dic
        self.all_pass_filters = []  # list to store all-pass filters

        self.zeros_lst = []
        self.poles_lst = []
        self.zeros_pos = []
        self.poles_pos = []

        print("Setting up the scene for zplane.")
        self.scene = QtWidgets.QGraphicsScene(self)
        self.zplane.setScene(self.scene)
        print("Scene set up successfully.")
        # self.zeros_pos = []
        # self.poles_pos = []

        self.unit_circle = UnitCircle(self, self.scene, self.zplane, self.zero_button, self.pole_button, self.conjugate,
                                      self.magnitude_response_widget, self.phase_response_widget)
        self.digital_filter = DigitalFilter(self.zeros, self.poles, self.magnitude_response_widget,
                                            self.phase_response_widget,self.all_pass_phase)


        # allpass correction filters
        self.all_phase_correction_filters = [
            0.99, 0.345, 0.732, 0.456]
        self.checked_phase_correction_filters = []
        # all pass
        self.all_pass_zeros = []
        self.all_pass_poles = []
        # self.phase_correction = PhaseCorrectionWindow(self, self.all_pass_phase, self.selescte_filter_phase,
        #                                               self.all_phase_correction_filters
        #                                               , self.checked_phase_correction_filters, self.unit_circle,
        #                                               self.all_pass_poles, self.all_pass_zeros, self.lineEdit
        #                                               , self.filtersList, self.zeros, self.poles)
        #add filter
        # self.add_filter_but.clicked.connect(self.phase_correction.add_filter)
        self.unit_circle.draw_unit_circle()

        # Initialize real-time filter variables
        self.chunk_size = 100  # Number of points to process in each update
        self.current_position = 0

        # Set up the timer for real-time updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_filter)
        self.timer.start(500)

        # clear all zeros:
        self.clear_zeros.clicked.connect(lambda: self.unit_circle.clear_all_zeros_and_poles(self.unit_circle.zeros))
        self.clear_poles.clicked.connect(lambda: self.unit_circle.clear_all_zeros_and_poles(self.unit_circle.poles))
        print("vhvhb:", self.unit_circle.poles)
        # remove all
        self.clear_all.clicked.connect(
            lambda: self.unit_circle.clear_all_zeros_and_poles(self.unit_circle.zeros, self.unit_circle.poles))
        # restart
        self.restart_but.clicked.connect(self.restart)
        # laod signal
        self.load_signal.clicked.connect(self.open_file)

        # self.zeros_pos, self.poles_pos = self.calculate_zeros_poles_Pos()
        # self.zeroslst, self.poleslst = self.unit_circle.on_mouse_press(self.zplane.mousePressEvent)
        # self.padding_area = PaddingArea(self)
        # # print("zerooos:", self.unit_circle.pooles)
        # self.padd_area.layout().addWidget(self.padding_area)

        # update signal while dragging zero and pol
        for zero in self.unit_circle.zeros:
            zero.sigDragged.connect(self.update_filter)
        for pole in self.unit_circle.poles:
            pole.sigDragged.connect(self.update_filter)

        # filter speed
        self.Speed_slider.setMinimum(1)
        self.Speed_slider.setMaximum(100)
        self.Speed_slider.setValue(1)  # Initial value
        self.Speed_slider.valueChanged.connect(self.update_filter_speed)
        self.point_per_second = 1
        # set grid
        plot_lst = [self.magnitude_response_widget, self.phase_response_widget, self.input_signal_graph,
                    self.output_signal_graph, self.selescte_filter_phase]
        for plot in plot_lst:
            self.set_grid(plot)

    def open_file(self):
        self.clear()
        self.file_name, _ = QFileDialog.getOpenFileName(self, 'Open file', './',
                                                        'CSV Files (*.csv);;Text Files (*.txt);;Excel Files (*.xlsx)')
        if self.file_name:
            data = pd.read_csv(self.file_name)
            x = data.iloc[:, 0].values
            y = data.iloc[:, 1].values
            self.input_signal.extend(y)

            self.timer.start(500)


    def update_filter(self):
        print("enter")
        # Filter a chunk of data in each iteration
        numerator, denominator = zpk2tf(self.zeros_pos, self.poles_pos, 1)
        print("Numerator:", numerator)
        print("Denominator:", denominator)

        # print("digital_filter.zeros_pos:", zeros)
        # print("digital_filter.poles_pos:", poles)
        if self.current_position + self.point_per_second <= len(self.input_signal):
            chunk_data = self.input_signal[self.current_position:self.current_position + self.point_per_second]
            output_chunk = lfilter(numerator, denominator, chunk_data)
            # Take the real part of the output before extending the list
            self.filtered_signal.extend(np.real(output_chunk))
            self.plot_input_and_output_signal()
            self.current_position += self.point_per_second
        else:
            # All data processed, stop the timer
            self.timer.stop()

    def plot_input_and_output_signal(self):
        # Update the plot for the input and output signals
        self.input_signal_graph.plot(self.input_signal[:self.current_position + self.point_per_second],
                                     pen='b', clear=True)
        self.output_signal_graph.plot(self.filtered_signal, pen='r', clear=True)

    def restart(self):
        self.current_position = 0
        self.filtered_signal = []

        # Restart the timer
        self.timer.start(100)

    def update_filter_speed(self, val):
        self.point_per_second = val
        self.speed_val.setText(f"{self.point_per_second} points/sec")

    def set_grid(self, plot_item):
        plot_item.plotItem.showGrid(True, True)

    def clear(self):
        self.input_signal = []
        self.filtered_signal = []
        self.input_signal_graph.clear()
        self.output_signal_graph.clear()

    # def calculate_zeros_poles_Pos(self, zeros, poles):
    #     zeros_pos = [
    #         complex(self.digital_filter.convert_coordinates(-item.scenePos().x()),
    #                 self.digital_filter.convert_coordinates(-item.scenePos().y()))
    #         for item in zeros]
    #     poles_pos = [
    #         complex(self.digital_filter.convert_coordinates(-item.scenePos().x()),
    #                 self.digital_filter.convert_coordinates(-item.scenePos().y()))
    #         for item in poles]
    #     # print("poools:", self.unit_circle.poles)
    #     return zeros_pos, poles_pos

    def calculate_zeros_poles_Pos(self, zeros, poles):
        zeros_pos = [
            complex(self.digital_filter.convert_coordinates(-item.scenePos().x()),
                    self.digital_filter.convert_coordinates(-item.scenePos().y()))
            for item in zeros]
        poles_pos = [
            complex(self.digital_filter.convert_coordinates(-item.scenePos().x()),
                    self.digital_filter.convert_coordinates(-item.scenePos().y()))
            for item in poles]
        # print("poools:", self.unit_circle.poles)
        return zeros_pos, poles_pos

    def update_zeros_poles(self, zeros, poles):
        self.zeros = zeros
        self.poles = poles
        self.update_phase_corr(self.zeros, self.poles)
        self.zeros_pos, self.poles_pos = self.calculate_zeros_poles_Pos(self.zeros, self.poles)
        self.padding_area = PaddingArea(self, self.zeros_pos, self.poles_pos)
        # print("zerooos:", self.unit_circle.pooles)
        self.padd_area.layout().addWidget(self.padding_area)
        # Now, you can use self.zeros_pos and self.poles_pos as needed
        print("Updated zeros:", self.zeros_pos)
        print("Updated poles:", self.poles_pos)

    def update_phase_corr(self, zeros, poles):
        zeros_pos = [
            complex(self.digital_filter.convert_coordinates(item.scenePos().x()),
                    self.digital_filter.convert_coordinates(-item.scenePos().y()))
            for item in zeros]
        poles_pos = [
            complex(self.digital_filter.convert_coordinates(item.scenePos().x()),
                    self.digital_filter.convert_coordinates(-item.scenePos().y()))
            for item in poles]

        self.phase_correction = PhaseCorrectionWindow(self, self.all_pass_phase, self.selescte_filter_phase,
                                                      self.all_phase_correction_filters
                                                      , self.checked_phase_correction_filters, self.unit_circle,
                                                      self.all_pass_poles, self.all_pass_zeros, self.lineEdit
                                                      , self.filtersList, zeros_pos, poles_pos, zeros,
                                                      poles)
        self.add_filter_but.clicked.connect(self.phase_correction.add_filter)






def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()