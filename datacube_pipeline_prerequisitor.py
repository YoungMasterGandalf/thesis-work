import os
import shutil
import json
import numpy as np
import itertools

from typing import Union, Optional

### AUTOMATED PART SETTINGS ###

DRMS_REQUESTS: dict[str, Optional[str]] = {
    "hmi.v_45s[2011.01.11_00:00:00_TAI/1d]{Dopplergram}": None
}
LATITUDES: list[float] = [-20., 20.]
LONGITUDES: list[float] = [70., 100.]
LOWER_VELOCITY_LIMIT: float = -300.
UPPER_VELOCITY_LIMIT: float = 300.
VELOCITY_SAMPLE_COUNT: int = 3
OUTPUT_ROOT_FOLDER: str = "/nfsscratch/chmurnyd/Datacubes"
#OUTPUT_ROOT_FOLDER: str = "/Users/daniel/Downloads/Datacubes"

### AUTOMATED PART SETTINGS END ###


### STATIC CONF SETTINGS ###

TEST_MODE: bool = False
SHAPE: list[int] = [512, 512]
TIME_STEP: float = 45.0
SCALE: list[float] = [0.12, 0.12]
R_SUN: float = 696.0
JSOC_EMAIL: str = "daniel123chmurny@gmail.com"

TRAVEL_TIMES_ROOT_FOLDER: str = "/nfsscratch/chmurnyd/travel-times"
#TRAVEL_TIMES_ROOT_FOLDER: str = "/Users/daniel/Downloads/travel_times"
PARAM_EXAMPLE_CONF_PATH: str = os.path.join(TRAVEL_TIMES_ROOT_FOLDER, "PARAM-EXAMPLE.conf")

### STATIC CONF SETTINGS END ###

REQUESTS_FILE_PATH = "./datacube_pipeline_helper_files/requests_ready_for_download.json"
    
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
    request_output_dir_dict: dict[str, str] = {}

    # for i, request in enumerate(DRMS_REQUESTS):
    for request, data_path in DRMS_REQUESTS.items():
        if data_path is None:
            data_path = os.path.join(OUTPUT_ROOT_FOLDER, request)
            print(f'Creating data directory for request {request}:\n"{data_path}"...')
            os.makedirs(data_path)
            
            request_output_dir_dict[request] = data_path
        
        for j, origin in enumerate(origins):
            for k, velocity in enumerate(velocities):
                print(f'Request {i}: "{request}"')
                print(f'Origin {j}: {origin}')
                print(f'Velocity {k}: {velocity}')
                
                datacube_dir_name = create_datacube_directory_name(request, origin, velocity)
                datacube_dir_path = os.path.join(OUTPUT_ROOT_FOLDER, datacube_dir_name)                
                print(f'Creating datacube directory: "{datacube_dir_path}"...')
                os.makedirs(datacube_dir_path)
                
                drms_temp_path = os.path.join(datacube_dir_path, "drms_temp_files")
                #print(f'Creating drms files directory: "{drms_temp_path}"...')
                #os.makedirs(drms_temp_path)
                
                logs_path = os.path.join(datacube_dir_path, "logs")
                print(f'Creating logs directory: "{logs_path}"...')
                os.makedirs(logs_path)
                logs_path = logs_path.replace("/nfsscratch/chmurnyd/", "") # just a hotfix --> get rid of this ASAP
                
                # travel_times_dir_path = 
                
                with open("datacube_maker/conf.json", "r") as file:
                    conf_dict = json.load(file)
                    
                conf_dict["folder_path"] = data_path
                conf_dict["test_mode"] = TEST_MODE
                conf_dict["origin"] = origin
                conf_dict["shape"] = SHAPE
                conf_dict["time_step"] = TIME_STEP
                conf_dict["scale"] = SCALE
                conf_dict["r_sun"] = R_SUN
                conf_dict["artificial_lon_velocity"] = velocity
                conf_dict["output_dir"] = datacube_dir_path
                conf_dict["filename"] = f'{datacube_dir_name}.fits'
                
                conf_file_path = os.path.join(datacube_dir_path, "conf.json")
                print(f'Storing configuration into "{conf_file_path}"...')
                with open(conf_file_path, "w") as file:
                    json.dump(conf_dict, file, indent=4)
                    
                traveltime_conf_file_name = f'TT_{datacube_dir_name}.conf'
                new_travel_time_conf_path = os.path.join(TRAVEL_TIMES_ROOT_FOLDER, traveltime_conf_file_name)
                print(f'New TT conf file path: {new_travel_time_conf_path}')
                shutil.copyfile(PARAM_EXAMPLE_CONF_PATH, new_travel_time_conf_path)
                
                with open(new_travel_time_conf_path, 'r') as file:
                    conf_file_lines = file.readlines()
                    
                datacube_path = os.path.join(datacube_dir_path, f'{datacube_dir_name}.fits')
                travel_time_outdir = f'TT_{datacube_dir_name}'
                travel_time_outdir_path = os.path.join(TRAVEL_TIMES_ROOT_FOLDER, travel_time_outdir)
                os.makedirs(travel_time_outdir_path)
                    
                is_query_changed = False
                is_outdir_changed = False
                for i, line in enumerate(conf_file_lines):
                    if line.startswith("p.query"):
                        conf_file_lines[i] = f"p.query='{datacube_path}';"
                        is_query_changed = True
                        
                    if line.startswith("p.outdir"):
                        conf_file_lines[i] = f"p.outdir='./{travel_time_outdir}/';"
                        is_outdir_changed = True
                        
                    if is_query_changed and is_outdir_changed:
                        break
                    
                with open(new_travel_time_conf_path, 'w') as file:
                    text = "\n".join(conf_file_lines)
                    file.write(text)
                    
                datacube_maker_input = {
                    "working_dir": os.path.join(os.getcwd(), "datacube_maker"),
                    "log_dir": logs_path,
                    "conf_file": conf_file_path,
                    "TT_conf_file": traveltime_conf_file_name
                }
                
                datacube_maker_inputs.append(datacube_maker_input)
                
    return datacube_maker_inputs, request_output_dir_dict

if __name__ == "__main__":
    if not os.path.exists(OUTPUT_ROOT_FOLDER):
        print(f'Creating root directory "{OUTPUT_ROOT_FOLDER}"...')
        os.makedirs(OUTPUT_ROOT_FOLDER)

    origins = list(itertools.product(LONGITUDES, LATITUDES))
    velocities = np.random.uniform(low=LOWER_VELOCITY_LIMIT, high=UPPER_VELOCITY_LIMIT, size=VELOCITY_SAMPLE_COUNT)
    datacube_maker_inputs, request_output_dir_dict = create_folder_structure(origins, velocities)
    
    with open(REQUESTS_FILE_PATH, "w") as file:
        json.dump(request_output_dir_dict, file, indent=2)
            
    with open("./datacube_pipeline_helper_files/datacube_maker_inputs.json", "w") as file:
        json.dump(datacube_maker_inputs, file, indent=2)
            
            
