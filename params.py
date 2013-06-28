from lj_potential import LenardJonesPotential
from gb_potential import GayBernesPotential

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

# The potential to use.
POTENTIAL = LenardJonesPotential(
    epsilon0=(10**(-16)))

##################################################################
#                   Algorithm Properties                         #
##################################################################

# The spacing between spin locations.
SPACING = 1.0
# The standard deviation of the gaussian random spacing in the system.
SPACING_STDEV = 0.1
# The standard deviation of the gaussian random spin orientation.
SPIN_STDEV = 1.0

# Number of Metropolis steps to perform in each cooling steps.
METROPOLIS_NUM_STEPS = 1000
# Number of steps in the cooling process to wait if there is no improvement
# before lowering the temperature further.
MAX_NON_IMPROVING_STEPS = 3

AVIZ_OUTPUT_PATH = "output"
