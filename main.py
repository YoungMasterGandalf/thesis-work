from dopplergram import Dopplergram, create_datacube_from_files_in_folder, create_fits_file_from_data_array
import datetime
import drms
import os
import shutil

from conf import (TEST_MODE, FOLDER_PATH, TIME_STEP, OUTPUT_DIR, FILENAME, SAVE_FILE, PATH, JSOC_EMAIL, DRMS_FILES_PATH, DOPPL_REQUEST, RUN_VIA_DRMS, 
					DELETE_FILES_WHEN_FINISHED)

def download_fits_files_from_jsoc(jsoc_email, files_path, request):
	# Download data from JSOC
	client = drms.Client(email=jsoc_email, verbose=True)

	if not os.path.exists(files_path):
		os.mkdir(files_path)

		export_request = client.export(request + '{Dopplergram}', method="url", protocol="fits") 
		export_request.download(files_path)

if __name__ == "__main__":
	## TODO: Maybe this if-else structure could be better (better build, less arguments etc.)
	if RUN_VIA_DRMS:
		download_fits_files_from_jsoc(jsoc_email=JSOC_EMAIL, files_path=DRMS_FILES_PATH, request=DOPPL_REQUEST)

	if TEST_MODE:
		if RUN_VIA_DRMS:
			files = [os.path.join(DRMS_FILES_PATH, file) for file in os.listdir(DRMS_FILES_PATH) if file.endswith(".fits")]
			file = files[0]
		else:
			file = PATH

		dg = Dopplergram(file)
		data = dg.get_postel_projected_data()
	else:
		start = datetime.datetime.now()

		if RUN_VIA_DRMS:
			datacube_array = create_datacube_from_files_in_folder(DRMS_FILES_PATH, TIME_STEP)
		else:
			datacube_array = create_datacube_from_files_in_folder(FOLDER_PATH, TIME_STEP)
		
		print("TOTAL RUNTIME ", datetime.datetime.now() - start) 
	
	if not TEST_MODE and SAVE_FILE:
		# TODO: There should be a default name, e.g. hmi.v_45s_2022.11.01_TAI depending on what set of dopplergrams we calculated with
		create_fits_file_from_data_array(datacube_array, OUTPUT_DIR, FILENAME) 

	if RUN_VIA_DRMS and DELETE_FILES_WHEN_FINISHED:
		shutil.rmtree() # Delete fits files downloaded from JSOC, equivalent to '$ rm -rs <out_dir>'
