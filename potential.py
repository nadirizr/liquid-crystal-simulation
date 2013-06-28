class Potential:
    """
    This is the interface for all potentials.
    """

    def calculate(self, spins, locations, dimensions, indices):
        """
        Calculates the potential for the given spin.
        """
        raise NotImplemented

class NearestNeighboursPotential(Potential):
    """
    This is an abstract class for nearest neighbours potentials.
    """
    
    def calculateTwoSpins(self, spin1, location1, spin2, location2):
        """
        Calculates the potential between the given spins.
        """
        raise NotImplemented

    def calculate(self, spins, locations, dimensions, indices):
        """
        Calculates the nearest neighbours potential for the given spin.
        """
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

                u += self.calculateTwoSpins(current_spin,
                                            current_location,
                                            neighbour_spin,
                                            neighbour_location)

                indices[dindex] -= neighbour_index

        return u
