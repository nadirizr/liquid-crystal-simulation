import cProfile
import os
import shutil
import sys
import time

from lc import LiquidCrystalSystem
from lc_state_manager import LiquidCrystalSystemStateManager
from algorithms.monte_carlo_algorithm import MonteCarloAlgorithm
from algorithms.new_state_selector import *

def parseCommandLineArgs(args):
    parameters = {}
    args = args[:]

    parameters["profile"] = False
    if "--profile" in args or "-p" in args:
        parameters["profile"] = True
        try:
            args.remove("--profile")
        except:
            pass
        try:
            args.remove("-p")
        except:
            pass

    parameters["model"] = "default"
    if len(args) > 1:
        parameters["model"] = args[1]

    return parameters

def readParametersFromFile(model):
    filename = "models/%s.py" % model
    print "Loading configuration: %s" % model
    parameters = {}
    exec file(filename, "r") in parameters
    return parameters

def main(args):
    parameters = readParametersFromFile(args["model"])
    DIMENSIONS = parameters["DIMENSIONS"]
    INITIAL_TEMPERATURE = float(parameters["INITIAL_TEMPERATURE"])
    USE_MC_HEATER = bool(parameters["USE_MC_HEATER"])
    MC_HEATER_STATE_SELECTOR = parameters.get("MC_HEATER_STATE_SELECTOR",
                                              SelectByHigherVariance)
    USE_MC_COOLER = bool(parameters["USE_MC_COOLER"])
    MC_COOLER_STATE_SELECTOR = parameters.get("MC_COOLER_STATE_SELECTOR",
                                              SelectByLowerEnergy)
    INITIAL_STATE = parameters.get("INITIAL_STATE", None)

    # Set the run dir under which all other dirs are created.
    current_time = time.gmtime()
    parameters["RUN_DIR"] = "runs/%04d%02d%02d_%02d%02d%02d_%s" % (
            current_time.tm_year, current_time.tm_mon, current_time.tm_mday,
            current_time.tm_hour, current_time.tm_min, current_time.tm_sec,
            args["model"])
    os.makedirs(parameters["RUN_DIR"])

    # Copy the model file to the run dir.
    shutil.copy("models/%s.py" % (args["model"],), parameters["RUN_DIR"])

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
        mch = MonteCarloAlgorithm(lcs, MC_HEATER_STATE_SELECTOR(),
                                  parameters, parameter_prefix="MC_HEATER_")
        print "// @@@@@@@ BEFORE HEATING: lcs.getTemperature() = %s" % lcs.getTemperature()
        mch.run()
        lcs = mch.getLCS()
        print "// @@@@@@@ AFTER HEATING: lcs.getTemperature() = %s" % lcs.getTemperature()

        # Save the heated up state.
        lcs_manager.saveState("heated", lcs)
        lcs_manager.saveState("current", lcs)

    # Cool down the LCS.
    if USE_MC_COOLER:
        mcc = MonteCarloAlgorithm(lcs, MC_COOLER_STATE_SELECTOR(),
                                  parameters, parameter_prefix="MC_COOLER_")
        print "// @@@@@@@ BEFORE COOLING: lcs.getTemperature() = %s" % lcs.getTemperature()
        mcc.run()
        lcs = mcc.getLCS()
        print "// @@@@@@@ AFTER COOLING: lcs.getTemperature() = %s" % lcs.getTemperature()

        # Save the cooled down state.
        lcs_manager.saveState("cooled", lcs)
        lcs_manager.saveState("current", lcs)
    
    lcs_manager.saveState("final", lcs)

if __name__ == "__main__":
    args = parseCommandLineArgs(sys.argv)
    if args["profile"]:
        cProfile.run("main(args)", "profile.out")
    else:
        main(args)
