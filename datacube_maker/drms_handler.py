import os
import drms
import datetime
import pandas as pd

from urllib.request import urlretrieve
from urllib.error import HTTPError, URLError

from utils import save_list_to_text_file, create_request_name_from_request_string

# TODO: Fix and reintroduce logger
# from log import setup_logger

# module_logger = setup_logger(__name__)

def download_data_from_jsoc_via_drms(jsoc_email: str, request: str, output_dir: str, time_step: float = 45.0):
    dh = DrmsHandler(jsoc_email=jsoc_email)
    dh.create_new_jsoc_export_request(request=request)
    rec_times_list, missing_rec_times_list = dh.check_for_missing_frames_in_request(time_step=time_step)

    frame_info_files_path = os.path.join(output_dir, "frame_info_files")
    request_name = create_request_name_from_request_string(request=request)
    rec_times_file_name = f"{request_name}_rec_times.txt"
    missing_rec_times_file_name = f"{request_name}_missing_frames_rec_times.txt"
    save_list_to_text_file(rec_times_list, frame_info_files_path, rec_times_file_name)
    if missing_rec_times_list:
        save_list_to_text_file(missing_rec_times_list, frame_info_files_path, missing_rec_times_file_name)
        # missing_frames_message = '\033[91m These frames are missing:\n \033[0m' + "\n".join(missing_rec_times_list)
        missing_frames_message = 'These frames are missing:\n' + "\n".join(missing_rec_times_list)
        print(missing_frames_message)

    dh.download_fits_files_from_jsoc(files_path=output_dir)

class DrmsHandler:
    def __init__(self, jsoc_email:str):
        self.jsoc_email = jsoc_email
        self.client = drms.Client(email=self.jsoc_email, verbose=True)
        self.export_request = None
        
    @staticmethod
    def _next_available_filename(fname):
        """
        Find next available filename, append a number if neccessary.
        
        Note: a copy of the same method in drms.ExportRequest
        """
        i = 1
        new_fname = fname
        while os.path.exists(new_fname):
            new_fname = f"{fname}.{int(i)}"
            i += 1
        return new_fname

    def create_new_jsoc_export_request(self, request, method="url", protocol="fits"):
        """
        Creates a new export request via JSOC client.

        Needs to be called before any other return methods, i.e. `download_fits_files_from_jsoc` or 
        `check_for_missing_frames_in_request`.

        Parameters:
            request: str ... JSOC request string - mainly taken from conf.py and passed from main.py
            method:str (default: "url") ... method used in the JSOC request (look to JSOC for options)
            protocol:str (default: "fits") ... protocol used in the JSOC request (look to JSOC for options)
        """
        self.export_request = self.client.export(request, method=method, protocol=protocol)

    def download_fits_files_from_jsoc(self, files_path: str, verbose: bool = True, download_attempts_limit: int = 25) -> pd.DataFrame:
        """Calls a download method on the JSOC export request --> downloads files specified in the request from JSOC database.

        Args:
            files_path (str): A path to a directory, where the files will be saved (if non-existent, it will be created).
            verbose (bool, optional): If True, process messages are printed. Defaults to True.
            download_attempts_limit (int, optional): Maximum number of download retries if the initial download of a file fails. 
            Defaults to 25.

        Raises:
            RuntimeError: Raised if one of the files can't be downloaded even within the download attempts limit.

        Returns:
            pandas.DataFrame: A DataFrame containing record queries, urls and local file paths of the downloaded files.
        """      
          
        self._assert_export_request_created()

        # If folder exists already ==> new folder with a name 'init_name_{todays_date}' is created
        # TODO: Is this a good approach? If automated, how to pass the info about the new folder name?
        if not os.path.exists(files_path):
            os.makedirs(files_path)
        else:
            todays_date = str(datetime.datetime.now().date())
            files_path = f'{files_path}_{todays_date}'
            os.makedirs(files_path)
            print(f"Files folder already exists, new folder created in path: '{files_path}'")

        #! Deprecated for own custom solution - drms solution does not support retry of download when it fails
        # self.export_request.download(files_path)
        
        #* New implementation instead of export_request.download()
        self.export_request.wait(timeout=900, verbose=verbose) # Wait for the server to process the export request.

        data = self.export_request.urls
        ndata = len(data)

        downloads = []
        for i in range(ndata):
            di = data.iloc[i]
            filename = di.filename

            fpath = os.path.join(files_path, filename)
            
            download_attempt_index = 1
            is_download_complete = False
            
            fpath_new = self._next_available_filename(fpath)
            fpath_tmp = self._next_available_filename(f"{fpath_new}.part")
            
            while (not is_download_complete) and (download_attempt_index < download_attempts_limit):
                if verbose:
                    print(f"Downloading file {int(i + 1)} (try no. {download_attempt_index}) of {int(ndata)}...")
                    print(f"    record: {di.record}")
                    print(f"  filename: {di.filename}")
                try:
                    urlretrieve(di.url, fpath_tmp)
                except (HTTPError, URLError):
                    print(f'Download {download_attempt_index} failed.')
                    download_attempt_index += 1
                else:
                    fpath_new = self._next_available_filename(fpath)
                    os.rename(fpath_tmp, fpath_new)
                    if verbose:
                        print(f"  -> {os.path.relpath(fpath_new)}")
                    is_download_complete = True
                
            if is_download_complete:
                downloads.append(fpath)
            else:
                runtime_error_message = "File missing, download aborted."
                print(runtime_error_message)
                raise RuntimeError(runtime_error_message)

        result = data[["record", "url"]].copy()
        result["download"] = downloads

        return result

    def check_for_missing_frames_in_request(self, time_step:int=45, datetime_format:str = "%Y.%m.%d_%H:%M:%S"):
        """
        Goes through the records of the JSOC requests and compares the time interval between them. 

        Parameters:
            time_step:int (default: 45) ... time step used to comparison between following frames to find missing frames
            datetime_format:str (default: "%Y.%m.%d_%H:%M:%S") ... datetime format used to parse datetime strings to datetime objects
                                                                   (datetimes are retrieved from record names which are strings)

        Returns:
            rec_times_list ... list of all frame datetimes in form of strings
            missing_rec_times_list ... list of missing frames datetimes in form of strings

            --> return rec_times_list, missing_rec_times_list
        """

        self._assert_export_request_created()

        record_names = self.export_request.data["record"]
        record_datetimes = self._transform_record_names_to_datetimes(record_names, datetime_format=datetime_format)
 
        missing_rec_times_list = []
        time_delta_list = []

        for i, record_datetime in enumerate(record_datetimes[:-1]):
            datetime1 = record_datetime
            datetime2 = record_datetimes[i+1]
            
            time_delta = datetime2 - datetime1
            time_delta_list.append(time_delta.seconds)
            
            if time_delta.seconds > time_step:
                datetime1 += datetime.timedelta(seconds=time_step)
                while datetime1 < datetime2:
                    missing_rec_times_list.append(str(datetime1))
                    datetime1 += datetime.timedelta(seconds=time_step)

        rec_times_list = [str(x) for x in record_datetimes]

        return rec_times_list, missing_rec_times_list

    def _transform_record_names_to_datetimes(self, record_names, datetime_format:str = "%Y.%m.%d_%H:%M:%S"):

        for i, record in enumerate(record_names):
            datetime_str = self._extract_datetime_string_from_jsoc_export_record(record)
            corrected_datetime_str = self._remove_substring_from_string_if_present(datetime_str, "_TAI")
            datetime_record = datetime.datetime.strptime(corrected_datetime_str, datetime_format)
            record_names[i] = datetime_record

        return record_names

    def _extract_datetime_string_from_jsoc_export_record(self, record:str):

        assert "[" in record and "]" in record

        left_bracket_index = record.index("[")
        right_bracket_index = record.index("]")
        datetime_str = record[left_bracket_index + 1: right_bracket_index]

        return datetime_str

    def _remove_substring_from_string_if_present(self, string, substring):
        if substring in string:
            string = string.replace(substring, "")

        return string
    
    def _assert_export_request_created(self):
        message = "JSOC export request not created. Call 'create_new_jsoc_export_request' method to create one."
        assert self.export_request is not None, message