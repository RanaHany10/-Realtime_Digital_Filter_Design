import numpy as np
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QPushButton, QCheckBox, QListWidgetItem, QWidget
from pyqtgraph import Point
from PyQt5 import QtWidgets, uic
import numpy
import pandas as pd
from digital_filter import DigitalFilter


class PhaseCorrectionWindow(QtWidgets.QMainWindow):
    def __init__(self, mainWindow, all_pass_phase,selescte_filter_phase, all_phase_correction_filters, checked_phase_correction_filters, unit_circle, all_pass_poles, all_pass_zeros,
                 lineEdit, filtersList, zeros_pos, poles_pos, zeros, poles):
        super(PhaseCorrectionWindow, self).__init__()
        uic.loadUi(r'filter.ui', self)

        self.MainWindow = mainWindow
        # self.destroyed.connect(self.on_window_closed)
        self.digital_filter = DigitalFilter
        self.all_pass_poles = all_pass_poles if all_pass_poles is not None else []


        self.all_pass_phase=all_pass_phase
        # self.add_filter_but.clicked.connect(self.add_filter)
        self.selescte_filter_phase = selescte_filter_phase
        self.all_phase_correction_filters= all_phase_correction_filters
        self.checked_phase_correction_filters=checked_phase_correction_filters
        self.lineEdit=lineEdit
        self.all_pass_poles=all_pass_poles
        self.all_pass_zeros=all_pass_zeros
        self.unit_circle=unit_circle
        self.filtersList=filtersList
        # self.mainWindow = self.parent()
        # Plot the phase response
        self.zeros=zeros_pos

        self.poles=poles_pos
        self.zeros_unit=zeros
        self.poles_unit=poles
        self.all_pass_phase.setLabel('left', 'Phase (degree)')
        self.all_pass_phase.setLabel('bottom', 'W (radian/sample)')
        # Plot the phase response
        self.selescte_filter_phase.setLabel('left', 'Phase (degree)')
        self.selescte_filter_phase.setLabel('bottom', 'W (radian/sample)')
        self.all_pass_phase.showGrid(True, True)
        # # Set labels
        # self.selescte_filter_phase.plotItem.setLabel('left', 'Phase (degree)')
        # self.selescte_filter_phase.plotItem.setLabel('bottom', 'W (radian/sample)')
        # Show grid
        self.selescte_filter_phase.plotItem.showGrid(True, True)



        self.fill_filters_list()

        if self.all_pass_poles:
            self.plot_graphs()

        print("Poles All Pass:")

        for pole in self.all_pass_poles:
            print(pole)

        print("Zeros All Pass:")
        for zero in self.all_pass_zeros:
            print(zero)

        print("all Phase Correction Filters:")
        for phase_filter in self.all_phase_correction_filters:
            print(phase_filter)

        print("checked Phase Correction Filters:")
        for phase_filter in self.checked_phase_correction_filters:
            print(phase_filter)


    #
    def add_filter(self):
        print("maraaaaaaaaaaaaaaaaa")
        text = self.lineEdit.text()


        custom_widget = QWidget()
        layout = QHBoxLayout()

        label = QLabel(text)
        label.setStyleSheet("color: white;")
        #to delete filter
        icon_button = QPushButton()
        icon_button.setIcon(QIcon("Icons/delete-svgrepo-com.svg"))
        icon_button.setStyleSheet("background-color:transparent")
        icon_button.clicked.connect(
            lambda: self.delete_from_filters(custom_widget))

        checkbox = QCheckBox()
        checkbox.stateChanged.connect(
            lambda: self.handle_checkbox_change(complex(text))
        )
        print("complex(text)", complex(text))

        layout.addWidget(icon_button)
        layout.addWidget(label)
        layout.addWidget(checkbox)
        custom_widget.setLayout(layout)

        item = QListWidgetItem()
        item.setSizeHint(custom_widget.sizeHint())
        self.filtersList.addItem(item)
        self.filtersList.setItemWidget(item, custom_widget)

        try:
            # text = "1+2j"  # Replace this with the actual value of your text variable
            new_filter = complex(text)
        except ValueError as e:
            print(f"Error: {e}. Please enter a valid complex number.")
        # text = "1"
        # new_filter = complex(text)
        self.all_phase_correction_filters.append(new_filter)
        print("self.all_phase_correction_filters",self.all_phase_correction_filters)

        self.lineEdit.clear()
    #
    def handle_checkbox_change(self, value):
        item = None
        if self.sender().isChecked():
            try:
                item = complex(value)
                print("item", item)
            except ValueError as e:
                print(f"Error: {e}. Please enter a valid complex number.")

            self.checked_phase_correction_filters.append(item)
            if not self.all_pass_zeros:
                self.all_pass_zeros = [1 / item.conjugate()]
            else:
                self.all_pass_zeros.append(1 / item.conjugate())

            if not self.all_pass_poles:
                self.all_pass_poles = [item]
            else:
                self.all_pass_poles.append(item)

        else:
            item = complex(value)
            new_checked_phase_correction_filters = []
            for p in self.checked_phase_correction_filters:
                if str(p) != str(item):
                    new_checked_phase_correction_filters.append(p)
            self.checked_phase_correction_filters = new_checked_phase_correction_filters

            new_all_pass_zeros = []
            for z in self.all_pass_zeros:
                if str(z) != str(1 / item.conjugate()):
                    new_all_pass_zeros.append(z)
                else:
                    for target in self.zeros_unit:
                        print(f"Point is", Point(z.real, z.imag))
                        print(f"target is", target.pos())
                        if Point(z.real, z.imag) == target.pos():

                            self.unit_circle.remove_item(target)
            self.all_pass_zeros = new_all_pass_zeros
            print("self.all_pass_zeros1", self.all_pass_zeros)

            new_all_pass_poles = []
            for p in self.all_pass_poles:
                if str(p) != str(item):
                    new_all_pass_poles.append(p)
                else:
                    for target in self.poles_unit:
                        if Point(p.real, p.imag) == target.pos():
                            self.unit_circle.remove_item(target)
            print("self.zeros_unit", self.zeros_unit)
            print("self.poles_unit", self.poles_unit)

            self.all_pass_poles = new_all_pass_poles
            print("self.all_pass_poles",self.all_pass_poles)

        self.plot_graphs(item)
    #
    def delete_from_filters(self, custom_widget):
        # Find the corresponding item in the QListWidget
        item = self.filtersList.itemAt(custom_widget.pos())
        if item is not None:
            row = self.filtersList.row(item)
            self.filtersList.takeItem(row)

            if 0 <= row < len(self.all_phase_correction_filters):
                removed_filter = complex(self.all_phase_correction_filters.pop(row))
                self.checked_phase_correction_filters = [
                    p for p in self.checked_phase_correction_filters if str(p) != str(removed_filter)]
                self.all_pass_zeros =[z for z in self.all_pass_zeros if str(z) != str(1 / removed_filter.conjugate())]
                self.all_pass_poles = [p for p in self.all_pass_poles if str(p) != str(removed_filter)]

            self.plot_graphs()
    #
    def plot_graphs(self, item=None):
        if item:
            print("abdooooooooooooooo")
            w, _, selected_filter_phase = self.digital_filter.get_the_mag_and_phase(
                self, self.all_pass_zeros, self.all_pass_poles
            )

            # print("w:", w)
            # print("selected_filter_phase:", selected_filter_phase)

            self.selescte_filter_phase.clear()
            self.selescte_filter_phase.plot(w, selected_filter_phase)

            new_zeros_list = self.zeros + self.all_pass_zeros
            new_poles_list = self.poles + self.all_pass_poles

            print("new_zeros_list:", new_zeros_list)
            print("new_poles_list:", new_poles_list)

            w1, _, phase_all_pass = self.digital_filter.get_the_mag_and_phase(
                self, new_zeros_list, new_poles_list
            )

            print("w1:", w1)

            phase_all_pass = np.unwrap(phase_all_pass)
            print("phase_after:", phase_all_pass)

            self.all_pass_phase.clear()
            self.all_pass_phase.plot(w1, np.degrees(phase_all_pass))

    def fill_filters_list(self):
        # Clear the existing items in the filtersList
        self.filtersList.clear()

        # Iterate over the poles and add items to the filtersList
        for phase_correction_filter in self.all_phase_correction_filters:
            self.add_filter_from_pole(phase_correction_filter)

        # self.plot_graphs()
    #
    def add_filter_from_pole(self, pole):
        custom_widget = QWidget()
        layout = QHBoxLayout()

        label = QLabel(str(pole))
        label.setStyleSheet("color:white")

        icon_button = QPushButton()
        icon_button.setIcon(QIcon("Icons/delete-svgrepo-com.svg"))
        icon_button.setStyleSheet("background-color:transparent")
        icon_button.clicked.connect(
            lambda: self.delete_from_filters(custom_widget))

        checkbox = QCheckBox()
        if pole in self.checked_phase_correction_filters:
            checkbox.setCheckState(Qt.CheckState.Checked)
        checkbox.stateChanged.connect(
            lambda: self.handle_checkbox_change(pole)
        )

        layout.addWidget(icon_button)
        layout.addWidget(label)
        layout.addWidget(checkbox)
        custom_widget.setLayout(layout)

        item = QListWidgetItem()
        item.setSizeHint(custom_widget.sizeHint())
        self.filtersList.addItem(item)
        self.filtersList.setItemWidget(item, custom_widget)




