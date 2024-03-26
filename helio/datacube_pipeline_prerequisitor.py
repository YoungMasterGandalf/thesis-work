import os
import shutil
import json
import itertools
import random

from datacube_maker.utils import create_request_name_from_request_string, create_datacube_directory_name
# from log import setup_logger TODO: Fix and reintroduce logger

### AUTOMATED PART SETTINGS ###

DRMS_REQUESTS: dict[str, dict] = {
    "hmi.v_45s[2017.03.12_00:00:00_TAI-2017.03.12_06:00:00_TAI]{Dopplergram}": {
        "data_path": "/nfshome/chmurnyd/datacubes-data/datacubes_6h/hmi.v_45s_2017.03.12_00.00.00_6h_data",
        "origin_longitudes": [280.]
    },
    "hmi.v_45s[2017.05.12_00:00:00_TAI-2017.05.12_06:00:00_TAI]{Dopplergram}": {
        "data_path": "/nfshome/chmurnyd/datacubes-data/datacubes_6h/hmi.v_45s_2017.05.12_00.00.00_6h_data",
        "origin_longitudes": [200.]
    },
    "hmi.v_45s[2017.08.13_00:00:00_TAI-2017.08.13_06:00:00_TAI]{Dopplergram}": {
        "data_path": "/nfshome/chmurnyd/datacubes-data/datacubes_6h/hmi.v_45s_2017.08.13_00.00.00_6h_data",
        "origin_longitudes": [40.]
    },
    "hmi.v_45s[2017.10.08_00:00:00_TAI-2017.10.08_06:00:00_TAI]{Dopplergram}": {
        "data_path": "/nfshome/chmurnyd/datacubes-data/datacubes_6h/hmi.v_45s_2017.10.08_00.00.00_6h_data",
        "origin_longitudes": [30.]
    },
    "hmi.v_45s[2017.11.03_00:00:00_TAI-2017.11.03_06:00:00_TAI]{Dopplergram}": {
        "data_path": "/nfshome/chmurnyd/datacubes-data/datacubes_6h/hmi.v_45s_2017.11.03_00.00.00_6h_data",
        "origin_longitudes": [40.]
    },
    "hmi.v_45s[2017.12.01_00:00:00_TAI-2017.12.01_00:00:00_TAI]{Dopplergram}": {
        "data_path": "/nfshome/chmurnyd/datacubes-data/datacubes_6h/hmi.v_45s_2017.12.01_00.00.00_6h_data",
        "origin_longitudes": [40.]
    },
    "hmi.v_45s[2018.03.26_00:00:00_TAI-2018.03.26_06:00:00_TAI]{Dopplergram}": {
        "data_path": "/nfshome/chmurnyd/datacubes-data/datacubes_6h/hmi.v_45s_2018.03.26_00.00.00_6h_data",
        "origin_longitudes": [310.]
    },
    "hmi.v_45s[2019.01.20_00:00:00_TAI-2019.01.20_06:00:00_TAI]{Dopplergram}": {
        "data_path": "/nfshome/chmurnyd/datacubes-data/datacubes_6h/hmi.v_45s_2019.01.20_00.00.00_6h_data",
        "origin_longitudes": [315.]
    },
    "hmi.v_45s[2019.12.19_00:00:00_TAI-2019.12.19_06:00:00_TAI]{Dopplergram}": {
        "data_path": "/nfshome/chmurnyd/datacubes-data/datacubes_6h/hmi.v_45s_2019.12.19_00.00.00_6h_data",
        "origin_longitudes": [70.]
    },
    "hmi.v_45s[2020.05.10_00:00:00_TAI-2020.05.10_06:00:00_TAI]{Dopplergram}": {
        "data_path": "/nfshome/chmurnyd/datacubes-data/datacubes_6h/hmi.v_45s_2020.05.10_00.00.00_6h_data",
        "origin_longitudes": [160.]
    }
}
LATITUDES: list[float] = [0.0]
LOWER_VELOCITY_LIMIT: int = -500
UPPER_VELOCITY_LIMIT: int = 500
VELOCITY_SAMPLE_COUNT: int = 10
OUTPUT_ROOT_FOLDER: str = "/nfshome/chmurnyd/Datacubes"

### AUTOMATED PART SETTINGS END ###


### STATIC CONF SETTINGS ###

TEST_MODE: bool = False
SHAPE: list[int] = [512, 512]
TIME_STEP: float = 45.0
SCALE: list[float] = [0.12, 0.12]
R_SUN: float = 696.0
JSOC_EMAIL: str = "daniel123chmurny@gmail.com"

TRAVEL_TIMES_ROOT_FOLDER: str = "/nfshome/chmurnyd/travel-times"
PARAM_EXAMPLE_CONF_PATH: str = os.path.join(TRAVEL_TIMES_ROOT_FOLDER, "PARAM-EXAMPLE.conf")

### STATIC CONF SETTINGS END ###

REQUESTS_FILE_PATH = "/nfshome/chmurnyd/GitHub/thesis-work/helio/datacube_pipeline_helper_files/requests_ready_for_download.json"

# TODO: Fix and reintroduce logger
# module_logger = setup_logger(__name__)

def create_data_directory_from_request(output_root_folder: str, request: str) -> str:
    """Creates a directory for data from a JSOC request in a specified root folder with a name based on this request query.

    Args:
        output_root_folder (str): Folder (path) in which the data directory will be created.
        request (str): JSOC query string, e.g. "hmi.v_45s[2011.01.11_00:00:00_TAI/1d]{Dopplergram}"

    Returns:
        str: A PATH to the newly created data folder.
    """    
    request_name = create_request_name_from_request_string(request=request)
    data_folder_name = f'{request_name}_data'
    data_path = os.path.join(output_root_folder, data_folder_name)
    
    print(f'Creating data directory for request {request}:\n"{data_path}"...')
    
    os.makedirs(data_path)
    
    return data_path

def create_datacube_directory(output_root_folder: str, request: str, origin: list[float], velocity: float) -> tuple[str, str]:
    """Creates a directory for for a datacube created from data given by JSOC request at given origin point and artificial 
    longitudinal velocity in a specified root folder.

    Args:
        output_root_folder (str): Folder (path) in which the datacube directory will be created.
        request (str): JSOC query string, e.g. "hmi.v_45s[2011.01.11_00:00:00_TAI/1d]{Dopplergram}"
        origin (list[float]): Origin of Postel projections made on the datacube (will be cast to the name)
        velocity (float): Artificial longitudinal velocity added to the Carrington rotation (will be cast to name)

    Returns:
        tuple[str, str]: Datacube directory name and absolute path of this directory
    """    
    datacube_dir_name = create_datacube_directory_name(request, origin, velocity)
    datacube_dir_path = os.path.join(output_root_folder, datacube_dir_name) 
                   
    print(f'Creating datacube directory: "{datacube_dir_path}"...')
    
    os.makedirs(datacube_dir_path)
    
    return datacube_dir_name, datacube_dir_path

def create_datacube_logs_directory(datacube_dir_path: str) -> str:
    logs_path = os.path.join(datacube_dir_path, "logs")
    
    print(f'Creating logs directory: "{logs_path}"...')
    
    os.makedirs(logs_path)
    
    return logs_path

def copy_and_fill_in_conf_json(datacube_dir_path: str, data_path: str, origin: list[float], velocity: float, 
                               datacube_dir_name: str) -> str:
    with open("datacube_maker/conf.json", "r") as file:
        conf_dict = json.load(file)
        
    conf_dict["folder_path"] = data_path
    conf_dict["test_mode"] = False # hard-set to False as test mode is for single frame plotting only
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
        
    return conf_file_path
        
def copy_traveltime_conf_file_to_new_path(travel_times_root_folder: str, traveltime_conf_file_name: str, 
                                          param_example_conf_path: str) -> str:
    new_travel_time_conf_path = os.path.join(travel_times_root_folder, traveltime_conf_file_name)
    
    print(f'New TT conf file path: {new_travel_time_conf_path}')
    
    shutil.copyfile(param_example_conf_path, new_travel_time_conf_path)
    
    return new_travel_time_conf_path

def update_datacube_path_and_traveltime_outdir_in_new_travel_time_conf(new_travel_time_conf_path: str, 
                                                                       datacube_path: str, travel_time_outdir: str):
    with open(new_travel_time_conf_path, 'r') as file:
        conf_file_lines = file.readlines()
        
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

def create_folder_structure(drms_requests: dict[str, dict], velocities:list[float], latitudes: list[float], 
                            output_root_folder: str, travel_times_root_folder: str):
    datacube_maker_inputs: list[dict] = []
    request_output_dir_dict: dict[str, str] = {}

    for request, request_dict in drms_requests.items():
        if "data_path" not in request_dict or "origin_longitudes" not in request_dict:
            raise IndexError(f'"data_path" or "origin_longitudes" key is missing in "{request}" request dictionary.')
        
        data_path = request_dict["data_path"]
        origin_longitudes = request_dict["origin_longitudes"]
        
        if type(origin_longitudes) != list:
            message = f'"origin_longitudes" element in the request dictionary must be of type list[float], not {type(origin_longitudes)}.'
            raise TypeError(message)
        
        if data_path is None:
            data_path = create_data_directory_from_request(output_root_folder=output_root_folder, request=request)
            
            request_output_dir_dict[request] = data_path
            
        origins = list(itertools.product(origin_longitudes, latitudes))
        
        for j, origin in enumerate(origins):
            for k, velocity in enumerate(velocities):
                print(f'Preparing folder structure for Origin {j}: {origin} and Velocity {k}: {velocity}')
                
                datacube_dir_name, datacube_dir_path = create_datacube_directory(output_root_folder=output_root_folder, 
                                                                                 request=request, origin=origin, 
                                                                                 velocity=velocity)
                
                logs_path = create_datacube_logs_directory(datacube_dir_path=datacube_dir_path)
                
                conf_file_path = copy_and_fill_in_conf_json(datacube_dir_path, data_path, origin, velocity, 
                                                            datacube_dir_name)
                    
                traveltime_conf_file_name = f'TT_{datacube_dir_name}.conf'
                new_travel_time_conf_path = copy_traveltime_conf_file_to_new_path(TRAVEL_TIMES_ROOT_FOLDER, 
                                                                                  traveltime_conf_file_name, 
                                                                                  PARAM_EXAMPLE_CONF_PATH)
                    
                datacube_path = os.path.join(datacube_dir_path, f'{datacube_dir_name}.fits')
                travel_time_outdir = f'TT_{datacube_dir_name}'
                travel_time_outdir_path = os.path.join(travel_times_root_folder, travel_time_outdir)
                os.makedirs(travel_time_outdir_path)
                
                travel_time_logs_path = os.path.join(travel_time_outdir_path, "logs")
                os.makedirs(travel_time_logs_path)
                
                update_datacube_path_and_traveltime_outdir_in_new_travel_time_conf(new_travel_time_conf_path, 
                                                                                   datacube_path, travel_time_outdir)
                    
                datacube_maker_input = {
                    "working_dir": os.path.abspath("datacube_maker"),
                    "log_dir": logs_path,
                    "conf_file": conf_file_path,
                    "TT_conf_file": traveltime_conf_file_name,
                    "TT_log_dir": travel_time_logs_path
                }
                
                datacube_maker_inputs.append(datacube_maker_input)
                
    return datacube_maker_inputs, request_output_dir_dict

if __name__ == "__main__":
    if not os.path.exists(OUTPUT_ROOT_FOLDER):
        print(f'Creating root directory "{OUTPUT_ROOT_FOLDER}"...')
        os.makedirs(OUTPUT_ROOT_FOLDER)

    velocities = random.sample(range(LOWER_VELOCITY_LIMIT, UPPER_VELOCITY_LIMIT + 1), VELOCITY_SAMPLE_COUNT)
    # velocities = np.floor(np.linspace(start=LOWER_VELOCITY_LIMIT, stop=UPPER_VELOCITY_LIMIT, num=VELOCITY_SAMPLE_COUNT))
    
    datacube_maker_inputs, request_output_dir_dict = create_folder_structure(DRMS_REQUESTS, velocities, LATITUDES, 
                                                                             OUTPUT_ROOT_FOLDER, TRAVEL_TIMES_ROOT_FOLDER)
    
    with open(REQUESTS_FILE_PATH, "w") as file:
        json.dump(request_output_dir_dict, file, indent=2)
            
    with open("./datacube_pipeline_helper_files/datacube_maker_inputs.json", "w") as file:
        json.dump(datacube_maker_inputs, file, indent=2)
            
            
