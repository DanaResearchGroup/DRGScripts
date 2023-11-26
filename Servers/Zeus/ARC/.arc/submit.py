
"""
Submit scripts
sorted in a dictionary with server names as keys
"""


submit_scripts = {
    'local': {
        'gaussian': """#!/bin/bash -l

#PBS -q mafat_new_q
#PBS -N {name}
#PBS -l select=1:ncpus={cpus}:mem={memory}:mpiprocs={cpus}
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

rm -vrf $GAUSS_SCRDIR

touch final_time

        """,
        'molpro': """#!/bin/bash -l

#PBS -q zeus_long_q
#PBS -N {name}
#PBS -l select=1:ncpus={cpus}:mem={memory}:mpiprocs={cpus}
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
       
rm -vrf $MOLPRO_SCRDIR

touch final_time
    
        """,
        'orca': """#!/bin/bash -l

#PBS -q mafat_new_q
#PBS -N {name}
#PBS -l select=1:ncpus={cpus}:mem={memory}
#PBS -o out.txt
#PBS -e err.txt

. ~/.bashrc

export OrcaDir=/usr/local/orca-5.0.4
export PATH=$PATH:$OrcaDir

export OMPI_Dir=/usr/local/openmpi-4.1.1
export PATH=$PATH:$OMPI_Dir

export LD_LIBRARY_PATH=/usr/local/openmpi-4.1.1/lib:$LD_LIBRARY_PATH

PBS_O_WORKDIR={pwd}
cd $PBS_O_WORKDIR

touch initial_time

ORCA_SCRDIR=/gtmp/$PBS_JOBID
mkdir -p $ORCA_SCRDIR
export ORCA_SCRDIR=$ORCA_SCRDIR
cd $ORCA_SCRDIR 

source /usr/local/orca-5.0.4/setup.sh
source /usr/local/openmpi-4.1.1/setup.sh

which orca

cp "$PBS_O_WORKDIR/input.in" .

${{OrcaDir}}/orca input.in > input.log

cd $PBS_O_WORKDIR
cp "$ORCA_SCRDIR/input.log" .
cp "$ORCA_SCRDIR/input_property.txt" .

touch final_time

rm -vrf $ORCA_SCRDIR
        """,
        },
}
