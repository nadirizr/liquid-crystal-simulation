from util import *
from potential import *

class LenardJonesPotential(NearestNeighboursPotential):
    """
    Lenard-Jones potential implementation.
    """
    def __init__(self, epsilon0):
        self.epsilon0 = epsilon0

    def calculateTwoSpins(self, spin1, location1, spin2, location2):
        """
        Calculates the Lenard-Jones potential contribution from two spins.
        """
        return self.epsilon0 * P2(dot(spin1, spin2))
