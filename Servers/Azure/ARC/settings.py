
"""
ARC's settings
"""

import os
import string


servers = {
    'azure': {
        'cluster_soft': 'Slurm',
        'address': '{IPADDRESS}',
        'un': '{USERNAME}',
        'key': '/home/mambauser/.ssh/ubuntu.pem',
        'cpus': 16,
        'memory': 32,
        'path': '/mount/nfsshareslurm/nfs/{USERNAME}',
    },
}

global_ess_settings = {
    'qchem': ['azure'],
    'molpro': ['azure']
}

supported_ess = ['qchem',
'molpro']

# TS methods to try when appropriate for a reaction (other than user guesses which are always allowed):
ts_adapters = ['heuristics', 'AutoTST', 'GCN', 'KinBot']

default_job_settings = {
    'job_total_memory_gb': 32,
    'job_cpu_cores': 16,
}


check_status_command = {'OGE': 'export SGE_ROOT=/opt/sge; /opt/sge/bin/lx24-amd64/qstat',
                        'Slurm': '/usr/bin/squeue',
                        'PBS': '/opt/pbs/bin/qstat',
                        }

submit_command = {'OGE': 'export SGE_ROOT=/opt/sge; /opt/sge/bin/lx24-amd64/qsub',
                  'Slurm': '/usr/bin/sbatch',
                  'PBS': '/opt/pbs/bin/qsub',
                  }

delete_command = {'OGE': 'export SGE_ROOT=/opt/sge; /opt/sge/bin/lx24-amd64/qdel',
                  'Slurm': '/usr/bin/scancel',
                  'PBS': '/opt/pbs/bin/qdel',
                  }

list_available_nodes_command = {'OGE': 'export SGE_ROOT=/opt/sge; /opt/sge/bin/lx24-amd64/qstat -f | grep "/8 " | grep "long" | grep -v "8/8"| grep -v "aAu"',
                                'Slurm': 'sinfo -o "%n %t %O %E"',
                                'PBS': '/opt/pbs/bin/pbsnodes',
                                }


