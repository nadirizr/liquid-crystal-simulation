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

        self.neighbour_lists = []
        self.cycles_before_update = 0

    def calculate(self, spins, locations, dimensions, indices):
        """
        Calculates the nearest neighbours potential for the given spin.
        """
        # Update the counter of cycles to the next neighbour update, and update
        # the neighbour lists if needed.
        # This is only done every time we calculate the [0,0,...,0] spin.
        if not any(indices) or not self.neighbour_lists:
            self.cycles_before_update -= 1
            if self.cycles_before_update <= 0:
                self._updateNeighbourLists(locations, dimensions)

        # U is the total potential energy.
        U = 0

        # Calculate the current spin and location pointed to by the indices.
        # Also, get the neighbour list for the current spin.
        current_spin = spins
        current_location = locations
        current_neighbour_list = self.neighbour_lists
        for i in indices:
            current_spin = current_spin[i]
            current_location = current_location[i]
            current_neighbour_list = current_neighbour_list[i]

        # Go over the list of neighbours and calculate the potential for each.
        for neighbour_indices in current_neighbour_list:
            # Get the details of the current neighbour.
            neighbour_spin = spins
            neighbour_location = locations
            for i in neighbour_indices:
                neighbour_spin = neighbour_spin[i]
                neighbour_location = neighbour_location[i]

            # Add the potential contribution.
            U += self.potential.calculateTwoSpins(current_spin,
                                                  current_location,
                                                  neighbour_spin,
                                                  neighbour_location)

        return U / 2.0

    def _updateNeighbourLists(self, locations, dimensions):
        """
        Updates the list of neighbours for each of the spins based on the
        locations of the spins and the system dimensions.
        Only supported in 2D and 3D.
        """
        self.neighbour_lists = []
        self.cycles_before_update = int(
            self.parameters["NEAREST_NEIGHBOURS_UPDATE_CYCLES"])

        if len(dimensions) == 2:
            self._updateNeighbourLists2D(locations, dimensions)
        elif len(dimensions) == 3:
            self._updateNeighbourLists3D(locations, dimensions)
        else:
            raise NotImplementedError

    def _updateNeighbourLists2D(self, locations, dimensions):
        """
        2D version of _updateNeighbourLists.
        """
        R2 = float(self.parameters["NEAREST_NEIGHBOURS_MAX_RADIUS"]) ** 2
        MAX_INDEX_RANGE = int(
            self.parameters["NEAREST_NEIGHBOURS_MAX_INDEX_RANGE"])

        for x1 in range(dimensions[0]):
            current_x_neighbour_list = []
            self.neighbour_lists.append(current_x_neighbour_list)
            for y1 in range(dimensions[1]):
                current_neighbour_list = []
                current_x_neighbour_list.append(current_neighbour_list)

                min_x_index = max(0, x1 - MAX_INDEX_RANGE)
                max_x_index = min(dimensions[0], x1 + MAX_INDEX_RANGE + 1)
                for x2 in range(min_x_index, max_x_index):
                    min_y_index = max(0, y1 - MAX_INDEX_RANGE)
                    max_y_index = min(dimensions[1], y1 + MAX_INDEX_RANGE + 1)
                    for y2 in range(min_y_index, max_y_index):
                        if x1 == x2 and y1 == y2:
                            continue

                        r2 = self._calculateDistanceSquared(
                                locations[x1][y1], locations[x2][y2])
                        if r2 <= R2:
                            current_neighbour_list.append([x2, y2])

    def _updateNeighbourLists3D(self, locations, dimensions):
        """
        3D version of _updateNeighbourLists.
        """
        R2 = float(self.parameters["NEAREST_NEIGHBOURS_MAX_RADIUS"]) ** 2
        MAX_INDEX_RANGE = int(
            self.parameters("NEAREST_NEIGHBOURS_MAX_INDEX_RANGE"))

        for x1 in range(dimensions[0]):
            current_x_neighbour_list = []
            self.neighbour_lists.append(current_x_neighbour_list)
            for y1 in range(dimensions[1]):
                current_y_neighbour_list = []
                current_x_neighbour_list.append(current_y_neighbour_list)
                for z1 in range(dimensions[2]):
                    current_neighbour_list = []
                    current_y_neighbour_list.append(current_neighbour_list)

                    min_x_index = max(0, x1 - MAX_INDEX_RANGE)
                    max_x_index = min(dimensions[0],
                                      x1 + MAX_INDEX_RANGE + 1)
                    for x2 in range(min_x_index, max_x_index):
                        min_y_index = max(0, y1 - MAX_INDEX_RANGE)
                        max_y_index = min(dimensions[1],
                                          y1 + MAX_INDEX_RANGE + 1)
                        for y2 in range(min_y_index, max_y_index):
                            min_z_index = max(0, z1 - MAX_INDEX_RANGE)
                            max_z_index = min(dimensions[2],
                                              z1 + MAX_INDEX_RANGE + 1)
                            for z2 in range(min_z_index, max_z_index):
                                if x1 == x2 and y1 == y2 and z1 == z2:
                                    continue

                                r2 = self._calculateDistanceSquared(
                                        locations[x1][y1][z1],
                                        locations[x2][y2][z2])
                                if r2 <= R2:
                                    current_neighbour_list.append([x2, y2, z2])

    def _calculateDistanceSquared(self, location1, location2):
        """
        Calculates the distance between the given two locations squared.
        """
        assert len(location1) == len(location2)

        distance = 0.0
        for i in range(len(location1)):
            distance += (location1[i] - location2[i]) ** 2

        return distance
