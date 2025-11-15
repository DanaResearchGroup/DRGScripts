#!/bin/bash -l

#PBS -N ST_2BF_xmr_2043
#PBS -q mafat_new_q
#PBS -l select=1:ncpus=16
#PBS -o out.txt
#PBS -e err.txt

source /home/nellymitnik/.bashrc

PBS_O_WORKDIR=~/runs/scripts_runs/SA/ST/2BF_xmr_2043/
cd $PBS_O_WORKDIR

conda activate t3_env

python /home/nellymitnik/runs/scripts_runs/SA/ST/2BF_xmr_2043/ST_T3_sa.py
