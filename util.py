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
#kB = 1.3806488*(10**(-16))
kB = 1.0

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
