from monte_carlo_algorithm import MonteCarloAlgorithm
from util import *

class MonteCarloHeatingAlgorithm(MonteCarloAlgorithm):

    def isNewStateBetter(self, current_state, new_state):
        """
        For a heating algorithm, a higher entropy is better which means a
        higher spin orientation variance.
        """
        current_spin_variance = current_state.getSpinOrientationVariance()
        print "Current spin orientation variance: %s" % (current_spin_variance,)
        new_spin_variance = new_state.getSpinOrientationVariance()
        print "New spin orientation variance: %s" % (new_spin_variance,)
        return new_spin_variance > current_spin_variance
