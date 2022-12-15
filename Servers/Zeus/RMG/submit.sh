#!/bin/bash -l

#PBS -N <name>  # Note: Manually change this job name, and delete this comment
#PBS -q zeus_new_q
#PBS -l walltime=72:00:00
#PBS -l select=1:ncpus=10
#PBS -o out.txt
#PBS -e err.txt

PBS_O_WORKDIR=~/runs/RMG/x1001/
cd $PBS_O_WORKDIR

conda activate rmg_env

python-jl $rmg_code/rmg.py -n 10 input.py

