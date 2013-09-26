import sys

from lc import LiquidCrystalSystem
from algorithms.monte_carlo_cooler import MonteCarloCoolerAlgorithm
from algorithms.monte_carlo_hitter import MonteCarloHitterAlgorithm

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
    INITIAL_TEMPERATURE = float(parameters["INITIAL_TEMPERATURE"])
    DIMENSIONS = parameters["DIMENSIONS"]

    print "*"*70
    print "*"*70
    print ("Starting the Simulation with T*=%s and dimensions=%s" %
           (INITIAL_TEMPERATURE, DIMENSIONS))
    print "*"*70
    print "*"*70
    lcs = LiquidCrystalSystem(parameters, INITIAL_TEMPERATURE)
#    mc = MonteCarloHitterAlgorithm(lcs, parameters)
#    mc.run()
    mc = MonteCarloCoolerAlgorithm(lcs, parameters)
    mc.run()

if __name__ == "__main__":
    main()
