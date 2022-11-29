from dopplergram import Dopplergram, create_datacube_from_files_in_folder, create_fits_file_from_data_array
import numpy as np
import datetime
import drms
import os
import shutil

from conf import FOLDER_PATH, TIME_STEP, OUTPUT_DIR, FILENAME, SAVE_FILE, PATH, JSOC_EMAIL, OUT_DIR, DOPPL_REQUEST, RUN_VIA_DRMS

if __name__ == "__main__":

	# dg = Dopplergram(PATH, time_delta_relative_to_base=45*900)
	# data = dg.get_postel_projected_data()

	if RUN_VIA_DRMS:
		# Download data from JSOC
		client = drms.Client(email=JSOC_EMAIL, verbose=True)

		if not os.path.exists(OUT_DIR):
			os.mkdir(OUT_DIR)

		export_request = client.export(DOPPL_REQUEST + '{Dopplergram}') 
		export_request.download(OUT_DIR)
		path_to_fits_files = OUT_DIR
	else:
		path_to_fits_files = FOLDER_PATH

	start = datetime.datetime.now()
	# datacube_array = create_datacube_from_files_in_folder(FOLDER_PATH, TIME_STEP)
	datacube_array = create_datacube_from_files_in_folder(path_to_fits_files, TIME_STEP)
	print("TOTAL RUNTIME ", datetime.datetime.now() - start) 
	
	if SAVE_FILE:
		create_fits_file_from_data_array(datacube_array, OUTPUT_DIR, FILENAME)

	if RUN_VIA_DRMS:
		shutil.rmtree(OUT_DIR) # Delete fits files downloaded from JSOC, equivalent to '$ rm -rs <out_dir>'
