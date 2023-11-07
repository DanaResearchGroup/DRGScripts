
"""
ARC's settings
"""

import os
import string


servers = {
    'local': {  # Each Zeus node containes 80 cores and 378 GB RAM
        'cluster_soft': 'PBS',
        'un': 'alon',
        'cpus': 16,  # 20
        'memory': 160,  # 360 / 4.0
    },
}

global_ess_settings = {
    'gaussian': 'local',
    'orca': 'local',
    'molpro': 'local',
}

supported_ess = ['gaussian', 'molpro', 'orca']

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


