"""
Submit scripts and incore commands
"""

# commands to execute ESS incore (without cluster software submission)
# stored as a dictionary with server and software as primary and secondary keys
incore_commands = {
    'local': {
        'gaussian': ['g16 < input.gjf > input.log', 'formchk check.chk check.fchk'],
    },
}

# Submission scripts for pipe.py stored as a dictionary with server as the key
pipe_submit = {
    'local': """#!/bin/bash -l
#SBATCH -p normal
#SBATCH -J {name}
#SBATCH -N 1
#SBATCH -n {cpus}
#SBATCH --time={t_max}
#SBATCH --mem-per-cpu={memory}
#SBATCH --array=1-{max_task_num}  # todo??
#SBATCH -o out.txt
#SBATCH -e err.txt

source activate arc_env

python {arc_path}/job/scripts/pipe.py {hdf5_path}

""",
}

# Submission scripts stored as a dictionary with server and software as primary and secondary keys
submit_scripts = {
    'local': {
        # Atlas uses HTCondor, see docs here: https://htcondor.readthedocs.io/en/latest/
        # Gaussian 09
        'gaussian': """Universe      = vanilla

+JobName      = "{name}"

log           = job.log
output        = out.txt
error         = err.txt

getenv        = True
+g09root      = "/Local/ce_dana"
+PATH         = "$(g09root)/g09:$PATH"
+GAUSS_EXEDIR = "$(g09root)/g09:$GAUSS_EXEDIR"
environment   = "GAUSS_EXEDIR=/Local/ce_dana/g09 GAUSS_SCRDIR=/storage/ce_dana/{un}/scratch/g09/ g09root=/Local/ce_dana"

should_transfer_files = no

executable = job.sh

request_cpus  = {cpus}
request_memory = {memory}MB

queue

""",
        # will be renamed to ``job.sh`` when uploaded
        'gaussian_job': """#!/bin/csh

touch start

source /Local/ce_dana/g09/bsd/g09.login

/Local/ce_dana/g09/g09 < input.gjf > input.log

""",

        # Orca
        'orca': """Universe      = vanilla

+JobName      = "{name}"

log           = job.log
output        = out.txt
error         = err.txt

getenv        = True
+WorkDir      = "/storage/ce_dana/{un}/scratch/orca/{name}"
environment   = "WorkDir=/storage/ce_dana/{un}/scratch/orca/{name}"

should_transfer_files = no

executable = job.sh

request_cpus  = {cpus}
request_memory = {memory}MB

queue

""",
        # will be renamed to ``job.sh`` when uploaded
        'orca_job': """#!/bin/bash -l

export OrcaDir=/Local/ce_dana/orca_4_0_1_2_linux_x86-64_openmpi202
export PATH=$PATH:$OrcaDir

export OMPI_Dir=/Local/ce_dana/openmpi-2.0.2/bin
export PATH=$PATH:$OMPI_Dir

export LD_LIBRARY_PATH=/Local/ce_dana/openmpi-2.0.2/lib:$LD_LIBRARY_PATH

SubmitDir=`pwd`

which orca

mkdir -p $WorkDir
cd $WorkDir

cp "$SubmitDir/input.in" .

${OrcaDir}/orca input.in > input.log
cp * "$SubmitDir/"

rm -rf $WorkDir

""",
    },
}

