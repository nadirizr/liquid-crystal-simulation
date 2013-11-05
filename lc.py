import os

from util import *

class LiquidCrystalSystem:
    """
    This class represents the system that we are cooling.
    It holds the positions and angles of molecules in a liquid crystal, and can
    perform a Monte Carlo Metropolis cooling of the liquid crystal.
    """
    def __init__(self, parameters, initial_temperature, 
                 initial_spins=None, initial_locations=None,
                 original_locations=None):
        """
        Initializes the system from the given dimensions (or the default) and
        an initial nested list of initial angles, as well as the temperature.
        If no initial system properties are given it is randomly set up.
        """
        DIMENSIONS = parameters["DIMENSIONS"]
        BOUNDARY_CONDITIONS = parameters["BOUNDARY_CONDITIONS"]
        INITIAL_SPACING = parameters["INITIAL_SPACING"]
        INITIAL_SPACING_STDEV = parameters["INITIAL_SPACING_STDEV"]
        INITIAL_SPIN_ORIENTATION = parameters["INITIAL_SPIN_ORIENTATION"]
        INITIAL_SPIN_ORIENTATION_STDEV = parameters["INITIAL_SPIN_ORIENTATION_STDEV"]
        POTENTIAL = parameters["POTENTIAL"]
        TWO_SPIN_POTENTIAL = parameters["TWO_SPIN_POTENTIAL"]

        self.parameters = parameters
        self.temperature = initial_temperature
        self.potential = POTENTIAL(TWO_SPIN_POTENTIAL(parameters), parameters)
        self.dimensions = DIMENSIONS[:]
        self.boundary_conditions = BOUNDARY_CONDITIONS[:]
        self.spacing = INITIAL_SPACING[:]

        if initial_spins is None:
            initial_spins = self.createPropertyList(
                    lambda indices: CreateNormalizedVector(
                            [random.uniform(INITIAL_SPIN_ORIENTATION[i] -
                                            INITIAL_SPIN_ORIENTATION_STDEV[i],
                                            INITIAL_SPIN_ORIENTATION[i] +
                                            INITIAL_SPIN_ORIENTATION_STDEV[i])
                             for i in range(len(indices))]))
        self.spins = initial_spins

        if initial_locations is None:
            initial_locations = self.createPropertyList(
                    lambda indices: array(
                            [random.uniform(index * INITIAL_SPACING[i] -
                                            INITIAL_SPACING_STDEV[i],
                                            index * INITIAL_SPACING[i] +
                                            INITIAL_SPACING_STDEV[i])
                             for i, index in enumerate(indices)]))
        self.locations = initial_locations

        if original_locations is None:
            original_locations = self.copyPropertyList(self.locations)
        self.original_locations = original_locations

    def copy(self):
        """
        Returns a copy of this LiquidCrystalSystem object.
        """
        #print "// LiquidCrystalSystem.copy:"
        parameters = self.parameters.copy()
        spins = self.copyPropertyList(self.spins)
        locations = self.copyPropertyList(self.locations)
        original_locations = self.copyPropertyList(self.original_locations)
        lcs = LiquidCrystalSystem(parameters, self.temperature,
                                  spins, locations, original_locations)
        #print "// lcs.getTemperature() = %s" % (lcs.getTemperature(),)
        #print "// lcs.getPotentialEnergy() = %s" % (lcs.getPotentialEnergy(),)
        #print "// lcs.getAverageSpinOrientation() = %s, self.getSpinOrientationVariance() = %s" % (lcs.getAverageSpinOrientation(), lcs.getSpinOrientationVariance())
        #print "// lcs.potential = %s, self.potential = %s" % (lcs.potential, self.potential)
        #lcs.print2DSystem()
        return lcs

    def getTemperature(self):
        """
        Returns the current system temperature.
        """
        return self.temperature

    def setTemperature(self, temperature):
        """
        Set the system temperature to the given one.
        """
        self.temperature = temperature

    def getThermalEnergy(self):
        """
        Calculates and returns the thermal energy of the system.
        """
        d = len(self.dimensions)
        N = reduce(lambda a,b: a*b, self.dimensions, 1)
        T = self.temperature
        return d * 0.5 * N * kB * T

    def getPotentialEnergy(self):
        """
        Calculates and returns the potential energy of the system.
        """
        self.potential.update()

        h = 0
        index_iterator = self.getSystemIndexIterator()
        for indices in index_iterator:
            h += self.getPotentialEnergyForSpin(indices)

        return h

    def getPotentialEnergyForSpin(self, indices):
        """
        Calculate the potential energy for the spin at the given indices.
        """
        return self.potential.calculate(self, indices)

    def getCanonicalEnsembleProbability(self, energy=None):
        """
        Calculates the non-normalized canonical ensemble probability of the
        system, which is: e^(-E/(kB*T))
        """
        E = energy
        if E is None:
            E = self.getPotentialEnergy()
        T = self.temperature
        return math.exp(-(E / (kB * T)))

    def getAverageSpinOrientation(self):
        """
        Calculates the average spin orientation of the system, indicating how
        ordered the system is.
        """
        sum_spin = array([0.0 for i in range(len(self.dimensions))])
        spin_iterator = self.getSystemPropertyIterator(self.spins)
        num_spins = 0
        for spin in spin_iterator:
            sum_spin += spin
            num_spins += 1
        return sum_spin / num_spins

    def getSpinOrientationVariance(self):
        """
        Calculates the variance of the spin orientation compared to the average
        (a value close to 0 is ordered).
        """
        spin_variance = 0.0
        average_spin = self.getAverageSpinOrientation()
        spin_iterator = self.getSystemPropertyIterator(self.spins)
        num_spins = 0
        for spin in spin_iterator:
            average_diff_spin = spin - average_spin
            spin_variance += dot(average_diff_spin, average_diff_spin)
            num_spins += 1
        spin_variance /= len(self.spins)
        return spin_variance

    def getSpin(self, indices):
        """
        Returns the spin of the given set of indices.
        """
        return self.getProperty(self.spins, indices)

    def setSpin(self, indices, spin):
        """
        Sets the spin of the given set of indices.
        """
        self.setProperty(self.spins, indices, spin)

    def getLocation(self, indices, locations=None):
        """
        Returns the location of the cell with the given indices.
        If any of the indices are negative or more than the number of cells in a
        certain dimension, and boundary conditions are preiodic, the location is
        translated accordingly.
        """
        # If no locations list was given, default to self.locations.
        if not locations:
            locations = self.locations

        # Get the location property.
        location = self.getProperty(locations, indices).copy()
        
        # Translate it if necessary.
        for (dim, index) in enumerate(indices):
            if self.boundary_conditions[dim] == "P" and \
               (index < 0 or index >= self.dimensions[dim]):
                location[dim] += ((index / self.dimensions[dim]) *
                                  self.spacing[dim])

        return location

    def setLocation(self, indices, location):
        """
        Sets the location of the cell with the given indices.
        If any of the indices are negative or more than the number of cells in a
        certain dimension, and boundary conditions are preiodic, the location is
        translated accordingly.
        """
        # Translate the location if necessary.
        for (dim, index) in enumerate(indices):
            if self.boundary_conditions[dim] == "P" and \
               (index < 0 or index >= self.dimensions[dim]):
                location[dim] -= ((index / self.dimensions[dim]) *
                                  self.spacing[dim])

        # Set the location property.
        self.setProperty(self.locations, indices, location)

    def getOriginalLocation(self, indices):
        """
        Returns the original location of the cell with the given indices.
        If any of the indices are negative or more than the number of cells in a
        certain dimension, and boundary conditions are preiodic, the location is
        translated accordingly.
        """
        return self.getLocation(indices, self.original_locations)

    def getCellNeighboursList(self, indices, index_ranges=None):
        """
        Returns a list of tuples of neighbours to the given cell, where each
        tuple is: (indices, location, spin).
        This method obeys the boundary conditions of the system, and if they are
        periodic in a certain direction then indices are given as negative or
        over the dimension of the system.
        The index ranges list should be of the same length of indices (the
        dimensions of the system), and should indicate how many cells to each
        direction should be added to the neighbour list.
        If index ranges are not given, then all cells are considered as
        neighbours, which is the same as giving the DIMENSIONS / 2.
        """
        # If no index ranges were given, go NEAREST_NEIGHBOURS_MAX_INDEX_RANGE
        # to every direction.
        if not index_ranges:
            index_ranges = [self.dimensions[i] / 2
                            for i in range(len(indices))]

        # Use specialized methods for efficiency in 2D and 3D.
        if len(self.dimensions) == 2:
            return self.getCellNeighboursList2D(indices, index_ranges)
        if len(self.dimensions) == 3:
            return self.getCellNeighboursList3D(indices, index_ranges)

        # Calculate the actual ranges of cells to include.
        neighbour_index_range = self._calculateNeighbourIndexRanges(
                indices, index_ranges)

        # Go over all the cells and check if any of them are within the given
        # bounds, and if so add them to the neighbour list.
        index_iterator = self.getSystemIndexIterator()
        neighbour_list = []
        for neighbour_indices in index_iterator:
            # Check if all of the indices are within range.
            indices_in_range = [neighbour_indices[i] in neighbour_index_range[i]
                                for i in range(len(indices))]
            if not all(indices_in_range):
                continue

            # If this is the origianl cell, skip it.
            if neighbour_indices == indices:
                continue

            # Calculate the translated neighbour indices.
            for dim in range(len(neighbour_indices)):
                # We only need to translate anything if there are periodic
                # boundary conditions.
                if self.boundary_conditions[dim] != "P":
                    continue

                min_range_index = indices[dim] - index_ranges[dim]
                max_range_index = indices[dim] + index_ranges[dim]
                lower_neighbour_index = (neighbour_indices[dim] -
                                         self.dimensions[dim])
                upper_neighbour_index = (neighbour_indices[dim] +
                                         self.dimensions[dim])
                if min_range_index <= lower_neighbour_index <= max_range_index:
                    neighbour_indices[dim] = lower_neighbour_index
                if min_range_index <= upper_neighbour_index <= max_range_index:
                    neighbour_indices[dim] = upper_neighbour_index

            # Add the indices to the neighbour list.
            neighbour_list.append(neighbour_indices[:])

        return neighbour_list

    def getCellNeighboursList2D(self, indices, index_ranges):
        """
        Specialized version for getCellNeighboursList in 2D.
        """
        # Calculate minimum and maximum indices in range in each dimension.
        x = indices[0]
        y = indices[1]
        min_x_range_index, max_x_range_index = \
                self._calculateNeighbourIndexRangeBoundaries(
                        indices, index_ranges, 0)
        min_y_range_index, max_y_range_index = \
                self._calculateNeighbourIndexRangeBoundaries(
                        indices, index_ranges, 1)

        # Go over the 2 dimensions back and forth according to the index_ranges.
        neighbour_list = []
        for nx in xrange(min_x_range_index, max_x_range_index + 1):
            for ny in xrange(min_y_range_index, max_y_range_index + 1):
                neighbour_indices = [nx, ny]

                # If this is the original cell, ignore it.
                if neighbour_indices == indices:
                    continue

                # Add the indices to the neighbour list.
                neighbour_list.append(neighbour_indices)

        return neighbour_list

    def getCellNeighboursList3D(self, indices, index_ranges):
        """
        Specialized version for getCellNeighboursList in 3D.
        """
        # Calculate minimum and maximum indices in range in each dimension.
        x = indices[0]
        y = indices[1]
        z = indices[2]
        min_x_range_index, max_x_range_index = \
                self._calculateNeighbourIndexRangeBoundaries(
                        indices, index_ranges, 0)
        min_y_range_index, max_y_range_index = \
                self._calculateNeighbourIndexRangeBoundaries(
                        indices, index_ranges, 1)
        min_z_range_index, max_z_range_index = \
                self._calculateNeighbourIndexRangeBoundaries(
                        indices, index_ranges, 2)

        # Go over the 3 dimensions back and forth according to the index_ranges.
        neighbour_list = []
        for nx in xrange(min_x_range_index, max_x_range_index + 1):
            for ny in xrange(min_y_range_index, max_y_range_index + 1):
                for nz in xrange(min_z_range_index, max_z_range_index + 1):
                    neighbour_indices = [nx, ny, nz]

                    # If this is the original cell, ignore it.
                    if neighbour_indices == indices:
                        continue

                    # Add the indices to the neighbour list.
                    neighbour_list.append(neighbour_indices)

        return neighbour_list

    def _calculateNeighbourIndexRangeBoundaries(self,
                                                cell_indices,
                                                index_ranges,
                                                dim):
        """
        Calculates and returns the lower and upper boundaries of indices for
        the given dimension according to the set boundary conditions and the
        given index range in that dimension.
        """
        min_range_index = cell_indices[dim] - index_ranges[dim]
        max_range_index = cell_indices[dim] + index_ranges[dim]
        if self.boundary_conditions[dim] == "P":
            min_range_index = min_range_index
            max_range_index = max_range_index
        elif self.boundary_conditions[dim] == "F":
            min_range_index = max(0, min_range_index)
            max_range_index = min(self.dimensions[dim] - 1, max_range_index)
        else:
            raise Exception("Unsupported boundary condition: %s" %
                            self.boundary_conditions[dim])
        return min_range_index, max_range_index

    def _calculateNeighbourIndexRanges(self, cell_indices, index_ranges):
        """
        Calculates and returns the list of indices for each dimension of
        neighbours of the given cell indices with a range to each direction
        given by index ranges according to the boundary conditions.
        For example, if in 2 dimensions there are periodic boundary conditions
        on X and fixed boundary conditions on Y, and the cell is [0,0] with
        index ranges of [1,1] then the returned indices would be:
        [[1,0], [2,0], [0,1], [1,1], [2,1]]
        """
        def calculate_index_range(dim):
            min_range_index, max_range_index = \
                    self._calculateNeighbourIndexRangeBoundaries(
                            cell_indices, index_ranges, dim)
            indices_range = range(min_range_index, max_range_index + 1)
            return [index % self.dimensions[dim] for index in indices_range]

        return [calculate_index_range(i) for i in range(len(cell_indices))]

    def getSystemIndexIterator(self):
        """
        Returns an iterator that returns a list of indices to the system.
        Each call to next() will return the next set of indices.
        """
        class SystemIndexIterator:
            def __init__(self, dimensions):
                self._dimensions = dimensions
                self._current_indices = [0 for d in dimensions]
                self._current_indices[0] -= 1

            def __iter__(self):
                return self

            def next(self):
                self._current_indices[0] += 1
                for i in range(len(self._current_indices)):
                    if self._current_indices[i] < self._dimensions[i]:
                        break

                    if i == len(self._dimensions) - 1:
                        raise StopIteration

                    self._current_indices[i] = 0
                    self._current_indices[i+1] += 1

                return self._current_indices

        return SystemIndexIterator(self.dimensions)

    def getSystemPropertyIterator(self, property_values):
        """
        Returns an iterator that returns on each call to next a value from the
        given system property list, such as angles.
        The system property values must be of the system dimensions.
        """
        class SystemPropertyIterator:
            def __init__(self, propety_values, index_iterator):
                self._property_values = property_values
                self._index_iterator = index_iterator

            def __iter__(self):
                return self

            def next(self):
                index_list = self._index_iterator.next()
                value_list = self._property_values
                for i in index_list:
                    value_list = value_list[i]
                return value_list

        index_iterator = self.getSystemIndexIterator()
        return SystemPropertyIterator(property_values, index_iterator)
    
    def createPropertyList(self, value_generator):
        """
        Creates and returns a multi-dimensional list populated with values
        returned from the given value generator function that is given the
        list of indices of the current value to generate.
        """
        index_iterator = self.getSystemIndexIterator()
        value_list = []
        for indices in index_iterator:
            current_values = value_list
            for (i, index) in enumerate(indices):
                if index >= len(current_values):
                    current_values.extend(
                            [[] for j in range(self.dimensions[i])])
                if i == len(self.dimensions) - 1:
                    current_values[index] = value_generator(indices)
                else:
                    current_values = current_values[index]

        return value_list

    def copyPropertyList(self, property_values):
        """
        Returns a complete deep copy of the given property values
        multi-dimensional list.
        """
        return self.createPropertyList(
            lambda indices: self.getProperty(property_values, indices).copy())

    def getProperty(self, property_values, indices):
        """
        Returns the property value pointed to by the given indices into the
        given property values multi-dimensional list.
        """
        current_values = property_values
        for (dim, index) in enumerate(indices):
            real_index = index % self.dimensions[dim]
            current_values = current_values[real_index]
        return current_values

    def setProperty(self, property_values, indices, new_value):
        """
        Sets the property value pointed to by the given indices into the given
        property values multi-dimensional list to the given new value.
        """
        current_values = property_values
        for (dim, index) in enumerate(indices):
          real_index = index % self.dimensions[dim]
          if dim == len(self.dimensions) - 1:
              current_values[real_index] = new_value
          else:
              current_values = current_values[real_index]

    def outputToAvizFile(self, filepath):
        """
        Outputs the current state of the system (locations and spins) to the
        given file path in Aviz XYZ format.
        """
        if len(self.dimensions) > 3:
            return

        dirpath = os.path.dirname(filepath)
        if not os.path.isdir(dirpath):
            os.makedirs(dirpath)
        f = file(filepath, "w")

        # Write the number of points in this file.
        num_points = reduce(lambda x,y: x*y, self.dimensions, 1)
        f.write("%s\n" % num_points)

        # Write the name for the set of data points.
        f.write("Liquid Crystal Spins\n")

        # Write the spins and locations.
        # Format: X Y Z Sx Sy Sz
        DIMS = 3
        location_iterator = self.getSystemPropertyIterator(self.locations)
        spin_iterator = self.getSystemPropertyIterator(self.spins)
        for (location, spin) in itertools.izip(location_iterator,
                                               spin_iterator):
            aviz_location = ([0.0] * (DIMS - len(location))) + list(location)
            aviz_spin = ([0.0] * (DIMS - len(spin))) + list(spin)
            f.write("Sp %s %s\n" % (" ".join([str(l) for l in aviz_location]),
                                    " ".join([str(s) for s in aviz_spin])))

        f.flush()
        f.close()


    def outputInformationToFile(self, filepath):
        """
        Outputs the current information such as <U>, Cv etc to a text file.
        """
        if len(self.dimensions) > 3:
            return

        dirpath = os.path.dirname(filepath)
        if not os.path.isdir(dirpath):
            os.makedirs(dirpath)

        f = file(filepath, "a")
        avg_director = self.getAverageSpinOrientation()
        avg_energy = self.getPotentialEnergy()
        t = self.getTemperature()
        f.write("%s\t%s\t%s\n" % (t, avg_energy, avg_director))
        f.flush()
        f.close()

    def print2DSystem(self):
        """
        Prints the system properties (energy, temperature, angles).
        This method only prints the system itself if there are 2 dimensions.
        """
        print "Potential Energy: %s[erg]" % self.getPotentialEnergy()
        print "Temperature*: %s" % self.temperature

        if len(self.dimensions) != 2:
            return
        
        print "Spin Angles:",
        index_iterator = self.getSystemIndexIterator()
        spin_iterator = self.getSystemPropertyIterator(self.spins)
        location_iterator = self.getSystemPropertyIterator(self.locations)
        for (indices, spin, location) in itertools.izip(index_iterator,
                                                        spin_iterator,
                                                        location_iterator):
            if indices[0] == 0:
                print
                print
            angle = math.atan(spin[1] / spin[0])
            print "%.3f,%.3f (%.3f Pi)   " % (location[0], location[1],
                                              angle / math.pi),
        print
        print
