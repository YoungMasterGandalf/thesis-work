import os

import drms
import datetime

class DrmsHandler:
    def __init__(self, jsoc_email:str):
        self.jsoc_email = jsoc_email
        self.client = drms.Client(email=self.jsoc_email, verbose=True)
        self.export_request = None

    def create_new_jsoc_export_request(self, request, method="url", protocol="fits"):
        self.export_request = self.client.export(request, method=method, protocol=protocol)

    # def download_fits_files_from_jsoc(self, files_path, request):
    def download_fits_files_from_jsoc(self, files_path):

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

        # export_request = self.client.export(request + '{Dopplergram}', method="url", protocol="fits") 
        self.export_request.download(files_path)

    def check_for_missing_frames_in_request(self, time_step:int=45, datetime_format:str = "%Y.%m.%d_%H:%M:%S"):

        self._assert_export_request_created()

        record_names = self.export_request.data["record"]
        record_datetimes = self._transform_record_names_to_datetimes(record_names, datetime_format=datetime_format)
 
        # rec_times_list = record_datetimes.to_list()
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

        # rec_times_list = [str(x) for x in rec_times_list]
        rec_times_list = [str(x) for x in record_datetimes]

        return rec_times_list, missing_rec_times_list

    # Deprecated, TODO: delete in the following commit
    """
    def check_for_missing_frames_in_request(self, request, time_step:int=45, datetime_format:str = "%Y.%m.%d_%H:%M:%S"):

        keys = self.client.query(request, key='T_REC') 
        record_times = keys["T_REC"]
        # record_times = drms.to_datetime(record_times)
        record_times = record_times.apply(self._remove_substring_from_string_if_present, args = ("_TAI",)) 
        rec_times_list = record_times.to_list()
        missing_rec_times_list = []
        time_delta_list = []

        for i, rec_time_str in enumerate(rec_times_list[:-1]):
            time1 = datetime.datetime.strptime(rec_time_str, datetime_format)
            time2 = datetime.datetime.strptime(rec_times_list[i+1], datetime_format)
            
            time_delta = time2 - time1
            time_delta_list.append(time_delta.seconds)
            
            if time_delta.seconds > time_step:
                time1 += datetime.timedelta(seconds=time_step)
                while time1 < time2:
                    missing_rec_times_list.append(str(time1))
                    time1 += datetime.timedelta(seconds=time_step)

        rec_times_list = [str(x) for x in rec_times_list]

        return rec_times_list, missing_rec_times_list
    """

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
        assert self.export_request is not None, "JSOC export request not created. Call 'create_new_jsoc_export_request' method to create one."