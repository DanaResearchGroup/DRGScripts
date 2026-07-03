"""
Local T3 settings for the Zeus (PBS) cluster.

T3 loads this file from ``~/.t3/t3_settings.py`` and any variable defined here
overrides the corresponding one in T3's built-in ``t3/settings/t3_settings.py``.
Each override replaces the whole variable, so dicts below are kept complete.
"""

# Execution type per software:
#   'incore' - run in the calling T3 process
#   'local'  - submit a job to this server's queue
# RMG is submitted to the Zeus queue; ARC runs in-process and submits its own
# ESS jobs via Servers/Zeus/ARC/.arc.
execution_type = {
    'rmg': 'local',
    'arc': 'incore',
}

servers = {
    'local': {  # Each Zeus node has 80 cores and 378 GB RAM
        'cluster_soft': 'PBS',
        'cpus': 16,
        'max mem': 40,  # GB
    },
}

# Zeus keeps its PBS binaries under /opt/pbs/bin (matches Servers/Zeus/ARC/.arc/settings.py).
check_status_command = {
    'OGE': 'export SGE_ROOT=/opt/sge; /opt/sge/bin/lx24-amd64/qstat -u $USER',
    'Slurm': '/usr/bin/squeue -u $USER',
    'PBS': '/opt/pbs/bin/qstat -u $USER',
    'HTCondor': """condor_q -cons 'Member(Jobstatus,{1,2})' -af:j '{"0","P","R","X","C","H",">","S"}[JobStatus]' RequestCpus RequestMemory JobName '(Time() - EnteredCurrentStatus)'""",
}

submit_command = {
    'OGE': 'export SGE_ROOT=/opt/sge; /opt/sge/bin/lx24-amd64/qsub',
    'Slurm': '/usr/bin/sbatch',
    'PBS': '/opt/pbs/bin/qsub',
    'HTCondor': 'condor_submit',
}

submit_filenames = {
    'OGE': 'submit.sh',
    'Slurm': 'submit.sl',
    'PBS': 'submit.sh',
    'HTCondor': 'submit.sub',
}

rmg_initial_memory = 25  # GB, initial memory for an RMG job submitted to the queue
