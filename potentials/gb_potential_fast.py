from util import *
from potential import TwoSpinPotential

try:
    from cpp.potentials.gb_potential_impl import GayBernesPotentialImpl
except:
    from gb_potential import GayBernesPotential
    GayBernesPotentialImpl = None

class GayBernesPotentialFast(TwoSpinPotential):
    """
    Gay-Bernes potential implementation.
    """
    def __init__(self, parameters):
        EPSILON_0 = float(parameters["EPSILON_0"])
        SIGMA_S = float(parameters["SIGMA_S"])
        MIU = float(parameters["MIU"])
        NI = float(parameters["NI"])
        KAPPA = float(parameters["KAPPA"])
        KAPPA_TAG = float(parameters["KAPPA_TAG"])

        if GayBernesPotentialImpl is None:
            self.impl = GayBernesPotential(parameters)
        else:
            self.impl = GayBernesPotentialImpl(
                    EPSILON_0, SIGMA_S, MIU, NI, KAPPA, KAPPA_TAG)

    def calculateTwoSpins(self, spin1, location1, spin2, location2):
        """
        Calculates the Gay-Bernes potential contribution from two spins.
        """
        return self.impl.calculateTwoSpins(
                spin1, location1, spin2, location2)
