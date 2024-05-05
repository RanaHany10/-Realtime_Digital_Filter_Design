from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QVBoxLayout
from scipy.signal import zpk2tf, lfilter
import numpy as np
from scipy import signal



class PaddingArea(QWidget):
    def __init__(self, mainWindow, zeros, poles):
        super().__init__()
        # print("event3")
        self.mainWindow = mainWindow
        # self.zeros_pos, self.poles_pos = zeros, poles
        print("event3")
        self.first_time_enter = True
        self.numerator = []
        self.denominator = []
        self.order = None
        self.zeros_pos, self.poles_pos = zeros, poles
        self.zeros = []
        self.poles = []
        # # Set a QVBoxLayout for self.padding_area
        # layout = QVBoxLayout(self)
        # self.setLayout(layout)
        # Start capturing mouse movement
        self.setMouseTracking(True)
        # self.zeros = self.unit_circle.get_zeros()
        # self.poles = self.unit_circle.get_poles()
        # self.zeros_pos, self.poles_pos = self.calculate_zeros_poles_Pos(self.zeros, self.poles)
        # print("insal:", self.poles_pos)
        # self.update_changes()

    # def convert_coordinates(self, pos, old_range=(-165, 165), new_range=(-1, 1)):
    #     old_min, old_max = old_range
    #     new_min, new_max = new_range
    #
    #     old_range_size = old_max - old_min
    #     new_range_size = new_max - new_min
    #
    #     # Scale the position from the old range to the new range
    #     scaled_pos = (pos - old_min) / old_range_size * new_range_size + new_min
    #
    #     return scaled_pos
    #
    # def calculate_zeros_poles_Pos(self, zeros, poles):
    #     zeros_pos = [
    #         complex(self.convert_coordinates(-item.scenePos().x()),
    #                 self.convert_coordinates(-item.scenePos().y()))
    #         for item in zeros]
    #     poles_pos = [
    #         complex(self.convert_coordinates(-item.scenePos().x()),
    #                 self.convert_coordinates(-item.scenePos().y()))
    #         for item in poles]
    #     # print("poools:", self.unit_circle.poles)
    #     return zeros_pos, poles_pos

    # def update_zeros_poles(self, zeros, poles):
    #     self.zeros = zeros
    #     self.poles = poles
    #     self.zeros_pos, self.poles_pos = self.calculate_zeros_poles_Pos(self.zeros, self.poles)
    #     # Now, you can use self.zeros_pos and self.poles_pos as needed
    #     print("Updated zeros:", self.zeros_pos)
    #     print("Updated poles:", self.poles_pos)
    #     self.update_changes(self.zeros_pos, self.poles_pos)

    def enterEvent(self, event):
        # self.update_changes()
        print("enterEvent - Before get_zeros_poles - self.poles_pos:", self.poles_pos)
        print("event")
        if self.first_time_enter:
            print("enterEvent - After get_zeros_poles - self.poles_pos:", self.poles_pos)
            # self.mainWindow.chunk_size = 0
            self.mainWindow.output_signal_graph.clear()
            self.mainWindow.input_signal_graph.clear()
            self.mainWindow.input_signal = []
            self.mainWindow.filtered_signal = []
            self.first_time_enter = False
            print("evvvvvv")
            # self.zeros_pos, self.poles_pos = self.calculate_zeros_poles_Pos(self.unit_circle.get_zeros(),
            #                                                                 self.unit_circle.get_poles())
            # print("unit_circle:", self.zeros)
            self.numerator, self.denominator = zpk2tf(
                self.zeros_pos, self.poles_pos, 1)
            print("enterEvent - After zpk2tf - self.poles_pos:", self.poles_pos)
            print("evvvvvviiii")
            print("self.zeros_padd:", self.zeros_pos)
            print("self.poles_padd:", self.poles_pos)
            print("self.numerator:", self.numerator)
            print("self.denominator:", self.denominator)

            # Get the order of the numerator and denominator
            self.order = (len(self.numerator) - 1) + (len(self.denominator) - 1)

            if len(self.mainWindow.input_signal) < self.order:
                self.mainWindow.input_signal = [0.21] * abs(len(self.mainWindow.input_signal) - self.order)

    def mouseMoveEvent(self, event):
        print("event1")
        print("self.first_time_enter1:", self.first_time_enter)
        if not self.first_time_enter:
            y = event.y()
            self.mainWindow.input_signal.append(y)
            print("self.mainWindow.input_signal", self.mainWindow.input_signal)
            self.plot()

    def plot(self):
        # # Update self.order before using it
        # self.update_order()
        # self.update_numerator_denominator()
        print("self.denominator55:", self.denominator)
        if self.mainWindow.input_signal:
            print("ool:", self.order)
            input_data = self.mainWindow.input_signal[-1 * self.order:]
            # input_data = self.mainWindow.input_signal[-1:]
            print("input_data", input_data)
            output_points_after_filter = np.real(
                lfilter(self.numerator, self.denominator, input_data))
            print("output_points_after_filter", output_points_after_filter)

            self.mainWindow.filtered_signal.append(
                output_points_after_filter[-1])
            print("self.mainWindow.input_signa:", self.mainWindow.input_signal)
            print("self.mainWindow.filtered_signal:", self.mainWindow.filtered_signal)
            # print("difference:", (np.array(self.mainWindow.input_signal)-np.array(self.mainWindow.filtered_signal)))

            # Plot updated output signal
            self.mainWindow.input_signal_graph.plot(
                self.mainWindow.input_signal, pen='b')

            self.mainWindow.output_signal_graph.plot(
                self.mainWindow.filtered_signal, pen='r')
    # def get_zeros_poles(self, zeros, poles):
    #     self.zeros = zeros
    #     self.poles = poles
    #
    # def get_poles_pos(self):
    #     self.zeros_pos, self.poles_pos = self.calculate_zeros_poles_Pos(zeros, poles)
    #     print("self.poles_padd1:", self.poles_pos)

    # def update_zeros_poles(self, zeros, poles):
    #     self.zeros = zeros
    #     self.poles = poles
    #     self.zeros_pos, self.poles_pos = self.calculate_zeros_poles_Pos(self.zeros, self.poles)
    #     # Now, you can use self.zeros_pos and self.poles_pos as needed
    #     print("Updated zeros:", self.zeros_pos)
    #     print("Updated poles:", self.poles_pos)
    #
    # def enterEvent(self, event):
    #     print("enterEvent - Before get_zeros_poles - self.poles_pos:", self.poles_pos)
    #     print("event")
    #     if self.first_time_enter:
    #         print("enterEvent - After get_zeros_poles - self.poles_pos:", self.poles_pos)
    #         # self.mainWindow.chunk_size = 0
    #         self.mainWindow.output_signal_graph.clear()
    #         self.mainWindow.input_signal_graph.clear()
    #         self.mainWindow.input_signal = []
    #         self.mainWindow.filtered_signal = []
    #         self.first_time_enter = False
    #         print("evvvvvv")
    #         # self.zeros_pos, self.poles_pos = self.calculate_zeros_poles_Pos(self.unit_circle.get_zeros(),
    #         #                                                                 self.unit_circle.get_poles())
    #         # print("unit_circle:", self.zeros)
    #         self.numerator, self.denominator = zpk2tf(
    #             self.zeros_pos, self.poles_pos, 1)
    #         print("enterEvent - After zpk2tf - self.poles_pos:", self.poles_pos)
    #         print("evvvvvviiii")
    #         print("self.zeros_padd:", self.zeros_pos)
    #         print("self.poles_padd:", self.poles_pos)
    #         print("self.numerator:", self.numerator)
    #         print("self.denominator:", self.denominator)
    #
    #         # Get the order of the numerator and denominator
    #         self.order = (len(self.numerator) - 1) + (len(self.denominator) - 1)
    #
    #         if len(self.mainWindow.input_signal) < self.order:
    #             self.mainWindow.input_signal = [0.21] * abs(len(self.mainWindow.input_signal) - self.order)
    # def plot(self):
    #     if self.mainWindow.input_signal:
    #         chunk_size = 1000  # Adjust the chunk size based on your memory constraints
    #
    #         if any(self.denominator):
    #             # Get the initial conditions for the filter
    #             zi = signal.lfilter_zi(self.numerator, self.denominator)
    #
    #             for i in range(0, len(self.mainWindow.input_signal), chunk_size):
    #                 chunk = self.mainWindow.input_signal[i:i + chunk_size]
    #
    #                 # Apply the filter in chunks using initial conditions
    #                 output_points_after_filter, zi = signal.lfilter(self.numerator, self.denominator, chunk, zi=zi)
    #
    #                 # Plot updated output signal for the current chunk
    #                 self.mainWindow.input_signal_graph.plot(chunk, pen='b')
    #                 self.mainWindow.output_signal_graph.plot(output_points_after_filter, pen='r')
    #
    #                 # Clear the plot for the next update (optional)
    #                 self.mainWindow.app.processEvents()
    #         else:
    #             print("Denominator has all zero coefficients. Unable to perform filtering.")

    # def update_filter(self):
    #     print("enter")
    #     # Filter a chunk of data in each iteration
    #     self.zeros_lst = [
    #         complex(self.digital_filter.convert_coordinates(item.scenePos().x()), self.digital_filter.convert_coordinates(-item.scenePos().y()))
    #         for item in self.unit_circle.zeros]
    #     self.poles_lst = [
    #         complex(self.digital_filter.convert_coordinates(item.scenePos().x()), self.digital_filter.convert_coordinates(-item.scenePos().y()))
    #         for item in self.unit_circle.poles]
    #
    #     numerator, denominator = zpk2tf(self.zeros_lst, self.poles_lst, 1)
    #     print("digital_filter.zeros_pos:", self.unit_circle.zeros)
    #     print("digital_filter.poles_pos:", self.poles_lst)
    #     if self.current_position + self.chunk_size <= len(self.input_signal):
    #         chunk_data = self.input_signal[self.current_position:self.current_position + self.chunk_size]
    #         output_chunk = lfilter(numerator, denominator, chunk_data)
    #
    #         # Take the real part of the output before extending the list
    #         self.filtered_signal.extend(np.real(output_chunk))
    #         self.plot_input_and_output_signal()
    #
    #
    #         self.current_position += self.chunk_size
    #         # if self.current_position >= len(self.input_signal):
    #         #     self.restart()
    #
    #
    #     else:
    #         # All data processed, stop the timer
    #         self.timer.stop()
