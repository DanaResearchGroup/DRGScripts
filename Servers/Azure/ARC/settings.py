
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

default_levels_of_theory = {'conformer': 'wb97x-d/def2-svp',  # it's recommended to choose a method with dispersion
                            'ts_guesses': 'wb97x-d/def-2svp',
                            'opt': 'wb97x-d/def2-tzvp',  # good default for Gaussian
                            # 'opt': 'wb97m-v/def2tzvp',  # good default for QChem
                            'freq': 'wb97x-d/def2-tzvp',  # should be the same level as opt (to calc freq at min E)
                            'scan': 'wb97x-d/def2-tzvp',  # should be the same level as freq (to project out rotors)
                            'sp': 'ccsd(t)-f12/cc-pvtz-f12',  # This should be a level for which BAC is available
                            # 'sp': 'b3lyp/6-311+g(3df,2p)',
                            'irc': 'wb97x-d/def2-tzvp',  # should be the same level as opt
                            'orbitals': 'wb97x-d3/def2-tzvp',  # save orbitals for visualization
                            'scan_for_composite': 'B3LYP/CBSB7',  # This is the frequency level of CBS-QB3
                            'freq_for_composite': 'B3LYP/CBSB7',  # This is the frequency level of CBS-QB3
                            'irc_for_composite': 'B3LYP/CBSB7',  # This is the frequency level of CBS-QB3
                            'orbitals_for_composite': 'B3LYP/CBSB7',  # This is the frequency level of CBS-QB3
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


