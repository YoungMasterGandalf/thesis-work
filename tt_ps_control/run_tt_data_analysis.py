import os
import sys
import re
import subprocess

PATTERN: str = "TT_hmi\.v_45s_(\d{4})\.(\d{2})\.(\d{2})_00\.00\.00_lon_(plus|minus)_(\d+)_lat_(plus|minus)_(\d+)_vel_(plus|minus)_(\d+)"
RUN_VIA_QSUB: bool = False

def main(folder_path, pattern):
    # Store current working dir (containing the python script for data analysis) to a variable
    python_script_dir = os.getcwd()
    python_script_path = os.path.join(python_script_dir, "analyze_tt_results.py")

    # Go to the folder
    os.chdir(folder_path)

    # Compile regex pattern
    regex_pattern = re.compile(pattern)

    # Find folders containing the pattern and pass each as an argument to the python script
    for folder in os.listdir("."):
        if os.path.isdir(folder) and regex_pattern.match(folder):
            subprocess.run(["python", python_script_path, folder])
            print(f"Finished analyzing {folder}.")

    print("Finished analyzing folders.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <folder_path>")
        sys.exit(1)

    folder_path = sys.argv[1]
    main(folder_path, PATTERN)
