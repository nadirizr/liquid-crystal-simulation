class Potential:
    """
    This is the interface for all potentials.
    """

    def calculate(self, spins, locations, dimensions, indices):
        """
        Calculates the potential for the given spin.
        """
        raise NotImplemented

class TwoSpinPotential:
    """
    This is the interface for a two spin potential.
    """

    def calculateTwoSpins(self, spin1, location1, spin2, location2):
        """
        Calculates the potential between the given spins.
        """
        raise NotImplemented
