#!/bin/bash -l

#PBS -N <name>  # Note: Manually change this job name, and delete this comment
#PBS -q zeus_new_q
#PBS -l walltime=72:00:00
#PBS -l select=1:ncpus=1
#PBS -o out.txt
#PBS -e err.txt

PBS_O_WORKDIR=~/runs/ARC/<run_dir>/   # Note: Manually change "<run_dir>" to your run directory, and delete this comment
cd $PBS_O_WORKDIR

conda activate arc_env

python $arc_code/ARC.py input.yml
