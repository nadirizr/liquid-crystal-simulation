import os

from params import *
from util import *

class LiquidCrystalSystem:
    """
    This class represents the system that we are cooling.
    It holds the positions and angles of molecules in a liquid crystal, and can
    perform a Monte Carlo Metropolis cooling of the liquid crystal.
    """
    def __init__(self, temperature, potential, dimensions,
                 initial_spins=None, initial_locations=None):
        """
        Initializes the system from the given dimensions (or the default) and
        an initial nested list of initial angles, as well as the temperature.
        If no initial system properties are given it is randomly set up.
        """
        self.temperature = temperature
        self.potential = potential
        self.dimensions = dimensions[:]

        if initial_spins is None:
            initial_spins = self._createPropertyList(
                    lambda indices: CreateNormalizedVector(
                            [random.uniform(0, 1.0)
                             for i in range(len(indices))]))
        self.spins = initial_spins

        if initial_locations is None:
            initial_locations = self._createPropertyList(
                    lambda indices: array(
                            [random.uniform(i*SPACING - SPACING_STDEV,
                                            i*SPACING + SPACING_STDEV)
                             for i in indices]))
        self.locations = initial_locations

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

        index_iterator = self._getSystemIndexIterator()
        for indices in index_iterator:
            h += self.potential.calculate(
                    self.spins, self.locations, self.dimensions, indices)

        return h

    def getCanonicalEnsembleProbability(self):
        """
        Calculates the non-normalized canonical ensemble probability of the
        system, which is: e^(-E/(kB*T))
        """
        E = self.getPotentialEnergy()
        T = self.temperature
        return math.exp(-(abs(E) / (kB * T)))

    def performMonteCarloCooling(self, final_tempareture, temperature_delta):
        """
        Run the Monte Carlo cooling algorithm for this system, from the current
        system temperature to the given final temperature, in the temperature
        delta decrements that were given.
        """
        print "Running Monte Carlo cooling on the system:"
        print
        round_number = 0
        while self.temperature > final_tempareture:
            round_number += 1
            print ("--------------------(T = %s[K])--------------------" %
                   str(self.temperature))
            self._print2DSystem()
            self._outputToAvizFile(
                    "%s/lqc%s.xyz" % (AVIZ_OUTPUT_PATH, hex(round_number)))
    
            # Continue running Metropolis steps until we reach a point where in
            # MAX_NON_IMPROVING_STEPS steps there was no energy improvement.
            best_energy = self.getPotentialEnergy()
            k = 0
            while k < MAX_NON_IMPROVING_STEPS:
                print "Performing Metropolis step... ",
                current_spins = self._copyPropertyList(self.spins)
                current_locations = self._copyPropertyList(self.locations)
                self._performMetropolisStep()
                new_energy = self.getPotentialEnergy()

                if new_energy < best_energy:
                    best_energy = new_energy
                    k = 0
                    print "Got better energy."
                else:
                    self.spins = current_spins
                    self.locations = current_locations
                    k += 1
                    print "Didn't get better energy (k=%s)" % k
            
            # Next step with lower temperature.
            print ("Cooling... (T=%s[K]->%s[K])" %
                   (self.temperature, self.temperature - temperature_delta))
            print
            self.temperature -= temperature_delta

        print "End of Simulation."
        #TODO:do something

    def _getSystemIndexIterator(self):
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

    def _getSystemPropertyIterator(self, property_values):
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

        index_iterator = self._getSystemIndexIterator()
        return SystemPropertyIterator(property_values, index_iterator)
    
    def _createPropertyList(self, value_generator):
        """
        Creates and returns a multi-dimensional list populated with values
        returned from the given value generator function that is given the
        list of indices of the current value to generate.
        """
        index_iterator = self._getSystemIndexIterator()
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

    def _copyPropertyList(self, property_values):
        """
        Returns a complete deep copy of the given property values
        multi-dimensional list.
        """
        return self._createPropertyList(
            lambda indices: self._getProperty(property_values, indices))

    def _getProperty(self, property_values, indices):
        """
        Returns the property value pointed to by the given indices into the
        given property values multi-dimensional list.
        """
        current_values = property_values
        for index in indices:
            current_values = current_values[index]
        return current_values

    def _setProperty(self, property_values, indices, new_value):
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

    def _getNewRandomSpin(self, current_spin):
        """
        Returns a new random spin based on the current one, from a gaussian
        distribution.
        """
        new_spin = current_spin.copy()
        for d in range(len(new_spin)):
            new_spin[d] = random.gauss(new_spin[d], SPIN_STDEV)
        new_spin /= linalg.norm(new_spin)
        return new_spin

    def _getNewRandomLocation(self, current_location):
        """
        Returns a new random location based on the current one, from a gaussian
        distribution.
        """
        new_location = current_location.copy()
        for d in range(len(new_location)):
            new_location[d] = random.gauss(new_location[d], SPACING_STDEV)
        new_location /= linalg.norm(new_location)
        return new_location

    def _performMetropolisStep(self):
        """
        Go over each of the spins in the system, and find a new random angle for
        them, according to the canonical ensemble probability density function.
        This is done using the Metropolis algorithm, in the following way:
        1) Use a gaussian random function to select a new angle for the spin.
        2) Calculate the new energy of the entire system.
        3) If it is lower than the original energy, accept it.
        4) If not, pick it with a probability of P(NewE)/P(OldE), where P is the
           canonical probability distribution function.
        5) Continue performing these improvements NUM_METROPOLIS_STEPS times.
        """
        # Go over all of the particles, and change the angles for each one.
        index_iterator = self._getSystemIndexIterator()
        for indices in index_iterator:
            # TODO: Select the initial spin and location.
            # Perform METROPOLIS_NUM_STEPS steps and each time select a new
            # spin orientation from a distribution that should become more and
            # more as the Boltzmann energy distribution.
            for step in xrange(METROPOLIS_NUM_STEPS):
                # Select a new spin and location based on the current.
                current_spin = self._getProperty(self.spins, indices)
                current_location = self._getProperty(self.locations, indices)
                new_spin = self._getNewRandomSpin(current_spin)
                new_location = self._getNewRandomLocation(current_location)

                # Calculate the coefficient that is proportional to the density
                # of the Boltzmann distibution.
                old_probability = self.getCanonicalEnsembleProbability()
                self._setProperty(self.spins, indices, new_spin)
                self._setProperty(self.locations, indices, new_location)
                new_probability = self.getCanonicalEnsembleProbability()
                alpha = new_probability / old_probability

                alpha = min(1.0, alpha)
                p = random.random()
                if p > alpha:
                    self._setProperty(self.spins, indices, current_spin)
                    self._setProperty(self.locations, indices, current_location)

    def _outputToAvizFile(self, filepath):
        """
        Outputs the current state of the system (locations and spins) to the
        given file path in Aviz XYZ format.
        """
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
        location_iterator = self._getSystemPropertyIterator(self.locations)
        spin_iterator = self._getSystemPropertyIterator(self.spins)
        for (location, spin) in itertools.izip(location_iterator,
                                               spin_iterator):
            f.write("Sp %s %s\n" % (" ".join([str(l) for l in location]),
                                    " ".join([str(s) for s in spin])))

        f.flush()
        f.close()

    def _print2DSystem(self):
        """
        Prints the system properties (energy, temperature, angles).
        This method only prints the system itself if there are 2 dimensions.
        """
        print "Potential Energy: %s[erg]" % self.getPotentialEnergy()
        print "Temperature: %s[K]" % self.temperature

        if len(self.dimensions) != 2:
            return
        
        print "Spin Angles:",
        index_iterator = self._getSystemIndexIterator()
        spin_iterator = self._getSystemPropertyIterator(self.spins)
        location_iterator = self._getSystemPropertyIterator(self.locations)
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
