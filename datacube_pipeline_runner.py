import os
import json
import subprocess
import time

DRMS_DATACUBE_PBS_PATH: str = "/nfsscratch/chmurnyd"
# PIPELINE_DEPENDENCIES_SH_PATH: str = "pipeline_dependencies.sh"
RUN_TT_PIPELINE_PBS_PATH: str = "/nfsscratch/chmurnyd/thesis-work/"
RUN_TT_PIPELINE_WD: str = "/nfsscratch/chmurnyd/travel-times/torque"

SLEEP_TIME_AFTER_FIRST_REQUEST: int = 900 # in seconds - for 1 day request 900 s (15 min) is optimal --> other request types can be scaled accordingly

#! Not used now - replaced by bash function
# TODO: Utilize or delete.
def run_datacube_creation_query(working_dir:str, log_dir:str, conf_file_path:str):
    os.chdir(DRMS_DATACUBE_PBS_PATH)
    command = f'qsub -l nodes=radegast-local -v WD={working_dir},LD={log_dir},CONFFILE={conf_file_path} drms_datacube.pbs'
    print(f'Running datacube creation query with a command: {command}')
    # os.system(command)
    result = subprocess.run(command, capture_output=True, shell=True, text=True)
    output = result.stdout
    print(f'Query ran succesfully. Output: {output}.')
    
    return output

def run_traveltime_pipeline_job_on_datacube(datacube_job_id: str, conf_file_path: str):
    os.chdir(RUN_TT_PIPELINE_PBS_PATH)
    command = f'qsub -W depend=afterok:{datacube_job_id} -v WD={RUN_TT_PIPELINE_WD},CONFFILE={conf_file_path} run_tt_pipeline.pbs'
    print(f'Running TT pipeline job with a command: {command}')    

    result = subprocess.run(command, capture_output=True, shell=True, text=True)
    output = result.stdout
    print(f'Query ran succesfully. Output: {output}.')
    
    return output
#!#!#!#!#!#!#!#!#!#!#!#!#

def run_drms_and_tt_via_bash(drms_wd:str, drms_ld:str, drms_conffile:str, tt_wd:str, tt_conffile:str):
    command = f'bash run_drms_and_tt.sh {DRMS_DATACUBE_PBS_PATH} {RUN_TT_PIPELINE_PBS_PATH} {drms_wd} {drms_ld} {drms_conffile} {tt_wd} {tt_conffile}'
    print(f'Running command: {command}')
    os.system(command)

if __name__ == "__main__":
    with open("./datacube_maker_inputs.json", "r") as file:
        maker_inputs = json.load(file)
        
    for i, maker_input in enumerate(maker_inputs):
        print(f'Processing input no. {i}...')
        working_dir = maker_input["working_dir"]
        log_dir = maker_input["log_dir"]
        conf_file = maker_input["conf_file"]

        print(f'WD: {working_dir}')
        print(f'LOG dir: {log_dir}')
        
        #datacube_job_id = run_datacube_creation_query(working_dir, log_dir, conf_file)
        
        tt_conf_file = maker_input["TT_conf_file"]
        
        #run_traveltime_pipeline_job_on_datacube(datacube_job_id, tt_conf_file)

        run_drms_and_tt_via_bash(working_dir, log_dir, conf_file, RUN_TT_PIPELINE_WD, tt_conf_file)

        if i == 0:
            time.sleep(SLEEP_TIME_AFTER_FIRST_REQUEST)
        else:
            time.sleep(3) # wait before sending another request - so as not to get blocked by JSOC
