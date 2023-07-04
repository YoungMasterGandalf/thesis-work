"""
Auxiliary configuration file, do not change the configuration manually here! 
All configuration changes should be done in conf.json only!

This file serves mainly as a storage for comments of various parameters (might be deprecated in the future).
"""

import json
from dataclasses import dataclass
from typing import Union

# TODO Daniel: Think about using dataclasses.make_dataclass to automatically create the dataclass from conf dict and just store it's instance here
@dataclass
class Configuration:
   file_path: Union[str, None] = None
   folder_path: Union[str, None] = None
   test_mode: bool = False
   origin: Union[list[float], None] = None
   shape: Union[list[int], None] = None
   time_step: Union[float, None] = None
   scale: Union[list[float], None] = None
   r_sun: Union[float, None] = None
   artificial_lon_velocity: Union[float, None] = None
   output_dir: Union[str, None] = None
   filename: Union[str, None] = None
   run_via_drms: bool = True
   jsoc_email: str = "daniel123chmurny@gmail.com"
   doppl_request: str = "hmi.v_45s[2011.01.11_00:00:00_TAI/1h]{Dopplergram}"
   drms_files_path: Union[str, None] = None
   delete_files_when_finished: bool = True
   
   # path: Union[str, None] = None
   # input_data_conf: Union[dict, None] = None
   # postel_projection_conf: Union[dict, None] = None
   # output_data_conf: Union[dict, None] = None
   # drms_conf: Union[dict, None] = None
   
# Default blank dataclass - to be filled from .json conf file
conf = Configuration()

# Disabled for now
# TODO Daniel: Decide if it's still useful. If not --> delete.
"""
with open("conf.json", 'r') as file:
   conf = json.load(file)
   
input_data_conf = conf["input_data_conf"]
postel_projection_conf = conf["postel_projection_conf"]
output_data_conf = conf["output_data_conf"]
drms_conf = conf["drms_conf"]

# Input data configuration
PATH = input_data_conf["file_path"]
FOLDER_PATH = input_data_conf["folder_path"]

# Configuration of the Postel projection(s)
TEST_MODE = postel_projection_conf["test_mode"] # if True: creates only one projection and plots it --> used for testing purposes (that all is working as expected, coordinates are reasonable etc.)

ORIGIN = postel_projection_conf["origin"] # base point for Postel projections' origins
SHAPE = postel_projection_conf["shape"] # in [px] ... dimension of each projection
TIME_STEP: float = postel_projection_conf["time_step"] # in [seconds] ... time step between two consecutive files
SCALE = postel_projection_conf["scale"] # in [deg/px] ... scaling of the Postel projection
R_SUN: float = postel_projection_conf["r_sun"] # in [Mm] ... Sun's radius
ARTIFICIAL_LON_VELOCITY: float = postel_projection_conf["artificial_lon_velocity"] # in [m/s] ... origin of each projection will be moved with Sun's rotation and this velocity

# Output data configuration
OUTPUT_DIR = output_data_conf["output_dir"]
FILENAME = output_data_conf["filename"]

# DRMS conf 
RUN_VIA_DRMS = drms_conf["run_via_drms"] # if False --> takes files locally
JSOC_EMAIL = drms_conf["jsoc_email"]
DOPPL_REQUEST = drms_conf["doppl_request"]
DRMS_FILES_PATH = drms_conf["drms_files_path"]
DELETE_FILES_WHEN_FINISHED = drms_conf["delete_files_when_finished"] # After the datacube is created: True ==> deletes downloaded .fits files (can preserve disk storage)
"""

