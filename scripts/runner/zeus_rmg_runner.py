#!/usr/bin/env python3
# encoding: utf-8

"""
A "keep alive" runner tool for RMG on Zeus (you should use Screen for it...),
to be executed locally on the head node from an arc_env.

Execution from a folder that contains an RMG input.py file and bears the name of the run (e.g., 'x1001'):

python zeus_rmg_runner.py
"""

import datetime
import os
import time

from arc.job.local import execute_command, parse_running_jobs_ids


NODES = 1
CPUS = 20
SUBMIT_COMMAND = '/usr/local/bin/qsub'
SLEEP_TIME = 2  # hours

submit_file = """#!/bin/bash -l

#PBS -N {name}
#PBS -q zeus_all_q
#PBS -l walltime=24:00:00
#PBS -l select={nodes}:ncpus={cpus}
#PBS -o out.txt
#PBS -e err.txt

PBS_O_WORKDIR={pwd}
cd $PBS_O_WORKDIR

conda activate rmg_env

python-jl ~/Code/RMG-Py/rmg.py -n {cpus} input.py

"""


def write_submit_script(pwd: str, name: str):
    """Write the submit.sh file"""
    content = submit_file.format(pwd=pwd, name=name, nodes=NODES, cpus=CPUS)
    with open('submit.sh', 'w') as f:
        f.write(content)


def log_message(content: str, runner_log_path: str, add_empty_lines=False):
    """Append a message to the runner log file"""
    local_time = datetime.datetime.now().strftime("%H%M%S_%b%d_%Y")
    content = '\n\n\n' if add_empty_lines else f'{local_time}: {content} \n'
    mode = 'a' if os.path.isfile(runner_log_path) else 'w'
    with open(runner_log_path, mode) as f:
        f.write(content)


def submit_job(path: str, runner_log_path: str):
    """Submit the RMG job"""
    job_status = ''
    job_id = 0
    cmd = f"cd {path}; {SUBMIT_COMMAND} submit.sh"
    stdout, stderr = execute_command(cmd)
    if not len(stdout):
        time.sleep(10)
        stdout, stderr = execute_command(cmd)
    if not len(stdout):
        return None, None
    if len(stderr) > 0 or len(stdout) == 0:
        log_message(f'Got the following error when trying to submit job:\n{stderr}.', runner_log_path)
        job_status = 'errored'
    else:  # PBS
        job_id = stdout[0].split('.')[0]
    log_message(f'Successfully submitted job {job_id}.', runner_log_path)
    return job_status, job_id


def check_running_jobs_ids() -> list:
    """
    Check which jobs are still running on the server for this user.

    Returns:
        List(str): List of job IDs.
    """
    cmd = '/usr/local/bin/qstat -u $USER'
    stdout = execute_command(cmd)[0]
    running_job_ids = parse_running_jobs_ids(stdout, cluster_soft='pbs')
    return running_job_ids


def determine_rmg_conversion(rmg_log_path: str):
    """Determine whether an RMG job has converged"""
    rmg_converged = False
    with open(rmg_log_path, 'r') as f:
        lines = f.readlines()
        len_lines = len(lines)
        for i in range(10):
            if 'MODEL GENERATION COMPLETED' in lines[len_lines - i]:
                rmg_converged = True
                break
    return rmg_converged


def write_restart_file(pwd: str, runner_log_path: str):
    """Convert an RMG input file into an RMG restart file"""
    restart_string = "restartFromSeed(path='seed')"
    rmg_input_path = os.path.join(pwd, 'input.py')
    with open(rmg_input_path, 'r') as f:
        content = f.read()
    if restart_string not in content:
        log_message('Converting the RMG input file into an RMG restart file', runner_log_path)
        content = f'{restart_string}\n\n{content}'
        with open(rmg_input_path, 'w') as f:
            f.write(content)


def main():
    """The main executable function"""
    pwd = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    name = os.path.split(pwd)[-1]
    rmg_log_path = os.path.join(pwd, 'RMG.log')
    runner_log_path = os.path.join(pwd, 'rmg_runner.log')
    if os.path.isfile(runner_log_path):
        log_message('', runner_log_path, add_empty_lines=True)
    log_message('Initializing', runner_log_path)

    if not os.path.isfile('submit.sh'):
        log_message('writing submit script', runner_log_path)
        write_submit_script(pwd, name)

    job_status, job_id = submit_job(path=pwd, runner_log_path=runner_log_path)

    rmg_converged = False

    while not rmg_converged:
        server_job_ids = check_running_jobs_ids()
        if job_id not in server_job_ids:
            # job has completed
            log_message('RMG job terminated', rmg_log_path)
            rmg_converged = determine_rmg_conversion(rmg_log_path)
            if rmg_converged:
                log_message('RMG has converged!\n'
                            'Terminating runner', rmg_log_path)
                break
            log_message('RMG did not converge', rmg_log_path)
            write_restart_file(pwd, runner_log_path)
            log_message('Re-running RMG', rmg_log_path)
            job_status, job_id = submit_job(path=pwd, runner_log_path=runner_log_path)
        else:
            log_message('RMG is still running', rmg_log_path)
        log_message(f'Slipping for {SLEEP_TIME} hours. ZZZ... ZZZ...', rmg_log_path)
        time.sleep(SLEEP_TIME * 60 * 60)  # wait SLEEP_TIME hours before bugging the servers again


if __name__ == '__main__':
    main()
