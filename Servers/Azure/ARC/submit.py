submit_scripts = {
    'azure': {
        'qchem': """#!/bin/bash -l
#SBATCH -p hpc,htc
#SBATCH -J {name}
#SBATCH --account={un}
#SBATCH -N 1
#SBATCH --cpus-per-task={cpus}
#SBATCH --mem={memory}
#SBATCH -o out.txt
#SBATCH -e err.txt

# Load QChem module
module load easybuild/EasyBuild
module load QChem-6.1

# Get Current Directory
export CWD="{pwd}"

# Set up scratch directory
export SCRATCH=/mnt/{un}/scratch/$SLURM_JOB_ID
if [ -d $SCRATCH ]; then
        sudo rm -vrf $SCRATCH
fi
sudo mkdir -p $SCRATCH

# Change permissions
sudo chmod 777 $SCRATCH
export QCSCRATCH=$SCRATCH

echo "============================================================"
echo "Job ID : $SLURM_JOB_ID"
echo "Job Name : $SLURM_JOB_NAME"
echo "Starting on : $(date)"
echo "Running on node : $SLURMD_NODENAME"
echo "Current directory : "{pwd}""
echo "============================================================"

# Change permissions for {un} directory on the VM storage
export QC_RUN=/mnt/{un}/$SLURM_JOB_ID
sudo chmod 777 $QC_RUN

# Now, copy the input file to the VM storage
cp input.in $QC_RUN

# Create a file to measure the time of execution
touch initial_time

# Change directory to the VM storage
cd $QC_RUN

# Run QChem
qchem -slurm -nt {cpus} input.in output.out

# Remove the scratch directory 
sudo rm -vrf $SCRATCH

# Copy all the files back to the current directory
cp -vfr $QC_RUN/* "{pwd}"

# Change directory back to the current directory
cd "{pwd}"

# Create a file to measure the time of execution
touch final_time

    """,
        'molpro': """#!/bin/bash -l
#SBATCH -p hpc,htc
#SBATCH -J {name}
#SBATCH --account={un}
#SBATCH -N 1
#SBATCH --ntasks-per-node={cpus}
#SBATCH --mem={memory}
#SBATCH -o out.txt
#SBATCH -e err.txt

# Load Molpro module
module load easybuild/EasyBuild
module load Molpro-2022.3.1

# Set up scratch directory
export SCRATCH=/mnt/{un}/scratch/molpro/{name}
if [ -d $SCRATCH ]; then
        sudo rm -rf $SCRATCH
fi
sudo mkdir -p $SCRATCH
sudo chmod 777 $SCRATCH
export MOLPRO_TMPDIR=$SCRATCH

echo "============================================================"
echo "Job ID : $SLURM_JOB_ID"
echo "Job Name : $SLURM_JOB_NAME"
echo "Starting on : $(date)"
echo "Running on node : $SLURMD_NODENAME"
echo "Current directory : "{pwd}""
echo "============================================================"

# Create a file to measure the time of execution
touch initial_time

# Get Current Directory
export CWD="{pwd}"

# Create a directory on the VM storage
export MOLPRO_RUN=/mnt/{un}/molpro/{name}
sudo mkdir -p $MOLPRO_RUN
sudo chmod 777 $MOLPRO_RUN

# Now, copy the input file to the VM storage
cp input.in $MOLPRO_RUN

# Change directory to the VM storage
cd $MOLPRO_RUN

# Run Molpro
molpro -n{cpus} -d $MOLPRO_TMPDIR input.in -o output.out

sudo rm -rf $MOLPRO_TMPDIR

# Copy all the files back to the current directory
cp -vfr $MOLPRO_RUN/* "{pwd}"

# Change directory back to the current directory
cd "{pwd}"

# Create a file to measure the time of execution
touch final_time

    """,
        'orca': """#!/bin/bash -l
#SBATCH -p hpc,htc
#SBATCH -J {name}
#SBATCH --account={un}
#SBATCH -N 1
#SBATCH --ntasks-per-node={cpus}
#SBATCH --mem={memory}
#SBATCH -o out.txt
#SBATCH -e err.txt

# Load ORCA module
. /etc/profile.d/z00_lmod.sh
module load ORCA

# Set up scratch directory
export ORCA_SCRDIR=/mnt/{un}/orca/{name}
if [ -d $ORCA_SCRDIR ]; then
        sudo rm -rf $ORCA_SCRDIR
fi
sudo mkdir -p $ORCA_SCRDIR
sudo chmod 777 $ORCA_SCRDIR

echo "============================================================"
echo "Job ID : $SLURM_JOB_ID"
echo "Job Name : $SLURM_JOB_NAME"
echo "Starting on : $(date)"
echo "Running on node : $SLURMD_NODENAME"
echo "Current directory : "{pwd}""
echo "============================================================"

# Create a file to measure the time of execution
touch initial_time

# Get Current Directory
export CWD="{pwd}"

# Now, copy the input file to the VM storage
cp input.in $ORCA_SCRDIR

# Change directory to the VM storage
cd $ORCA_SCRDIR

# ORCA requires the full dir path to be used when running in parallel, hence this variable and the subsequent run
export ORCA_DIR=$(which orca)

# Run Orca
$ORCA_DIR input.in > input.log

# Copy all the files back to the current directory
cd $CWD
cp "$ORCA_SCRDIR/input.log" .
cp "$ORCA_SCRDIR/input_property.txt" .

sudo rm -vrf $ORCA_SCRDIR

# Create a file to measure the time of execution
touch final_time

    """

    },
}
