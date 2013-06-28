from lc import *
from lj_potential import *

##################################################################
#                    System Parameters                           #
##################################################################

# These are the system dimensions.
DIMENSIONS = [2, 2]

# Initial temperature in [K].
INITIAL_TEMPERATURE = 298
# Final temperature to cool the system to.
FINAL_TEMPERATURE = 100
# Change of temperature in each cooling step in [K].
TEMPERATURE_DELTA = 10

##################################################################
#                         Main                                   #
##################################################################

def main():
    print "*"*70
    print "*"*70
    print ("Starting the Simulation with T=%s[K] and N=%s, M=%s" %
           (INITIAL_TEMPERATURE, DIMENSIONS[0], DIMENSIONS[1]))
    print "*"*70
    print "*"*70
    system = LiquidCrystalSystem(
            temperature=INITIAL_TEMPERATURE,
            potential=LenardJonesPotential(sigma0=(10**(-16))),
            dimensions=DIMENSIONS)
    system.performMonteCarloCooling(
            final_tempareture=FINAL_TEMPERATURE,
            temperature_delta=TEMPERATURE_DELTA)

if __name__ == "__main__":
    main()
