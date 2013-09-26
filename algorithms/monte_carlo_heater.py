from util import *

class MonteCarloHitterAlgorithm:
    
    def __init__(self, lcs, parameters):
        self.lcs = lcs
        self.parameters = parameters
    
    def run(self):
        """
        Run the Monte Carlo cooling algorithm for the given system, from the
        current system temperature to the given final temperature, in the
        temperature delta decrements that were given.
        """
        AVIZ_OUTPUT_PATH = str(self.parameters["AVIZ_OUTPUT_PATH"])
        MC_MAX_NON_IMPROVING_STEPS = int(self.parameters["MC_MAX_NON_IMPROVING_STEPS"])
        MC_TEMPERATURES = self.parameters["MC_TEMPERATURES"]
        
        print "Running Metropolis heating on the system:"
        print
        self.lcs.print2DSystem()
        round_number = 0
        aviz_file_number = 0        
        self.lcs.outputToAvizFile(
                "%s/lqc%08d.xyz" % (AVIZ_OUTPUT_PATH,
                                    aviz_file_number))
        print ("--------------------(T* = %s)--------------------" %
               str(self.lcs.getTemperature()))
        print "Setting heating temperature: T* = %s" % MC_TEMPERATURES[0]
        self.lcs.setTemperature(MC_TEMPERATURES[0])
    
        # Continue running Metropolis steps until we reach a point where in
        # MC_MAX_NON_IMPROVING_STEPS steps there was no energy improvement.
        best_energy = self.lcs.getPotentialEnergy()
        k = 0
        while k < MC_MAX_NON_IMPROVING_STEPS:
            print "Performing Metropolis step... ",
            current_spins = self.lcs.copyPropertyList(self.lcs.spins)
            current_locations = self.lcs.copyPropertyList(self.lcs.locations)
            self._performMetropolisStep()
            new_energy = self.lcs.getPotentialEnergy()
            print new_energy
            if new_energy > best_energy:
                best_energy = new_energy
                k = 0
                print "Got better energy."
                self.lcs.print2DSystem()
                aviz_file_number += 1
                self.lcs.outputToAvizFile(
                        "%s/lqc%08d.xyz" % (AVIZ_OUTPUT_PATH,
                                            aviz_file_number))
                print
            else:
                #print new_energy,best_energy
                self.lcs.spins = current_spins
                self.lcs.locations = current_locations
                k += 1
                print "Didn't get better energy (k=%s)" % k

        print "End of heating"
        self.lcs.print2DSystem()
        print
        print "-------------------------------------------------"
        print "-------------------------------------------------"
        print

    def _getNewRandomSpin(self, current_spin):
        """
        Returns a new random spin based on the current one, from a gaussian
        distribution.
        """
        MC_SPIN_STDEV = float(self.parameters["MC_SPIN_STDEV"])

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
        MC_SPACING_STDEV = float(self.parameters["MC_SPACING_STDEV"])

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
        5) Continue performing these improvements NUM_METROPOLIS_STEPS times.
        """
        MC_METROPOLIS_NUM_STEPS = int(self.parameters["MC_METROPOLIS_NUM_STEPS"])

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
