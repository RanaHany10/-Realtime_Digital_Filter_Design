from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt
from digital_filter import DigitalFilter
# from padding_area import PaddingArea



class UnitCircle:
    def __init__(self, mainWindow, scene, zplane, zero_button, pole_button, conjugate, magnitude_response_widget, phase_response_widget):
        self.mainWindow = mainWindow
        self.scene = scene
        self.zplane = zplane
        self.zero_button = zero_button
        self.pole_button = pole_button
        self.conjugate = conjugate
        self.zeros = []
        self.poles = []
        self.magnitude_response_widget = magnitude_response_widget
        self.phase_response_widget = phase_response_widget
        self.digital_filter = DigitalFilter(self.zeros, self.poles, self.magnitude_response_widget,
                                            self.phase_response_widget,self.mainWindow.all_pass_phase)
        # self.padding_area = PaddingArea(self.mainWindow)


    def draw_unit_circle(self):
        # Function to draw the unit circle on the z-plane
        circle = QtWidgets.QGraphicsEllipseItem(-165, -165, 330, 330)
        pen = QtGui.QPen(QtGui.QColor(Qt.white))
        pen.setWidth(2)  # Set the pen width to a larger value for boldness
        circle.setPen(pen)
        self.scene.addItem(circle)

        # Add x-axis line
        x_axis = QtWidgets.QGraphicsLineItem(-165, 0, 165, 0)
        pen.setWidth(2)
        x_axis.setPen(pen)
        x_axis.setPos(0, 0)
        self.scene.addItem(x_axis)

        # Add y-axis line
        y_axis = QtWidgets.QGraphicsLineItem(0, -165, 0, 165)
        y_axis.setPen(pen)
        y_axis.setPos(0, 0)
        self.scene.addItem(y_axis)

        # Add grid
        grid_pen = QtGui.QPen(QtGui.QColor(Qt.gray))
        grid_pen.setWidth(1)
        for i in range(-165, 165, 33):  # Adjust the range and step as needed
            # Horizontal lines
            h_line = QtWidgets.QGraphicsLineItem(-165, i, 165, i)
            h_line.setPen(grid_pen)
            self.scene.addItem(h_line)
            # Vertical lines
            v_line = QtWidgets.QGraphicsLineItem(i, -165, i, 165)
            v_line.setPen(grid_pen)
            self.scene.addItem(v_line)

        self.zplane.mousePressEvent = self.on_mouse_press
        self.zplane.mouseMoveEvent = self.on_mouse_move

    # Function to add a zero or pole on the unit circle
    def add_zero_pole(self, x, y, is_zero=True):
        item = None
        pen_color = Qt.green if is_zero else Qt.red

        if is_zero:
            item = QtWidgets.QGraphicsEllipseItem(-10, -10, 20, 20)
        else:
            item = QtWidgets.QGraphicsPathItem()
            path = QtGui.QPainterPath()
            path.moveTo(-10, -10)
            path.lineTo(10, 10)
            path.moveTo(10, -10)
            path.lineTo(-10, 10)
            item.setPath(path)

        pen = QtGui.QPen(pen_color)
        pen.setWidth(3)  # to adjust thickness of pole and zero
        item.setZValue(1)
        item.setPen(pen)
        item.setPos(x, y)
        self.scene.addItem(item)
        return item

    def on_mouse_press(self, event):
        # Handle mouse press event for adding zeros and poles
        pos = self.zplane.mapToScene(event.pos())
        items = self.scene.items(pos)
        print(items)
        existing_poles = [item for item in self.poles if item.sceneBoundingRect().contains(pos)]
        existing_zeros = [item for item in self.zeros if item.sceneBoundingRect().contains(pos)]
        if event.buttons() & Qt.LeftButton:
            for item in items:
                print("sara")
                if item in self.zeros:
                    print("abdo")
                    self.zeros.remove(item)
                    self.scene.removeItem(item)
                elif item in self.poles:
                    self.poles.remove(item)
                    self.scene.removeItem(item)
                self.digital_filter.plot_magnitude_and_phase()

            if not existing_zeros and not existing_poles:
                if self.zero_button.isChecked():
                    print("sara")
                    if self.conjugate.isChecked():
                        # Add conjugate zeros and poles
                        # self.zeros.append(self.add_zero_pole(pos.x(), pos.y(),True))
                        # self.zeros.append(self.add_zero_pole(pos.x(), -pos.y(),True))
                        self.zeros.extend([
                            self.add_zero_pole(pos.x(), pos.y(), True),
                            self.add_zero_pole(pos.x(), -pos.y(), True)
                        ])
                    else:
                        self.zeros.append(self.add_zero_pole(pos.x(), pos.y(), True))
                    # Set the z-value for the zeros
                elif self.pole_button.isChecked():
                    if self.conjugate.isChecked():
                        # Add conjugate zeros and poles
                        # self.poles.append(self.add_zero_pole(pos.x(), pos.y(),False))
                        # self.poles.append(self.add_zero_pole(pos.x(), -pos.y(),False))
                        self.poles.extend([
                            self.add_zero_pole(pos.x(), pos.y(), False),
                            self.add_zero_pole(pos.x(), -pos.y(), False)
                        ])
                    else:
                        self.poles.append(self.add_zero_pole(pos.x(), pos.y(), False))
            print(len(self.zeros), len(self.poles))
            # After adding or removing zeros/poles, update the magnitude response plot
            self.digital_filter.plot_magnitude_and_phase()
            self.mainWindow.update_zeros_poles(self.zeros, self.poles)
            print("self.pooooooles:", self.poles)


    def on_mouse_move(self, event):
        # Handle mouse move event for modifying placed zeros and poles
        pos = self.zplane.mapToScene(event.pos())
        items = self.scene.items(pos)

        for item in items:
            if item in self.zeros or item in self.poles:
                item.setPos(pos.x(), pos.y())
        self.digital_filter.plot_magnitude_and_phase()
        # self.mainWindow.update_zeros_poles(self.zeros, self.poles)

    def clear_all_zeros_and_poles(self, *lists):
        for lst in lists:
            for item in lst:
                self.scene.removeItem(item)
            lst.clear()
        self.digital_filter.plot_magnitude_and_phase()

    def get_zeros(self):
        return self.zeros

    def get_poles(self):
        return self.poles


