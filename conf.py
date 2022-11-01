# Input data configuration
PATH = "./data/test_doppl/hmi.v_45s.20181129_000000_TAI.2.Dopplergram.fits"
FOLDER_PATH = "./data/test_doppl"

# Configuration of the Postel projection(s)
ORIGIN = [250., 30.] # base point for Postel projections' origins
SHAPE = [512, 512] # in [px] ... dimension of each projection
TIME_STEP: float = 45.0 # in [seconds] ... time step between two consecutive files
SCALE = [0.12, 0.12] # in [deg/px] ... scaling of the Postel projection
MAKE_PLOT: bool = True
R_SUN: float = 696.0 # in [Mm] ... Sun's radius
ARTIFICIAL_LON_VELOCITY: float = 10.0 # in [m/s] ... origin of each projection will be moved with Sun's rotation and this velocity

# Output data configuration
SAVE_FILE: bool = False
OUTPUT_DIR = "."
FILENAME = "test_file.fits"