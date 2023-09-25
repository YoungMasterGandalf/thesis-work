import os
import json

from datacube_maker.drms_handler import download_data_from_jsoc_via_drms
from datacube_pipeline_prerequisitor import JSOC_EMAIL, TIME_STEP, REQUESTS_FILE_PATH # TODO: probably not ideal, think about an implementation without this import

if __name__ == "__main__":
    if not os.path.exists(REQUESTS_FILE_PATH):
        raise FileNotFoundError(f"'{REQUESTS_FILE_PATH}' does not exist. Try running 'datacube_pipeline_prerequisitor.py' first.")
     
    with open(REQUESTS_FILE_PATH, "r") as file:
        request_output_dir_dict = json.load(file)
        
    if not request_output_dir_dict:
        raise Exception("No requests prepared for download. Try running 'datacube_pipeline_prerequisitor.py' first.")
    
    for request, output_dir in request_output_dir_dict.items():
        download_data_from_jsoc_via_drms(jsoc_email=JSOC_EMAIL, request=request, output_dir=output_dir, time_step=TIME_STEP)
        
        with open(REQUESTS_FILE_PATH, "r") as file:
            file_content: dict = json.load(file)
        
        if request in file_content:
            file_content.pop(request)
            
            with open(REQUESTS_FILE_PATH, "w") as file:
                json.dump(file_content, file, indent=2)
        
    
    