"""
Submit scripts
sorted in a dictionary with server names as keys
"""


submit_scripts = {
    'local': {
        'gaussian': """#!/bin/sh

#PBS -q zeus_all_q
#PBS -N {name}
#PBS -l select=1:ncpus={cpus}:mem={memory}
#PBS -o out.txt
#PBS -e err.txt

PBS_O_WORKDIR={pwd}
cd $PBS_O_WORKDIR

GAUSS_SCRDIR=/home/{un}/scratch/g09/$PBS_JOBID
export $GAUSS_SCRDIR
mkdir -p $GAUSS_SCRDIR

. ~/.bashrc

which g09

touch initial_time

source /usr/local/g09/setup.sh

g09 < input.gjf > input.log

rm -rf $GAUSS_SCRDIR

touch final_time

        """,
	        'molpro': """#!/bin/sh

#PBS -q zeus_all_q
#PBS -N {name}
#PBS -l select=1:ncpus={cpus}:mem={memory}
#PBS -o out.txt
#PBS -e err.txt

PBS_O_WORKDIR={pwd}
cd $PBS_O_WORKDIR

. ~/.bashrc

touch initial_time
chmod 777 $PBS_O_WORKDIR
/home/kaplan.kfir/Code/Molpro/bin/molpro -n {cpus} -t 1 input.in

touch final_time

        """,
          
        },
}


