from dopplergram import Dopplergram, create_datacube_from_files_in_folder, create_fits_file_from_data_array
import numpy as np
import datetime

from conf import FOLDER_PATH, TIME_STEP, OUTPUT_DIR, FILENAME, SAVE_FILE, PATH

if __name__ == "__main__":

	# dg = Dopplergram(PATH, time_delta_relative_to_base=45*900)
	# data = dg.get_postel_projected_data()
	
	start = datetime.datetime.now()
	datacube_array = create_datacube_from_files_in_folder(FOLDER_PATH, TIME_STEP)
	print("TOTAL RUNTIME ", datetime.datetime.now() - start)
	
	if SAVE_FILE:
		create_fits_file_from_data_array(datacube_array, OUTPUT_DIR, FILENAME)