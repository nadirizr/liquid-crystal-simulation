import __future__

from math import *
from numpy import *

import itertools
import math
import numpy
import random
import time

from constants import *
import progressbar

def P2(x):
    """
    Second order legendre polynomial.
    """
    return (3.0 * (x**2) - 1.0) / 2.0

def CreateNormalizedVector(v):
    a = array(v)
    return a / linalg.norm(a)

def frange(start, end, step):
    return list(arange(start, end + step, step))

def any(iterable):
    for i in iterable:
        if i:
            return True
    return False

def all(iterable):
    for i in iterable:
        if not i:
            return False
    return True
