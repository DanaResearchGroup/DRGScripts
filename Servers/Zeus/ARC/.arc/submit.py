
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

PBS_O_WORKDIR="{pwd}"
cd "$PBS_O_WORKDIR"

source /usr/local/g09/setup.sh

GAUSS_SCRDIR="/gtmp/{un}/scratch/g09/$PBS_JOBID"

mkdir -p "$GAUSS_SCRDIR"

export GAUSS_SCRDIR="$GAUSS_SCRDIR"

touch initial_time

cd "$GAUSS_SCRDIR"

cp "$PBS_O_WORKDIR/input.gjf" "$GAUSS_SCRDIR"

if [ -f "$PBS_O_WORKDIR/check.chk" ]; then
    cp "$PBS_O_WORKDIR/check.chk" "$GAUSS_SCRDIR/"
fi

g09 < input.gjf > input.log

cp input.* "$PBS_O_WORKDIR/"

if [ -f check.chk ]; then
    cp check.chk "$PBS_O_WORKDIR/"
fi

rm -vrf "$GAUSS_SCRDIR"

cd "$PBS_O_WORKDIR"

touch final_time

        """,
        'molpro': """#!/bin/bash -l

#PBS -q zeus_long_q
#PBS -N {name}
#PBS -l select=1:ncpus={cpus}:mem={memory}:mpiprocs={cpus}
#PBS -o out.txt
#PBS -e err.txt

PBS_O_WORKDIR="{pwd}"
cd "$PBS_O_WORKDIR"

MOLPRO_SCRDIR="/tmp/{un}/scratch/molpro/$PBS_JOBID"
export MOLPRO_SCRDIR="$MOLPRO_SCRDIR"
mkdir -p "$MOLPRO_SCRDIR"

which molpro

touch initial_time

cd "$MOLPRO_SCRDIR"

cp "$PBS_O_WORKDIR/input.in" "$MOLPRO_SCRDIR/"

molpro -n {cpus} -d $MOLPRO_SCRDIR input.in

cp input.* "$PBS_O_WORKDIR/"

if [ ! -f geometry.* ]; then
	echo "Geometry files don't exist at this time"
else
	cp geometry.* ""$PBS_O_WORKDIR"/"
fi
       
rm -vrf "$MOLPRO_SCRDIR"

touch final_time
    
        """,
        'qchem': """#!/bin/bash -l
#PBS -q mafat_new_q
#PBS -N {name}
#PBS -l select=1:ncpus={cpus}:mem={memory}:mpiprocs={cpus}
#PBS -o out.txt
#PBS -e err.txt

# Source QChem environment
source /usr/local/qchem/qcenv.sh

# Set up Qchem
export QC=/usr/local/qchem

# Get Current Directory
export CWD="{pwd}"
cd $CWD

# Set up scratch directory
export SCRATCH=/gtmp/{un}/scratch/qchem/$PBS_JOBID
if [ -d $SCRATCH ]; then
        rm -vrf $SCRATCH
fi

mkdir -p $SCRATCH

# Now, copy the input file to the VM storage
cp input.in $SCRATCH

# Create a file to measure the time of execution
touch initial_time

# Change directory to the VM storage
cd $SCRATCH

# Run QChem
qchem -pbs -nt {cpus} input.in output.out

# Copy all the files back to the current directory
cp -vfr $SCRATCH/* $CWD

# Change directory back to the current directory
cd $CWD

# Remove the scratch directory 
rm -vrf $SCRATCH

# Create a file to measure the time of execution
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

PBS_O_WORKDIR="{pwd}"
cd "$PBS_O_WORKDIR"

touch initial_time

ORCA_SCRDIR="/gtmp/$PBS_JOBID"
mkdir -p "$ORCA_SCRDIR"
export ORCA_SCRDIR="$ORCA_SCRDIR"
cd "$ORCA_SCRDIR"

source /usr/local/orca-5.0.4/setup.sh
source /usr/local/openmpi-4.1.1/setup.sh

which orca

cp "$PBS_O_WORKDIR/input.in" .

${{OrcaDir}}/orca input.in > input.log

cd "$PBS_O_WORKDIR"
cp "$ORCA_SCRDIR/input.log" .
cp "$ORCA_SCRDIR/input_property.txt" .

touch final_time

rm -vrf "$ORCA_SCRDIR"
        """,
        },
}
