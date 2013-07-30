from util import *
from potential import *

class GayBernesPotential(NearestNeighboursPotential):
    """
    Gay-Bernes potential implementation.
    """
    def __init__(self, sigma0, epsilon0, kappa, kappa_tag):
        self.sigma0 = sigma0
        self.epsilon0 = epsilon0
        self.kappa = kappa
        self.chi = (self.kappa**2 - 1.0) / (self.kappa**2 + 1.0)
        self.kappa_tag = kappa_tag
        self.chi_tag = (self.kappa_tag - 1.0) / (self.kappa_tag + 1.0)

    def calculateTwoSpins(self, spin1, location1, spin2, location2):
        """
        Calculates the Gay-Bernes potential contribution from two spins.
        """
        r = location1 - location2
        nr = r / linalg.norm(r)
        Ugb = self._calculateGBPotential(spin1, spin2, r, nr)
        Udipole = self._calculateDipolePotential(spin1, spin2, r, nr)
        return Ugb + Udipole

    def _calculateGBPotential(self, spin1, spin2, r, nr):
        """
        Calculates the Gay Bernes potential energy of the given two spins.
        """
        R = self._calculateR(spin1, spin2, r, nr)
        epsilon = self._calculateEpsilon(spin1, spin2, nr)
        return (4 * epsilon * (R**(-12) - R**(-6)))

    def _calculateDipolePotential(self, spin1, spin2, r, nr):
        """
        Calculates the dipole-dipole potential between the two given spins.
        """
        d = linalg.norm(r)
        A = -g * miuB / h_bar
        return ((A**2) *
                (dot(spin1, spin2)*(d**2) - 3*(dot(spin1,r)*dot(spin2,r))) /
                (d**5))

    def _calculateR(self, spin1, spin2, r, nr):
        """
        Calculates R from the two spins and the distance vector between the
        two locations.
        """
        sigma = self._calculateSigma(spin1, spin2, nr)
        return ((linalg.norm(r) - sigma + self.sigma0) / self.sigma0)

    def _calculateSigma(self, spin1, spin2, nr):
        """
        Calculates Sigma from the two spins and the normalized distance vector
        between locations.
        """
        numerator = (dot(spin1,nr)**2 + dot(spin2,nr)**2 -
                     2*self.chi*dot(spin1,nr)*dot(spin2,nr)*dot(spin1,spin2))
        denominator = (1.0 - (self.chi**2)*(dot(spin1,spin2)**2))
        return (self.sigma0 / sqrt(1.0 - self.chi*numerator/denominator))

    def _calculateEpsilon(self, spin1, spin2, nr):
        """
        Calculates Epsilon from the two spins and the normalized distance vector
        between locations.
        """
        return (self.epsilon0 *
                self._calculateEpsilonNi(spin1, spin2) *
                self._calculateEpsilonTag(spin1, spin2, nr))

    def _calculateEpsilonNi(self, spin1, spin2):
        """
        Calculates Epsilon-Ni from the two spins.
        """
        return 1.0 / sqrt(1.0 - (self.chi**2) * (dot(spin1,spin2)**2))

    def _calculateEpsilonTag(self, spin1, spin2, nr):
        """
        Calculates Epsilon Tag from the two spins and the normalized distance
        vector between locations.
        """
        numerator = (dot(spin1,nr)**2 + dot(spin2,nr)**2 -
                     2*self.chi_tag*dot(spin1,nr)*dot(spin2,nr)*dot(spin1,spin2))
        denominator = (1.0 - (self.chi_tag**2)*(dot(spin1,spin2)**2))
        return (1.0 - self.chi_tag*numerator/denominator)
