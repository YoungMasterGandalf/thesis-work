import json
import subprocess

DRMS_DATACUBE_PBS_PATH: str = "drms_datacube.pbs"
# PIPELINE_DEPENDENCIES_SH_PATH: str = "pipeline_dependencies.sh"
RUN_TT_PIPELINE_PBS_PATH: str = "run_tt_pipeline.pbs"
RUN_TT_PIPELINE_WD: str = "./torque"

def run_datacube_creation_query(working_dir:str, log_dir:str, conf_file_path:str):
    command = f'qsub -v WD={working_dir},LD={log_dir},CONFFILE={conf_file_path} {DRMS_DATACUBE_PBS_PATH}'
    
    # os.system(command)
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    output = result.stdout
    
    return output

def run_traveltime_pipeline_job_on_datacube(datacube_job_id: str, conf_file_path: str):
    command = f'qsub -W depend=afterok:{datacube_job_id} {RUN_TT_PIPELINE_PBS_PATH} -v WD={RUN_TT_PIPELINE_WD},CONFFILE={conf_file_path}'
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    output = result.stdout
    
    return output

if __name__ == "__main__":
    with open("./datacube_maker_inputs.json", "r") as file:
        maker_inputs = json.load(file)
        
    for maker_input in maker_inputs:
        working_dir = maker_input["working_dir"]
        log_dir = maker_input["log_dir"]
        conf_file = maker_input["conf_file"]
        
        datacube_job_id = run_datacube_creation_query(working_dir, log_dir, conf_file)
        
        tt_conf_file = maker_input["TT_conf_file"]
        
        run_traveltime_pipeline_job_on_datacube(datacube_job_id, tt_conf_file)
