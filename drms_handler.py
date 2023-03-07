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

        if not os.path.exists(files_path):
            os.makedirs(files_path)

            # export_request = self.client.export(request + '{Dopplergram}', method="url", protocol="fits") 
            self.export_request.download(files_path)

    def check_for_missing_frames_in_request(self, time_step:int=45, datetime_format:str = "%Y.%m.%d_%H:%M:%S"):

        self._assert_export_request_created()

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

    def _remove_substring_from_string_if_present(self, string, substring):
        if substring in string:
            string = string.replace(substring, "")

        return string
    
    def _assert_export_request_created(self):
        assert self.export_request is not None, "JSOC export request not created. Call 'create_new_jsoc_export_request' method to create one."