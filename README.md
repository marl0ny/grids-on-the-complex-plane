# Plotting in the Complex Plane

Interactively plot complex functions in real time! To use this program
first ensure that you have Python with Numpy, Scipy, Sympy, Matplotlib, Tkinter, and optionally
Numba. Then download or clone this repository and run `tkapp.py` to launch the program.

## Usage

<img src="https://raw.githubusercontent.com/marl0ny/grids-on-the-complex-plane/master/example.gif" />

Hold down the left mouse button on the plot and move the mouse around to change the view of the plot. 
Use the mouse wheel to zoom in or out. To plot a new function either type a new function in the `Enter f(z)` entry box and hit the return key,
or select a new function in the `Preset f(z)` dropdown menu. Note that the function entered must at least depend on z, where any other variable
becomes a parameter that you can vary using the sliders. To view the initial input of the function
press `Toggle grid input`. To change the input of the function click on `Set grid input..` and then change the input from here.

This program is inspired by and based upon the 3Blue1Brown video on the [Riemann zeta function](https://www.youtube.com/watch?v=sD0NjbwqlYw) (and complex functions in general),
as well as [Complex Mapping Viewer](https://www.falstad.com/complexviewer/) by Keith Orpen, Djun Kim, Kent Pearce, and Paul Falstad.
A relatively fast and easy method to compute the analytic continuation of the Riemann zeta function is given by [this StackExchange answer](https://math.stackexchange.com/a/3274)
by user ["J. M. is a poor mathematician"](https://math.stackexchange.com/users/498/j-m-is-a-poor-mathematician)
([Original question](https://math.stackexchange.com/q/3271) by [Pratik Deoghare](https://math.stackexchange.com/users/705/pratik-deoghare)).
