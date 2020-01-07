"""
main Tkinter GUI program

TODO:
-Get the modify grid properly working
-Add sliders to the modify grid
-Decrease the computational time of the zeta and eta functions
-Look at better ways to toggle blitting.
-Need to improve moving the plots by mouse

ISSUES:
-The logarithmic function looks wrong.
-The implementation of the (approximate) zeta function
 may be unstable.
"""

import tkinter as tk
from numpy import pi
from complex_graph import ComplexAnimator, VariableNotFoundError
from matplotlib.backends import backend_tkagg
from numpy import sqrt


class App(ComplexAnimator):
    """
    Tkinter app.
    """
    def __init__(self) -> None:
        """
        The constructor.
        """
        self.window = tk.Tk()
        self.window.title("Complex Mapper")
        width = self.window.winfo_screenwidth()
        dpi = int(150*width//1920)
        ComplexAnimator.__init__(self, dpi, (6.4, 4.4), 0)

        # Thanks to StackOverflow user rudivonstaden for
        # giving a way to get the colour of the tkinter widgets:
        # https://stackoverflow.com/questions/11340765/
        # default-window-colour-tkinter-and-hex-colour-codes
        #
        #     https://stackoverflow.com/q/11340765
        #     [Question by user user2063:
        #      https://stackoverflow.com/users/982297/user2063]
        #
        #     https://stackoverflow.com/a/11342481
        #     [Answer by user rudivonstaden:
        #      https://stackoverflow.com/users/1453643/rudivonstaden]
        #
        colour = self.window.cget('bg')
        if colour == 'SystemButtonFace':
            colour = "#F0F0F0"
        # Thanks to StackOverflow user user1764386 for
        # giving a way to change the background colour of a plot.
        #
        #    https://stackoverflow.com/q/14088687
        #    [Question by user user1764386:
        #     https://stackoverflow.com/users/1764386/user1764386]
        #
        self.figure.patch.set_facecolor(colour)

        self.canvas = backend_tkagg.FigureCanvasTkAgg(
            self.figure,
            master=self.window
            )
        self.canvas.get_tk_widget().grid(
                row=0, column=0, rowspan=12, columnspan=3)
        self.toggle_domain_button = tk.Button(self.window,
                                              text="Toggle "
                                                   "grid input",
                                              command=self.toggle_domain)
        self.toggle_domain_button.grid(row=0, column=3,
                                       sticky=tk.S + tk.E + tk.W,
                                       padx=(10, 10),
                                       pady=(0, 0))
        self.grid_popup_button = tk.Button(self.window,
                                           text="Set grid input...",
                                           command=self.adjust_grid)
        self.grid_popup_button.grid(row=1, column=3,
                                    sticky=tk.N + tk.S + tk.E + tk.W,
                                    padx=(10, 10),
                                    pady=(0, 0))
        self.function_string = ""
        self._zeta_selected_from_dropdown = False
        self._grid_before_zeta_selected = None
        self.function_dropdown_dict = {
            "identity": "z",
            "sine": "a*sin(w*z)",
            "cosine": "a*cos(w*z)",
            "exp": "a*exp(w*z)",
            "erf": "a*erf(w*z)",
            "gaussian": "a*exp(-z**2/(2*(sigma)**2))/2",
            "sinc": "a*sinc(w*(6.5)*z)/2",
            "inverse z": "w/(z - a)",
            "zeta": "zeta(k*(z - w))"
            }
        self.function_dropdown_string = tk.StringVar(self.window)
        self.function_dropdown_string.set("Preset f(z)")
        self.function_dropdown = tk.OptionMenu(
            self.window,
            self.function_dropdown_string,
            *tuple(key for key in self.function_dropdown_dict),
            command=self.set_function_dropdown
            )
        self.function_dropdown.grid(
                row=2, column=3, padx=(10, 10), pady=(0, 0))
        self.enter_function_label = tk.Label(
                self.window,
                text="Enter f(z)",
                )
        self.enter_function_label.grid(row=3, column=3,
                                       sticky=tk.S + tk.E + tk.W,
                                       padx=(10, 10),
                                       pady=(0, 0))
        self.enter_function = tk.Entry(self.window)
        self.enter_function.grid(row=4, column=3,
                                 sticky=tk.N + tk.E + tk.W + tk.S,
                                 padx=(10, 10))
        self.enter_function.bind("<Return>", self.set_function_entry)
        self.update_button = tk.Button(self.window, text='OK',
                                       command=self.set_function_entry)
        self.update_button.grid(row=5, column=3,
                                sticky=tk.N + tk.E + tk.W,
                                padx=(10, 10),
                                pady=(0, 0)
                                )

        # Right click menu
        # self.menu = tk.Menu(self.window, tearoff=0)
        # self.menu.add_command(label="Differentiate Function",
        #                       command=self.differentiate)
        # self.menu.add_command(label="Antidifferentiate Function",
        #                       command=self.antidifferentiate)
        # self.window.bind("<ButtonRelease-3>", self.popup_menu)

        self.canvas.get_tk_widget().bind_all("<MouseWheel>", self.zoom)
        self.canvas.get_tk_widget().bind_all("<Button-4>", self.zoom)
        self.canvas.get_tk_widget().bind_all("<Button-5>", self.zoom)
        self._prev_mouse_position = []
        self.canvas.get_tk_widget().bind("<B1-Motion>", self.mouse_movement)
        self.canvas.get_tk_widget().bind("<B4-Motion>", self.mouse_movement)
        self.canvas.get_tk_widget().bind("<B5-Motion>", self.mouse_movement)
        self.canvas.get_tk_widget().bind("<Key>", self.key_input)

        self.real_sliderslist = []
        self.imag_sliderslist = []
        self.circles_slider = None
        self.slider_speed = None
        self._speed = 1
        self.quit_button = None
        self._set_widgets_after_param_sliders()

    def _set_widgets_after_param_sliders(self, k: int = 5) -> None:
        """
        Set widgets after parameter sliders
        """
        self.quit_button = tk.Button(
                self.window, text='QUIT',
                command=lambda *args: [
                        self.window.quit(), self.window.destroy()]
                    )
        self.quit_button.grid(row=k+3, column=3, pady=(0, 0))

    def set_function_entry(self, *event: tk.Event):
        """
        Update the function using the text entry.
        """
        self.enter_function.focus()
        try:
            if self._zeta_selected_from_dropdown:
                self._grid = self._grid_before_zeta_selected
                self._zeta_selected_from_dropdown = False
            self.function_string = self.enter_function.get()
            self.set_function(self.function_string)
            self.set_widgets()
        except VariableNotFoundError:
            print("Input not recognized.\nInput function must:\n"
                  "- depend on at least z\n"
                  "- be a recognized function\n"
                  "- use '**' instead of '^' for powers\n")

    def set_function_dropdown(self, *event: tk.Event) -> None:
        """
        Update the function by the dropdown menu.
        """
        event = event[0]
        if event == "zeta" and not self._zeta_selected_from_dropdown:
            self._grid_before_zeta_selected = self._grid.get_copy()
            s = pi/30
            self.set_grid([-8*pi/5, -pi, 8*pi/5, pi],
                          250, int((8*pi/5)/s), int((2*pi)/s))
            self._zeta_selected_from_dropdown = True
        elif event != "zeta" and self._zeta_selected_from_dropdown:
            self._grid = self._grid_before_zeta_selected
            self._zeta_selected_from_dropdown = False
        self.function_string = self.function_dropdown_dict[event]
        self.set_function(self.function_string)
        self.set_widgets()

    def slider_update(self, *event: tk.Event) -> None:
        """
        Update the parameters using the sliders.
        """
        params = []
        for i in range(len(self.real_sliderslist)):
            params.append(self.real_sliderslist[i].get())
            params[i] += 1.0j*self.imag_sliderslist[i].get()
        self.set_params(*params)

    def set_widgets(self) -> None:
        """
        Set the widgets
        """
        rnge = 10.0
        for slider in self.real_sliderslist:
            slider.destroy()
        for slider in self.imag_sliderslist:
            slider.destroy()
        self.real_sliderslist = []
        self.imag_sliderslist = []
        self.quit_button.destroy()
        default_vals = self.function.get_default_values()
        k = 0
        for i, symbol in enumerate(self.function.parameters):
            self.real_sliderslist.append(tk.Scale(self.window,
                                                  label="change Re(%s):" % (
                                                          str(symbol)),
                                                  from_=-rnge, to=rnge,
                                                  resolution=0.01,
                                                  orient=tk.HORIZONTAL,
                                                  length=200,
                                                  command=self.slider_update))
            self.real_sliderslist[i].grid(row=2*i + 6, column=3,
                                          sticky=tk.N + tk.E + tk.W,
                                          padx=(10, 10), pady=(0, 0))
            self.real_sliderslist[i].set(default_vals[symbol])
            self.imag_sliderslist.append(tk.Scale(self.window,
                                                  label="change Im(%s):" % (
                                                          str(symbol)),
                                                  from_=-rnge, to=rnge,
                                                  resolution=0.01,
                                                  orient=tk.HORIZONTAL,
                                                  length=200,
                                                  command=self.slider_update))
            self.imag_sliderslist[i].grid(row=2*i + 7, column=3,
                                          sticky=tk.N + tk.E + tk.W,
                                          padx=(10, 10), pady=(0, 0))
            k += 1
        self._set_widgets_after_param_sliders(2*k+5)

    def mouse_movement(self, event) -> None:
        """
        Respond to mouse movement on the canvas.
        """
        self.canvas.get_tk_widget().focus()
        x = event.x
        y = event.y
        if self._prev_mouse_position != []:
            x_prev, y_prev = self._prev_mouse_position
            distance = sqrt((x - x_prev)**2 + (y - y_prev)**2)
            if distance < 1e-30:
                return
            dx = (x - x_prev)/distance
            dy = (y - y_prev)/distance
            self.move_axes(-dx/25.0, dy/25.0)
            self._prev_mouse_position[0] = x
            self._prev_mouse_position[1] = y
        else:
            self._prev_mouse_position.extend([x, y])

    def zoom(self, event: tk.Event) -> None:
        """
        Zoom in and out on the plot.
        """
        if event.delta == -120 or event.num == 5:
            self.scale_axes(1.1, 1.1)
        elif event.delta == 120 or event.num == 4:
            self.scale_axes(0.9, 0.9)

    def key_input(self, event: tk.Event) -> None:
        """
        Respond to key input on the canvas.
        """
        c = str(repr(event.char))
        letters = (
            'a', 'w', 's', 'd',
            'r', 'f',
            'W', 'A', 'S', 'D')
        if any([(letter in c) for letter in letters]):
            if 'f' in c:
                self.scale_axes(1.1, 1.1)
            elif 'r' in c:
                self.scale_axes(0.9, 0.9)
            if ('w' in c) or ('W' in c):
                self.move_axes(0.0, 0.1)
            if ('a' in c) or ('A' in c):
                self.move_axes(-0.1, 0.0)
            if ('s' in c) or ('S' in c):
                self.move_axes(0.0, -0.1)
            if ('d' in c) or ('D' in c):
                self.move_axes(0.1, 0.0)

    def adjust_grid(self) -> None:
        ModifyGridPopup(self)

    # def popup_menu(self, event) -> None:
    #     """
    #     popup menu upon right click.
    #     """
    #     self.menu.tk_popup(event.x_root, event.y_root, 0)

    # def differentiate(self, *args) -> None:
    #     """
    #     Differentiate the function.
    #     """
    #     self.function.derivative()
    #     self.update_title()
    #     self.notify_change()

    # def antidifferentiate(self, *args) -> None:
    #     """
    #     Anti-differentiate the function.
    #     """
    #     self.function.antiderivative()
    #     self.update_title()
    #     self.notify_change()


class ModifyGridPopup:
    """
    Modify domain grid popup.
    """

    def __init__(self, main_window) -> None:
        """
        Constructor
        """
        self.main_window = main_window
        self.window = tk.Toplevel()
        # self.window.pack()
        self.widgets = {}
        xlim = self.main_window.get_grid().get_xlim()
        ylim = self.main_window.get_grid().get_ylim()

        self.widgets['Set xmin label'] = tk.Label(self.window,
                                                  text="Set minimum x value",
                                                  width=40)
        self.widgets['Set xmin label'].pack()
        self.widgets[0] = tk.Entry(self.window)
        self.widgets[0].pack()
        self.widgets[0].insert(0, str(xlim[0]))

        self.widgets['Set ymin label'] = tk.Label(self.window,
                                                  text="Set minimum y value")
        self.widgets['Set ymin label'].pack()
        self.widgets[1] = tk.Entry(self.window)
        self.widgets[1].pack()
        self.widgets[1].insert(0, str(ylim[0]))

        self.widgets['Set xmax label'] = tk.Label(self.window,
                                                  text="Set maximum x value")
        self.widgets['Set xmax label'].pack()
        self.widgets[2] = tk.Entry(self.window)
        self.widgets[2].pack()
        self.widgets[2].insert(0, str(xlim[1]))

        self.widgets['Set ymax label'] = tk.Label(self.window,
                                                  text="Set maximum y value")
        self.widgets['Set ymax label'].pack()
        self.widgets[3] = tk.Entry(self.window)
        self.widgets[3].pack()
        self.widgets[3].insert(0, str(ylim[1]))

        self.widgets['Set number of vertical lines'] = tk.Label(self.window,
                                                                text=""
                                                                "Set number of"
                                                                "vertical "
                                                                "lines")
        self.widgets['Set number of vertical lines'].pack()
        self.widgets[4] = tk.Entry(self.window)
        self.widgets[4].pack()
        m = self.main_window.get_grid().get_number_of_vertical_lines()
        self.widgets[4].insert(0, m)

        self.widgets['Set number of horizontal lines'] = tk.Label(self.window,
                                                                  text=""
                                                                  "Set number "
                                                                  "of "
                                                                  "horizontal "
                                                                  "lines")
        self.widgets['Set number of horizontal lines'].pack()
        self.widgets[5] = tk.Entry(self.window)
        self.widgets[5].pack()
        m = self.main_window.get_grid().get_number_of_horizontal_lines()
        self.widgets[5].insert(0, m)

        self.widgets['OK'] = tk.Button(self.window,
                                       text="OK",
                                       command=self.adjust_grid)
        self.widgets['OK'].pack()

    def adjust_grid(self) -> None:
        """
        Adjust the parameters of the grid.
        """
        if int(self.widgets[4].get()) > 120:
            return
        dimensions = [float(self.widgets[i].get()) for i in range(4)]
        self.main_window.set_grid(dimensions,
                                  1000,
                                  int(self.widgets[5].get()),
                                  int(self.widgets[4].get()))

    def slider_update(self, *event: tk.Event) -> None:
        """
        Update the grid using sliders.
        """
        pass


if __name__ == "__main__":
    app = App()
    app.animation_loop()
    tk.mainloop()
