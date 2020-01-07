"""
Complex Mapper
"""
import matplotlib.pyplot as plt
import numpy as np
import scipy.special as spec
from time import perf_counter
from typing import Union, Callable, List


# A relatively fast and easy method to compute
# the analytic continuation of the Riemann zeta function
# is given by the
# StackExchange answer at https://math.stackexchange.com/a/3274,
# by user J. M. is a poor mathematician:
# https://math.stackexchange.com/users/498/j-m-is-a-poor-mathematician.
# Original question by Pratik Deoghare:
# https://math.stackexchange.com/users/705/pratik-deoghare.


def _binomial_coefficients_table(n: int) -> np.ndarray:
    bc = np.zeros((n, n))
    for i in range(n):
        for j in range(i//2 + 2):
            bc[i][j] = spec.comb(i, j)
        for j in range(i//2 + 2, i + 1):
            bc[i][j] = bc[i][i-j]
    return bc


def _eta_coefficients(bc: np.ndarray) -> np.ndarray:
    n = len(bc[0])
    ec = np.array([])
    for i in range(n):
        ec = np.append(ec, [0.0])
        for j in range(n):
            ec[i] += bc[j][i]/(2.0**(j + 1.0))
    return ec


def _fast_eta(s: Union[np.complex, np.ndarray],
              ec: np.ndarray) -> Union[np.complex, np.ndarray]:
    summation = 0.0
    plusminus = -1
    m = len(ec)
    for k in range(m):
        plusminus *= -1
        summation += plusminus*ec[k]/((k + 1.0)**s)
    return summation


def _fast_zeta(s: Union[np.complex, np.ndarray],
               ec: np.ndarray) -> Union[np.complex, np.ndarray]:
    return (_fast_eta(s, ec)/(1.0 - 2.0**(1.0 - s)))


eta_coefficients = _eta_coefficients(_binomial_coefficients_table(256))


def get_zeta(ec: np.ndarray) -> Callable:
    """
    Get the zeta function, from an array of coefficients
    used to compute the eta function.

    Parameters:
    ec: coefficients used to calculate the eta function.

    Returns:
    The zeta function, up to some finite number of terms.
    """
    def f_zeta(
            s: Union[np.complex, np.ndarray]) -> Union[np.complex, np.ndarray]:
        summation = 0.0
        plusminus = -1
        m = len(ec)
        for k in range(m):
            plusminus *= -1
            summation += plusminus*ec[k]/((k + 1.0)**s)
        return (summation/(1.0 - 2.0**(1.0 - s)))
    return f_zeta

zeta = get_zeta(eta_coefficients)


def remainder(numerator: int, denominator: int) -> float:
    num = float(numerator)
    den = float(denominator)
    frac = num/den
    return den*(frac % 1)


def integer_division(numerator: int, denominator: int) -> int:
    num = float(numerator)
    den = float(denominator)
    frac = num / den
    return int(frac//1)


class ComplexGridPlotFormat:
    """
    Format object for the complex grid plot
    """
    def __init__(self) -> None:
        """
        Initialize this object
        """
        self._title = ""
        self._grid_boundaries = [-5, 5, -5, 5]
        self._plot_boundaries = None
        self._n_of_points = 100
        self._spacing = 0.0

    def set_title(self, title: str) -> None:
        """
        Set the title

        Parameters:
        title: The title of the plot.
        """
        self._title = title

    def get_title(self) -> str:
        """
        Get the title

        Returns:
        The title of the plot.
        """
        return self._title

    def set_grid_boundaries(self, 
                            grid_boundaries: List[int]) -> None:
        """
        Set the grid boundaries

        Parameters:
        grid_boundaries: The boundaries of the complex input grid.
        This is the list [x_min, y_min, x_max, y_max],
        where x_min and y_min are the minimum real and imaginary values,
        and x_max and y_max  are the maximum real and imaginary values.
        """
        self._grid_boundaries = grid_boundaries

    def get_grid_boundaries(self) -> List[int]:
        """
        Get the grid boundaries

        Returns:
        The grid boundaries. This is the list
        [x_min, y_min, x_max, y_max],
        where x_min and y_min are the minimum real and imaginary values,
        and x_max and y_max  are the maximum real and imaginary values.
        """
        return self._grid_boundaries

    def set_plot_boundaries(self, 
                            plot_boundaries: 
                            Union[List[int], None]) -> None:
        """
        Set the plot boundaries.
        
        Parameters:
        plot_boundaries: A list of the boundaries of plot.
        This can either be None, in which case the plot boundaries
        are set automatically, or they are the list
        [xmin, xmax, ymin, ymax], where xmin and xmax are the limits
        on the x axis and ymin and ymax are the limits of the yaxis.
        """
        self._plot_boundaries = plot_boundaries

    def get_plot_boundaries(self) -> Union[List[int], None]:
        """
        Get the plot boundaries

        Returns:
        A list of the boundaries of plot.
        This can either be None, in which case the plot boundaries
        are set automatically, or they are the list
        [xmin, xmax, ymin, ymax], where xmin and xmax are the limits
        on the x axis and ymin and ymax are the limits of the yaxis.
        """
        return self._plot_boundaries

    def set_number_of_points_per_line(self, number_of_points: int) -> None:
        """
        Set the number of points alloted to each of the lines that comprise
        the grid.

        Parameters:
        number_of_points: The number of points to use for each line.
        """
        self._n_of_points = number_of_points

    def get_number_of_points_per_line(self) -> int:
        """
        Getter for the number of points for each of the horizontal or vertical
        lines that comprise the grid.

        Returns:
        number_of_points: The number of points to use for each line.
        """
        return self._n_of_points

    def set_domain_grid_spacing(self, spacing: int) -> None:
        """
        Set the spacing between each of the lines of the grid.

        Parameter:
        spacing: the spacing between each grid line.
        """
        self._spacing = spacing

    def get_domain_grid_spacing(self) -> float:
        """
        Get the spacing between each of the lines of the grid.

        Returns:
        The spacing between each grid line.
        """
        return self._spacing


def complex_grid_plot(plot_format: ComplexGridPlotFormat,
                      function: Callable,
                      *args: Union[np.complex, np.array]) -> None:
    """
    Complex Grid Plot

    Parameters:
    plot_format: The ComplexGridPlotFormat object that controls
                 how the plot should be formatted.
    function: The complex function to plot.
    *args: Addition arguments to pass into the function.
    """

    title = plot_format.get_title()
    grid_boundaries = plot_format.get_grid_boundaries()
    dlim = plot_format.get_plot_boundaries()
    n_of_points = plot_format.get_number_of_points_per_line()
    spacing = plot_format.get_domain_grid_spacing()
    minx, maxx, miny, maxy = grid_boundaries

    # These define the lines that form the edge of the grid
    x_bottom_line = np.linspace(minx, maxx, n_of_points)
    y_bottom_line = np.ones(n_of_points)*miny
    x_upper_line = np.linspace(minx, maxx, n_of_points)
    y_upper_line = np.ones(n_of_points)*maxy
    x_leftmost_line = np.ones(n_of_points)*minx
    y_leftmost_line = np.linspace(miny, maxy, n_of_points)
    x_rightmost_line = np.ones(n_of_points)*maxx
    y_rightmost_line = np.linspace(miny, maxy, n_of_points)
    if args != ():
        z_bottom_line = function(x_bottom_line + 1.0j*y_bottom_line, *args)
        z_upper_line = function(x_upper_line + 1.0j*y_upper_line, *args)
        z_leftmost_line = function(
                x_leftmost_line + 1.0j*y_leftmost_line, *args)
        z_rightmost_line = function(
                x_rightmost_line + 1.0j*y_rightmost_line, *args)
    else:
        z_bottom_line = function(x_bottom_line + 1.0j*y_bottom_line)
        z_upper_line = function(x_upper_line + 1.0j*y_upper_line)
        z_leftmost_line = function(
                x_leftmost_line + 1.0j*y_leftmost_line)
        z_rightmost_line = function(
                x_rightmost_line + 1.0j*y_rightmost_line)

    # These plot the vertical lines at the edges
    plt.plot(np.real(z_leftmost_line), np.imag(z_leftmost_line),
             color='orange', linewidth=0.6)
    plt.plot(np.real(z_rightmost_line), np.imag(z_rightmost_line),
             color='darkorange', linewidth=0.6)

    # These plot the horizontal lines at the edges
    plt.plot(np.real(z_bottom_line),
             np.imag(z_bottom_line), color='blue', linewidth=0.6)
    plt.plot(np.real(z_upper_line),
             np.imag(z_upper_line), color='darkblue', linewidth=0.6)

    # Create the vertical interior grid lines
    number_of_interior_vertical_lines = integer_division(
            maxx - minx, spacing)
    if remainder(maxx - minx, spacing) == 0:
        for i in range(number_of_interior_vertical_lines):
            x = np.ones(n_of_points)*(minx+i*spacing)
            y = np.linspace(miny, maxy, n_of_points)
            if args != ():
                z = function(x + 1.0j*y, *args)
            else:
                z = function(x + 1.0j*y)
            plt.plot(np.real(z), np.imag(z),
                     color="orange", linewidth=0.3)
    else:
        space_of_furthest_vertical_lines = (spacing +
                                            remainder(
                                                      maxx - minx,
                                                      spacing))/2.0
        for i in range(number_of_interior_vertical_lines):
            x = np.ones(n_of_points)*(
                    minx + space_of_furthest_vertical_lines + i*spacing)
            y = np.linspace(miny, maxy, n_of_points)
            if args != ():
                z = function(x + 1.0j*y, *args)
            else:
                z = function(x + 1.0j*y)
            plt.plot(np.real(z),
                     np.imag(z), color="orange", linewidth=0.3)

    # Create the horizontal interior grid lines
    number_of_interior_horizontal_lines = integer_division(
            maxy - miny, spacing)
    if remainder(maxy - miny, spacing) == 0:
        for i in range(number_of_interior_horizontal_lines):
            y = np.ones(n_of_points)*(miny + i*spacing)
            x = np.linspace(minx, maxx, n_of_points)
            z = function(x+1.0j*y)
            # plt.plot (x, y, ',', color="blue", linewidth = 0.5)
            plt.plot(np.real(z), np.imag(z),
                     color="blue", linewidth=0.3)
    else:
        space_of_furthest_horizontal_lines = (
                spacing + remainder(maxy - miny, spacing))/2.0
        for i in range(number_of_interior_horizontal_lines):
            y = np.ones(n_of_points)*(miny
                                      + space_of_furthest_horizontal_lines
                                      + i*spacing)
            x = np.linspace(minx, maxx, n_of_points)
            if args != ():
                z = function(x+1.0j*y, *args)
            else:
                z = function(x+1.0j*y)
            # plt.plot (x, y, ',', color="blue", linewidth = 0.5)
            plt.plot(np.real(z), np.imag(z),
                     color="blue", linewidth=0.3)

    # These sets the aspect ratio to the correct scale,
    # As well as adding title and labels.
    plt.gca().set_aspect('equal', adjustable='box')
    plt.title(title)
    plt.xlabel("x")
    plt.ylabel("iy")

    # These lines of code remove the labels.
    # Uncomment these and comment the labels above to remove labels.
    # plt.xticks([])
    # plt.yticks([])

    # Set the plot boundaries
    if dlim is not None:
        plt.xlim(dlim[0], dlim[1])
        plt.ylim(dlim[2], dlim[3])
    plt.savefig(title + '.png', dpi=400)


def complex_grid_plot_showing_both_domain_and_range(plot_format,
                                                    function, *args):
    """
    Complex Grid Plot of both the input and output of the function.

    Parameters:
    plot_format: The ComplexGridPlotFormat object that controls
                 how the plot should be formatted.
    function: The complex function to plot.
    *args: Addition arguments to pass into the function.
    """
    complex_grid_plot(plot_format, lambda z: z, *args)
    complex_grid_plot(plot_format, function, *args)


def plot_line_in_complex_plane(t: np.ndarray,
                               xf: Callable, yf: Callable,
                               function: Callable, title: str,
                               dlim: List[int] = [],
                               show_identity=False) -> None:
    """
    Plot a complex function along a parameterized line
    in the complex plane. Here the x and y axes correspond
    to the real and imaginary parts.

    Parameters:
    t: The variable to parameterize the function
    xf: function that parameterizes the real value xf(t)
    yf: function that parameterizes the imaginary value i*yf(t)
    function: The complex function that takes z = xf(t) + i*yf(t)
    as input.
    title: The title of the plot.
    dlim: The limits of the plot. This is either None, in which
    the limits are set automatically, or this is the list
    [xmin, xmax, ymin, ymax], where xmin and xmax are
    the minimum and maximum x values, and ymin and ymax are
    the mimimum and maximum y values.
    show_identity: Plot the line xf(t) + i*yf(t)
    """
    x = xf(t)
    y = yf(t)
    z = function(x + 1.0j*y)
    if show_identity is True:
        a, = plt.plot(x, y, color="black", linewidth=0.75)
        b, = plt.plot(np.real(z), np.imag(z), color="aqua", linewidth=0.75)
        plt.legend((a, b), ['z', 'f(z)'])
    b = plt.plot(np.real(z), np.imag(z), linewidth=0.75)
    # These set the aspect ratio to the correct scale,
    # as well as adding a title and labels.
    plt.gca().set_aspect('equal', adjustable='box')
    plt.title(title)
    plt.xlabel("x")
    plt.ylabel("iy")
    plt.grid(True)

    # The following lines of code remove the axis label.
    # Uncomment these and comment the labels above to remove labels.
    # plt.xticks([])
    # plt.yticks([])

    if (len(dlim) == 4):
        plt.xlim(dlim[0], dlim[1])
        plt.ylim(dlim[2], dlim[3])
    plt.savefig(title + '.png', dpi=400)
    plt.show()
    plt.close()


def plot_complex_values_along_line(t: np.ndarray,
                                   xf: Callable, yf: Callable,
                                   function: Callable,
                                   title: str) -> None:
    """
    Plot a complex function along a parameterized line,
    where the horizontal plot axis displays the
    complex values of the parameterized line, 
    and the vertical axis displays the real, imaginary, and 
    absolute values of the complex function.

    Parameters:
    t: The variable to parameterize the function
    xf: function that parameterizes the real value xf(t)
    yf: function that parameterizes the imaginary value i*yf(t)
    function: The complex function that takes z = xf(t) + i*yf(t)
               as input.
    title: The title of the plot.
    """
    x = xf(t)
    y = yf(t)
    z = function(x + 1.0j*y)
    re, = plt.plot(t, np.real(z), color='red', linewidth=0.75)
    im, = plt.plot(t, np.imag(z), color='blue', linewidth=0.75)
    ab, = plt.plot(t, np.abs(z), color='grey', linewidth=0.75)
    # plt.legend((re,im,ab),['Re(z)','Im(z)','|z|'],
    # loc='center left', bbox_to_anchor=(1, 0.5))
    plt.legend((re, im, ab), ['Re(z)', 'Im(z)', '|z|'])
    plt.xlim(t[0], t[-1])
    n_of_ticks = 6
    ttick = int(len(t)/(n_of_ticks - 1))
    ticks = []
    for i in range(n_of_ticks - 1):
        ticks.append(str(np.round(x[i*ttick], 1)) + "\n" +
                     str(np.round(y[i*ttick], 1))+"i")
    ticks.append(
            str(np.round(x[-1], 1)) + "\n" + str(np.round(y[-1], 1)) + "i")
    plt.xticks(np.linspace(t[0], t[-1], n_of_ticks), ticks)

    # The following lines of code set the aspect ratio to the correct scale,
    # as well as adding a title and labels.
    # plt.gca().set_aspect('equal', adjustable='box')
    plt.title(title)
    plt.xlabel("real \n imaginary")
    plt.grid(True)

    # The following lines of code removes the axis label.
    # Uncomment these and comment the labels above to remove labels.
    # plt.xticks([])
    # plt.yticks([])

    plt.savefig(title+'.png', dpi=400)
    plt.show()
    plt.close()


def find_zeroes(t: np.ndarray,
                xf: Callable, yf: Callable,
                function: Callable) -> None:
    """
    Find the zeroes of the complex function.
    """
    distance = t[-1] - t[0]
    x = xf(t)
    y = yf(t)
    z = function(x+1.0j*y)
    lst = []
    n_of_iterations = 3
    for j in range(n_of_iterations):
        t2 = np.array([])
        for i in range(len(t)):
            if np.round(np.abs(z[i]), (j + 1)) == 0:
                t2 = np.block([t2, np.linspace(
                        float(t[i]) - distance/(float(j+1)*100.),
                        float(t[i]) + distance/(float(j+1)*100.), 1000)])
        t = t2
        x = xf(t)
        y = yf(t)
        z = function(x+1.0j*y)
    print(t)
    for k in range(len(t)):
        if np.round(np.abs(z[k]), (n_of_iterations)) == 0:
            lst.append(t[k])
    return lst
