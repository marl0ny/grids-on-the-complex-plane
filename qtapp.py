import sys
from qt_widgets import QtWidgets, QtCore, QtGui
from qt_widgets import HorizontalEntryBox
from qt_widgets import VariableSlidersManager
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from complex_graph import ComplexAnimator
from typing import Union, Tuple, Any


class SetGridInputWidget(QtWidgets.QStackedWidget):
    """
    Set grid input widget.
    """

    def __init__(self, ani: ComplexAnimator) -> None:
        """
        Constructor.

        Parameters:
         ani: complex animator object.
        """
        self._ani = ani
        QtWidgets.QStackedWidget.__init__(self)
        self.setMaximumHeight(50)
        self.setMaximumWidth(300)
        self._button = QtWidgets.QPushButton("Set grid input...")
        self._scroll_area = QtWidgets.QScrollArea()
        self._frame = QtWidgets.QFrame()
        layout = QtWidgets.QVBoxLayout()
        self._frame.setLayout(layout)
        x_min_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(x_min_layout)
        x_min_edit = QtWidgets.QLineEdit()
        x_min_layout.addWidget(QtWidgets.QLabel("x min:"))
        x_min_layout.addWidget(x_min_edit)
        x_max_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(x_max_layout)
        x_max_edit = QtWidgets.QLineEdit()
        x_max_layout.addWidget(QtWidgets.QLabel("x max:"))
        x_max_layout.addWidget(x_max_edit)
        y_min_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(y_min_layout)
        y_min_edit = QtWidgets.QLineEdit()
        y_min_layout.addWidget(QtWidgets.QLabel("y min:"))
        y_min_layout.addWidget(y_min_edit)
        y_max_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(y_max_layout)
        y_max_edit = QtWidgets.QLineEdit()
        y_max_layout.addWidget(QtWidgets.QLabel("y max:"))
        y_max_layout.addWidget(y_max_edit)
        h_lines = QtWidgets.QHBoxLayout()
        layout.addLayout(h_lines)
        h_lines_edit = QtWidgets.QLineEdit()
        h_lines.addWidget(QtWidgets.QLabel(
            "horizontal lines:"))
        h_lines.addWidget(h_lines_edit)
        v_lines = QtWidgets.QHBoxLayout()
        layout.addLayout(v_lines)
        v_lines_edit = QtWidgets.QLineEdit()
        v_lines.addWidget(QtWidgets.QLabel(
            "vertical lines:"))
        v_lines.addWidget(v_lines_edit)
        ok_button = QtWidgets.QPushButton("OK")
        layout.addWidget(ok_button)
        self._line_edits = [x_min_edit, y_min_edit,
                            x_max_edit, y_max_edit,
                            h_lines_edit, v_lines_edit]
        for edit in self._line_edits:
            edit.textChanged.connect(self.on_line_edit_changed)
        self.addWidget(self._button)
        self._scroll_area.setWidget(self._frame)
        self.addWidget(self._scroll_area)
        self._frame.setMaximumWidth(self.width()*0.77)
        ok_button.pressed.connect(self.switch_to_button)
        self._button.pressed.connect(self.switch_to_scroll_area)

    def switch_to_scroll_area(self) -> None:
        """
        Set this widget to show the scroll area
        """
        self.setMaximumHeight(200)
        self.setCurrentIndex(1)

    def switch_to_button(self) -> None:
        """
        Set this widget to show only a button.
        """
        self.setMaximumHeight(50)
        self.setCurrentIndex(0)

    def set_line_edit_text(self) -> None:
        """
        Update the line edit text from the ComplexAnimation
        attribute.
        """
        grid = self._ani.get_grid()
        n_horizontal = grid.get_number_of_horizontal_lines()
        n_vertical = grid.get_number_of_vertical_lines()
        boundaries = [str(grid.get_xlim()[0]),
                      str(grid.get_ylim()[0]),
                      str(grid.get_xlim()[1]),
                      str(grid.get_ylim()[1])]
        boundaries.extend([str(n_horizontal), str(n_vertical)])
        for z in zip(self._line_edits, boundaries):
            z[0].setText(z[1])

    def on_line_edit_changed(self, *arg: Any) -> None:
        """
        On line edit changed function.
        """
        grid = self._ani.get_grid()
        points_per_line = grid.get_number_of_points_per_line()
        try:
            texts = [float(edit.text()) for edit in self._line_edits]
        except ValueError:
            return
        # texts[4] += 1
        # texts[5] += 1
        if texts[0] >= texts[2] or texts[1] >= texts[3]:
            return
        if (texts[4] <= 0 or texts[5] <= 0 or
            texts[4] > 250 or texts[5] > 250):
            return
        self._ani.set_grid(texts[0: 4], points_per_line,
                           int(texts[4]), int(texts[5]))
        print("grid changed")


class ComplexAnimatorQt(ComplexAnimator):
    """
    Extend the ComplexAnimator class for use with
    the PySide2 GUI.
    """

    def set_raw_grid(self, grid: "ComplexGridArray"):
        """
        Switch to a new grid instance.
        """
        self._grid = grid


class Canvas(FigureCanvasQTAgg):
    """
    The canvas.
    """

    def __init__(self,
                 parent: QtWidgets.QMainWindow,
                 rect: QtCore.QRect) -> None:
        """
        The constructor.

        Parameters:
         parent: The parent widget that this
         canvas is being created from
         rect: used to get information
         about the screen width and screen height.
        """
        width = rect.width()
        dpi = int(150*width//1920)
        self._parent = parent
        self._mouse_count = 0
        self._ani = ComplexAnimatorQt(dpi, (6.4, 4.4), 0)
        FigureCanvasQTAgg.__init__(self, self._ani.figure)
        self.setMinimumHeight(400)
        # self.setMinimumWidth(int(width*0.75))
        self._mouse_usage = 0
        self._prev_mouse_position = []

    def _mouse_coordinates_transform(self, 
                                     x: int, y: int) -> Tuple[float, float]:
        """
        Transform the location of the mouse as expressed in terms
        of the coordinates of the GUI window into the coordinates
        of the plot.

        Parameters:
         x: x location of mouse
         y: y location of mouse

        Returns:
         A tuple containing the transformed x and y coordinates.
        """
        ax = self.figure.get_axes()[0]
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        pixel_xlim = [ax.bbox.xmin, ax.bbox.xmax]
        pixel_ylim = [ax.bbox.ymin, ax.bbox.ymax]
        height = self.figure.bbox.ymax
        mx = (xlim[1] - xlim[0])/(pixel_xlim[1] - pixel_xlim[0])
        my = (ylim[1] - ylim[0])/(pixel_ylim[1] - pixel_ylim[0])
        x = (x - pixel_xlim[0])*mx + xlim[0]
        y = (height - y - pixel_ylim[0])*my + ylim[0]
        return x, y

    def _mouse_handler(self, qt_event: QtGui.QMouseEvent) -> None:
        """
        Mouse handling helper function.

        Parameters:
         qt_event: mouse event.
        """
        x = qt_event.x()
        y = qt_event.y()
        if qt_event.buttons() == QtCore.Qt.LeftButton:
            self._mouse_count += 1
            x, y = self._mouse_coordinates_transform(x, y)
            if self._prev_mouse_position != []:
                x_prev, y_prev = self._prev_mouse_position
                dx = x - x_prev
                dy = y - y_prev
                ax = self._ani.figure.get_axes()[0]
                xlim = ax.get_xlim()
                ylim = ax.get_ylim()
                xlim = [xlim[0] - dx,
                        xlim[1] - dx]
                ylim = [ylim[0] - dy,
                        ylim[1] - dy]
                # self._ani.toggle_blit()
                ax.set_xlim(xlim)
                ax.set_ylim(ylim)
                self.draw()
                # self._ani.toggle_blit()
        else:
            self._prev_mouse_position.extend([x, y])
        if qt_event.buttons() == QtCore.Qt.MidButton:
            pass
        if qt_event.buttons() == QtCore.Qt.RightButton:
            pass

    def set_mouse_usage(self, usage: int) -> None:
        """
        Set how the mouse should be used.

        Parameters:
         usage: the mouse usage number.
        """
        self._mouse_usage = usage

    def mousePressEvent(self, qt_event: QtGui.QMouseEvent) -> None:
        """
        Mouse is pressed.

        Parameters:
         qt_event: mouse event.
        """
        # self._ani.toggle_blit()
        self._mouse_count = 0
        if qt_event.buttons() == QtCore.Qt.RightButton:
            self._menu.popup(self.mapToGlobal(qt_event.pos()))
            # if not self._menu.isTearOffEnabled():
            #     self._menu.setTearOffEnabled(True)
            #     self._menu.popup(qt_event.pos())
            #     # self._menu.showTearOffMenu()
            # else:
            #     self._menu.setTearOffEnabled(False)
        x, y = self._mouse_coordinates_transform(qt_event.x(), qt_event.y())
        self._prev_mouse_position = [x, y]
        self._mouse_handler(qt_event)
        # self._ani.toggle_blit()
        self.setMouseTracking(True)

    def mouseMoveEvent(self, qt_event: QtGui.QMouseEvent) -> None:
        """
        Mouse is moved.

        Parameters:
         qt_event: mouse event.
        """
        self._mouse_handler(qt_event)

    def mouseReleaseEvent(self, qt_event: QtGui.QMouseEvent) -> None:
        """
        Mouse is released.

        Parameters:
         qt_event: mouse event.
        """
        self.draw()
        self.setMouseTracking(False)

    def wheelEvent(self, qt_event: QtGui.QWheelEvent) -> None:
        """
        The mouse wheel is moved.

        Parameters:
         qt_event: mouse wheel event.
        """
        wheel_scroll = qt_event.angleDelta().y()
        touch_scroll = qt_event.delta()
        if abs(wheel_scroll) != 120 and touch_scroll != 0.0:
            delta = touch_scroll/5000
            self._ani.scale_axes(1.0 - delta, 1.0 - delta)
        elif abs(wheel_scroll) == 120:
            if wheel_scroll == 120:
                self._ani.scale_axes(0.9, 0.9)
            elif wheel_scroll == -120:
                self._ani.scale_axes(1.1, 1.1)
        self.draw()

    def get_animation(self):
        """
        Getter for the animation object.

        Returns:
         The animation object.
        """
        return self._ani

    def animation_loop(self) -> None:
        """
        Do the main animation loop.
        """
        self._ani.animation_loop()


class App(QtWidgets.QMainWindow):
    """
    Main qt5 app.
    """

    def __init__(self) -> None:
        """
        Initializer.
        """
        QtWidgets.QMainWindow.__init__(self)
        self.setWindowTitle("A simple GUI")
        self.menu_bar = self.menuBar()
        file_menu = self.menu_bar.addMenu('&file')
        file_menu.addAction("Save figure",
                            lambda: self.canvas.get_animation().
                                    figure.savefig("figure.png"))
        file_menu.addAction("Quit",
                            lambda: QtWidgets.QApplication.exit())
        self.help = self.menu_bar.addMenu('&help')
        dialogue = QtWidgets.QMessageBox(self)
        # dialogue.aboutQt(self, "Title")
        self.message_box = dialogue
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.help.addAction("instructions", self.show_instructions)
        self.help.addAction("about the GUI", self.show_about_gui)
        # self._scroll_area = None
        # self.sliders = []
        self._setting_sliders = False
        self.variable_sliders = VariableSlidersManager(parent=self)
        self.window = QtWidgets.QWidget(self)
        self.layout = QtWidgets.QHBoxLayout(self.window)
        rect = QtWidgets.QApplication.desktop().screenGeometry()
        self.canvas = Canvas(self, rect)
        color_name = self.window.palette().color(
                QtGui.QPalette.Background).name()
        self.canvas.get_animation().figure.patch.set_facecolor(color_name)
        # self.layout.addWidget(self.menu_bar)
        self.set_grid_input = SetGridInputWidget(self.canvas.get_animation())
        self.layout.addWidget(self.canvas)
        self.control_widgets = QtWidgets.QVBoxLayout()
        self.layout.addLayout(self.control_widgets)
        self._build_control_widgets()
        self.setCentralWidget(self.window)
        self.canvas.animation_loop()
        self.on_dropdown_changed(0)

    def _build_control_widgets(self):
        """
        Build the control widgets.
        """
        self.toggle_id = \
            QtWidgets.QPushButton(text="Toggle grid input")
        self.toggle_id.setMaximumWidth(300)
        ani = self.canvas.get_animation()
        self.toggle_id.pressed.connect(
            lambda *arg: (ani.toggle_domain(), self.canvas.draw()))
        self.entry = HorizontalEntryBox(
            "Enter f(z)")
        self.dropdown_dict = {
            "identity": "z",
            "sine": "a*sin(w*z)",
            "cosine": "a*cos(w*z)",
            "exp": "a*exp(w*z)",
            "erf": "a*erf(w*z)",
            "gaussian": "a*exp(-z**2/(2*(sigma)**2))/2",
            "sinc": "a*sinc(w*(6.5)*z)/2",
            "inverse z": "w/(z - a)",
            "zeta": "zeta(k*(z - w))",
            "inverse z squared": "1/(w*(z-a))**2"
            }
        dropdown_list = ["Preset f(z)"]
        dropdown_list.extend([key for key in self.dropdown_dict])
        self.dropdown = QtWidgets.QComboBox(self)
        self.dropdown.setMaximumWidth(300)
        self.dropdown.addItems(dropdown_list)
        self._zeta_selected_from_dropdown = False
        self._grid_before_zeta_selected = None
        if hasattr(self.dropdown, "textActivated"):
            self.dropdown.textActivated.connect(self.on_dropdown_changed)
        else:
            self.dropdown.activated.connect(self.on_dropdown_changed)
        self.entry.set_observers([self])
        # self.control_widgets.addWidget(self.mouse_dropdown)
        self.set_grid_input.set_line_edit_text()
        self.control_widgets.addWidget(self.toggle_id)
        self.set_grid_input.setMinimumHeight(0)
        self.control_widgets.addWidget(self.set_grid_input)
        self.control_widgets.addWidget(self.dropdown)
        self.control_widgets.addWidget(self.entry)

    def show_instructions(self) -> None:
        """
        Show instructions.
        """
        message = (
            "Hold down the left mouse button on the plot and move "
            "the mouse around to change the view of the plot. "
            "Use the mouse wheel to zoom in or out. To plot a new function " 
            "either type a new function in the Enter f(z) entry box and hit "
            "the return key, or select a new function in the "
            "Preset f(z) dropdown menu. Note that the function entered must "
            "at least depend on z, where any other variable"
            " becomes a parameter that you can vary using the sliders. "
            "The value of these sliders may be changed by either using the "
            "mouse to change the position of the slider, or by"
            " double clicking the label above and changing the text to "
            "a different value. To change the range of the slider right click "
            "and select the Select Range option. "
            "This adds a range control widget directly below the slider "
            "with options for changing the slider's "
            "maximum and minimum values, as well as its tick count. "
            "To view the initial input of the function "
            "press Toggle grid input. To change the input of the "
            "function click on Set grid input button and then change the"
            " input from here."
        )
        self.message_box.about(self, "Instructions", message)

    def show_about_gui(self) -> None:
        """
        Show the about dialog.
        """
        message = (r"The GUI is built using "
                   r"<a href=https://wiki.qt.io/Qt_for_PythonPySide2>"
                   r"PySide2</a>,"
                   r" which is published under the"
                   r" <a href=https://www.gnu.org/licenses/"
                   r"lgpl-3.0.en.html>LGPL</a>."
                   )
        self.message_box.about(self, "About", message)

    def on_dropdown_changed(self, text: Union[int, str]) -> None:
        """
        Perform an action when the dropdown is changed.

        Parameters:
         text: either the index of the dropdown or text
         at the given index of the dropdown.
        """
        if isinstance(text, int):
            n = text
            text = self.dropdown.itemText(n)
        if not text == "Preset f(z)":
            if not self._zeta_selected_from_dropdown and text == "zeta":
                self._zeta_selected_from_dropdown = True
                self._grid_before_zeta_selected = (
                    self.canvas.
                    get_animation().get_grid().get_copy())
                pi = 3.141592653589793
                s = pi/30
                self.canvas.get_animation().set_grid([-8*pi/5, -pi, 8*pi/5, pi],
                                                      250, int((8*pi/5)/s), 
                                                      int((2*pi)/s))
                self.set_grid_input.set_line_edit_text()
            elif self._zeta_selected_from_dropdown and text != "zeta":
                ani = self.canvas.get_animation()
                ani.set_raw_grid(self._grid_before_zeta_selected)
                self._zeta_selected_from_dropdown = False
                self.set_grid_input.set_line_edit_text()
            self.set_function_from_text(self.dropdown_dict[text])

    def set_function_from_text(self, text: str) -> None:
        """
        Set the function from text.

        Parameters:
         text: function expressed as a string.
        """
        if text.strip() != "":
            function_name = text
            try:
                ani = self.canvas.get_animation()
                ani.set_function(function_name)
            except Exception as e:
                print(e)
                return
            self.destroy_sliders()
            self._setting_sliders = True
            # d = ani.function.get_default_values()
            d = ani.function.get_enumerated_default_values()
            d2 = {}
            for i in range(len(d)):
                symbol = d[i][0]
                val = d[i][1]
                d2[2*i] = ["Re(%s)" % symbol, val]
                d2[2*i + 1] = ["Im(%s)" % symbol, 0]
            self.variable_sliders.set_sliders(
                [self.control_widgets], d2)
            # self.control_widgets.addWidget(self.circles_slider)
            # self.control_widgets.addWidget(self.slider_speed)
            self._setting_sliders = False
            self.on_slider_changed({})
            self.canvas.draw()

    def on_slider_changed(self, slider_input: dict) -> None:
        """
        When the slider is changed perform some action.

        Parameters:
         slider_input: a dictionary containing information
         about the slider.
        """
        if slider_input == {}:
            ani = self.canvas.get_animation()
            ani.set_params()
        if not self._setting_sliders:
            params = self.variable_sliders.get_slider_parameters()
            params2 = [params[i] + params[i + 1]*1.0j
                       for i in range(0, len(params), 2)]
            ani = self.canvas.get_animation()
            ani.set_params(*params2)

    def destroy_sliders(self) -> None:
        """
        Destroy the sliders.
        """
        self.variable_sliders.destroy_sliders(
            [self.control_widgets, self.layout])

    def on_entry_returned(self, text: str) -> None:
        """
        Perform an action when the enter function is pressed.

        Parameters:
         text: a string from an entry box.
        """
        self.set_function_from_text(text)


if __name__ == "__main__":
    # import matplotlib.pyplot as plt
    qt_app = QtWidgets.QApplication(sys.argv)
    app = App()
    # style = QtWidgets.QStyle()
    # style.s
    # app.setStyle(QtWidgets.QStyle())
    app.show()
    sys.exit(qt_app.exec_())
