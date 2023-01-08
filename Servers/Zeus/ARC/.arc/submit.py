"""
Submit scripts
sorted in a dictionary with server names as keys
"""


submit_scripts = {
    'local': {
        'gaussian': """#!/bin/bash -l

#PBS -q zeus_all_q
#PBS -N {name}
#PBS -l select=1:ncpus={cpus}:mem={memory}
#PBS -o out.txt
#PBS -e err.txt

. ~/.bashrc

PBS_O_WORKDIR={pwd}
cd $PBS_O_WORKDIR

source /usr/local/g09/setup.sh

GAUSS_SCRDIR=/gtmp/$PBS_JOBID
mkdir -p $GAUSS_SCRDIR
export GAUSS_SCRDIR=$GAUSS_SCRDIR

which g09

touch initial_time

g09 < input.gjf > input.log

rm -rf $GAUSS_SCRDIR

touch final_time

        """,
        },
}


