import datetime
import os
import shutil
import argparse
import json

import conf
from dopplergram import Dopplergram, create_datacube_from_files_in_folder, create_fits_file_from_data_array
from drms_handler import DrmsHandler

def save_list_to_text_file(list_var:list, dir_path, filename):
	
	# Create the file directory if non-existent
	if not os.path.isdir(dir_path):
		os.makedirs(dir_path)

	with open(os.path.join(dir_path, filename), "w") as file:
		for element in list_var:
			file.write(f'{element}\n')
   
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
     
	# conf.conf = conf.Configuration(conf_file_path, **conf_dict)
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

	# Sanity check --> test mode can be run only locally
	if config.test_mode or config.run_via_drms:
		assert config.test_mode != config.run_via_drms, "Test Mode can be used only locally --> TEST_MODE and RUN_VIA_DRMS can't be both set to True"

	if config.test_mode:
		file = config.file_path

		dg = Dopplergram(origin=config.origin, shape=config.shape, time_step=config.time_step, scale=config.scale, r_sun=config.r_sun, 
                   artificial_lon_velocity=config.artificial_lon_velocity, test_mode=config.test_mode, file_path=file)
		data = dg.get_postel_projected_data()
	else:
		start = datetime.datetime.now()
		if config.run_via_drms:

			dh = DrmsHandler(jsoc_email=config.jsoc_email)
			dh.create_new_jsoc_export_request(request=config.doppl_request)
			rec_times_list, missing_rec_times_list = dh.check_for_missing_frames_in_request(time_step=config.time_step)

			rec_times_file_name = f"{config.filename}_rec_times.txt"
			missing_rec_times_file_name = f"{config.filename}_missing_frames_rec_times.txt"
			save_list_to_text_file(rec_times_list, config.output_dir, rec_times_file_name)
			if missing_rec_times_list:
				save_list_to_text_file(missing_rec_times_list, config.output_dir, missing_rec_times_file_name)
				missing_frames_message = '\033[91m These frames are missing:\n \033[0m' + "\n".join(missing_rec_times_list)
				print(missing_frames_message)

			dh.download_fits_files_from_jsoc(files_path=config.drms_files_path)

			datacube_array = create_datacube_from_files_in_folder(config.origin, config.shape, config.scale, config.r_sun, 
							 config.artificial_lon_velocity, config.test_mode, config.drms_files_path, config.time_step)
			if config.delete_files_when_finished:
				shutil.rmtree(config.drms_files_path) # Delete fits files downloaded from JSOC, equivalent to '$ rm -rf <out_dir>'
		else:
			datacube_array = create_datacube_from_files_in_folder(config.origin, config.shape, config.scale, config.r_sun, 
							 config.artificial_lon_velocity, config.test_mode, config.folder_path, config.time_step)
		print("TOTAL RUNTIME ", datetime.datetime.now() - start) 

		# TODO: There should be a default name, e.g. hmi.v_45s_2022.11.01_TAI depending on what set of dopplergrams we calculated with
		create_fits_file_from_data_array(datacube_array, config.origin, config.scale, config.time_step, config.r_sun, 
                                   config.output_dir, config.filename) 
