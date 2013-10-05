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

    def calculate2D(self, spins, locations, dimensions, indices):
        """
        Calculates the nearest neighbours potential for the given spin in 2D.
        """
        U = 0

        x = indices[0]
        y = indices[1]
        current_spin = spins[x][y]
        current_location = locations[x][y]

        if x < dimensions[0] - 1:
            neighbour_spin = spins[x+1][y]
            neighbour_location = locations[x+1][y]
            U += self.potential.calculateTwoSpins(current_spin,
                                                  current_location,
                                                  neighbour_spin,
                                                  neighbour_location)
        if y < dimensions[1] - 1:
            neighbour_spin = spins[x][y+1]
            neighbour_location = locations[x][y+1]
            U += self.potential.calculateTwoSpins(current_spin,
                                                  current_location,
                                                  neighbour_spin,
                                                  neighbour_location)

        return U

    def calculate3D(self, spins, locations, dimensions, indices):
        """
        Calculates the nearest neighbours potential for the given spin in 3D.
        """
        U = 0

        x = indices[0]
        y = indices[1]
        z = indices[2]
        current_spin = spins[x][y][z]
        current_location = locations[x][y][z]

        if x < dimensions[0] - 1:
            neighbour_spin = spins[x+1][y][z]
            neighbour_location = locations[x+1][y][z]
            U += self.potential.calculateTwoSpins(current_spin,
                                                  current_location,
                                                  neighbour_spin,
                                                  neighbour_location)
        if y < dimensions[1] - 1:
            neighbour_spin = spins[x][y+1][z]
            neighbour_location = locations[x][y+1][z]
            U += self.potential.calculateTwoSpins(current_spin,
                                                  current_location,
                                                  neighbour_spin,
                                                  neighbour_location)
        if z < dimensions[2] - 1:
            neighbour_spin = spins[x][y][z+1]
            neighbour_location = locations[x][y][z+1]
            U += self.potential.calculateTwoSpins(current_spin,
                                                  current_location,
                                                  neighbour_spin,
                                                  neighbour_location)

        return U

    def calculate(self, spins, locations, dimensions, indices):
        """
        Calculates the nearest neighbours potential for the given spin.
        """
        if len(dimensions) == 2:
            return self.calculate2D(spins, locations, dimensions, indices)
        if len(dimensions) == 3:
            return self.calculate3D(spins, locations, dimensions, indices)

        U = 0

        # Calculate the current spin and location pointed to by the indices.
        current_spin = spins
        current_location = locations
        for i in indices:
            current_spin = current_spin[i]
            current_location = current_location[i]

        # Go over each of the dimensions, and check the nearest neighbours.
        for (dindex, dsize) in enumerate(dimensions):
            # Check the -1,+1 neighbours for the current dimension.
            neighbours_to_check = []
            if indices[dindex] > 0:
                neighbours_to_check.append(-1)
            if indices[dindex] < dsize - 1:
                neighbours_to_check.append(+1)

            # Check all relevant neighbours for the current dimension.
            for neighbour_index in neighbours_to_check:
                indices[dindex] += neighbour_index

                neighbour_spin = spins
                neighbour_location = locations
                for i in indices:
                    neighbour_spin = neighbour_spin[i]
                    neighbour_location = neighbour_location[i]

                U += self.potential.calculateTwoSpins(current_spin,
                                                      current_location,
                                                      neighbour_spin,
                                                      neighbour_location)

                indices[dindex] -= neighbour_index

        return U / 2.0
