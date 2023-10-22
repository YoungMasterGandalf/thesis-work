#!/bin/bash

# Check if correct number of arguments are provided
if [ $# -ne 2 ]; then
    echo "Usage: $0 <folder_path> <pattern>"
    exit 1
fi

folder_path=$1
pattern=$2

# Go to the folder
cd "$folder_path" || exit

# Activate conda environment on the cluster
echo "Running hook ..."
eval "$(/software/anaconda3/bin/conda shell.bash hook)"
echo "Activating conda environment ..."

# Find folders containing the pattern and pass each as an argument to the python script
find . -type d -name "$pattern" -exec python analyze_f_and_p_mode_results.py {} \;

echo "Finished analyzing folders."
