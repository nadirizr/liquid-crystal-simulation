from potential import Potential, TwoSpinPotential

class FixedNearestNeighboursPotential(Potential):
    """
    This is an implementation of the potential interface for fixed nearest
    neighbours potentials which can be passed on in the constructor.
    """
    
    def __init__(self, potential, parameters):
        """
        Uses the given two spin potential for the calculations.
        """
        self.potential = potential

    def calculate(self, lcs, indices):
        """
        Calculates the nearest neighbours potential for the given spin.
        """
        U = 0

        # Get the neighbour list for the given cell.
        NEAREST_NEIGHBOURS_MAX_INDEX_RANGE = list(
                self.parameters["NEAREST_NEIGHBOURS_MAX_INDEX_RANGE"])
        index_ranges = [NEAREST_NEIGHBOURS_MAX_INDEX_RANGE
                        for i in range(len(indices))]
        neighbours = lcs.getCellNeighboursList(indices, index_ranges)

        # Get the location and spin for the given cell.
        location = lcs.getProperty(lcs.locations, indices)
        spin = lcs.getProperty(lcs.spins, indices)

        for (n_indices, n_location, n_spin) in neighbours:
            U += self.potential.calculateTwoSpins(spin,
                                                  location,
                                                  n_spin,
                                                  n_location)

        return U / 2.0
