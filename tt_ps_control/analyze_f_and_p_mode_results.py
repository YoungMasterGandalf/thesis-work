import os
import re
import argparse
import pandas as pd

import test_traveltimes as tt

from matlab_file_reading import read_mat_file

def find_files(working_dir: str):
    # Define the regular expression pattern for the file names
    pattern = re.compile(r'tt_(f|p1|p2|p3)_(sin|cos)_m[01]_([5-9]|1[0-9]|20)\.mat$')

    # Initialize a list to store the file paths
    file_paths = []

    # Walk through all files and folders in the current directory
    for root, dirs, files in os.walk(working_dir):
        for file in files:
            # Check if the file name matches the pattern
            if pattern.match(file):
                # If it does, store the file path in the list
                file_paths.append(os.path.join(root, file))

    # Return the list of file paths
    return file_paths

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    
    working_dir_help = """Path leading to the working directory, i.e. a folder containing the data from the travel-time 
    pipeline (e.g. 'tt_f_cos_m0_10.mat)"""
    parser.add_argument('working_dir', type=str, help=working_dir_help)
    
    args = parser.parse_args()
    
    working_dir = args.working_dir
    
    if not os.path.exists(working_dir):
        raise FileNotFoundError(f'Entered PATH "{working_dir}" does not exist.')
    
    if not os.path.isdir(working_dir):
        raise NotADirectoryError(f'Entered PATH "{working_dir}" does not lead to a folder.')
    
    print(f"Running f and p modes data analysis in a directory '{working_dir}'")
    
    # Get the list of file paths
    file_paths = find_files(working_dir=working_dir)
    
    extracted_data = []
    
    for file_path in file_paths:
        mat_file = read_mat_file(file_path)
        
        tt_plus, tt_minus = tt.get_traveltime_data_from_mat_file(mat_file)
        param_dict = tt.create_param_dict_from_mat_file(mat_file)
        
        mode = param_dict["komega_filter"] # e.g.: f, p1, p2, p3
        geometry = param_dict["avefilter"] # e.g.: cos_m0 (o-i), cos_m1 (e-w), sin_m1 (s-n)
        distance = param_dict["distance"] 
        
        mean_around_center = tt.calculate_mean_traveltime_value_around_center(tt_plus, tt_minus)
        
        extracted_data.append(
            {
                "mode": mode,
                "geometry": geometry,
                "distance": distance,
                "traveltime_mean": mean_around_center
            }
        )
        
    extracted_data_df = pd.DataFrame(extracted_data)
    extracted_data_df.sort_values(by=["mode"]) # sort data in DF by mode, i.e. f -> p1 -> p2 -> p3
    
    # Save data to a csv file located in the working directory
    csv_file_path = os.path.join(working_dir, "f_and_p_modes_analysis.csv")
    extracted_data_df.to_csv(csv_file_path)
        