#!/bin/bash -l

#PBS -q zeus_long_q
#PBS -N {name}
#PBS -l select=1:ncpus={cpus}:mem={memory}
#PBS -o out.txt
#PBS -e err.txt

PBS_O_WORKDIR={pwd}
cd $PBS_O_WORKDIR

conda activate rmg_env

python-jl $rmg_code/rmg.py -n 10 input.py

