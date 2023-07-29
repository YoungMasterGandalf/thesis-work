#!/bin/bash

drms_path=$1
tt_path=$2

drms_wd=$3
drms_ld=$4
drms_conffile=$5

tt_wd=$6
tt_conffile=$7

cd $drms_path
drms_output=`qsub -l nodes=radegast-local -v WD=$drms_wd,LD=$drms_ld,CONFFILE=$drms_conffile drms_datacube.pbs`
echo $drms_output

cd $tt_path
tt_output=`qsub -W depend=afterok:$drms_output -v WD=$tt_wd,CONFFILE=$tt_conffile run_tt_pipeline.pbs`
echo $tt_output
