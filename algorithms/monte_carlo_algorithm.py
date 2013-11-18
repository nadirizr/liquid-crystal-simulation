import os
import sys

from lc import LiquidCrystalSystem
from new_state_selector import MonteCarloNewStateSelector
from util import *

class MonteCarloAlgorithm:
    
    def __init__(self, lcs, new_state_selector,
                 parameters, parameter_prefix="MC_"):
        self.lcs = lcs
        self.new_state_selector = new_state_selector
        self.parameters = parameters
        self.parameter_prefix = parameter_prefix

    def isNewStateBetter(self, current_lcs, new_lcs):
        """
        Returns true if the new state is better than the current one.
        This must be implemented by any Monte Carlo Algorithm class.
        """
        return self.new_state_selector.isNewStateBetter(current_lcs, new_lcs)

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
        AVIZ_OUTPUT_PATH = os.path.join(
            str(self.parameters["RUN_DIR"]),
            str(self.parameters[self.parameter_prefix + "AVIZ_OUTPUT_PATH"]))
        MC_TEMPERATURES = list(
            self.parameters[self.parameter_prefix + "TEMPERATURES"])
        MC_MAX_STEPS = int(
            self.parameters[self.parameter_prefix + "MAX_STEPS"])
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
        self.lcs.outputInformationToFile(
                "%sinfo.txt" % (AVIZ_OUTPUT_PATH))
        for temperature in MC_TEMPERATURES + [MC_TEMPERATURES[-1]]:
            round_number += 1
            print ("--------------------(T* = %s)--------------------" %
                   self.lcs.getTemperature())
    
            # Continue running Metropolis steps until we reach a point where in
            # MAX_NON_IMPROVING_STEPS steps there was no energy improvement.
            i = 0
            k = 0
            while k < MC_MAX_NON_IMPROVING_STEPS and i < MC_MAX_STEPS:
                current_lcs = self.lcs.copy()

                print "Performing Metropolis step... "
                originalE = self.lcs.getPotentialEnergy()
                originalEcurrent = current_lcs.getPotentialEnergy()
                assert originalE == originalEcurrent
                self._performMetropolisStep()
                originalEafter = current_lcs.getPotentialEnergy()
                assert originalE == originalEafter

                if self.isNewStateBetter(current_lcs, self.lcs):
                    print "--> GOT BETTER STATE!"
                    print
                    self.lcs.print2DSystem()

                    k = 0
                    aviz_file_number += 1
                    self.lcs.outputToAvizFile(
                            "%s%08d.xyz" % (AVIZ_OUTPUT_PATH,
                                            aviz_file_number))
                    self.lcs.outputInformationToFile(
                            "%sinfo.txt" % (AVIZ_OUTPUT_PATH))
                else:
                    print "--> Didn't get better state (k=%s)" % (k+1)
                    print
                    k += 1
                    self.lcs = current_lcs

                i += 1
            
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

    def _getNewRandomLocation(self, current_location, original_location):
        """
        Returns a new random location based on the current one, from a gaussian
        distribution.
        """
        MC_SPACING_STDEV = float(
            self.parameters[self.parameter_prefix + "SPACING_STDEV"])
        MC_SPACING_FROM_ORIGINAL_LOCATION_CUTOFF = float(
            self.parameters[self.parameter_prefix +
                            "SPACING_FROM_ORIGINAL_LOCATION_CUTOFF"])

        # Generate a random new location.
        new_location = current_location.copy()
        distance2 = 0.0
        for d in range(len(new_location)):
            new_location[d] = random.gauss(new_location[d], MC_SPACING_STDEV)
            distance2 += (new_location[d] - original_location[d]) ** 2

        # If it is out of the cutoff sphere of the original location, keep the
        # old location.
        if distance2 > (MC_SPACING_FROM_ORIGINAL_LOCATION_CUTOFF ** 2):
            #print "// $$$ distance too big: distance^2 = %s, spacing^2 = %s" % (distance2, MC_SPACING_FROM_ORIGINAL_LOCATION_CUTOFF ** 2)
            return current_location

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
        print "E = %s" % E

        # Create the progress bar.
        num_steps = MC_METROPOLIS_NUM_STEPS
        widgets = ['Running Metropolis (%s steps): ' % (num_steps,),
                   progressbar.Percentage(), ' (', progressbar.ETA(), ') ',
                   progressbar.Bar(), ' ', progressbar.FileTransferSpeed()]
        pbar = progressbar.ProgressBar(
                widgets=widgets, maxval=num_steps, term_width=120).start()

        # Go over all of the particles, and change the angles for each one.
        average_alpha = 0.0
        num_calcs = 0
        for step in xrange(MC_METROPOLIS_NUM_STEPS):
            # Perform METROPOLIS_NUM_STEPS steps and each time select a new
            # spin orientation from a distribution that should become more and
            # more as the Boltzmann energy distribution.
            index_iterator = self.lcs.getSystemIndexIterator()
            for (i, indices) in enumerate(index_iterator):
                # Select a new spin and location based on the current.
                current_spin = self.lcs.getSpin(indices)
                current_location = self.lcs.getLocation(indices)
                original_location = self.lcs.getOriginalLocation(indices)
                new_spin = self._getNewRandomSpin(current_spin)
                new_location = self._getNewRandomLocation(current_location,
                                                          original_location)

                # Calculate the coefficient that is proportional to the density
                # of the Boltzmann distibution.
                current_spin_energy = self.lcs.getPotentialEnergyForSpin(indices)
                oldE = E

                self.lcs.setProperty(self.lcs.spins, indices, new_spin)
                self.lcs.setProperty(self.lcs.locations, indices, new_location)
                new_spin_energy = self.lcs.getPotentialEnergyForSpin(indices)
                energy_difference = new_spin_energy - current_spin_energy
                E += energy_difference

                # Calculate the transition probability alpha.
                alpha = 1.0
                if energy_difference >= 0.0:
                    alpha = self.lcs.getCanonicalEnsembleProbability(
                            energy=energy_difference)

                # Perform the transition with probability alpha, or go back to
                # the original state with probability 1-alpha.
                p = random.random()
                if p > alpha:
                    self.lcs.setSpin(indices, current_spin)
                    self.lcs.setLocation(indices, current_location)
                    E = oldE

                average_alpha += alpha
                num_calcs += 1
        
            pbar.update(step+1)

        pbar.finish()
        print "// average_alpha = %s" % (average_alpha / num_calcs)
        print "Done."
