import numpy as np
from typing import Tuple, List, Callable, Any


def _horizontal_grid_array(grid_origin: Tuple[float, float],
                           grid_dimensions: Tuple[float, float],
                           n_points_per_line: int,
                           n_lines: int) -> Tuple[np.ndarray, np.ndarray]:
    """
    Horizontal Grid Array
    """
    x0, y0 = grid_origin
    w, h = grid_dimensions

    x_horizontal = np.linspace(x0, x0 + w, n_points_per_line)
    y_horizontal = np.ones([n_points_per_line])
    x_vertical = np.ones([n_points_per_line//n_lines])
    y_vertical = np.linspace(0, h/n_lines, n_points_per_line//n_lines)
    x_horizontal_flip = np.flip(x_horizontal, 0)
    y_horizontal_flip = np.flip(y_horizontal, 0)
    x = np.array([])
    y = np.array([])

    centre = w/2 + x0
    offset_from_centre = w/2
    grid_spacing = h/n_lines
    for i in range(0, n_lines):
        if i % 2 == 0:
            x = np.append(x, x_horizontal)
            y = np.append(y, y_horizontal*(grid_spacing*i + y0))
        else:
            x = np.append(x, x_horizontal_flip)
            y = np.append(y, y_horizontal_flip*(grid_spacing*i + y0))
        x = np.append(x, x_vertical*(offset_from_centre + centre))
        y = np.append(y, y_vertical + (grid_spacing*i + y0))
        offset_from_centre *= -1
    x = np.append(x, x_horizontal)
    y = np.append(y, y_horizontal*(grid_spacing*n_lines + y0))
    return x, y


def _vertical_grid_array(grid_origin: Tuple[float, float],
                         grid_dimensions: Tuple[float, float],
                         n_points_per_line: int,
                         n_lines: int) -> Tuple[np.ndarray, np.ndarray]:
    """
    Vertical Grid Array
    """
    x0, y0 = grid_origin
    w, h = grid_dimensions

    x_vertical = np.ones([n_points_per_line])
    y_vertical = np.linspace(y0, y0 + h, n_points_per_line)
    x_horizontal = np.linspace(0, w/n_lines, n_points_per_line//n_lines)
    y_horizontal = np.ones([n_points_per_line//n_lines])
    x_vertical_flip = np.flip(x_vertical, 0)
    y_vertical_flip = np.flip(y_vertical, 0)
    x = np.array([])
    y = np.array([])

    centre = h/2 + y0
    offset_from_centre = h/2
    grid_spacing = w/n_lines
    for i in range(0, n_lines):
        if i % 2 == 0:
            x = np.append(x, x_vertical*(grid_spacing*i + x0))
            y = np.append(y, y_vertical)
        else:
            x = np.append(x, x_vertical_flip*(grid_spacing*i + x0))
            y = np.append(y, y_vertical_flip)
        y = np.append(y, y_horizontal*(offset_from_centre + centre))
        x = np.append(x, x_horizontal + (grid_spacing*i + x0))
        offset_from_centre *= -1
    y = np.append(y, y_vertical)
    x = np.append(x, x_vertical*(grid_spacing*n_lines + x0))
    return x, y


def grid_array(grid_origin: Tuple[float, float],
               grid_dimensions: Tuple[float, float],
               n_points_per_line: int,
               n_vertical_lines: int,
               n_horizontal_lines: int) -> Tuple[
                                   np.ndarray, np.ndarray]:
    """
    Grid Array

    grid_origin [Tuple[float, float]]: origin point of the grid
                (this is the bottom-left corner)
    grid_dimensions [Tuple[float, float]]: the dimensions
                    of the grid (width, height)
    n_points_per_line [int]: Number of points per each line
    n_vertical_lines [int]: Number of vertical lines
    n_horizontal_lines [int]: Number of horizontal lines

    returns: the array of horizontal and vertical lines.
    """
    x_horizontal, y_horizontal = _horizontal_grid_array(
            grid_origin, grid_dimensions,
            n_points_per_line, n_horizontal_lines)
    x_vertical, y_vertical = _vertical_grid_array(
            grid_origin, grid_dimensions,
            n_points_per_line, n_vertical_lines)
    x_vertical = np.flip(x_vertical, 0)
    y_vertical = np.flip(y_vertical, 0)
    x = np.append(x_horizontal, x_vertical)
    y = np.append(y_horizontal, y_vertical)
    return x, y


class ComplexGridArray:
    """
    Complex Grid Array
    """

    def __init__(self, dimensions: List[int],
                 n_points_per_line: int,
                 n_horizontal_lines: int,
                 n_vertical_lines: int) -> None:
        """
        dimensions [List[int]]: the dimensions of the
                   complex grid array relative to
                   a coordinate system. These are
                   x_0, y_0, x_f, and y_f
        n_points_per_line [int]: Number of points per line
        n_horizontal_lines [int]: Number of horizontal lines
        n_vertical_lines [int]: Number of vertical lines
        """
        x0, y0, xf, yf = dimensions
        grid_origin = (x0, y0)
        grid_dimensions = (xf - x0, yf - y0)
        x_horizontal, y_horizontal = _horizontal_grid_array(
            grid_origin, grid_dimensions,
            n_points_per_line, n_horizontal_lines)
        x_vertical, y_vertical = _vertical_grid_array(
            grid_origin, grid_dimensions,
            n_points_per_line, n_vertical_lines)
        self._horizontal_lines = x_horizontal + 1.0j*y_horizontal
        self._vertical_lines = x_vertical + 1.0j*y_vertical
        self._y_max = np.linspace(x0, xf, n_points_per_line) + 1.0j*yf*np.ones(
                [n_points_per_line])
        self._y_min = np.linspace(x0, xf, n_points_per_line) + 1.0j*y0*np.ones(
                [n_points_per_line])
        self._x_min = x0*np.ones([n_points_per_line]) + 1.0j*np.linspace(
                y0, yf, n_points_per_line)
        self._x_max = xf*np.ones([n_points_per_line]) + 1.0j*np.linspace(
                y0, yf, n_points_per_line)
        self._n_vertical_lines = n_vertical_lines
        self._n_horizontal_lines = n_horizontal_lines

    def get_copy(self):
        """
        Get a copy of this object.
        """
        xlim = self.get_xlim()
        ylim = self.get_ylim()
        dimensions = [xlim[0], ylim[0], xlim[1], ylim[1]]
        return ComplexGridArray(dimensions,
                                len(self._x_min),
                                self._n_horizontal_lines,
                                self._n_vertical_lines)

    def get_horizontal_lines(self) -> np.ndarray:
        """
        Getter for the array of horizontal lines
        """
        return self._horizontal_lines

    def get_vertical_lines(self) -> np.ndarray:
        """
        Getter for the array of vertical lines
        """
        return self._vertical_lines

    def get_boundaries(self) -> List[np.ndarray]:
        """
        Get the line boundaries of the plot.
        These are x_min, y_min, x_max, and y_max.
        """
        return [self._x_min, self._y_min, self._x_max, self._y_max]

    def get_xlim(self) -> List[float]:
        """
        Get the x-limits of the plot.
        """
        return [np.real(self._x_min[0]), 
                np.real(self._x_max[0])]

    def get_ylim(self) -> List[float]:
        """
        Get the y-limits of the plot.
        """
        return [np.imag(self._y_min[0]), 
                np.imag(self._y_max[0])]

    def get_number_of_points_per_line(self) -> int:
        """
        Get the number of points per line.
        """
        return len(self._x_min)

    def get_number_of_vertical_lines(self) -> int:
        """
        Get the number of vertical lines
        """
        return self._n_vertical_lines

    def get_number_of_horizontal_lines(self) -> int:
        """
        Get the number of horizontal lines
        """
        return self._n_horizontal_lines


def plot_complex_grid(ax: Any, g: ComplexGridArray,
                      function: Callable) -> List[Any]:
    """
    Plot the complex grid

    ax: matplotlib axes object.
    g [ComplexGridArray]: complex grid array
    function [Callable]: A callable function

    returns a list of matplotlib axes objects.
    """
    plot_list = []
    z = function(g.get_horizontal_lines())
    plot1, = ax.plot(z.real, z.imag, linewidth=0.3, alpha=1.0)
    z = function(g.get_vertical_lines())
    plot2, = ax.plot(z.real, z.imag, linewidth=0.3, alpha=1.0)
    plot_list.append(plot1)
    plot_list.append(plot2)
    ax.set_xlabel("x")
    ax.set_ylabel("iy")
    zs = g.get_boundaries()
    for i in range(len(zs)):
        z = function(zs[i])
        if i % 2 == 0:
            plot_object, = ax.plot(z.real, z.imag, linewidth=1.0, alpha=1.0,
                                   color="orange")
        else:
            plot_object, = ax.plot(z.real, z.imag, linewidth=1.0, alpha=1.0,
                                   color="darkblue")
        plot_list.append(plot_object)
    return plot_list


def update_complex_grid(plot_list: List[Any],
                        g: ComplexGridArray,
                        function: Callable) -> List[Any]:
    """
    Update the plots of complex grid

    plot_list [List]: A list of matplotlib artists.
    g [ComplexGridArray]: complex grid array
    function [Callable]: A callable function.

    returns a list of matplotlib artists.
    """
    z = function(g.get_horizontal_lines())
    plot_list[0].set_xdata(z.real)
    plot_list[0].set_ydata(z.imag)
    z = function(g.get_vertical_lines())
    plot_list[1].set_xdata(z.real)
    plot_list[1].set_ydata(z.imag)
    zs = g.get_boundaries()
    for i in range(len(zs)):
        z = function(zs[i])
        plot_list[i+2].set_xdata(z.real)
        plot_list[i+2].set_ydata(z.imag)
    return plot_list
