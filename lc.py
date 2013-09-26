import os

from util import *

class LiquidCrystalSystem:
    """
    This class represents the system that we are cooling.
    It holds the positions and angles of molecules in a liquid crystal, and can
    perform a Monte Carlo Metropolis cooling of the liquid crystal.
    """
    def __init__(self, parameters, initial_temperature, 
                 initial_spins=None, initial_locations=None):
        """
        Initializes the system from the given dimensions (or the default) and
        an initial nested list of initial angles, as well as the temperature.
        If no initial system properties are given it is randomly set up.
        """
        DIMENSIONS = parameters["DIMENSIONS"]
        INITIAL_SPACING = parameters["INITIAL_SPACING"]
        INITIAL_SPACING_STDEV = parameters["INITIAL_SPACING_STDEV"]
        INITIAL_SPIN_ORIENTATION = parameters["INITIAL_SPIN_ORIENTATION"]
        INITIAL_SPIN_ORIENTATION_STDEV = parameters["INITIAL_SPIN_ORIENTATION_STDEV"]
        POTENTIAL = parameters["POTENTIAL"]

        self.parameters = parameters
        self.temperature = initial_temperature
        self.potential = POTENTIAL(self.parameters)
        self.dimensions = DIMENSIONS[:]

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
        h = 0

        index_iterator = self.getSystemIndexIterator()
        for indices in index_iterator:
            h += self.potential.calculate(
                    self.spins, self.locations, self.dimensions, indices)

        return h

    def getCanonicalEnsembleProbability(self, energy=None):
        """
        Calculates the non-normalized canonical ensemble probability of the
        system, which is: e^(-E/(kB*T))
        """
        E = energy or self.getPotentialEnergy()
        T = self.temperature
        res =  math.exp(-(abs(E) / (kB * T)))
        #if res == 0.0:
            #print "getCanonicalEnsembleProbability: res=%s, E=%s, kB=%s" % (res , E , kB)
        return res

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
            lambda indices: self.getProperty(property_values, indices))

    def getProperty(self, property_values, indices):
        """
        Returns the property value pointed to by the given indices into the
        given property values multi-dimensional list.
        """
        current_values = property_values
        for index in indices:
            current_values = current_values[index]
        return current_values

    def setProperty(self, property_values, indices, new_value):
        """
        Sets the property value pointed to by the given indices into the given
        property values multi-dimensional list to the given new value.
        """
        current_values = property_values
        for (d, index) in enumerate(indices):
          if d == len(self.dimensions) - 1:
              current_values[index] = new_value
          else:
              current_values = current_values[index]

    def getPotentialEnergyForSpin(self, indices):
        """
        Calculate the potential energy for the spin at the given indices.
        """
        return self.potential.calculate(
                self.spins, self.locations, self.dimensions, indices)

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

    def print2DSystem(self):
        """
        Prints the system properties (energy, temperature, angles).
        This method only prints the system itself if there are 2 dimensions.
        """
        print "Potential Energy: %s[erg]" % self.getPotentialEnergy()
        print "Thermal Energy: %s[erg]" % self.getThermalEnergy()
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
