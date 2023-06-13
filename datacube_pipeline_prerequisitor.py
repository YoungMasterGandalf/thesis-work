import os
import json
import numpy as np

from typing import Union

### AUTOMATED PART SETTINGS ###

DRMS_REQUESTS: list[str] = [
    "hmi.v_45s[2011.02.13_00:00:00_TAI/1h]{Dopplergram}",
    # "hmi.v_45s[2011.04.22_00:00:00_TAI/1h]{Dopplergram}",
    # "hmi.v_45s[2011.07.05_00:00:00_TAI/1h]{Dopplergram}"
]
LATITUDES: list[float] = [-20., 0., 20.]
LONGITUDES: list[float] = [70., 100., 120.]
LOWER_VELOCITY_LIMIT: float = -300.
UPPER_VELOCITY_LIMIT: float = 300.
VELOCITY_SAMPLE_COUNT: int = 5
# OUTPUT_ROOT_FOLDER: str = "/nfsscratch/chmurnyd/Datacubes"
OUTPUT_ROOT_FOLDER: str = "/Users/daniel/Downloads/Datacubes"

### AUTOMATED PART SETTINGS END ###


### STATIC CONF SETTINGS ###

TEST_MODE: bool = False
SHAPE: list[int] = [512, 512]
TIME_STEP: float = 45.0
SCALE: list[float] = [0.12, 0.12]
R_SUN: float = 696.0
RUN_VIA_DRMS: bool = True
JSOC_EMAIL: str = "daniel123chmurny@gmail.com"
DELETE_FILES_WHEN_FINISHED: bool = True

### STATIC CONF SETTINGS END ###


# Disabled - will be moved to runner file
# TODO Daniel: implement runner file, then delete
"""
def run_datacube_creation_query(working_dir:str, log_dir:str, conf_file_path:str):
    command = f'qsub -v WD={working_dir},LD={log_dir},CONFFILE={conf_file_path} drms_datacube.pbs'
    
    os.system(command)
"""
    
def get_plus_minus_value_string_from_value(value: Union[int, float], round_value:bool=True) -> str:
    """Converts a numerical value to string representation with it's sign represented as a word.

    Args:
        value (Union[int, float]): A numerical value to be parsed to string.
        round_value (bool, optional): If true a value is round to an integer. Defaults to True.

    Returns:
        str: A string representation of the initial value.
        
    Example 1:
        value = -13.8
        round_value = True
        
        returns: "minus_14"
        
    Example 2:
        value = 4.7
        round_value = False
        
        returns: "plus_4.7"
    """    
    if round_value:
        value = round(value)
        
    sign_string = "plus" if value >= 0 else "minus"
    
    value_string = f'{sign_string}_{str(abs(value))}'
    
    return value_string

def create_request_name_from_request_string(request:str) -> str:
    tai_index = request.index("_TAI")
    req_name = request[:tai_index]
    req_name = req_name.replace("[", "_")
    req_name = req_name.replace(":", ".")
    
    return req_name

def create_datacube_directory_name(request:str, origin:list[float], velocity:float):
    req_name = create_request_name_from_request_string(request)
    lon_string = f'lon_{get_plus_minus_value_string_from_value(origin[0])}'
    lat_string = f'lat_{get_plus_minus_value_string_from_value(origin[1])}'
    velocity_string = f'vel_{get_plus_minus_value_string_from_value(velocity)}'
    
    datacube_dir_name = f'{req_name}_{lon_string}_{lat_string}_{velocity_string}'
    
    return datacube_dir_name

def create_folder_structure(origins:list[list[float]], velocities:list[float]):
    datacube_maker_inputs: list[dict] = []

    for i, request in enumerate(DRMS_REQUESTS):
        for j, origin in enumerate(origins):
            for k, velocity in enumerate(velocities):
                print(f'Request {i}: "{request}"')
                print(f'Origin {j}: {origin}')
                print(f'Velocity {k}: {velocity}')
                
                datacube_dir_name = create_datacube_directory_name(request, origin, velocity)
                datacube_dir_path = os.path.join(OUTPUT_ROOT_FOLDER, datacube_dir_name)

                drms_temp_path = os.path.join(datacube_dir_path, "drms_temp_files")
                logs_path = os.path.join(datacube_dir_path, "logs")
                
                print(f'Creating datacube directory: "{datacube_dir_path}"...')
                os.makedirs(datacube_dir_path)
                
                print(f'Creating drms files directory: "{drms_temp_path}"...')
                os.makedirs(drms_temp_path)
                
                print(f'Creating logs directory: "{logs_path}"...')
                os.makedirs(logs_path)
                
                with open("datacube_maker/conf.json", "r") as file:
                    conf_dict = json.load(file)
                    
                conf_dict["test_mode"] = TEST_MODE
                conf_dict["origin"] = origin
                conf_dict["shape"] = SHAPE
                conf_dict["time_step"] = TIME_STEP
                conf_dict["scale"] = SCALE
                conf_dict["r_sun"] = R_SUN
                conf_dict["artificial_lon_velocity"] = velocity
                conf_dict["output_dir"] = datacube_dir_path
                conf_dict["filename"] = f'{datacube_dir_name}.fits'
                conf_dict["run_via_drms"] = RUN_VIA_DRMS
                conf_dict["doppl_request"] = request
                conf_dict["drms_files_path"] = drms_temp_path
                conf_dict["delete_files_when_finished"] = DELETE_FILES_WHEN_FINISHED
                
                conf_file_path = os.path.join(datacube_dir_path, "conf.json")
                print(f'Storing configuration into "{conf_file_path}"...')
                with open(conf_file_path, "w") as file:
                    json.dump(conf_dict, file, indent=4)
                    
                datacube_maker_input = {
                    "working_dir": os.getcwd(),
                    "log_dir": logs_path,
                    "conf_file": conf_file_path
                }
                
                datacube_maker_inputs.append(datacube_maker_input)
                
    return datacube_maker_inputs

if __name__ == "__main__":
    if not os.path.exists(OUTPUT_ROOT_FOLDER):
        print(f'Creating root directory "{OUTPUT_ROOT_FOLDER}"...')
        os.makedirs(OUTPUT_ROOT_FOLDER)

    origins = list(zip(LONGITUDES, LATITUDES))
    velocities = np.random.uniform(low=LOWER_VELOCITY_LIMIT, high=UPPER_VELOCITY_LIMIT, size=VELOCITY_SAMPLE_COUNT)
    datacube_maker_inputs = create_folder_structure(origins, velocities)
            
    with open("datacube_maker_inputs.json", "w") as file:
        json.dump(datacube_maker_inputs, file, indent=4)
            
            
