"""
T3's settings

You may keep a short version of this file in a local ".t3" folder under your home folder.
Any definitions made to the local file will take precedence over this file.
"""


# The execution type can be either 'incore', i.e., executed in the same processor,
# or 'local', i.e., to be submitted to the server queue if running on a server.
# If running on a local server, ARC's settings for ``local`` will be used.
execution_type = {
    'rmg': 'queue',
    'arc': 'queue',
}

servers = {
    'azure': {
        'cluster_soft': 'Slurm',
        'address': '{IPADDRESS}',
        'un': '{USERNAME}',
        'key': '/home/{LOCAL_USERNAME}}/.ssh/ubuntu-image_key.pem',
        'cpus': 16,
        'memory': 32,
        'path': '/mount/nfsshareslurm/nfs/',
        'max_job_time': '128:00:00'
    },
}

check_status_command = {'OGE': 'export SGE_ROOT=/opt/sge; /opt/sge/bin/lx24-amd64/qstat -u $USER',
                        'Slurm': '/usr/bin/squeue -u $USER',
                        'PBS': '/usr/local/bin/qstat -u $USER',
                        'HTCondor': """condor_q -cons 'Member(Jobstatus,{1,2})' -af:j '{"0","P","R","X","C","H",">","S"}[JobStatus]' RequestCpus RequestMemory JobName  '(Time() - EnteredCurrentStatus)'""",
                        }

submit_command = {'OGE': 'export SGE_ROOT=/opt/sge; /opt/sge/bin/lx24-amd64/qsub',
                  'Slurm': '/usr/bin/sbatch',
                  'PBS': '/usr/local/bin/qsub',
                  'HTCondor': 'condor_submit',
                  }

submit_filenames = {'OGE': 'submit.sh',
                    'Slurm': 'submit.sl',
                    'PBS': 'submit.sh',
                    'HTCondor': 'submit.sub',
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

rmg_initial_memory = 25  # The initial memory for an RMG job when submitted to the queue, in GB


