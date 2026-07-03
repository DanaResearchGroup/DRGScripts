"""
Local T3 submit scripts for the Zeus (PBS) cluster.

T3 loads this file from ``~/.t3/t3_submit.py`` and updates its built-in
``submit_scripts`` with the entries below. T3 fills the 'rmg' template via
str.format() with: name, cpus, memory, workdir, max_iterations.
"""

submit_scripts = {
    'rmg': """#!/bin/bash -l

#PBS -N {name}
#PBS -q alon_q
#PBS -l walltime=72:00:00
#PBS -l select=1:ncpus={cpus}:host=n170
#PBS -o out.txt
#PBS -e err.txt

PBS_O_WORKDIR={workdir}
cd $PBS_O_WORKDIR

conda activate rmg_env

touch initial_time

python $rmgpy_path/rmg.py {max_iterations} -n {cpus} input.py

touch final_time
""",
}
