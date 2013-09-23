import sys

from lc import LiquidCrystalSystem

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
    print "*"*70
    print "*"*70
    print ("Starting the Simulation with T=%s[K] and dimensions=%s" %
           (parameters["INITIAL_TEMPERATURE"], parameters["DIMENSIONS"]))
    print "*"*70
    print "*"*70
    system = LiquidCrystalSystem(parameters)
    system.performMonteCarloCooling(parameters)

if __name__ == "__main__":
    main()
