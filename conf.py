# Input data configuration
PATH = "/nfsscratch/chmurnyd/1day/hmi.v_45s.20181129_000000_TAI.2.Dopplergram.fits"
FOLDER_PATH = "/nfsscratch/chmurnyd/1day"

# Configuration of the Postel projection(s)
TEST_MODE = False # if True: creates only one projection and plots it --> used for testing purposes (that all is working as expected, coordinates are reasonable etc.)

ORIGIN = [70., -20.] # base point for Postel projections' origins
SHAPE = [512, 512] # in [px] ... dimension of each projection
TIME_STEP: float = 45.0 # in [seconds] ... time step between two consecutive files
SCALE = [0.12, 0.12] # in [deg/px] ... scaling of the Postel projection
R_SUN: float = 696.0 # in [Mm] ... Sun's radius
ARTIFICIAL_LON_VELOCITY: float = -170.0 # in [m/s] ... origin of each projection will be moved with Sun's rotation and this velocity

# Output data configuration
OUTPUT_DIR = "/nfsscratch/chmurnyd/1day/datacubes"
FILENAME = "new_quadr_surf_corr.fits"

# DRMS conf (TODO: maybe find a better place to store this into, e.g. .yaml file)
RUN_VIA_DRMS = True # if False --> takes files locally
JSOC_EMAIL = "daniel123chmurny@gmail.com"
DOPPL_REQUEST = "hmi.v_45s[2011.01.11_00:00:00_TAI/1d]"
DRMS_FILES_PATH = "/home/daniel/Downloads/drms_fits_files"
DELETE_FILES_WHEN_FINISHED = True # After the datacube is created: True ==> deletes downloaded .fits files (can preserve disk storage)
