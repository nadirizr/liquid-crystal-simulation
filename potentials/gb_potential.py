from util import *
from potential import *

class GayBernesPotential(TwoSpinPotential):
    """
    Gay-Bernes potential implementation.
    """
    def __init__(self, parameters):
        self.epsilon0 = float(parameters["EPSILON_0"])
        self.sigma_s = float(parameters["SIGMA_S"])
        self.miu = float(parameters["MIU"])
        self.ni = float(parameters["NI"])

        self.kappa = float(parameters["KAPPA"])
        self.chi = (self.kappa ** 2 - 1.0) / (self.kappa ** 2 + 1.0)

        self.kappa_tag = float(parameters["KAPPA_TAG"])
        self.chi_tag = ((self.kappa_tag ** (1.0 / self.miu) - 1.0) /
                        (self.kappa_tag ** (1.0 / self.miu) + 1.0))
        #print "// &&& GayBernesPotential: epsilon0 = %s, sigma_s = %s, miu = %s, ni = %s, kappa = %s, chi = %s, kappa_tag = %s, chi_tag = %s" % (self.epsilon0, self.sigma_s, self.miu, self.ni, self.kappa, self.chi, self.kappa_tag, self.chi_tag)

    def calculateTwoSpins(self, spin1, location1, spin2, location2):
        """
        Calculates the Gay-Bernes potential contribution from two spins.
        """
        r = location1 - location2
        nr = r / linalg.norm(r)
        Ugb = self._calculateGBPotential(spin1, spin2, r, nr)
        #print "// GayBernesPotential::calculateTwoSpins:"
        #print "// spin1 = %s, location1 = %s" % (spin1, location1)
        #print "// spin2 = %s, location2 = %s" % (spin2, location2)
        #print "// r = %s, nr = %s" % (r, nr)
        #print "// U = %s" % Ugb
        return Ugb

    def _calculateGBPotential(self, spin1, spin2, r, nr):
        """
        Calculates the Gay Bernes potential energy of the given two spins.
        """
        R = self._calculateR(spin1, spin2, r, nr)
        
        epsilon = self._calculateEpsilon(spin1, spin2, nr)
        res = (4 * epsilon * (R**12 - R**6))
        return res

    def _calculateR(self, spin1, spin2, r, nr):
        """
        Calculates R from the two spins and the distance vector between the
        two locations.
        """
        sigma = self._calculateSigma(spin1, spin2, nr)
        return (self.sigma_s / (linalg.norm(r) - sigma + self.sigma_s))

    def _calculateSigma(self, spin1, spin2, nr):
        """
        Calculates Sigma from the two spins and the normalized distance vector
        between locations.
        """
        first = (((dot(spin1, nr) + dot(spin2, nr)) ** 2) /
                 (1.0 + self.chi * dot(spin1, spin2)))
        second = (((dot(spin1, nr) - dot(spin2, nr)) ** 2) /
                  (1.0 - self.chi * dot(spin1, spin2)))
        return self.sigma_s / sqrt(1.0 - self.chi / 2.0 * (first + second))

    def _calculateEpsilon(self, spin1, spin2, nr):
        """
        Calculates Epsilon from the two spins and the normalized distance vector
        between locations.
        """
        return (self.epsilon0 *
                (self._calculateEpsilonNi(spin1, spin2) ** self.ni) *
                (self._calculateEpsilonTagMiu(spin1, spin2, nr) ** self.miu))

    def _calculateEpsilonNi(self, spin1, spin2):
        """
        Calculates Epsilon-Ni from the two spins.
        """
        return 1.0 / sqrt(1.0 - (self.chi ** 2) * (dot(spin1,spin2) ** 2))

    def _calculateEpsilonTagMiu(self, spin1, spin2, nr):
        """
        Calculates Epsilon Tag Miu from the two spins and the normalized
        distance vector between locations.
        """
        first = (((dot(spin1, nr) + dot(spin2, nr)) ** 2) /
                 (1.0 + self.chi_tag * dot(spin1, spin2)))
        second = (((dot(spin1, nr) - dot(spin2, nr)) ** 2) /
                  (1.0 - self.chi_tag * dot(spin1, spin2)))
        return 1.0 - self.chi_tag / 2.0 * (first + second)
