from models.common import *

##################################################################
#                    System Parameters                           #
##################################################################

# These are the system dimensions.
DIMENSIONS = [3, 3]

# Preiodicity and boundary conditions ("P" = Periodic, "F" = Fixed).
BOUNDARY_CONDITIONS = ["P", "F"]

# The spacing between spin locations (with the same dimensions as DIMENSIONS).
INITIAL_SPACING = [1.0, 1.0]
# The standard deviation of the random spacing around the initial position
# (with the same dimensions as DIMENSIONS).
INITIAL_SPACING_STDEV = [0.0, 0.0]
# The initial spin orientation vector (with the same dimensions as DIMENSIONS).
INITIAL_SPIN_ORIENTATION = [0.0, 1.0]
# The standard diviation of the initial spin orientation vector (with the same
# dimensions as DIMENSIONS).
INITIAL_SPIN_ORIENTATION_STDEV = [0.0, 0.0]

# Initial temperature in [K].
INITIAL_TEMPERATURE = 0.01

##################################################################
#                    Potential Parameters                        #
##################################################################

# The potential to use.
POTENTIAL = FixedNearestNeighboursPotential
TWO_SPIN_POTENTIAL = GayBernesPotential

# Nearest neighbours parameters.
NEAREST_NEIGHBOURS_MAX_INDEX_RANGE = 1

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
#                Heating Algorithm Properties                    #
##################################################################

# The standard deviation of the gaussian random spacing in the system.
MC_HEATER_SPACING_STDEV = 0.0
# The maximum radius from the original location where the molecule can be.
MC_HEATER_SPACING_FROM_ORIGINAL_LOCATION_CUTOFF = MC_HEATER_SPACING_STDEV * 5.0
# The standard deviation of the gaussian random spin orientation.
MC_HEATER_SPIN_STDEV = 0.5

# Number of Metropolis steps to perform in each cooling steps.
MC_HEATER_METROPOLIS_NUM_STEPS = 100000
# Number of steps in the cooling process to perform the Metropolis algorithm
# before lowering the temperature further.
MC_HEATER_MAX_STEPS = 3
# Number of steps in the cooling process to wait if there is no improvement
# before lowering the temperature further.
MC_HEATER_MAX_NON_IMPROVING_STEPS = 3

# The temperatures to use in the Monte Carlo algorithm.
MC_HEATER_TEMPERATURES = [3.0]

# The path to which to output the AVIZ files.
MC_HEATER_AVIZ_OUTPUT_PATH = "output/lqs_1_heat"
# The prefix to the names of the states.
MC_HEATER_STATE_PREFIX = "lqs_1_heat"

##################################################################
#                Cooling Algorithm Properties                    #
##################################################################

# The standard deviation of the gaussian random spacing in the system.
MC_COOLER_SPACING_STDEV = 0.0
# The maximum radius from the original location where the molecule can be.
MC_COOLER_SPACING_FROM_ORIGINAL_LOCATION_CUTOFF = MC_COOLER_SPACING_STDEV * 5.0
# The standard deviation of the gaussian random spin orientation.
MC_COOLER_SPIN_STDEV = 0.05

# Number of Metropolis steps to perform in each cooling steps.
MC_COOLER_METROPOLIS_NUM_STEPS = 100000
# Number of steps in the cooling process to perform the Metropolis algorithm
# before lowering the temperature further.
MC_COOLER_MAX_STEPS = 1
# Number of steps in the cooling process to wait if there is no improvement
# before lowering the temperature further.
MC_COOLER_MAX_NON_IMPROVING_STEPS = 3

# The temperatures to use in the Monte Carlo algorithm.
MC_COOLER_TEMPERATURES = frange(3.0, 0.1, -0.1)

# The path to which to output the AVIZ files.
MC_COOLER_AVIZ_OUTPUT_PATH = "output/lqs_2_cool"
# The prefix to the names of the states.
MC_COOLER_STATE_PREFIX = "lqs_2_cool"

##################################################################
#                     General Properties                         #
##################################################################

# Repository location for state files.
LCS_REPOSITORY_LOCATION = "states"
# The suffix to use for state files.
LCS_REPOSITORY_SUFFIX = "dat"
