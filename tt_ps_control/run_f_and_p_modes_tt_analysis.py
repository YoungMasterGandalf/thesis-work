import os
import sys
import re
import subprocess

def main(folder_path, pattern):
    # Store current working dir (containing the python script for data analysis) to a variable
    python_script_dir = os.getcwd()
    python_script_path = os.path.join(python_script_dir, "analyze_f_and_p_mode_results.py")

    # Go to the folder
    os.chdir(folder_path)

    # Activate conda environment on the cluster
    print("Running hook ...")
    subprocess.run(["/software/anaconda3/bin/conda", "shell.bash", "hook"])
    print("Activating conda environment ...")

    # Compile regex pattern
    regex_pattern = re.compile(pattern)

    # Find folders containing the pattern and pass each as an argument to the python script
    for folder in os.listdir("."):
        if os.path.isdir(folder) and regex_pattern.match(folder):
            subprocess.run(["python", python_script_path, folder])
            print(f"Finished analyzing {folder}.")
            # subprocess.run(["sleep", "3"])

    print("Finished analyzing folders.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <folder_path> <pattern>")
        sys.exit(1)

    folder_path = sys.argv[1]
    pattern = sys.argv[2]
    main(folder_path, pattern)
