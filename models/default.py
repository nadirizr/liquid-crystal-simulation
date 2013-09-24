from potentials.lj_potential import LenardJonesPotential
from potentials.gb_potential import GayBernesPotential
from constants import kB

##################################################################
#                    System Parameters                           #
##################################################################

# These are the system dimensions.
DIMENSIONS = [3, 3]

# Initial temperature in [K].
INITIAL_TEMPERATURE = 5.0
# Final temperature to cool the system to.
FINAL_TEMPERATURE = 2.0
# Change of temperature in each cooling step in [K].
TEMPERATURE_DELTA = 0.1

# The potential to use.
POTENTIAL = GayBernesPotential

# The potential parameters.
EPSILON_0 = kB
MIU = 1.0
NI = 3.0

KAPPA = 3.0
SIGMA_S = 0.5
SIGMA_E = KAPPA * SIGMA_S

KAPPA_TAG = 5.0
EPSILON_S = 1.0
EPSILON_E = EPSILON_S / KAPPA_TAG

##################################################################
#                   Algorithm Properties                         #
##################################################################

# The spacing between spin locations.
SPACING = 1.0
# The standard deviation of the gaussian random spacing in the system.
SPACING_STDEV = 0.0
# The standard deviation of the gaussian random spin orientation.
SPIN_STDEV = 1.0

# Number of Metropolis steps to perform in each cooling steps.
METROPOLIS_NUM_STEPS = 1000
# Number of steps in the cooling process to wait if there is no improvement
# before lowering the temperature further.
MAX_NON_IMPROVING_STEPS = 3

# The path to which to output the AVIZ files.
AVIZ_OUTPUT_PATH = "output"

##################################################################
#                  Repository Properties                         #
##################################################################

LCS_REPOSITORY_LOCATION = "states"
LCS_REPOSITORY_SUFFIX = "dat"
