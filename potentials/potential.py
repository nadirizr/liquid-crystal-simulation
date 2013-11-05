class Potential:
    """
    This is the interface for all potentials.
    """

    def calculate(self, lcs, indices):
        """
        Calculates the potential for the given spin.
        """
        raise NotImplemented

    def update(self):
        """
        Forces update of internal data structures.
        """
        pass

class TwoSpinPotential:
    """
    This is the interface for a two spin potential.
    """

    def calculateTwoSpins(self, spin1, location1, spin2, location2):
        """
        Calculates the potential between the given spins.
        """
        raise NotImplemented
