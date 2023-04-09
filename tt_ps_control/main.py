import os
import argparse

from matlab_file_reading import read_mat_file
from plot_powerspectrum import create_powerspectrum_fig_from_mat_file

import test_traveltimes as tt

#* PATH example
# FILE_PATH = "/Users/daniel/Documents/diploma_thesis_sidework/komega_cube.mat_controlplots.mat"

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    
    job_help = "Enter which job should be made: 'TT' for travel-times testing, 'PS' for power-spectrum plot."
    parser.add_argument('job', type=str, choices=["TT", "PS"], help=job_help)
    
    file_path_help = """Path leading to a .mat file containing k_omega data, 
    e.g.: "/Users/daniel/Documents/diploma_thesis_sidework/komega_cube.mat_controlplots.mat" """
    parser.add_argument('file_path', type=str, help=file_path_help)
    
    save_to_help = 'Where to save the .png plot. Write the full path ending with "/<filename>.png"!'
    parser.add_argument('save_to', type=str, help=save_to_help)
    
    args = parser.parse_args()
    
    FILE_PATH = args.file_path
    assert os.path.exists(FILE_PATH), f'Entered PATH "{FILE_PATH}" does not exist.'
    assert os.path.isfile(FILE_PATH), f'Entered PATH "{FILE_PATH}" does not lead to a file.'
    
    SAVE_TO_PATH = args.save_to
    assert SAVE_TO_PATH.endswith(".png"), 'save_to argument must end with /<filename>.png'
    
    folder_path = SAVE_TO_PATH[:SAVE_TO_PATH.rfind("/")]
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        
    JOB = args.job
    
    mat_file = read_mat_file(FILE_PATH)
    
    if JOB == "PS":
        create_powerspectrum_fig_from_mat_file(mat_file, SAVE_TO_PATH)
    elif JOB == "TT":
        tt_plus, tt_minus = tt.get_traveltime_data_from_mat_file(mat_file)
        
        param_dict = tt.create_param_dict_from_mat_file(mat_file)
        
        tt.print_mean_traveltime_value_around_center(tt_plus, tt_minus)
        tt.create_traveltime_plot(tt_plus, tt_minus, param_dict, SAVE_TO_PATH)