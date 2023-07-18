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
environment   = "GAUSS_EXEDIR=/Local/ce_dana/g09 GAUSS_SCRDIR=/storage/ce_dana/{un}/scratch/g09/{name}/ g09root=/Local/ce_dana"

should_transfer_files = no

executable = job.sh

request_cpus  = {cpus}
request_memory = {memory}MB

queue

""",
        # will be renamed to ``job.sh`` when uploaded
        'gaussian_job': """#!/bin/csh

touch initial_time

mkdir -p $GAUSS_SCRDIR

source /Local/ce_dana/g09/bsd/g09.login

/Local/ce_dana/g09/g09 < input.gjf > output.out

rm -rf $GAUSS_SCRDIR

touch final_time

""",

        # Molpro
        'molpro': """Universe      = vanilla

+JobName      = "{name}"

log           = job.log
output        = out.txt
error         = err.txt

getenv        = True
+PATH         = "/Local/ce_dana/molpro-mpp-2021.2.1/bin:$PATH"
environment   = "MOLPRO_SCRDIR=/storage/ce_dana/{un}/scratch/molpro/{name}/ SUBMIT_DIR={pwd}"

should_transfer_files = no

executable = job.sh

request_cpus  = {cpus}
request_memory = {memory}MB

queue

""",
        # will be renamed to ``job.sh`` when uploaded
        'molpro_job': """#!/bin/csh

touch initial_time

mkdir -p $MOLPRO_SCRDIR
cd $MOLPRO_SCRDIR

cp "$SUBMIT_DIR/input.in" .

/Local/ce_dana/molpro-mpp-2022.2.3/bin/molpro -n {cpus} -t 1 output.out

cp input.* "$SUBMIT_DIR/"
if [ ! -f geometry.* ]; then echo "Geometry files don't exist at this time" else cp geometry*.* "$SUBMIT_DIR/" fi

rm -rf $MOLPRO_SCRDIR

touch final_time

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

touch initial_time

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

${OrcaDir}/orca input.in > output.out
cp * "$SubmitDir/"

rm -rf $WorkDir

touch final_time

""",
    },
}

