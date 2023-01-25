
"""
Submit scripts
sorted in a dictionary with server names as keys
"""


submit_scripts = {
    'local': {
        'gaussian': """#!/bin/bash -l

#PBS -q zeus_long_q
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
        'molpro': """#!/bin/bash -l

#PBS -q zeus_long_q
#PBS -N {name}
#PBS -l select=1:ncpus={cpus}:mem={memory}
#PBS -o out.txt
#PBS -e err.txt

PBS_O_WORKDIR={pwd}
cd $PBS_O_WORKDIR

MOLPRO_SCRDIR=/tmp/{un}/scratch/molpro/$PBS_JOBID
export MOLPRO_SCRDIR=$MOLPRO_SCRDIR
mkdir -p $MOLPRO_SCRDIR

which molpro

touch initial_time

cd $MOLPRO_SCRDIR

cp "$PBS_O_WORKDIR/input.in" $MOLPRO_SCRDIR

molpro -n {cpus} -d $MOLPRO_SCRDIR input.in

cp input.* "$PBS_O_WORKDIR/"

if [ ! -f geometry.* ]; then
	echo "Geometry files don't exist at this time"
else
	cp geometry.* ""$PBS_O_WORKDIR"/"
fi
       
rm -rf $MOLPRO_SCRDIR

touch final_time
    
        """
        },
}
