import os
import argparse
import json

import conf
from dopplergram import Dopplergram, create_datacube_from_files_in_folder, create_fits_file_from_data_array
   
def set_up_configuration_from_json_conf_file(conf_file_path: str) -> conf.Configuration:
	"""Store the path to conf .json into a Configuration dataclass so it can be achieved from anywhere.

	Args:
		conf_file_path (str): Path to a configuration file; <path_to_folder><filename>.json

	Raises:
		FileNotFoundError: Raised if the configuration .json file does not exist (invalid path)
  
	Returns:
		Configuration: Configuration dataclass containing conf settings from the .json file
	"""
	if not os.path.exists:
		raise FileNotFoundError(f'File "{conf_file_path}" does not exist.')

	with open(conf_file_path, 'r') as file:
		conf_dict = json.load(file)
     
	conf.conf = conf.Configuration(**conf_dict)
 
	return conf.conf
 

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
    
	conf_file_path_help = "Enter a path leading to the configuration .json file. Type: str."
	parser.add_argument('-conf-path', type = str, default = None, required=False, help = conf_file_path_help)
	
	args = parser.parse_args()
	conf_file_path = args.conf_path
 
	if conf_file_path is None:
		conf_file_path = "./datacube_maker/conf.json"

	config = set_up_configuration_from_json_conf_file(conf_file_path)

	if config.test_mode:
		file = config.file_path

		dg = Dopplergram(origin=config.origin, shape=config.shape, time_step=config.time_step, scale=config.scale, r_sun=config.r_sun, 
                   artificial_lon_velocity=config.artificial_lon_velocity, test_mode=config.test_mode, file_path=file)
		data = dg.get_postel_projected_data()
	else:
		datacube_array = create_datacube_from_files_in_folder(config.origin, config.shape, config.scale, config.r_sun, 
							config.artificial_lon_velocity, config.test_mode, config.folder_path, config.time_step)

		# TODO: There should be a default name, e.g. hmi.v_45s_2022.11.01_TAI depending on what set of dopplergrams we calculated with
		create_fits_file_from_data_array(datacube_array, config.origin, config.scale, config.time_step, config.r_sun, 
                                   config.output_dir, config.filename) 
