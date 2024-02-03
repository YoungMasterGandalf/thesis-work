#!/bin/bash

drms_path=$1
tt_path=$2

drms_wd=$3
drms_ld=$4
drms_conffile=$5

tt_wd=$6
tt_ld=$7
tt_conffile=$8

cd $drms_path

## Run on radegast-local only --> should solve some issues with passing logs
drms_output=`qsub -l nodes=radegast-local -v WD=$drms_wd,LD=$drms_ld,CONFFILE=$drms_conffile drms_datacube.pbs`

## Run on any core --> better not use this
# drms_output=`qsub -v WD=$drms_wd,LD=$drms_ld,CONFFILE=$drms_conffile drms_datacube.pbs`

echo $drms_output

cd $tt_path
## Run on radegast-local only --> should solve some issues with passing logs
tt_output=`qsub -l nodes=radegast-local -W depend=afterok:$drms_output -v WD=$tt_wd,LD=$tt_ld,CONFFILE=$tt_conffile run_tt_pipeline.pbs`

## Run on any core --> better not use this
# tt_output=`qsub -W depend=afterok:$drms_output -v WD=$tt_wd,CONFFILE=$tt_conffile run_tt_pipeline.pbs`
echo $tt_output
