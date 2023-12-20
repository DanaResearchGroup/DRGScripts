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

rm -vrf $GAUSS_SCRDIR

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

# Create a file to store the initial time
touch initial_time

# Command to create scratch directory and change directory to it
mkdir -p $MOLPRO_SCRDIR
cd $MOLPRO_SCRDIR

# Command to copy input files
cp "$SUBMIT_DIR/input.in" .

# Command to run Molpro
/Local/ce_dana/molpro-mpp-2022.2.3/bin/molpro -n {cpus} -t 1 -d $MOLPRO_SCRDIR input.in -o output.out

# Command to copy output files
cp output.* "$SUBMIT_DIR/"

# Command to copy geometry files if they exist
if ( ! -e `find . -name "geometry.*" -print -quit` ) then
    echo "Geometry files don't exist at this time"
else
    cp geometry.* "$SUBMIT_DIR/"
endif

# Clean up of scratch directory
rm -vrf $MOLPRO_SCRDIR

#Change directory back to the original directory
cd $SUBMIT_DIR

# Create a file to store the final time
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

SubmitDir={pwd}

which orca

mkdir -p $WorkDir
cd $WorkDir

cp "$SubmitDir/input.in" .

${OrcaDir}/orca input.in > output.out
cp * "$SubmitDir/"

rm -rf $WorkDir

touch final_time

""",
    
    
    # QChem
        'qchem': """Universe      = vanilla
        
+JobName      = "{name}"

log           = job.log
output        = out.txt
error         = err.txt

getenv        = True
+PATH         = "/Local/ce_dana/Q-Chem/bin:$PATH"
environment   = "QCSCRATCH=/storage/ce_dana/{un}/scratch/qchem/{name}/ SUBMIT_DIR=\"{pwd}\" QC=/Local/ce_dana/Q-Chem"


should_transfer_files = no

executable = job.sh

request_cpus  = {cpus}
request_memory = {memory}MB

queue
    
""",
        # will be renamed to ``job.sh`` when uploaded
        'qchem_job': """#!/bin/csh

# Create a file to store the initial time
touch initial_time

# Command to create scratch directory and change directory to it
mkdir -p $QCSCRATCH
cd $QCSCRATCH

# Command to copy input files
cp "$SUBMIT_DIR/input.in" .

# Command to run QChem
/Local/ce_dana/Q-Chem/bin/qchem -nt {cpus} input.in output.out    

# Command to copy output files
cp output.* "$SUBMIT_DIR/"

# Remove the scratch directory
rm -rf $QCSCRATCH

#Change directory back to the original directory
cd "$SUBMIT_DIR"

# Create a file to store the final time
touch final_time

"""
    },
}

