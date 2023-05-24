# Accessing Azure Account Server From Out of Office

If you are a recognised user on the Cyclecloud and have provided your public key from your Office machine, you will then need to do the following to be able to access the scheduler using your Azure account.

This applies to:

- Out of office
- Home
- Docker Container

However, let's first review the steps to allow ARC to access the scheduler and submit jobs.

## File: settings.py

You will need to edit the file `settings.py` and change the following lines:

```python

servers = {
    'azure': {
        'cluster_soft': 'Slurm',
        'address': '{IPADDRESS}', # Edit line - IP address of the scheduler if it changes
        'un': '{USERNAME}', # Edit line - your username
        'key': '/home/mambauser/.ssh/ubuntu.pem', # Edit line - path to private key
        'cpus': 16,
        'memory': 32,
        'path': '/mount/nfsshareslurm/nfs/{USERNAME}', # Edit line - path to shared folder. You will only need to edit the username part of the path
    },
}
```

## Out of office access

Now, to access the scheduler from out of office, you will need to do the following:

1. Open a terminal on your office machine
2. Type `cat ~/.ssh/id_ed25519.pub` and copy the output (some users may have used a different key, so you may need to change the command to `cat ~/.ssh/id_rsa.pub`)

### Linux or Docker

3. On your out of office machine, open a terminal and type `nano ~/.ssh/authorized_keys`. Paste the output from the previous step into this file and save it.
4. Change the permissions of the file by typing `chmod 600 ~/.ssh/authorized_keys`.
5. Now, you should be able to access the scheduler from your out of office machine.

### Windows

3. On your out of office machine, open a Command Prompt or PowerShell window and type `notepad %userprofile%\.ssh\authorized_keys`. Paste the output from the previous step into this file and save it.
4. Change the permissions of the authorized_keys file by typing `icacls %userprofile%\.ssh\authorized_keys /inheritance:r /grant:r "%username%":"(R)"`. This command removes any inherited permissions from the file and grants read access to the current user only.
5. Now, you should be able to access the scheduler from your out of office machine.