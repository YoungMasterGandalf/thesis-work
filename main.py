from dopplergram import Dopplergram, create_datacube_iterator_from_files_in_folder, create_fits_file_from_data_array, stack_images
import numpy as np
import datetime
import os

from conf import data_conf, output_conf, postel_conf

file_path = data_conf["path"]
folder_path = data_conf["folder_path"]

save_file = output_conf["save_file"]
output_dir = output_conf["output_dir"]
filename = output_conf["filename"]

if __name__ == "__main__":
	file = file_path

	origin = postel_conf["origin"]
	shape = postel_conf["shape"]
	scale = postel_conf["scale"]
	make_plot = postel_conf["make_plot"]

	t_shape = len(os.listdir(folder_path))

	# dg = Dopplergram(file)
	# data = dg.get_postel_projected_data(origin=origin, shape=shape, scale=scale, make_plot=make_plot)
	
	start = datetime.datetime.now()
	# datacube_array = create_datacube_from_files_in_folder(folder_path)
	datacube_iter = create_datacube_iterator_from_files_in_folder(folder_path)
	print("TOTAL RUNTIME ", datetime.datetime.now() - start)

	datacube_array = stack_images(datacube_iter, (t_shape, shape[0], shape[1]))
	print("DATACUBE ARRAY SHAPE ", datacube_array.shape)
	
	if save_file:
		create_fits_file_from_data_array(datacube_array, output_dir, filename)