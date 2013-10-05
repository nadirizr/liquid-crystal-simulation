from util import *
from potential import *

class LenardJonesPotential(TwoSpinPotential):
    """
    Lenard-Jones potential implementation.
    """
    def __init__(self, parameters):
        self.epsilon0 = float(parameters["EPSILON_0"])

    def calculateTwoSpins(self, spin1, location1, spin2, location2):
        """
        Calculates the Lenard-Jones potential contribution from two spins.
        """
        return self.epsilon0 * P2(dot(spin1, spin2))
