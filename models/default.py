from potentials.lj_potential import LenardJonesPotential
from potentials.gb_potential import GayBernesPotential
from constants import kB
from util import frange

##################################################################
#                    System Parameters                           #
##################################################################

# These are the system dimensions.
DIMENSIONS = [3, 3]

# The spacing between spin locations (with the same dimensions as DIMENSIONS).
INITIAL_SPACING = [0.8, 0.8]
# The standard deviation of the random spacing around the initial position
# (with the same dimensions as DIMENSIONS).
INITIAL_SPACING_STDEV = [0.0, 0.0]
# The initial spin orientation vector (with the same dimensions as DIMENSIONS).
INITIAL_SPIN_ORIENTATION = [0.0, 1.0]
# The standard diviation of the initial spin orientation vector (with the same
# dimensions as DIMENSIONS).
INITIAL_SPIN_ORIENTATION_STDEV = [0.0, 0.0]

# Initial temperature in [K].
INITIAL_TEMPERATURE = 2.0

# The potential to use.
POTENTIAL = GayBernesPotential

# The potential parameters.
EPSILON_0 = kB
MIU = 1.0
NI = 3.0

KAPPA = 3.0
SIGMA_S = 0.005
SIGMA_E = KAPPA * SIGMA_S

KAPPA_TAG = 5.0
EPSILON_S = 1.0
EPSILON_E = EPSILON_S / KAPPA_TAG

##################################################################
#                Heating Algorithm Properties                    #
##################################################################

# The standard deviation of the gaussian random spacing in the system.
MC_HEATER_SPACING_STDEV = 0.0
# The standard deviation of the gaussian random spin orientation.
MC_HEATER_SPIN_STDEV = 1.0

# Number of Metropolis steps to perform in each cooling steps.
MC_HEATER_METROPOLIS_NUM_STEPS = 1000
# Number of steps in the cooling process to wait if there is no improvement
# before lowering the temperature further.
MC_HEATER_MAX_NON_IMPROVING_STEPS = 50

# The temperatures to use in the Monte Carlo algorithm.
MC_HEATER_TEMPERATURES = [5.0]

##################################################################
#                Cooling Algorithm Properties                    #
##################################################################

# The standard deviation of the gaussian random spacing in the system.
MC_COOLER_SPACING_STDEV = 0.0
# The standard deviation of the gaussian random spin orientation.
MC_COOLER_SPIN_STDEV = 1.0

# Number of Metropolis steps to perform in each cooling steps.
MC_COOLER_METROPOLIS_NUM_STEPS = 1000
# Number of steps in the cooling process to wait if there is no improvement
# before lowering the temperature further.
MC_COOLER_MAX_NON_IMPROVING_STEPS = 3

# The temperatures to use in the Monte Carlo algorithm.
MC_COOLER_TEMPERATURES = frange(5.0, 2.0, -0.1)

##################################################################
#                     General Properties                         #
##################################################################

# Repository location for state files.
LCS_REPOSITORY_LOCATION = "states"
# The suffix to use for state files.
LCS_REPOSITORY_SUFFIX = "dat"

# The path to which to output the AVIZ files.
AVIZ_OUTPUT_PATH = "output"
