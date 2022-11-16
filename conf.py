# Input data configuration
PATH = "/nfsscratch/chmurnyd/1day/hmi.v_45s.20181129_000000_TAI.2.Dopplergram.fits"
FOLDER_PATH = "/nfsscratch/chmurnyd/1day"

# Configuration of the Postel projection(s)
ORIGIN = [143., -20.] # base point for Postel projections' origins
SHAPE = [512, 512] # in [px] ... dimension of each projection
TIME_STEP: float = 45.0 # in [seconds] ... time step between two consecutive files
SCALE = [0.12, 0.12] # in [deg/px] ... scaling of the Postel projection
MAKE_PLOT: bool = False
R_SUN: float = 696.0 # in [Mm] ... Sun's radius
ARTIFICIAL_LON_VELOCITY: float = -170.0 # in [m/s] ... origin of each projection will be moved with Sun's rotation and this velocity

# Output data configuration
SAVE_FILE: bool = True
OUTPUT_DIR = "/nfsscratch/chmurnyd/1day/datacubes"
FILENAME = "new_quadr_surf_corr.fits"
