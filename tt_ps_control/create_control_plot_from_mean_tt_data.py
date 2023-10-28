import os
import sys
import re
import ast
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from scipy.stats import linregress
from typing import Literal

# PATTERN: str = "TT_hmi\.v_45s_(\d{4})\.(\d{2})\.(\d{2})_00\.00\.00_lon_(plus|minus)_(\d+)_lat_(plus|minus)_(\d+)_vel_(plus|minus)_(\d+)"
PATTERN: str = "TT_hmi\.v_45s_(\d{4})\.(\d{2})\.(\d{2})_00\.00\.00_lon_(plus|minus)_(\d+)_lat_(plus|minus)_0_vel_(plus|minus)_(\d+)"

MODE: Literal['f', 'p1', 'p2', 'p3'] = 'f'
GEOMETRY: Literal['cos_m0', 'cos_m1', 'sin_m1'] = 'cos_m1'
DISTANCE: int = 15

DATA_FILE_NAME: str = 'tt_data_analysis.csv'

SAVE_PLOT_TO: str = '/nfshome/chmurnyd/test_plot_f_cos_m1_15.png'

def create_velocity_value_from_string_representation(velocity_sign_str: str, velocity_value_str: str):
    velocity_value = ast.literal_eval(velocity_value_str)
    velocity_value = velocity_value if velocity_sign_str == "plus" else - velocity_value
    
    return velocity_value

def main(folder_path, pattern):
    # Store current working dir (containing the python script for data analysis) to a variable
    python_script_dir = os.getcwd()
    python_script_path = os.path.join(python_script_dir, "analyze_tt_results.py")

    # Go to the folder
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
                # Filter DataFrame and get traveltime_mean value
                traveltime_mean = df.loc[(df['mode'] == MODE) & (df['geometry'] == GEOMETRY) & (df['distance'] == DISTANCE), 
                                         'traveltime_mean'].values[0]
                velocities.append(velocity_value)
                mean_traveltimes.append(traveltime_mean)

    return velocities, mean_traveltimes

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python create_control_plot_from_mean_tt_data.py <folder_path>")
        sys.exit(1)

    folder_path = sys.argv[1]
    velocities, mean_traveltimes = main(folder_path, PATTERN)

    fig, ax = plt.subplots(figsize=(8, 6))

    # Scatter plot
    scatter = ax.scatter(velocities, mean_traveltimes, label='Mean traveltimes around center')

    # Fit data with linear regression
    slope, intercept, r_value, p_value, std_err = linregress(velocities, mean_traveltimes)
    line = np.poly1d([slope, intercept])
    plt.plot(velocities, line(velocities), color='red', label=f'Linear fit (y = {slope}x + {intercept})')
    
    ax.set_title(f'{MODE}_{GEOMETRY}_{DISTANCE} - 100 datacubes')

    # Labels
    ax.set_xlabel(r'Planted longitudinal velocity $(ms^{-1})$', fontsize=14)
    ax.set_ylabel(r'Mean travel time around center $(s)$', fontsize=14)

    # Legend
    ax.legend()

    # Ticks
    ax.tick_params(axis='both', which='major', labelsize=10)
    ax.minorticks_on()
    ax.tick_params(axis='both', which='minor', labelsize=8)

    # Gridlines for scientific plot design
    ax.grid(which='major', linestyle='-', linewidth='0.5', color='black')
    ax.grid(which='minor', linestyle=':', linewidth='0.5', color='black')

    # Save plot
    plt.savefig(SAVE_PLOT_TO, dpi=300)

