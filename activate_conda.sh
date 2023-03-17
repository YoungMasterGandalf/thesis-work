#! /bin/bash

echo "Running hook ..."
eval "$(/nfshome/ANACONDA3/bin/conda shell.bash hook)" &
wait
echo "Activating conda environment ..." &
conda activate py39
