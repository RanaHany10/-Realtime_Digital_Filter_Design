import numpy as np
from pyqtgraph import mkPen
from scipy import signal


class DigitalFilter:
    def __init__(self, zeros, poles, magnitude_response_widget, phase_response_widget, all_pass_phase):
        self.zeros = zeros
        self.poles = poles
        self.magnitude_response_widget = magnitude_response_widget
        self.phase_response_widget = phase_response_widget
        self.zeros_pos = []
        self.poles_pos = []
        self.all_pass_phase=all_pass_phase

    def convert_coordinates(self, pos, old_range=(-165, 165), new_range=(-1, 1)):
        old_min, old_max = old_range
        new_min, new_max = new_range

        old_range_size = old_max - old_min
        new_range_size = new_max - new_min

        # Scale the position from the old range to the new range
        scaled_pos = (pos - old_min) / old_range_size * new_range_size + new_min

        return scaled_pos

    # def frequency_response(self):
    #     # Get the zeros and poles from the lists
    #     # zeros = [complex(item.scenePos().x(), -item.scenePos().y()) for item in self.zeros]
    #     # poles = [complex(item.scenePos().x(), -item.scenePos().y()) for item in self.poles]
    #     self.zeros_pos = [complex(self.convert_coordinates(item.scenePos().x()), self.convert_coordinates(-item.scenePos().y()))
    #              for item in self.zeros]
    #     self.poles_pos = [complex(self.convert_coordinates(item.scenePos().x()), self.convert_coordinates(-item.scenePos().y()))
    #              for item in self.poles]
    #     print("Zeros:", self.zeros_pos)
    #     print("Poles:", self.poles)
    #
    #     # Calculate the system transfer function
    #     sys = signal.ZerosPolesGain(self.zeros_pos, self.poles_pos, 1)
    #
    #     # Compute the frequency response
    #     w, h = signal.freqz_zpk(sys.zeros, sys.poles, sys.gain)
    #
    #     # Update the magnitude response plot using pyqtgraph
    #     self.magnitude_response_widget.clear()
    #     pen_mag = mkPen(color=(0, 0, 255))  # Adjust color for magnitude plot
    #     self.magnitude_response_widget.plot(w, 20 * np.log10(np.abs(h)), pen=pen_mag)  # Plot in dB
    #     # self.magnitude_response_widget.plot(w, 20 * np.log10(np.abs(h) + 1e-15), pen=pen_mag)  # Plot in dB
    #
    #     self.magnitude_response_widget.setLabel('left', 'Magnitude', units='dB')
    #
    #     # Compute and plot the unwrapped phase response
    #     phase_response = np.unwrap(np.angle(h))
    #     self.phase_response_widget.clear()
    #     pen_phase = mkPen(color=(255, 0, 0))  # Adjust color for phase plot
    #     self.phase_response_widget.plot(w, np.degrees(phase_response), pen=pen_phase)
    #     self.phase_response_widget.setLabel('left', 'Phase', units='degrees')

    def get_the_mag_and_phase(self, zeros, poles):
        # Calculate the system transfer function
        sys = signal.ZerosPolesGain(zeros, poles, 1)

        # Compute the frequency response
        w, h = signal.freqz_zpk(zeros, poles, 1)
        frequencies = w
        mag_response = np.abs(h)
        phase_response = np.angle(h)

        return frequencies, mag_response, phase_response

    def plot_magnitude_and_phase(self):
        # Get the zeros and poles from the lists
        # zeros = [complex(item.scenePos().x(), -item.scenePos().y()) for item in self.zeros]
        # poles = [complex(item.scenePos().x(), -item.scenePos().y()) for item in self.poles]
        self.zeros_pos = [
            complex(self.convert_coordinates(item.scenePos().x()), self.convert_coordinates(-item.scenePos().y()))
            for item in self.zeros]
        self.poles_pos = [
            complex(self.convert_coordinates(item.scenePos().x()), self.convert_coordinates(-item.scenePos().y()))
            for item in self.poles]
        print("Zeros:", self.zeros_pos)
        print("Poles:", self.poles_pos)
        w, mag, phase = self.get_the_mag_and_phase(self.zeros_pos, self.poles_pos)

        # Update the magnitude response plot using pyqtgraph
        self.magnitude_response_widget.clear()
        pen_mag = mkPen(color=(0, 0, 255))  # Adjust color for magnitude plot
        self.magnitude_response_widget.plot(w, 20 * np.log10(mag), pen=pen_mag)  # Plot in dB
        # self.magnitude_response_widget.plot(w, 20 * np.log10(np.abs(h) + 1e-15), pen=pen_mag)  # Plot in dB

        self.magnitude_response_widget.setLabel('left', 'Magnitude', units='dB')

        # Compute and plot the unwrapped phase response
        phase_response = np.unwrap(phase)
        print("phase_before:", phase_response)
        self.phase_response_widget.clear()
        self.all_pass_phase.clear()
        pen_phase = mkPen(color=(255, 0, 0))  # Adjust color for phase plot
        self.phase_response_widget.plot(w, np.degrees(phase_response), pen=pen_phase)
        self.phase_response_widget.setLabel('left', 'Phase', units='degrees')
        self.all_pass_phase.plot(w, np.degrees(phase_response), pen=pen_phase)
        self.all_pass_phase.setLabel('left', 'Phase', units='degrees')
