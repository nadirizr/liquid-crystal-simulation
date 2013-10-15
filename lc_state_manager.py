import glob
import os
import pickle
import re

from lc import LiquidCrystalSystem

class LiquidCrystalSystemStateManager:
    """
    This class manages a repository of states of LiquidCrystalSystems, and can
    save a new one into the repository under an identifier, and load one from
    it.
    The states stored in the manager are persistent and can be loaded and saved
    in different runs.
    """
    def __init__(self, parameters):
        LCS_REPOSITORY_LOCATION = str(parameters["LCS_REPOSITORY_LOCATION"])
        LCS_REPOSITORY_SUFFIX = str(parameters["LCS_REPOSITORY_SUFFIX"])

        self.parameters = parameters

        self.repository_path = LCS_REPOSITORY_LOCATION
        if not os.path.isdir(self.repository_path):
            os.makedirs(self.repository_path)
        state_paths = glob.glob(os.path.join(self.repository_path,
                                             "*.%s" % LCS_REPOSITORY_SUFFIX))
        self.state_repository = {}
        for state_path in state_paths:
            s = re.search(r"^.*\/(.*)\.%s" % LCS_REPOSITORY_SUFFIX, state_path)
            if s and s.groups():
                state_name = s.groups()[0]
                self.state_repository[state_name] = state_path

    def getStateNames(self):
        """
        Returns all of the state names currently held in the repository.
        """
        return self.state_repository.keys()

    def loadState(self, state_name):
        """
        Loads the state with the given name and returns a LiquidCrystalSystem
        object loaded with it.
        If the given state name is not in the repository, None is returned.
        """
        if state_name not in self.state_repository:
            return None

        state_path = self.state_repository[state_name]
        state_data = pickle.load(file(state_path, "r"))

        temperature = state_data["temperature"]
        spins = state_data["spins"]
        locations = state_data["locations"]

        return LiquidCrystalSystem(parameters=self.parameters,
                                   initial_temperature=temperature,
                                   initial_spins=spins,
                                   initial_locations=locations)

    def saveState(self, state_name, lcs):
        """
        Saves the state of the given liquid crystal system under the state name.
        This state can be loaded later with loadState under the saved name.
        If the given state name already exists, it will be overriden.
        """
        LCS_REPOSITORY_SUFFIX = str(self.parameters["LCS_REPOSITORY_SUFFIX"])

        state_data = {
            "temperature": lcs.temperature,
            "spins": lcs.spins,
            "locations": lcs.locations,
        }

        state_path = os.path.join(self.repository_path,
                                  "%s.%s" % (state_name, LCS_REPOSITORY_SUFFIX))
        self.state_repository[state_name] = state_path

        pickle.dump(state_data, file(state_path, "w"))
