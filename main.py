from dopplergram import Dopplergram, create_datacube_from_files_in_folder, create_fits_file_from_data_array
import datetime
import os
import shutil

from drms_handler import DrmsHandler
from conf import (TEST_MODE, FOLDER_PATH, TIME_STEP, OUTPUT_DIR, FILENAME, PATH, JSOC_EMAIL, DRMS_FILES_PATH, DOPPL_REQUEST, RUN_VIA_DRMS, 
					DELETE_FILES_WHEN_FINISHED)

def save_list_to_text_file(list_var:list, dir_path, filename):
	with open(os.path.join(dir_path, filename), "w") as file:
		for element in list_var:
			file.write(f'{element}\n')

if __name__ == "__main__":

	# Sanity check --> test mode can be run only locally
	if TEST_MODE or RUN_VIA_DRMS:
		assert TEST_MODE != RUN_VIA_DRMS, "Test Mode can be used only locally --> TEST_MODE and RUN_VIA_DRMS can't be both set to True"

	if TEST_MODE:
		file = PATH

		dg = Dopplergram(file)
		data = dg.get_postel_projected_data()
	else:
		start = datetime.datetime.now()
		if RUN_VIA_DRMS:

			dh = DrmsHandler(jsoc_email=JSOC_EMAIL)
			rec_times_list, missing_rec_times_list = dh.check_for_missing_frames_in_request(DOPPL_REQUEST, TIME_STEP)

			rec_times_file_name = f"{FILENAME}_rec_times.txt"
			missing_rec_times_file_name = f"{FILENAME}_missing_frames_rec_times.txt"
			save_list_to_text_file(rec_times_list, OUTPUT_DIR, rec_times_file_name)
			if missing_rec_times_list:
				save_list_to_text_file(missing_rec_times_list, OUTPUT_DIR, missing_rec_times_file_name)
				missing_frames_message = '\033[91m These frames are missing:\n \033[0m' + "\n".join(missing_rec_times_list)
				print(missing_frames_message)

			dh.download_fits_files_from_jsoc(DRMS_FILES_PATH, DOPPL_REQUEST)

			datacube_array = create_datacube_from_files_in_folder(DRMS_FILES_PATH, TIME_STEP)
			if DELETE_FILES_WHEN_FINISHED:
				shutil.rmtree(DRMS_FILES_PATH) # Delete fits files downloaded from JSOC, equivalent to '$ rm -rs <out_dir>'
		else:
			datacube_array = create_datacube_from_files_in_folder(FOLDER_PATH, TIME_STEP)
		print("TOTAL RUNTIME ", datetime.datetime.now() - start) 

		# TODO: There should be a default name, e.g. hmi.v_45s_2022.11.01_TAI depending on what set of dopplergrams we calculated with
		create_fits_file_from_data_array(datacube_array, OUTPUT_DIR, FILENAME) 
