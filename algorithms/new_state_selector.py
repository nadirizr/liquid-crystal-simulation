class MonteCarloNewStateSelector:
    """
    This interface is used by the MonteCarloAlgorithm to select a new state.
    It simply returns whether a new state is preferable to the current one.
    """
    
    def isNewStateBetter(self, current_lcs, new_lcs):
        """
        Return true if the new LCS is better than the current one.
        For example, if the new LCS has a lower potential energy.
        """
        raise NotImplementedError

class SelectByLowerEnergy(MonteCarloNewStateSelector):

    def isNewStateBetter(self, current_lcs, new_lcs):
        """
        For a cooling algorithm, a lower energy is better.
        """
        current_energy = current_lcs.getPotentialEnergy()
        print "Current Energy: %s" % current_energy
        new_energy = new_lcs.getPotentialEnergy()
        print "New Energy: %s" % new_energy
        return new_energy < current_energy

class SelectByHigherVariance(MonteCarloNewStateSelector):
    
    def isNewStateBetter(self, current_lcs, new_lcs):
        """
        For a heating algorithm, a higher entropy is better which means a
        higher spin orientation variance.
        """
        current_spin_variance = current_lcs.getSpinOrientationVariance()
        print "Current spin orientation variance: %s" % (current_spin_variance,)
        new_spin_variance = new_lcs.getSpinOrientationVariance()
        print "New spin orientation variance: %s" % (new_spin_variance,)
        return new_spin_variance > current_spin_variance
