import sys

from lc import LiquidCrystalSystem
from algorithms.monte_carlo_algorithm import MonteCarloAlgorithm
from algorithms.new_state_selector import *

def readParametersFromFile(args):
    model = "default"
    if len(args) > 1:
        model = args[1]
    filename = "models/%s.py" % model

    print "Loading configuration: %s" % model
    parameters = {}
    exec file(filename, "r") in parameters
    return parameters

def main():
    parameters = readParametersFromFile(sys.argv)
    DIMENSIONS = parameters["DIMENSIONS"]
    INITIAL_TEMPERATURE = float(parameters["INITIAL_TEMPERATURE"])

    print "*"*70
    print "*"*70
    print ("Starting the Simulation with T*=%s and DIMENSIONS=%s" %
           (INITIAL_TEMPERATURE, DIMENSIONS))
    print "*"*70
    print "*"*70
    lcs = LiquidCrystalSystem(parameters, INITIAL_TEMPERATURE)
    print "// lcs.getAverageSpinOrientation() = %s" % lcs.getAverageSpinOrientation()
    print "// lcs.getSpinOrientationVariance() = %s" % lcs.getSpinOrientationVariance()
    mch = MonteCarloAlgorithm(lcs, SelectByHigherVariance(),
                              parameters, parameter_prefix="MC_HEATER_")
    print "// @@@@@@@ BEFORE HEATING: lcs.getTemperature() = %s" % lcs.getTemperature()
    mch.run()
    lcs = mch.getLCS()
    print "// @@@@@@@ AFTER HEATING: lcs.getTemperature() = %s" % lcs.getTemperature()
    mcc = MonteCarloAlgorithm(lcs, SelectByLowerEnergy(),
                              parameters, parameter_prefix="MC_COOLER_")
    print "// @@@@@@@ BEFORE COOLING: lcs.getTemperature() = %s" % lcs.getTemperature()
    mcc.run()
    lcs = mcc.getLCS()
    print "// @@@@@@@ AFTER COOLING: lcs.getTemperature() = %s" % lcs.getTemperature()

if __name__ == "__main__":
    main()
