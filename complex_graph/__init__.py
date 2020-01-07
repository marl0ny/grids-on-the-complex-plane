from .complex_animation import ComplexAnimator, plot_complex_grid
from .functions import VariableNotFoundError

def test():
    from .special_functions import test_special_functions
    from .functions import test_functions
    test_functions()
    test_special_functions()
