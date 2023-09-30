#! /bin/bash

echo "Running hook ..."
eval "$(/software/anaconda3/bin/conda shell.bash hook)"
echo "Activating conda environment ..."
