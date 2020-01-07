import numpy as np
import scipy.special as spec
try:
    from numba import jit, prange, c16, f8
    NUMBA_IMPORTED = True
except ImportError:
    NUMBA_IMPORTED = False
    # TODO: Don't do this!
    prange = None

    def jit(string, cache=False, nogil=False, nopython=False):
        return jit


def erf(z):
    return spec.erf(z)


def lambertw(z):
    return spec.lambertw(z)


def psi(z):
    return spec.psi(z)


def gamma(z):
    return spec.gamma(z)


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


def _pm_eta_coefficients(ec: np.ndarray) -> np.ndarray:
    return np.array(
            [(ec[i] if i % 2 == 0.0 else -ec[i]) for i in range(len(ec))])

@jit('c16[:](c16[:], c16[:])',
     cache=True, nogil=True, nopython=True)
def _inner_zeta(s, summation):
    return summation/(1.0 - 2.0**(1.0 - s))


@jit('c16[:](c16[:], c16[:], f8[:])',
     cache=True, nogil=True, nopython=True)
def _zeta_call(s, summation, pm_eta_coefficients):
    m = len(pm_eta_coefficients)
    n = len(s)
    for k in prange(m):
        for j in prange(n):
            summation[j] = summation[j] + pm_eta_coefficients[k]/((k + 1.0)**s[j])
    return _inner_zeta(s, summation)

@jit('c16[:](c16[:], c16[:], f8[:])',
     cache=True, nogil=True, nopython=True)
def _eta_call(s, eta, pm_eta_coefficients):
    m = len(pm_eta_coefficients)
    n = len(s)
    for k in prange(m):
        for j in prange(n):
            eta[j] = eta[j] + pm_eta_coefficients[k]/((k + 1.0)**s[j])
    return eta


class EtaFunction:
    
    def __init__(self, n) -> None:
        """
        """
        self._numba_imported = NUMBA_IMPORTED
        eta_coefficients = _eta_coefficients(
            _binomial_coefficients_table(n))
        self._pm_eta_coefficients = _pm_eta_coefficients(eta_coefficients)

    def __call__(self, s: np.ndarray) -> np.ndarray:
        """
        """
        if self._numba_imported:
            eta = np.zeros(
                [len(s)], np.complex)
            return _eta_call(s, eta,
                             self._pm_eta_coefficients)
        else:
            eta = np.zeros([len(s)], np.complex)
            m = len(self._pm_eta_coefficients)
            for k in range(m):
                eta += self._pm_eta_coefficients[k]/((k + 1.0)**s)
            return eta
     
    def toggle_use_numba(self):
        self._numba_imported = not self._numba_imported


class ZetaFunction:

    def __init__(self, n: int) -> None:
        """
        Constructor.
        """
        self._numba_imported = NUMBA_IMPORTED
        self._eta_coefficients = _eta_coefficients(
            _binomial_coefficients_table(n))
        self._pm_eta_coefficients = _pm_eta_coefficients(
                self._eta_coefficients)
        self._summation = np.zeros(
                [len(self._eta_coefficients)], np.complex)
        self._len = 0

    def __call__(self, s: np.ndarray) -> np.ndarray:
        """
        Make this class callable.
        """
        if self._numba_imported:
            self._summation = np.zeros(
                [len(s)], np.complex)
            return _zeta_call(s, self._summation,
                              self._pm_eta_coefficients)
        else:
            summation = 0.0
            plusminus = -1
            m = len(self._eta_coefficients)
            for k in range(m):
                plusminus *= -1
                summation += plusminus*self._eta_coefficients[k]/((k + 1.0)**s)
            return (summation/(1.0 - 2.0**(1.0 - s)))
     
    def toggle_use_numba(self) -> None:
        """
        Toggle whether to use numba or not.
        """
        self._numba_imported = not self._numba_imported


def test_special_functions() -> None:
    from time import perf_counter
    eta = EtaFunction(128)
    x = np.array([i for i in range(10)], np.complex)
    for i in range(len(x)):
        print(i, eta(x)[i])
##    zeta = ZetaFunction(128)
##    x = [i for i in range(-100, 100) if i != 1]
##    z = np.array(x, np.complex)
##    t1 = perf_counter()
##    for i in range(10):
##        w = zeta(z)
##    t2 = perf_counter()
##    for i in range(len(z)):
##        print(z[i], w[i])
##    print(t2 - t1)
##    zeta.toggle_use_numba()
##    x = [i for i in range(-100, 100) if i != 1]
##    z = np.array(x, np.complex)
##    t1 = perf_counter()
##    for i in range(10):
##        w = zeta(z)
##    t2 = perf_counter()
##    print(t2 - t1)
