"""
Auxiliary configuration file, do not change the configuration manually here! 
All configuration changes should be done in conf.json only!

This file serves mainly as a storage for comments of various parameters (might be deprecated in the future).
"""

import json

with open("conf.json", 'r') as file:
   conf = json.load(file)

# Input data configuration
PATH = conf["path"]
FOLDER_PATH = conf["file_path"]

# Configuration of the Postel projection(s)
TEST_MODE = conf["test_mode"] # if True: creates only one projection and plots it --> used for testing purposes (that all is working as expected, coordinates are reasonable etc.)

ORIGIN = conf["origin"] # base point for Postel projections' origins
SHAPE = conf["shape"] # in [px] ... dimension of each projection
TIME_STEP: float = conf["time_step"] # in [seconds] ... time step between two consecutive files
SCALE = conf["scale"] # in [deg/px] ... scaling of the Postel projection
R_SUN: float = conf["r_sun"] # in [Mm] ... Sun's radius
ARTIFICIAL_LON_VELOCITY: float = conf["artificial_lon_velocity"] # in [m/s] ... origin of each projection will be moved with Sun's rotation and this velocity

# Output data configuration
OUTPUT_DIR = conf["output_dir"]
FILENAME = conf["filename"]

# DRMS conf 
RUN_VIA_DRMS = conf["run_via_drms"] # if False --> takes files locally
JSOC_EMAIL = conf["jsoc_email"]
DOPPL_REQUEST = conf["doppl_request"]
DRMS_FILES_PATH = conf["drms_files_path"]
DELETE_FILES_WHEN_FINISHED = conf["delete_files_when_finished"] # After the datacube is created: True ==> deletes downloaded .fits files (can preserve disk storage)
