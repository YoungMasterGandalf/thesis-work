from dopplergram import Dopplergram, create_datacube_from_files_in_folder, create_fits_file_from_data_array
import numpy as np
import datetime
import drms
import os
import shutil

from astropy.io import fits

from conf import FOLDER_PATH, TIME_STEP, OUTPUT_DIR, FILENAME, SAVE_FILE, PATH, JSOC_EMAIL, OUT_DIR, DOPPL_REQUEST, RUN_VIA_DRMS

if __name__ == "__main__":

	if RUN_VIA_DRMS:
		# Download data from JSOC
		client = drms.Client(email=JSOC_EMAIL, verbose=True)

		if not os.path.exists(OUT_DIR):
			os.mkdir(OUT_DIR)

			export_request = client.export(DOPPL_REQUEST + '{Dopplergram}', method="url", protocol="fits") 
			export_request.download(OUT_DIR, 0)
		path_to_fits_files = OUT_DIR
	else:
		path_to_fits_files = FOLDER_PATH

	files = [os.path.join(path_to_fits_files, file) for file in os.listdir(path_to_fits_files) if file.endswith(".fits")]
	file = files[0]
	print("File ", file)

	hdul = fits.open(file)

	print(hdul.info())
	print(hdul[1].header)
	print(hdul[1].data)

	hdul.close()

	# dg = Dopplergram(PATH, time_delta_relative_to_base=45*900)
	dg = Dopplergram(file)
	data = dg.get_postel_projected_data()

	# start = datetime.datetime.now()
	# # datacube_array = create_datacube_from_files_in_folder(FOLDER_PATH, TIME_STEP)
	# datacube_array = create_datacube_from_files_in_folder(path_to_fits_files, TIME_STEP)
	# print("TOTAL RUNTIME ", datetime.datetime.now() - start) 
	
	if SAVE_FILE:
		create_fits_file_from_data_array(datacube_array, OUTPUT_DIR, FILENAME)

	if RUN_VIA_DRMS:
		shutil.rmtree(OUT_DIR) # Delete fits files downloaded from JSOC, equivalent to '$ rm -rs <out_dir>'
