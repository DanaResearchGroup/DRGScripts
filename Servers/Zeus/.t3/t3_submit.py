"""
Submit scripts
"""

# Submission scripts stored as a dictionary with software as the primary key.
submit_scripts = {
    'rmg': """#!/bin/bash -l

#PBS -N {name}
#PBS -q zeus_long_q
#PBS -l walltime=168:00:00
#PBS -l select=1:ncpus={cpus}
#PBS -o out.txt
#PBS -e err.txt

PBS_O_WORKDIR={workdir}
cd $PBS_O_WORKDIR

conda activate rmg_env

touch initial_time

python-jl ~/Code/RMG-Py/rmg.py -n {cpus} input.py {max_iterations}

touch final_time

""",
}
