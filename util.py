import __future__

from math import *
from numpy import *

import itertools
import math
import numpy
import random

##################################################################
#                     Natural Constants                          #
##################################################################

# Boltzmann constant in [erg]/[K].
kB = 1.3806488*(10**(-16))
#kB = 1.0

# Bohr Magneton in [erg]/[G].
miuB = 9.274009820*(10**(-21))

# g factor for spin dipole moment.
g = 1.0

# Planck's reduced constant [erg]*[sec].
h_bar = 1.0545726663*(10**-27)

##################################################################
#                     Utility Functions                          #
##################################################################

def P2(x):
    """
    Second order legendre polynomial.
    """
    return (3.0 * (x**2) - 1.0) / 2.0

def CreateNormalizedVector(v):
    a = array(v)
    return a / linalg.norm(a)
