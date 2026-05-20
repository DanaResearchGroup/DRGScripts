
"""
Submit scripts
sorted in a dictionary with server names as keys
"""


submit_scripts = {
    'local': {
        'gaussian': """#!/bin/bash -l

#PBS -q alon_q
#PBS -N {name}
#PBS -l select=1:ncpus={cpus}:mem={memory}mb:mpiprocs={cpus}
#PBS -o out.txt
#PBS -e err.txt

. ~/.bashrc

PBS_O_WORKDIR="{pwd}"
cd "$PBS_O_WORKDIR"

# source /usr/local/g09/setup.sh
# source /usr/local/g16/setup.sh
source /usr/local/g16-gpu/g16/setup.sh # faster gaussian 16 installation (rev C.02)

export GAUSS_SCRDIR="/gtmp/{un}/scratch/g16/$PBS_JOBID"

cleanup_on_kill() {{
    trap - TERM INT
    echo "Caught signal, cleaning up Gaussian scratch dir $GAUSS_SCRDIR"
    if [ -d "$GAUSS_SCRDIR" ]; then
        cp -f "$GAUSS_SCRDIR"/input.* "$PBS_O_WORKDIR/" 2>/dev/null
        cp -f "$GAUSS_SCRDIR"/check.chk "$PBS_O_WORKDIR/" 2>/dev/null
        cd "$PBS_O_WORKDIR"
        rm -rf "$GAUSS_SCRDIR"
    fi
    exit 143
}}
trap cleanup_on_kill TERM INT

mkdir -p "$GAUSS_SCRDIR"

touch initial_time

cd "$GAUSS_SCRDIR"

cp "$PBS_O_WORKDIR/input.gjf" "$GAUSS_SCRDIR/"

if [ -f "$PBS_O_WORKDIR/check.chk" ]; then
    cp "$PBS_O_WORKDIR/check.chk" "$GAUSS_SCRDIR/"
fi

g16 < input.gjf > input.log

cp input.* "$PBS_O_WORKDIR/"

if [ -f check.chk ]; then
    cp check.chk "$PBS_O_WORKDIR/"
fi

cd "$PBS_O_WORKDIR"
rm -rf "$GAUSS_SCRDIR"

touch final_time
""",
        'molpro': """#!/bin/bash -l

#PBS -q alon_q
#PBS -N {name}
#PBS -l select=1:ncpus={cpus}:mem={memory}mb:mpiprocs={cpus}
#PBS -o out.txt
#PBS -e err.txt

. ~/.bashrc

PBS_O_WORKDIR="{pwd}"
cd "$PBS_O_WORKDIR"

export MOLPRO_SCRDIR="/gtmp/{un}/scratch/molpro/$PBS_JOBID"

# $MOLPRO_SCRDIR also holds molpro's integral scratch files (via `-d`),
# which can be hundreds of GB for CCSD(T)/MRCI. DO NOT copy those back.
cleanup_on_kill() {{
    trap - TERM INT
    echo "Caught signal, cleaning up Molpro scratch $MOLPRO_SCRDIR"
    if [ -d "$MOLPRO_SCRDIR" ]; then
        cp -f "$MOLPRO_SCRDIR"/input.out "$PBS_O_WORKDIR/" 2>/dev/null
        cp -f "$MOLPRO_SCRDIR"/input.xml "$PBS_O_WORKDIR/" 2>/dev/null
        cp -f "$MOLPRO_SCRDIR"/geometry.* "$PBS_O_WORKDIR/" 2>/dev/null
        cd "$PBS_O_WORKDIR"
        rm -rf "$MOLPRO_SCRDIR"
    fi
    exit 143
}}
trap cleanup_on_kill TERM INT

mkdir -p "$MOLPRO_SCRDIR"

which molpro

touch initial_time

cd "$MOLPRO_SCRDIR"

cp "$PBS_O_WORKDIR/input.in" "$MOLPRO_SCRDIR/"

molpro -n {cpus} -d "$MOLPRO_SCRDIR" input.in

cp input.* "$PBS_O_WORKDIR/"

if compgen -G "geometry.*" >/dev/null; then
    cp geometry.* "$PBS_O_WORKDIR/"
fi

cd "$PBS_O_WORKDIR"
rm -rf "$MOLPRO_SCRDIR"

touch final_time
""",
        'qchem': """#!/bin/bash -l

#PBS -q alon_q
#PBS -N {name}
#PBS -l select=1:ncpus={cpus}:mem={memory}mb:mpiprocs={cpus}
#PBS -o out.txt
#PBS -e err.txt

. ~/.bashrc

. /usr/local/qchem/qcenv.sh

export PBS_O_WORKDIR="{pwd}"
cd "$PBS_O_WORKDIR"

export QCHEM_SCRDIR="/gtmp/{un}/qchem/$PBS_JOBID"
export QCSCRATCH="$QCHEM_SCRDIR/scratch"

cleanup_on_kill() {{
    trap - TERM INT
    echo "Caught signal, cleaning up QChem scratch $QCHEM_SCRDIR"
    if [ -d "$QCHEM_SCRDIR" ]; then
        cp -f "$QCHEM_SCRDIR"/output.out "$PBS_O_WORKDIR/" 2>/dev/null
        cp -f "$QCHEM_SCRDIR"/input.in "$PBS_O_WORKDIR/" 2>/dev/null
        cd "$PBS_O_WORKDIR"
        rm -rf "$QCHEM_SCRDIR"
    fi
    exit 143
}}
trap cleanup_on_kill TERM INT

mkdir -p "$QCSCRATCH"

cp "./input.in" "$QCHEM_SCRDIR/"

touch initial_time

cd "$QCHEM_SCRDIR"

qchem -nt {cpus} input.in output.out

rm -rf "$QCSCRATCH"

cp -fr "$QCHEM_SCRDIR"/* "$PBS_O_WORKDIR/"

cd "$PBS_O_WORKDIR"
rm -rf "$QCHEM_SCRDIR"

touch final_time
""",
        'orca': """#!/bin/bash -l

#PBS -q alon_q
#PBS -N {name}
#PBS -l select=1:ncpus={cpus}:mem={memory}mb:mpiprocs={cpus}
#PBS -o out.txt
#PBS -e err.txt

. ~/.bashrc

# export OrcaDir=/usr/local/orca-5.0.4
export OrcaDir=/usr/local/orca6
export PATH=$PATH:$OrcaDir

export OMPI_Dir=/usr/local/openmpi-4.1.1
export PATH=$OMPI_Dir:$PATH

export LD_LIBRARY_PATH=/usr/local/openmpi-4.1.1/lib:$LD_LIBRARY_PATH

# source /usr/local/orca-5.0.4/setup.sh
source /usr/local/orca6/setup.sh
source /usr/local/openmpi-4.1.1/setup.sh

PBS_O_WORKDIR="{pwd}"
cd "$PBS_O_WORKDIR"

export ORCA_SCRDIR="/gtmp/{un}/scratch/orca/$PBS_JOBID"

cleanup_on_kill() {{
    trap - TERM INT
    echo "Caught signal, cleaning up ORCA scratch $ORCA_SCRDIR"
    if [ -d "$ORCA_SCRDIR" ]; then
        cp -f "$ORCA_SCRDIR"/input.log "$PBS_O_WORKDIR/" 2>/dev/null
        cp -f "$ORCA_SCRDIR"/input.hess "$PBS_O_WORKDIR/" 2>/dev/null
        cp -f "$ORCA_SCRDIR"/input.property.txt "$PBS_O_WORKDIR/" 2>/dev/null
        cd "$PBS_O_WORKDIR"
        rm -rf "$ORCA_SCRDIR"
    fi
    exit 143
}}
trap cleanup_on_kill TERM INT

mkdir -p "$ORCA_SCRDIR"

touch initial_time

which orca

cd "$ORCA_SCRDIR"

cp "$PBS_O_WORKDIR/input.in" .

${{OrcaDir}}/orca input.in > input.log

cd "$PBS_O_WORKDIR"
cp "$ORCA_SCRDIR/input.log" .
cp "$ORCA_SCRDIR/input.hess" .
cp "$ORCA_SCRDIR/input.property.txt" .

rm -rf "$ORCA_SCRDIR"

touch final_time
""",
    },
}
