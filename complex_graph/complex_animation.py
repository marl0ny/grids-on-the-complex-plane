import numpy as np
from .animator import Animator
from sympy import abc
from .functions import FunctionZtoZ
from .complex_grid import ComplexGridArray
from .complex_grid import plot_complex_grid, update_complex_grid
from typing import Any, List


class ComplexAnimator(Animator):
    """
    Class that encapsulates animation for a plot of the complex grid.
    """

    def __init__(self, dpi: int, figsize: tuple, interval: int) -> None:
        """
        Initializer.
        """
        Animator.__init__(self, dpi, figsize, interval)
        ax = self.figure.add_subplot(111, aspect='equal')
        s = np.pi/60
        self._PRINT_FPS = False
        self._grid = ComplexGridArray(
            [-np.pi/2, -np.pi/3, np.pi/2, np.pi/3], 1000,
            int((np.pi/2)/s), int((2*np.pi/3)/s)
            )
        self.t = 0.0
        self._params = ()
        self.function = FunctionZtoZ("sin(z)", abc.z)
        ax.set_title("$f(z) = %s$" % (self.function.latex_repr))
        self.f = lambda z: self.function(z, *self._params)
        self._plots = plot_complex_grid(ax, self._grid, self.function)
        self._has_changed = True
        self._toggle_domain = True

    def notify_change(self) -> None:
        """
        Notify change.
        """
        self._has_changed = True

    def get_grid(self) -> ComplexGridArray:
        """
        Get the grid.
        """
        return self._grid

    def update_title(self) -> None:
        """
        update the title.
        """
        self.toggle_blit()
        try:
            self.figure.axes[0].set_title("$f(z) = %s$" % (
                        self.function.latex_repr))
        except ValueError:
            self.figure.axes[0].set_title("f(z)")
        self.toggle_blit()

    def set_grid(self, dimensions: List[int],
                 n_points_per_line: int,
                 n_horizontal_lines: int,
                 n_vertical_lines: int) -> None:
        """
        Adjust the dimensions of the grid.
        """
        self._grid = ComplexGridArray(dimensions,
                                      n_points_per_line,
                                      n_horizontal_lines,
                                      n_vertical_lines)
        self.notify_change()

    def toggle_domain(self) -> None:
        """
        Toggle the plot of the initial domain of the function.
        """
        if self._toggle_domain:
            self.toggle_blit()
            self.figure.axes[0].set_title("z")
            self.toggle_blit()
            self.f = lambda z: z
            self._has_changed = True
        else:
            self.toggle_blit()
            self.figure.axes[0].set_title("$f(z) = %s$" % (
                    self.function.latex_repr))
            self.toggle_blit()
            self.f = lambda z: self.function(z, *self._params)
            self._has_changed = True
        self._toggle_domain = not self._toggle_domain

    def update(self, delta_t: float) -> None:
        """
        Update.
        """
        self.t += delta_t
        if self._PRINT_FPS:
            print('\033[2J')
            print("%.1f fps" % (1/delta_t))
        if self._has_changed:
            try:
                update_complex_grid(self._plots, self._grid, self.f)
            except NameError as e:
                print(e)
            self._has_changed = False

    def set_function(self, function_name: str) -> None:
        """
        Setter for the function.

        function_name [str]: the name of the function
        """
        if not self._toggle_domain:
            self.toggle_domain()
        self.function = FunctionZtoZ(function_name, abc.z)
        self.toggle_blit()
        try:
            self.figure.axes[0].set_title("$f(z) = %s$" % (
                    self.function.latex_repr))
        except ValueError:
            self.figure.axes[0].set_title("f(z)")
        self.toggle_blit()
        self._params = ()
        self._has_changed = True

    def set_params(self, *args: Any) -> None:
        """
        Setter for the params

        args [Any]: the parameters for the function
        """
        self._params = args
        self._has_changed = True

    def scale_axes(self, x_scale_factor: float,
                   y_scale_factor: float) -> None:
        """
        Enlarge or reduce the range of the axes of the plots,
        with respect to the centre of the plot.

        x_scale_factor [float]: scale the x axes.
        y_scale_factor [float]: scale the y axes.
        """
        axes = self.figure.get_axes()
        ax = axes[0]
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        dx = xlim[1] - xlim[0]
        dy = ylim[1] - ylim[0]
        xc = (xlim[1] + xlim[0])/2
        yc = (ylim[1] + ylim[0])/2
        xlim = [xc - x_scale_factor*dx/2.0, xc + x_scale_factor*dx/2.0]
        ylim = [yc - y_scale_factor*dy/2.0, yc + y_scale_factor*dy/2.0]
        self.toggle_blit()
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        self.toggle_blit()

    def move_axes(self, move_by_x: float, move_by_y: float) -> None:
        """
        Translate the x and y axes.

        move_by_x [float]: translation value for the x axis.
        move_by_y [float]: translation value for the y axis.
        """
        ax = self.figure.get_axes()[0]
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        xlim = [xlim[0] + move_by_x,
                xlim[1] + move_by_x]
        ylim = [ylim[0] + move_by_y,
                ylim[1] + move_by_y]
        self.toggle_blit()
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        self.toggle_blit()
