from util import *
from potential import Potential, TwoSpinPotential

class SphereNearestNeighboursPotential(Potential):
    """
    This is an implementation of the potential interface for nearest neighbours
    potentials which can be passed on in the constructor.
    Nearest neighbours are selected within a sphere of a given radius, and the
    closest spins are recalculated every set number of calculations.
    NOTE: This currenty works only with 2D and 3D potentials.
    """
    
    def __init__(self, potential, parameters):
        """
        Uses the given two spin potential for the calculations.
        """
        self.potential = potential
        self.parameters = parameters

        self.neighbour_lists = {}
        self.cycles_before_update = 0

    def calculate(self, lcs, indices):
        """
        Calculates the nearest neighbours potential for the given spin.
        """
        # Update the counter of cycles to the next neighbour update, and update
        # the neighbour lists if needed.
        # This is only done every time we calculate the [0,0,...,0] spin.
        if not any(indices) or not self.neighbour_lists:
            self.cycles_before_update -= 1
            if self.cycles_before_update <= 0:
                self._updateNeighbourLists(lcs)

        # U is the total potential energy.
        U = 0

        # Get the current spin and location pointed to by the indices.
        spin = lcs.getSpin(indices)
        location = lcs.getLocation(indices)

        # Get the cached neighbour list for the current spin.
        neighbour_list = self.neighbour_lists[tuple(indices)]

        # Go over the list of neighbours and calculate the potential for each.
        for n_indices in neighbour_list:
            n_spin = lcs.getSpin(n_indices)
            n_location = lcs.getLocation(n_indices)
            U += self.potential.calculateTwoSpins(spin,
                                                  location,
                                                  n_spin,
                                                  n_location)

        return U / 2.0

    def _updateNeighbourLists(self, lcs):
        """
        Updates the list of neighbours for each of the spins based on the
        locations of the spins and the system dimensions.
        """
        # Reset the cached neighbour lists.
        self.neighbour_lists = {}
        self.cycles_before_update = int(
            self.parameters["NEAREST_NEIGHBOURS_UPDATE_CYCLES"])

        # Get the maximum sphere radius and the maximum index range of cells to
        # include in the calculation.
        R2 = float(self.parameters["NEAREST_NEIGHBOURS_MAX_RADIUS"]) ** 2
        MAX_INDEX_RANGE = int(
            self.parameters["NEAREST_NEIGHBOURS_MAX_INDEX_RANGE"])
        index_ranges = [MAX_INDEX_RANGE for dim in lcs.dimensions]

        # Go over each of the cells in turn, and for each one cache the
        # neighbours that are contained within the close sphere of
        # NEAREST_NEIGHBOURS_MAX_RADIUS size.
        index_iterator = lcs.getSystemIndexIterator()
        for indices in index_iterator:
            # Get the location and neighbours list for the current cell.
            location = lcs.getLocation(indices)
            neighbour_list = lcs.getCellNeighboursList(indices, index_ranges)

            # Create a new entry for the current cell in the cache.
            cached_neighbour_list = []
            self.neighbour_lists[tuple(indices)] = cached_neighbour_list

            # Go over each of the neighbours and check if it is within range.
            for n_indices in neighbour_list:
                n_location = lcs.getLocation(n_indices)
                r2 = self._calculateDistanceSquared(location, n_location)
                if r2 <= R2:
                    cached_neighbour_list.append(n_indices)

    def _calculateDistanceSquared(self, location1, location2):
        """
        Calculates the distance between the given two locations squared.
        """
        assert len(location1) == len(location2)

        distance = 0.0
        for i in range(len(location1)):
            distance += (location1[i] - location2[i]) ** 2

        return distance
