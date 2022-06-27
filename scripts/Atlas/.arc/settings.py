"""
ARC's settings
"""

import os
import string
import sys

servers = {
    'local': {
        'path': '/storage/ce_dana/',
        'cluster_soft': 'HTCondor',
        'un': '[username]',
        'cpus': 8,
        'memory': 256,
    },
}

# List here servers you'd like to associate with specific ESS.
# An ordered list of servers indicates priority
# Keeping this dictionary empty will cause ARC to scan for software on the servers defined above
global_ess_settings = {
    'gaussian': 'local',
    'orca': 'local',
    'molpro': 'local',
}

# Electronic structure software ARC may access (use lowercase):
supported_ess = ['gaussian', 'molpro', 'orca']


# Default job memory, cpu, time settings
default_job_settings = {
    'job_total_memory_gb': 6,
    'job_cpu_cores': 8,
}

