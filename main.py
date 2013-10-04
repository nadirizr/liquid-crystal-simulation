import sys

from lc import LiquidCrystalSystem
from algorithms.monte_carlo_cooler import MonteCarloCoolingAlgorithm
from algorithms.monte_carlo_heater import MonteCarloHeatingAlgorithm

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
    mc = MonteCarloHeatingAlgorithm(lcs, parameters)
    mc.run()
    mc = MonteCarloCoolingAlgorithm(lcs, parameters)
    mc.run()

if __name__ == "__main__":
    main()
