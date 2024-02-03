import os
import json
import time

# TODO: Fix and reintroduce logger
# from log import setup_logger

DRMS_DATACUBE_PBS_PATH: str = "/nfshome/chmurnyd/GitHub/thesis-work/helio"
RUN_TT_PIPELINE_PBS_PATH: str = "/nfshome/chmurnyd/GitHub/thesis-work/helio"
RUN_TT_PIPELINE_WD: str = "/nfshome/chmurnyd/travel-times/torque/"

WAIT_TIME_BETWEEN_JOBS = 3 # Set at least to 2 seconds so as to avoid duplication in job ids (temstamps)

# TODO: Fix and reintroduce logger
# module_logger = setup_logger(__name__)

def run_drms_and_tt_via_bash(drms_wd: str, drms_ld: str, drms_conffile: str, tt_wd: str, tt_ld: str, tt_conffile: str):
    command = f'bash run_drms_and_tt.sh {DRMS_DATACUBE_PBS_PATH} {RUN_TT_PIPELINE_PBS_PATH} {drms_wd} {drms_ld} {drms_conffile} {tt_wd} {tt_ld} {tt_conffile}'
    print(f'Running command: {command}')
    os.system(command)

if __name__ == "__main__":
    with open("./datacube_pipeline_helper_files/datacube_maker_inputs.json", "r") as file:
        maker_inputs = json.load(file)
        
    for i, maker_input in enumerate(maker_inputs):
        working_dir = maker_input["working_dir"]
        log_dir = maker_input["log_dir"]
        conf_file = maker_input["conf_file"]
        
        tt_conf_file = maker_input["TT_conf_file"]
        tt_log_dir = maker_input["TT_log_dir"]
        
        print(f'Processing input no. {i}, WD: {working_dir}, LD: {log_dir}')

        run_drms_and_tt_via_bash(working_dir, log_dir, conf_file, RUN_TT_PIPELINE_WD, tt_log_dir, tt_conf_file)

        time.sleep(WAIT_TIME_BETWEEN_JOBS) # Wait for a short moment between requests so the cluster keeps up