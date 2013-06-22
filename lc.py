import __future__
import itertools
import math
import random

##################################################################
#                     Natural Constants                          #
##################################################################

# Boltzmann constant in [erg]/[K].
kB = 1.3806488*(10**(-16))

##################################################################
#                     System Properties                          #
##################################################################

# These are the system dimensions.
DIMENSIONS = [2, 2]

# Change of temperature in each cooling step in [K].
TEMPERATURE_DELTA = 10
# Initial temperature in [K].
INITIAL_TEMPERATURE = 298
# Final temperature to cool the system to.
FINAL_TEMPERATURE = 100

# Number of Metropolis steps to perform in each cooling steps.
METROPOLIS_NUM_STEPS = 1000
# The standard deviation of the gaussian random selection in Metropolis.
METROPOLIS_STDEV = 1.0
# Number of steps in the cooling process to wait if there is no improvement
# before lowering the temperature further.
MAX_NON_IMPROVING_STEPS = 3

##################################################################
#                     Potential Functions                        #
##################################################################

def P2(x):
    """
    Second order legendre polynomial.
    """
    return (3.0 * (x**2) - 1.0) / 2.0

def UNearestNeighbours(angles, dimensions, indices):
    """
    Calculates the potential from the interactions of a single spin given by
    the indices, using only the nearest neighbour spins at the given angles.
    """
    u = 0

    # Calculate the current angle pointed to by the indices.
    current_angle = angles
    for i in indices:
        current_angle = current_angle[i]

    # Go over each of the dimensions, and check the nearest neighbours.
    for (dindex, dsize) in enumerate(dimensions):
        # Check the -1 neighbour for the current dimension.
        if indices[dindex] > 0:
            indices[dindex] -= 1

            neighbour_angle = angles
            for i in indices:
                neighbour_angle = neighbour_angle[i]

            u += P2(math.cos(current_angle - neighbour_angle))

            indices[dindex] += 1

        # Check the +1 neighbour for the current dimension.
        if indices[dindex] < dsize - 1:
            indices[dindex] += 1

            neighbour_angle = angles
            for i in indices:
                neighbour_angle = neighbour_angle[i]

            u += P2(math.cos(current_angle - neighbour_angle))

            indices[dindex] -= 1

    return u

#def U1(part,angles):  #calculates the potential between part and all the othe particles the come after it in their order
#    u=0
#    new_angle=angles[part[0]][part[1]]
#    
#    if part[0]<N:
#        for i in xrange(part[0]+1,N):
#            u=u+P2(cos((new_angle-angles[i][part[1]])%360))
#        for part2_x in xrange(part[0]+1,N):
#            if part[1]<M:
#                for part2_y in xrange(part[1]+1,M):
#                    u=u+P2(cos((new_angle-angles[part2_x][part2_y])%360))
#    if part[1]<M:
#        for i in xrange(part[1]+1,M):
#            u=u+P2(cos((new_angle-angles[part[0]][i])%360))
#        
#    return u

##################################################################
#                     System Class                               #
##################################################################

class LiquidCrystalSystem:
    """
    This class represents the system that we are cooling.
    It holds the positions and angles of molecules in a liquid crystal, and can
    perform a Monte Carlo Metropolis cooling of the liquid crystal.
    """
    def __init__(self,
                 temperature=INITIAL_TEMPERATURE,
                 potential=UNearestNeighbours,
                 dimensions=DIMENSIONS,
                 initial_angles=None):
        """
        Initializes the system from the given dimensions (or the default) and
        an initial nested list of initial angles, as well as the temperature.
        If no initial system properties are given it is randomly set up.
        """
        self.temperature = temperature
        self.potential = potential
        self.dimensions = dimensions[:]

        if initial_angles is None:
            initial_angles = self._createPropertyList(
                    lambda indices: random.uniform(0, 2*math.pi))
        self.angles = initial_angles

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
            h += self.potential(self.angles, self.dimensions, indices)

        return h * (10**(-16))

    def getCanonicalEnsembleProbability(self):
        """
        Calculates the non-normalized canonical ensemble probability of the
        system, which is: e^(-E/(kB*T))
        """
        E = self.getPotentialEnergy()
        T = self.temperature
        return math.exp(-(abs(E) / (kB * T)))

    def performMonteCarloCooling(self,
                                 final_tempareture=FINAL_TEMPERATURE,
                                 temperature_delta=TEMPERATURE_DELTA):
        """
        Run the Monte Carlo cooling algorithm for this system, from the current
        system temperature to the given final temperature, in the temperature
        delta decrements that were given.
        """
        print "Running Monte Carlo cooling on the system:"
        print
        while self.temperature > FINAL_TEMPERATURE:
            print ("--------------------(T = %s[K])--------------------" %
                   str(self.temperature))
            self._print2DSystem()
    
            # Continue running Metropolis steps until we reach a point where in
            # MAX_NON_IMPROVING_STEPS steps there was no energy improvement.
            best_energy = self.getPotentialEnergy()
            k = 0
            while k < MAX_NON_IMPROVING_STEPS:
                print "Performing Metropolis step... ",
                current_angles = self._copyPropertyList(self.angles)
                self._performMetropolisStep()
                new_energy = self.getPotentialEnergy()

                if new_energy < best_energy:
                    best_energy = new_energy
                    k = 0
                    print "Got better energy."
                else:
                    self.angles = current_angles
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
            # TODO: Select the initial angle.
            # Perform METROPOLIS_NUM_STEPS steps and each time select a new
            # angle from a distribution that should become more and more as the
            # boltzmann energy distribution.
            for step in xrange(METROPOLIS_NUM_STEPS):
                # Select a new angle based on the current one using a Gaussian
                # distribution.
                current_angle = self._getProperty(self.angles, indices)
                new_angle = random.gauss(current_angle, METROPOLIS_STDEV)
                new_angle %= 2 * math.pi

                # Calculate the coefficient that is proportional to the density
                # of the boltzmann distibution.
                old_probability = self.getCanonicalEnsembleProbability()
                self._setProperty(self.angles, indices, new_angle)
                new_probability = self.getCanonicalEnsembleProbability()
                alpha = new_probability / old_probability

                alpha = min(1.0, alpha)
                p = random.random()
                if p > alpha:
                    self._setProperty(self.angles, indices, current_angle)

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
        angle_iterator = self._getSystemPropertyIterator(self.angles)
        for (indices, angle) in itertools.izip(index_iterator, angle_iterator):
            if indices[0] == 0:
                print
                print
            print "%.3f Pi   " % (angle / math.pi),
        print
        print

##################################################################
#                         Main                                   #
##################################################################

def main():
    print "*"*70
    print "*"*70
    print ("Starting the Simulation with T=%s[K] and N=%s, M=%s" %
           (INITIAL_TEMPERATURE, DIMENSIONS[0], DIMENSIONS[1]))
    print "*"*70
    print "*"*70
    system = LiquidCrystalSystem()
    system.performMonteCarloCooling()

if __name__ == "__main__":
    main()
