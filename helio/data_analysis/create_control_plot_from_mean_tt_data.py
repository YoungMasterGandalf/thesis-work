import os
import sys
import re
import ast
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from scipy.stats import linregress
from typing import Literal
from uncertainties import ufloat

PATTERN: str = "TT_hmi\.v_45s_(\d{4})\.(\d{2})\.(\d{2})_00\.00\.00_lon_(plus|minus)_(\d+)_lat_(plus|minus)_(\d+)_vel_(plus|minus)_(\d+)"
DATA_FILE_NAME: str = "tt_data_analysis.csv"
OUTPUT_DIR: str = "/nfshome/chmurnyd"

INCLUDE_PLOT_TITLE: bool = False

SINGLE_PLOT_MODE: bool = True

# Single plot mode configuration
MODE: Literal['f', 'p1', 'p2', 'p3'] = 'f'
GEOMETRY: Literal['cos_m0', 'cos_m1', 'sin_m1'] = 'cos_m1'
DISTANCE: int = 15
OUTPUT_FILENAME: str = "test_plot_f_cos_m1_15.png"
# Single plot mode configuration END

# Constants used in plot creation
MODE_DISTANCE_MAPPING: dict = {
    'f': [20, 19, 10, 9, 8, 7, 5, 6, 12, 11, 17, 18, 15, 13, 14, 16], 
    'p1': [20, 19, 14, 13, 8, 9, 7, 5, 15, 10, 6, 12, 16, 11, 18, 17], 
    'p2': [20, 19, 15, 16, 10, 9, 8, 6, 12, 18, 5, 7, 11, 14, 13, 17], 
    'p3': [20, 19, 17, 14, 12, 10, 7, 6, 5, 9, 11, 13, 18, 16, 8, 15], 
    'p4': [10, 11, 6, 5, 15, 17, 8, 7, 20, 12, 9, 13, 16, 14, 19, 18],
    'td1': [3.4, 5.1, 2.5, 4.2, 6],
    'td2': [4.2, 5.1, 6.8, 6, 7.7],
    'td3': [6, 7.9, 7, 8.9, 9.9],
    'td4': [10.8, 11.6, 12.4, 13.3, 9.9],
    'td5': [15, 13, 17, 20, 18],
    'td6': [24, 22, 21, 18, 19],
    'td7': [29, 23, 25, 27, 22],
    'td8': [26, 28, 29, 31, 33],
    'td9': [30, 32, 34, 35, 37],
    'td10': [35, 36, 38, 39, 41],
    'td11': [39, 40, 42, 44, 46]
    }

GEOMETRIES = ["cos_m1"] # May contain: "cos_m0", "cos_m1", "sin_m1"

def create_velocity_value_from_string_representation(velocity_sign_str: str, velocity_value_str: str):
    velocity_value = ast.literal_eval(velocity_value_str)
    velocity_value = velocity_value if velocity_sign_str == "plus" else - velocity_value
    
    return velocity_value

def get_velocities_and_mean_traveltimes_for_one_plot_case(folder_path, pattern):
    os.chdir(folder_path)

    # Compile regex pattern
    regex_pattern = re.compile(pattern)
    
    velocities = []
    mean_traveltimes = []

    # Find folders containing the pattern and pass each as an argument to the python script
    for folder in os.listdir("."):
        match = regex_pattern.match(folder)
        if os.path.isdir(folder) and match:
            data_file_path = os.path.join(folder, DATA_FILE_NAME)
            if os.path.isfile(data_file_path):
                velocity_sign = match.group(8)
                velocity_value = match.group(9)
                velocity_value = create_velocity_value_from_string_representation(velocity_sign_str=velocity_sign, 
                                                                                  velocity_value_str=velocity_value)
                df = pd.read_csv(data_file_path)
                
                # To ensure "half away from zero" strategy instead of "half to even"
                distance_with_added_bias = DISTANCE + min(0.01 * DISTANCE, 0.001)
                
                # Filter DataFrame and get traveltime_mean value
                traveltime_mean = df.loc[(df['mode'] == MODE) & (df['geometry'] == GEOMETRY) & (df['distance'].round == round(distance_with_added_bias)), 
                                         'traveltime_mean'].values[0]
                velocities.append(velocity_value)
                mean_traveltimes.append(traveltime_mean)

    return velocities, mean_traveltimes

def parse_jsoc_query_part_from_TT_folder_path(folder_path: str):
    folder_name = folder_path.split('/')[-1]
    
    start_index = folder_name.index("hmi.")
    stop_index = folder_name.index("_lon")
    query_part = folder_name[start_index : stop_index]
    
    return query_part

def get_combined_dataframe_for_multiplot_case(folder_path, pattern):
    # Go to the folder
    os.chdir(folder_path)

    # Compile regex pattern
    regex_pattern = re.compile(pattern)
    
    total_df = None
    
    print(f'Starting creation of combined DataFrame...')
    print(f'Root directory: {folder_path}', f'Pattern: {pattern}', sep='\n')

    # Find folders containing the pattern and pass each as an argument to the python script
    for folder in os.listdir("."):
        match = regex_pattern.match(folder)
        if os.path.isdir(folder) and match:
            data_file_path = os.path.join(folder, DATA_FILE_NAME)
            if os.path.isfile(data_file_path):
                velocity_sign = match.group(8)
                velocity_value = match.group(9)
                velocity_value = create_velocity_value_from_string_representation(velocity_sign_str=velocity_sign, 
                                                                                  velocity_value_str=velocity_value)
                df = pd.read_csv(data_file_path)
                df['velocity'] = velocity_value
                
                jsoc_query_part = parse_jsoc_query_part_from_TT_folder_path(folder_path=folder)
                df['dataset'] = jsoc_query_part
                
                if type(total_df) == pd.DataFrame:
                    total_df = pd.concat([total_df, df], ignore_index=True)
                else:
                    total_df = df
                    
    print('Combined DataFrame creation finished.')

    return total_df

def create_mean_traveltime_vs_velocity_plot(velocities, mean_traveltimes, slope, intercept, mode, geometry, distance, output_file_path, dataset_id=None):
    fig, ax = plt.subplots(figsize=(8, 6))
    
    scatter_legend = f'Mean traveltimes around center (dataset: {dataset_id})' if dataset_id else 'Mean traveltimes around center'
    ax.scatter(velocities, mean_traveltimes, label=scatter_legend)

    line = np.poly1d([slope, intercept])
    plt.plot(velocities, line(velocities), color='red', label=r'Linear fit in range (-300, 300) ms$^{-1}$')
    
    if INCLUDE_PLOT_TITLE:
        ax.set_title(f'{mode}_{geometry}_{distance}')

    # Labels
    ax.set_xlabel(r'Planted longitudinal velocity $(ms^{-1})$', fontsize=14)
    ax.set_ylabel(r'Mean travel time around center $(s)$', fontsize=14)

    # Legend
    ax.legend()

    # Ticks
    ax.tick_params(axis='both', which='major', labelsize=10)
    ax.minorticks_on()
    ax.tick_params(axis='both', which='minor', labelsize=8)

    # Save plot
    plt.savefig(output_file_path, dpi=600)
    
    # Close plot to release memory
    plt.close(fig)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python create_control_plot_from_mean_tt_data.py <folder_path>")
        sys.exit(1)

    folder_path = sys.argv[1]
    
    if not os.path.exists(OUTPUT_DIR):
        print(f"Directory {OUTPUT_DIR} does not exist.")
        print(f"Creating output directory {OUTPUT_DIR}")
        os.makedirs(OUTPUT_DIR)
    
    if SINGLE_PLOT_MODE:
        velocities, mean_traveltimes = get_velocities_and_mean_traveltimes_for_one_plot_case(folder_path, PATTERN)
        
        # Fit data with linear regression on velocity interval (-300, 300) --> to avoid non-linearities
        velocity_tt_pairs = list(zip(velocities, mean_traveltimes))
        filtered_pairs = [(velocity, traveltime) for velocity, traveltime in velocity_tt_pairs if -300 <= velocity <= 300]
        filtered_velocities = [x[0] for x in filtered_pairs]
        filtered_mean_traveltimes = [x[1] for x in filtered_pairs]
        
        result = linregress(filtered_velocities, filtered_mean_traveltimes)
        slope, intercept = result.slope, result.intercept
        
        output_file_path = os.path.join(OUTPUT_DIR, OUTPUT_FILENAME)
        create_mean_traveltime_vs_velocity_plot(velocities=velocities, mean_traveltimes=mean_traveltimes, slope=slope,
                                                intercept=intercept, mode=MODE, geometry=GEOMETRY, distance=DISTANCE, 
                                                output_file_path=output_file_path)
    else:
        slope_intercept_df = pd.DataFrame(columns=['slope', 'intercept'])
        
        total_df = get_combined_dataframe_for_multiplot_case(folder_path=folder_path, pattern=PATTERN)
        dataset_ids = total_df['dataset'].unique().tolist()
        
        print('Starting multiplot creation (this might take a while)...\n')
        
        for mode, mode_distances in MODE_DISTANCE_MAPPING.items():
            for distance in mode_distances:
                for geometry in GEOMETRIES:
                    slopes, intercepts = [], []
                    
                    for dataset_id in dataset_ids:
                        print(f'Creating plot for configuration: {mode}_{geometry}_{distance}')
                        
                        # To ensure "half away from zero" strategy instead of "half to even"
                        distance_with_added_bias = distance + min(0.01 * distance, 0.001)
                        
                        velocities_and_mean_traveltimes = total_df.loc[
                            (total_df['mode'] == mode) & (total_df['geometry'] == geometry) & 
                            (total_df['distance'].round() == round(distance_with_added_bias)) & (total_df['dataset'] == dataset_id), 
                            ['velocity', 'traveltime_mean']
                            ]
                        velocities = velocities_and_mean_traveltimes['velocity'].tolist()
                        mean_traveltimes = velocities_and_mean_traveltimes['traveltime_mean'].tolist()
                        
                        # Fit data with linear regression on velocity interval (-300, 300) --> to avoid non-linearities
                        velocity_tt_pairs = list(zip(velocities, mean_traveltimes))
                        filtered_pairs = [(velocity, traveltime) for velocity, traveltime in velocity_tt_pairs if -300 <= velocity <= 300]
                        filtered_velocities = [x[0] for x in filtered_pairs]
                        filtered_mean_traveltimes = [x[1] for x in filtered_pairs]
                        
                        result = linregress(filtered_velocities, filtered_mean_traveltimes)
                        slope, slope_stderr  = result.slope, result.stderr
                        intercept, intercept_stderr = result.intercept, result.intercept_stderr
                        
                        slopes.append(ufloat(slope, slope_stderr))
                        intercepts.append(ufloat(intercept, intercept_stderr))

                        # new_row_columns = ['mode', 'geometry', 'distance', 'slope', 'slope_err', 'intercept', 'intercept_err']
                        # new_row_data = [[mode, geometry, distance, slope, slope_stderr, intercept, intercept_stderr]]
                        # new_row_df = pd.DataFrame(new_row_data, columns=new_row_columns)
                        # slope_intercept_df = pd.concat([slope_intercept_df, new_row_df], ignore_index=True)
                        
                        output_filename = f'{mode}_{geometry}_{distance}_{dataset_id}.png'
                        output_file_path = os.path.join(OUTPUT_DIR, output_filename)
                        create_mean_traveltime_vs_velocity_plot(velocities=velocities, mean_traveltimes=mean_traveltimes,
                                                                slope=slope, intercept=intercept, mode=mode,
                                                                geometry=geometry, distance=distance,
                                                                output_file_path=output_file_path)
                        print('Plot finished.\n')
                        
                    
                    slope_wavg = ufloat(
                        sum([slope.n/slope.s**2 for slope in slopes]) / sum([1/slope.s**2 for slope in slopes]),
                        1/np.sqrt(sum([1/slope.s**2 for slope in slopes]))
                        )
                    intercept_wavg = ufloat(
                        sum([intercept.n/intercept.s**2 for intercept in intercepts]) / sum([1/intercept.s**2 for intercept in intercepts]),
                        1/np.sqrt(sum([1/intercept.s**2 for intercept in intercepts]))
                        )
                        
                    new_row_columns = ['mode', 'geometry', 'distance', 'slope', 'slope_err', 'intercept', 'intercept_err']
                    new_row_data = [[mode, geometry, distance, slope_wavg.n, slope_wavg.s, intercept_wavg.n, intercept_wavg.s]]
                    new_row_df = pd.DataFrame(new_row_data, columns=new_row_columns)
                    slope_intercept_df = pd.concat([slope_intercept_df, new_row_df], ignore_index=True)
                    
        slope_intercept_results_filename = "slopes_and_intercepts.csv"
        slope_intercept_output_path = os.path.join(OUTPUT_DIR, slope_intercept_results_filename)
        slope_intercept_df.to_csv(slope_intercept_output_path)

