#!/bin/bash

# Check if correct number of arguments are provided
if [ $# -ne 2 ]; then
    echo "Usage: $0 <folder_path> <pattern>"
    exit 1
fi

# A path to working directory containing directories with travel time data from the TT pipeline
folder_path=$1

# Pattern for matching the directories with the data
# Pattern example: TT_hmi\.v_45s_(\d{4})\.(\d{2})\.(\d{2})_00\.00\.00_lon_(plus|minus)_(\d+)_lat_(plus|minus)_(\d+)_vel_(plus|minus)_(\d+)
# Pattern example match: TT_hmi.v_45s_2018.03.26_00.00.00_lon_plus_310_lat_plus_0_vel_minus_167
pattern=$2

# Store current working dir (containing the python script for data analysis) to a variable
python_script_dir=`pwd`

# Go to the folder
cd "$folder_path" || exit

# Activate conda environment on the cluster
echo "Running hook ..."
eval "$(/software/anaconda3/bin/conda shell.bash hook)"
echo "Activating conda environment ..."

python_script_path="$python_script_dir/python analyze_f_and_p_mode_results.py"
echo "Python script path: $python_script_path"

# Find folders containing the pattern and pass each as an argument to the python script
find . -type d -name "$pattern" -exec $python_script_path {} \;

echo "Finished analyzing folders."
