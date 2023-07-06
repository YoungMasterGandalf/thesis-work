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

