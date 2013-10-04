from lc import LiquidCrystalSystem
from util import *

class MonteCarloAlgorithm:
    
    def __init__(self, lcs, parameters, parameter_prefix="MC_"):
        self.lcs = lcs
        self.parameters = parameters
        self.parameter_prefix = parameter_prefix

    def isNewStateBetter(self, current_state, new_state):
        """
        Returns true if the new state is better than the current one.
        This must be implemented by any Monte Carlo Algorithm class.
        """
        raise NotImplementedError

    def getLCS(self):
        """
        Returns the liquid crystal system used by the algorithm.
        NOTE: The system may be changed during the course of the algorithm
              running since it duplicates states to determine which is better.
        """
        return self.lcs
    
    def run(self):
        """
        Run the Monte Carlo cooling algorithm for the given system, from the
        current system temperature to the given final temperature, in the
        temperature delta decrements that were given.
        """
        AVIZ_OUTPUT_PATH = str(
            self.parameters[self.parameter_prefix + "AVIZ_OUTPUT_PATH"])
        MC_TEMPERATURES = list(
            self.parameters[self.parameter_prefix + "TEMPERATURES"])
        MC_MAX_NON_IMPROVING_STEPS = int(
            self.parameters[self.parameter_prefix + "MAX_NON_IMPROVING_STEPS"])

        print ("Running the Monte Carlo algorithm on the system (T*=%s):" %
               self.lcs.getTemperature())
        print
        round_number = 0
        aviz_file_number = 0
        
        self.lcs.print2DSystem()
        self.lcs.outputToAvizFile(
                "%s%08d.xyz" % (AVIZ_OUTPUT_PATH,
                                aviz_file_number))
        for temperature in MC_TEMPERATURES + [MC_TEMPERATURES[-1]]:
            round_number += 1
            print ("--------------------(T* = %s)--------------------" %
                   self.lcs.getTemperature())
    
            # Continue running Metropolis steps until we reach a point where in
            # MAX_NON_IMPROVING_STEPS steps there was no energy improvement.
            k = 0
            while k < MC_MAX_NON_IMPROVING_STEPS:
                current_spins = self.lcs.copyPropertyList(self.lcs.spins)
                current_locations = self.lcs.copyPropertyList(self.lcs.locations)
                current_lcs = LiquidCrystalSystem(self.parameters,
                                                  self.lcs.getTemperature(),
                                                  current_spins,
                                                  current_locations)

                print "Performing Metropolis step... ",
                self._performMetropolisStep()

                if self.isNewStateBetter(current_lcs, self.lcs):
                    print "Got better state."
                    print
                    self.lcs.print2DSystem()

                    k = 0
                    aviz_file_number += 1
                    self.lcs.outputToAvizFile(
                            "%s%08d.xyz" % (AVIZ_OUTPUT_PATH,
                                            aviz_file_number))
                else:
                    print "Didn't get better state (k=%s)" % (k+1)
                    k += 1
                    self.lcs = current_lcs
            
            # Next step with the next temperature.
            print ("Changing Temperature ... (T*=%s -> %s)" %
                   (self.lcs.getTemperature(), temperature))
            print
            self.lcs.setTemperature(temperature)

        print "End of Simulation."

    def _getNewRandomSpin(self, current_spin):
        """
        Returns a new random spin based on the current one, from a gaussian
        distribution.
        """
        MC_SPIN_STDEV = float(
            self.parameters[self.parameter_prefix + "SPIN_STDEV"])

        new_spin = current_spin.copy()
        for d in range(len(new_spin)):
            new_spin[d] = random.gauss(new_spin[d], MC_SPIN_STDEV)
        new_spin /= linalg.norm(new_spin)
        return new_spin

    def _getNewRandomLocation(self, current_location):
        """
        Returns a new random location based on the current one, from a gaussian
        distribution.
        """
        MC_SPACING_STDEV = float(
            self.parameters[self.parameter_prefix + "SPACING_STDEV"])

        new_location = current_location.copy()
        for d in range(len(new_location)):
            new_location[d] = random.gauss(new_location[d], MC_SPACING_STDEV)
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
        5) Continue performing these improvements MC_NUM_METROPOLIS_STEPS times.
        """
        MC_METROPOLIS_NUM_STEPS = int(
            self.parameters[self.parameter_prefix + "METROPOLIS_NUM_STEPS"])

        # Calculate the current system energy.
        E = self.lcs.getPotentialEnergy()
        print "// E = %s" % E

        # Go over all of the particles, and change the angles for each one.
        index_iterator = self.lcs.getSystemIndexIterator()
        for indices in index_iterator:
            # TODO: Select the initial spin and location.
            # Perform METROPOLIS_NUM_STEPS steps and each time select a new
            # spin orientation from a distribution that should become more and
            # more as the Boltzmann energy distribution.
            for step in xrange(MC_METROPOLIS_NUM_STEPS):
                # Select a new spin and location based on the current.
                current_spin = self.lcs.getProperty(self.lcs.spins, indices)
                current_location = self.lcs.getProperty(self.lcs.locations, indices)
                new_spin = self._getNewRandomSpin(current_spin)
                new_location = self._getNewRandomLocation(current_location)

                # Calculate the coefficient that is proportional to the density
                # of the Boltzmann distibution.
                current_spin_energy = self.lcs.getPotentialEnergyForSpin(indices)
                oldE = E
                old_probability = self.lcs.getCanonicalEnsembleProbability(energy=E)

                self.lcs.setProperty(self.lcs.spins, indices, new_spin)
                self.lcs.setProperty(self.lcs.locations, indices, new_location)
                new_spin_energy = self.lcs.getPotentialEnergyForSpin(indices)
                E += new_spin_energy - current_spin_energy
                new_probability = self.lcs.getCanonicalEnsembleProbability(energy=E)

                #print "// newp = %s, oldp = %s" % (new_probability, old_probability)
                alpha = new_probability / old_probability
                alpha = min(1.0, alpha)
                p = random.random()
                if p >= alpha:
                    self.lcs.setProperty(self.lcs.spins, indices, current_spin)
                    self.lcs.setProperty(self.lcs.locations, indices, current_location)
                    E = oldE
