from lc import LiquidCrystalSystem
from params import *

def main():
    print "*"*70
    print "*"*70
    print ("Starting the Simulation with T=%s[K] and dimensions=%s" %
           (INITIAL_TEMPERATURE, DIMENSIONS))
    print "*"*70
    print "*"*70
    system = LiquidCrystalSystem(
            temperature=INITIAL_TEMPERATURE,
            potential=POTENTIAL,
            dimensions=DIMENSIONS)
    system.performMonteCarloCooling(
            final_tempareture=FINAL_TEMPERATURE,
            temperature_delta=TEMPERATURE_DELTA)

if __name__ == "__main__":
    main()
