import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from typing import Union
from scipy.stats import linregress

import test_traveltimes as tt

from matlab_file_reading import read_mat_file

# DATA_FILE_PATH = "/nfshome/chmurnyd/plots-2023-11-09/slopes_and_intercepts.csv"
DATA_FILE_PATH = "/Users/daniel/Downloads/slopes_and_intercepts.csv"
# KERNEL_ROOT_DIR = "/seismo2/michal/FLOW_KERNELS/PtA"
KERNEL_ROOT_DIR = "/Users/daniel/Downloads/kernels/kernels"
OUTPUT_FILE_PATH = "/nfshome/chmurnyd/slope_vs_kernel.png"

MODE_COLORS_DICT = {
    'f': '#1f77b4',    # Blue
    'p1': '#ff7f0e',   # Orange
    'p2': '#2ca02c',   # Lime Green
    'p3': '#d62728',   # Crimson Red
    'p4': '#9467bd',   # Violet
    'td1': '#8c564b',  # Rustic Brown
    'td2': '#e377c2',  # Rosy Pink
    'td3': '#7f7f7f',  # Charcoal Gray
    'td4': '#bcbd22',  # Olive
    'td5': '#17becf',  # Electric Cyan
    'td6': '#9b59b6',  # Mauve Lavender
    'td7': '#3498db',  # Sky Blue
    'td8': '#ff0000',  # Bright Red
    'td9': '#00ff00',  # Vivid Green
    'td10': '#0000ff', # Royal Blue
    'td11': '#ffff00'  # Sunshine Yellow
}

def create_kernel_filename(mode: str, geometry: str, distance: Union[int, float]):
    distance = int(distance) if distance.is_integer() else distance
    filename = f'k_ann_{mode}_kx_{geometry}_{distance}.mat'
    
    return filename

def get_integral_from_kernel_file(root_dir: str, filename: str):
    
    kernel_file_path = os.path.join(root_dir, filename)
    
    mat_file = read_mat_file(kernel_file_path)
    integral = mat_file["integral"]
    integral = tt.convert_data_from_h5py_dataset_to_numpy_array_if_needed(integral)
    integral = tt.flatten_array_and_get_first_value(integral)
    
    return integral

if __name__ == "__main__":
    if not os.path.exists(DATA_FILE_PATH):
        raise FileNotFoundError(f'File {DATA_FILE_PATH} does not exist.')
    
    df = pd.read_csv(DATA_FILE_PATH)
    
    df["slope"] = df["slope"] * 10**3 # To match kernel units
    
    integrals = []
    
    for i, row in df.iterrows():
        print(f'Processing row {i} out of {df.shape[0]}')
        kernel_filename = create_kernel_filename(mode=row["mode"], geometry=row["geometry"], distance=row["distance"])
        integral = get_integral_from_kernel_file(root_dir=KERNEL_ROOT_DIR, filename=kernel_filename)
        integrals.append(integral)
        
    df["integral"] = integrals
        
    # Fit data with linear regression
    fit_slope, fit_intercept, r_value, p_value, std_err = linregress(df["integral"], df["slope"])
    fit_slope, fit_intercept = round(fit_slope, 2), round(fit_intercept, 2)
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    for mode, color in MODE_COLORS_DICT.items():
        sub_df = df[df["mode"] == mode]
        mode_integrals = sub_df["integral"]
        mode_slopes = sub_df["slope"]
        ax.scatter(mode_integrals, mode_slopes, c=color, label=mode)

    line = np.poly1d([fit_slope, fit_intercept])
    plt.plot(integrals, line(integrals), color='red', label=f'Linear fit (y = {fit_slope}x + {fit_intercept})')
    
    ax.set_title("Kernel integrals vs. linear regressions slopes")

    # Labels
    ax.set_xlabel(r'Kernel integral', fontsize=14)
    ax.set_ylabel(r'Linear regression slope', fontsize=14)

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
    plt.savefig(OUTPUT_FILE_PATH, dpi=600)
    
    # Close plot to release memory
    plt.close(fig)
