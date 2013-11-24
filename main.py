import glob
import os
import shutil
import sys
import time

from lc import LiquidCrystalSystem
from lc_state_manager import LiquidCrystalSystemStateManager
from algorithms.monte_carlo_algorithm import MonteCarloAlgorithm
from algorithms.new_state_selector import *

def printUsage():
    print "Usage: ./run.sh <model | previous run> [PARAMETER OVERRIDES] [PROFILE=True]"
    print
    print "Command line arguments:"
    print "  model        - The name of a model in the models directory (without the .py suffix)"
    print "  OR"
    print "  previous run - The name of a previous run or part of it."
    print "                 If there is a directory with this name in the runs directory that is"
    print "                 not complete, it will ask if you would like to resume it."
    print "                 If there is more than one directory that matches the argument, the "
    print "                 latest one that isn't complete is taken."
    print
    print "Parameter overrides:"
    print "  Any parameter from a model file can be overriden at the command line."
    print "  For example:"
    print "    ./runs.sh fixed INITIAL_TEMPERATURE=10.0"
    print "    This will run with the fixed model, but override the initial temperature."
    print
    print "  PROFILE=True will specifically activate the profiler and generate a profile.out "
    print "  file that can be used with the cProfile module."
    print
    print "-h or --help will display this usage."

def parseCommandLineArgs(args):
    """
    Parses the command line arguments, and handles all value overrides, loading
    of the correct parameters file, returning the parameters dictionary.
    """
    parameters = {}
    args = args[1:]

    # If we have '-h' or '--help', display usage and exit.
    if "-h" in args or "--help" in args:
        raise RuntimeError()

    # Treat the first parameter as a model or previous run.
    model = "default"
    if len(args) > 0:
        model = args[0]

    # Check if there is an incomplete run with this name, and if so load it.
    previous_run_parameters = loadPreviousRun(model)
    if previous_run_parameters:
        return previous_run_parameters

    # If this was not a previous run, or the user chose not to continue with it,
    # treat it as a model.
    print "Loading configuration: %s" % model
    parameters = readParametersFromFile(model)
    parameters["MODEL"] = model

    # Treat all subsequent parameters as possible overrides of parameters.
    parameters["PROFILE"] = False
    for arg in args[1:]:
        try:
            exec arg in parameters
        except:
            raise RuntimeError("Invalid Parameter: '%s'" % arg)

    return parameters

def loadPreviousRun(previous_run_pattern):
    """
    Attempts to load a previous run, the latest one that is not complete with
    the given run pattern.
    """
    # Get all previous runs from the runs directory with the given pattern.
    previous_runs = glob.glob("runs/*%s*" % previous_run_pattern)
    if not previous_runs:
        return None

    # Go to the latest one, and check if it's complete.
    previous_runs.sort(reverse=True)
    for latest_run in previous_runs:
        # Find the model file inside the run, and if we can't skip this run.
        model_files = glob.glob("%s/*.py" % latest_run)
        if not model_files:
            continue
        model_file = model_files[0]
        model = os.path.basename(model_file)[:-3]
        run_parameters = readParametersFromFile(model)

        # Set basic parameters.
        run_parameters["RUN_DIR"] = latest_run
        run_parameters["PROFILE"] = False
        run_parameters["MODEL"] = model

        # Check if we have the final state indicating completion, and if it is
        # a completed run skip it.
        lc_state_manager = LiquidCrystalSystemStateManager(run_parameters)
        if "final" in lc_state_manager.getStateNames():
            continue

        # Ask the user if he wishes to continue this run.
        print "Previous run found: '%s'" % latest_run
        user_reply = raw_input("Do you wish to continue this run? [Y/N]: ")
        user_reply = user_reply.lower()
        if user_reply == "y" or user_reply == "yes":
            print "Previous run will be continued."
            print
            return run_parameters
        else:
            print "A new run will commence now."
            print
            return None

    return None

def readParametersFromFile(model):
    """
    Reads the parameter file for the given model.
    """
    filename = "models/%s.py" % model
    parameters = {}
    exec file(filename, "r") in parameters
    return parameters

def main(parameters):
    """
    Gathers all parameters and performs the actual run.
    """
    DIMENSIONS = parameters["DIMENSIONS"]
    INITIAL_TEMPERATURE = float(parameters["INITIAL_TEMPERATURE"])
    USE_MC_HEATER = bool(parameters.get("USE_MC_HEATER", True))
    MC_HEATER_STATE_SELECTOR = parameters.get("MC_HEATER_STATE_SELECTOR",
                                              SelectAlwaysNewer)
    USE_MC_COOLER = bool(parameters.get("USE_MC_COOLER", True))
    MC_COOLER_STATE_SELECTOR = parameters.get("MC_COOLER_STATE_SELECTOR",
                                              SelectAlwaysNewer)
    INITIAL_STATE = parameters.get("INITIAL_STATE", None)

    # Set the run dir under which all other dirs are created, or if this is a
    # continued run then use the previous dir.
    if "RUN_DIR" not in parameters:
        # Create the run directory itself.
        current_time = time.gmtime()
        parameters["RUN_DIR"] = "runs/%04d%02d%02d_%02d%02d%02d_%s" % (
                current_time.tm_year, current_time.tm_mon, current_time.tm_mday,
                current_time.tm_hour, current_time.tm_min, current_time.tm_sec,
                parameters["MODEL"])
        os.makedirs(parameters["RUN_DIR"])

        # Copy the model file to the run dir.
        shutil.copy("models/%s.py" % (parameters["MODEL"],),
                                      parameters["RUN_DIR"])

    # Set up the state manager.
    lcs_manager = LiquidCrystalSystemStateManager(parameters)

    # Set up the initial state.
    if INITIAL_STATE:
        lcs = lcs_manager.importState("initial", INITIAL_STATE)
        INITIAL_TEMPERATURE = lcs.getTemperature()
        DIMENSIONS = lcs.dimensions[:]
        print "Loaded initial state: %s" % INITIAL_STATE
    else:
        lcs = LiquidCrystalSystem(parameters, INITIAL_TEMPERATURE)

    print "*"*70
    print "*"*70
    print ("Starting the Simulation with T*=%s and DIMENSIONS=%s" %
           (INITIAL_TEMPERATURE, DIMENSIONS))
    print "*"*70
    print "*"*70
    lcs_manager.saveState("initial", lcs)
    lcs_manager.saveState("current", lcs)

    # Heat up the LCS.
    if USE_MC_HEATER:
        mch = MonteCarloAlgorithm(lcs, lcs_manager, MC_HEATER_STATE_SELECTOR(),
                                  parameters, parameter_prefix="MC_HEATER_")
        print "BEFORE HEATING: lcs.getTemperature() = %s" % lcs.getTemperature()
        mch.run()
        lcs = mch.getLCS()
        print "AFTER HEATING: lcs.getTemperature() = %s" % lcs.getTemperature()

        # Save the heated up state.
        lcs_manager.saveState("heated", lcs)
        lcs_manager.saveState("current", lcs)

    # Cool down the LCS.
    if USE_MC_COOLER:
        mcc = MonteCarloAlgorithm(lcs, lcs_manager, MC_COOLER_STATE_SELECTOR(),
                                  parameters, parameter_prefix="MC_COOLER_")
        print "BEFORE COOLING: lcs.getTemperature() = %s" % lcs.getTemperature()
        mcc.run()
        lcs = mcc.getLCS()
        print "AFTER COOLING: lcs.getTemperature() = %s" % lcs.getTemperature()

        # Save the cooled down state.
        lcs_manager.saveState("cooled", lcs)
        lcs_manager.saveState("current", lcs)
    
    lcs_manager.saveState("final", lcs)

if __name__ == "__main__":
    try:
        parameters = parseCommandLineArgs(sys.argv)
    except RuntimeError, e:
        print e
        print
        printUsage()
        sys.exit(1)

    if parameters["PROFILE"]:
        import cProfile
        cProfile.run("main(parameters)", "profile.out")
    else:
        main(parameters)
