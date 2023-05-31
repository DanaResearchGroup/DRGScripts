submit_scripts = {
    'azure': {
        'qchem': """#!/bin/bash -l
#SBATCH -p hpc
#SBATCH -J {name}
#SBATCH -N 1
#SBATCH --cpus-per-task={cpus}
#SBATCH --mem={memory}
#SBATCH -o out.txt
#SBATCH -e err.txt

# Source QChem environment
source /opt/qchem/qcenv.sh

# Set up Qchem
export QC=/opt/qchem

# Set up scratch directory
export SCRATCH=/mount/nfsshareslurm/nfs/{un}/scratch/qchem/{name}
if [ -d $SCRATCH ]; then
        rm -rf $SCRATCH
fi
mkdir -p $SCRATCH
export QCSCRATCH=$SCRATCH

echo "============================================================"
echo "Job ID : $SLURM_JOB_ID"
echo "Job Name : $SLURM_JOB_NAME"
echo "Starting on : $(date)"
echo "Running on node : $SLURMD_NODENAME"
echo "Current directory : $(pwd)"
echo "============================================================"

# Create a file to measure the time of execution
touch initial_time

# Run QChem
qchem -slurm -nt {cpus} input.in output.out

# Create a file to measure the time of execution
touch final_time

    """,
        'molpro': """#!/bin/bash -l
#SBATCH -p hpc
#SBATCH -J {name}
#SBATCH -N 1
#SBATCH --cpus-per-task={cpus}
#SBATCH --mem={memory}
#SBATCH -o out.txt
#SBATCH -e err.txt

# Set up scratch directory
export SCRATCH=/mount/nfsshareslurm/nfs/{un}/scratch/molpro/{name}
if [ -d $SCRATCH ]; then
        rm -rf $SCRATCH
fi
mkdir -p $SCRATCH
export MOLPRO_TMPDIR=$SCRATCH

echo "============================================================"
echo "Job ID : $SLURM_JOB_ID"
echo "Job Name : $SLURM_JOB_NAME"
echo "Starting on : $(date)"
echo "Running on node : $SLURMD_NODENAME"
echo "Current directory : $(pwd)"
echo "============================================================"

# Create a file to measure the time of execution
touch initial_time

# Run Molpro
molpro -n {cpus} -d $MOLPRO_TMPDIR input.in -o output.out

rm -rf $MOLPRO_TMPDIR

# Create a file to measure the time of execution
touch final_time

"""
    },
}
