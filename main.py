from dopplergram import Dopplergram, create_datacube_from_files_in_folder, create_fits_file_from_data_array
import numpy as np
import datetime
import yaml

def read_yaml(file_path):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)

if __name__ == "__main__":

	conf = read_yaml("conf.yml")

	data_conf = conf["data_conf"]
	postel_conf = conf["postel_conf"]
	output_conf = conf["output_conf"]

	file = data_conf["path"]
	folder_path = data_conf["folder_path"]

	origin = postel_conf["origin"]
	shape = postel_conf["shape"]
	time_step = postel_conf["time_step"]
	scale = postel_conf["scale"]
	make_plot = postel_conf["make_plot"]
	r_sun = postel_conf["r_sun"]
	artificial_lon_velocity = postel_conf["artificial_lon_velocity"]

	save_file = output_conf["save_file"]
	output_dir = output_conf["output_dir"]
	filename = output_conf["filename"]

	# dg = Dopplergram(file, time_delta_relative_to_base=45*900)
	# data = dg.get_postel_projected_data(origin=origin, shape=shape, scale=scale, r_sun=r_sun, artificial_lon_velocity=artificial_lon_velocity, make_plot=make_plot)
	
	start = datetime.datetime.now()
	datacube_array = create_datacube_from_files_in_folder(folder_path=folder_path)
	print("TOTAL RUNTIME ", datetime.datetime.now() - start)
	
	if save_file:
		create_fits_file_from_data_array(datacube_array, output_dir, filename)