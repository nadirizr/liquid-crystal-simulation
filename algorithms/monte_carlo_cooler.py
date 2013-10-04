from monte_carlo_algorithm import MonteCarloAlgorithm

class MonteCarloCoolingAlgorithm(MonteCarloAlgorithm):
    
    def __init__(self, lcs, parameters, parameter_prefix="MC_COOLER_"):
        MonteCarloAlgorithm.__init__(self, lcs, parameters, parameter_prefix)

    def isNewStateBetter(self, current_state, new_state):
        """
        For a cooling algorithm, a lower energy is better.
        """
        current_energy = current_state.getPotentialEnergy()
        new_energy = new_state.getPotentialEnergy()
        print "New energy: %s" % new_energy
        return new_energy < current_energy
