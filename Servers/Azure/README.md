# Setting up ARC to use Azure

If you are a recognised user on the Cyclecloud and have provided your public key from your Office machine, you are then well on your way to submitting jobs from your Office machine.

Firstly, submitting jobs to Azure is not how you would submit jobs to Atlas or Zeus. For Atlas and Zeus, we have copies of RMG/ARC/T3 on those servers and can need to ssh into those servers to submit jobs. 

For Azure, it is **different**. RMG, ARC and T3 are not installed on the scheduler. Instead, you will install them *locally* on your machine. You will run the jobs *locally* from your *local* terminal, and with the right settings, the jobs that concern QChem, MolPro etc. will be submitted to the scheduler via ssh (which you do not need to do manually).

So how do you set this up?

1. Ensure you have copies of RMG, ARC and T3 on your local machine. You can do this by cloning the repositories from GitHub.
2. Ensure you have properly installed the Conda environments for RMG, ARC and T3. You can do this by following the instructions in the respective repositories. I strongly suggest using `mambaforge` instead of `anaconda` or `miniconda`. You can install `mambaforge` by following the instructions [here](https://github.com/conda-forge/miniforge)
   1. If you have already installed `anaconda` or `miniconda`, then don't worry about it. However, I do strongly suggest you do run the following and then you should use the command `mamba` instead of `conda`:
        1. `conda update -n base --all`
        2. `conda install mamba -n base -c conda-forge`
   2. If your environments are already installed, then please ensure that rmg_env works properly. You can do this by activating the rmg environment and running `python-jl rmg.py --help` (for rmg_env - this should run without error). If you get an error, then you will need to reinstall the environment.
3. Ensure you have the `ubuntu-image_key.pem`. This should be placed into your `.ssh` folder in your home directory. If you do not have this, you can get it from the Dropbox folder - `DanaResearchGroup/Azure/SHH Private Key/`. If you do not have access to this folder, please contact me.
    1. Once this file is in your `.ssh` folder, you will need to change the permissions of the file. You can do this by typing `chmod 600 ~/.ssh/ubuntu-image_key.pem` in your terminal. 
    2. You will also need to add this key to your ssh agent. You can do this by typing `ssh-add ~/.ssh/ubuntu-image_key.pem` in your terminal.
4. Ensure you have a `.arc` folder in your home directory with customised settings and submission scripts. You can download them in this repository. Please see below [here](#file-settingspy) for more information on editing the settings file.
5. [**Optional**] Ensure you have a `.t3` folder in your home directory with customised settings and submission scripts. These have not been created yet, but will be soon. If you would like to use T3, please contact me and we can work on it together.
6. You are now ready to submit jobs to Azure!
7. In order to now run the job, you can either run it via your local terminal or through VSCode, although the latter is more for debugging purposes - If you are interested in debugging then go [here](#debugging-via-vscode).
8. To run the job via your local terminal, you will need first install `screen`. Youcan do this by typing `sudo apt install screen` in your terminal. You will only needto do this once.
9. Open a local terminal to where your `input.yml` file is located. Then, as youwould on Atlas, you set up a screen - `screen -S <name>`.
10. Activate then the relevant environment - `conda activate rmg_env` or `condaactivate arc_env` or `conda activate t3_env`.
11. Then, type either `rmg` or `arc` or `t3` to run the job.
12. Congratulations! You now have a running input file that is communicating withthe scheduler and submitting jobs to Azure.
13. Let's now check the status of a job - to do this, in another terminal you willneed to ssh into the Azure Scheduler using your username. You can do this by typing`ssh <username>@<IPADDRESS>`. 
14. When you are in, you can type `squeue` to see the status of your jobs. You canalso type `sinfo` to see the status of the nodes. Alternatively, I have createduniversal aliases for these commands, so you can type `st` or `stall` to see thestatus of your jobs and everyone else's jobs, respectively. You can also type`scancelall` to cancel all of your jobs.
15. If you would like to see the output of a job, you will need to navigate to the folder through Azure Scheduler like so:
        1. `cd /mount/nfsshareslurm/nfs/<username>/runs/ARC_Projects/<projectname>/`
        2. `ls` to see the output files
        3. `cat <outputfile>` to see the output of the file

> **Note**: You can make accessing the mounted driver easier by creating a soft link in your home directory. You can do this by typing the following in your terminal:
> ```bash
>ln -s /mount/ /shared/home/<USERNAME>/mount
>```
   
## File: settings.py

You will need to edit the file `settings.py` and change the following lines:

```python

servers = {
    'azure': {
        'cluster_soft': 'Slurm',
        'address': '{IPADDRESS}', # Edit line - IP address of the scheduler if it changes
        'un': '{USERNAME}', # Edit line - your username
        'key': '/home/{LOCAL_USERNAME}/.ssh/ubuntu-image_key.pem', # Edit line - path to private key
        'cpus': 16,
        'memory': 60,
        'path': '/mount/nfsshareslurm/nfs/',
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

### Windows [Work in Progress]

3. On your out of office machine, open a Command Prompt or PowerShell window and type `notepad %userprofile%\.ssh\authorized_keys`. Paste the output from the previous step into this file and save it.
4. Change the permissions of the authorized_keys file by typing `icacls %userprofile%\.ssh\authorized_keys /inheritance:r /grant:r "%username%":"(R)"`. This command removes any inherited permissions from the file and grants read access to the current user only.
5. Now, you should be able to access the scheduler from your out of office machine.

## Debugging via VSCode

First of all, ensure you have VSCode installed on your local machine. You can download it [here](https://code.visualstudio.com/download).

Secondly, have the following extensions installed - execute these commands in your terminal:

```bash
code --install-extension chekweitan.compare-view
code --install-extension christian-kohler.path-intellisense
code --install-extension codezombiech.gitignore
code --install-extension donjayamanne.git-extension-pack
code --install-extension donjayamanne.githistory
code --install-extension eamodio.gitlens
code --install-extension fnando.linter
code --install-extension GitHub.vscode-pull-request-github
code --install-extension GrapeCity.gc-excelviewer
code --install-extension ms-python.isort
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension ms-toolsai.jupyter
code --install-extension ms-toolsai.jupyter-keymap
code --install-extension ms-toolsai.jupyter-renderers
code --install-extension ms-toolsai.vscode-jupyter-cell-tags
code --install-extension ms-toolsai.vscode-jupyter-slideshow
code --install-extension ms-vscode.makefile-tools
code --install-extension rioj7.command-variable
code --install-extension rioj7.context-menu-extra
code --install-extension tal7aouy.theme
code --install-extension ziyasal.vscode-open-in-github
code --install-extension bierner.github-markdown-preview
code --install-extension bierner.markdown-checkbox
code --install-extension bierner.markdown-emoji
code --install-extension bierner.markdown-footnotes
code --install-extension bierner.markdown-mermaid
code --install-extension bierner.markdown-preview-github-styles
code --install-extension bierner.markdown-yaml-preamble
```


Use the following settings.json for debugging:

```json
{    
    // Use IntelliSense to learn about possible attributes.
    // Hover to view descriptions of existing attributes.
    // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: RMG_Env",
            "type": "python",
            "request": "launch",
            "program": "~/Code/RMG-Py/rmg.py",
            "console": "integratedTerminal",
            "justMyCode": false,
            "args": ["${input:pickDir}/input.py"]
        },
        {
            "name": "Python: ARC_Env",
            "type": "python",
            "request": "launch",
            "program": "~/Code/ARC/ARC.py",
            "console": "integratedTerminal",
            "justMyCode": false,
            "args": ["${input:pickDir}/input.yml"]
        },
        {
            "name": "Python: Restart_ARC_Env",
            "type": "python",
            "request": "launch",
            "program": "~/Code/ARC/ARC.py",
            "console": "integratedTerminal",
            "justMyCode": false,
            "args": ["${input:pickDir}/restart.yml"]
        },
        {
            "name": "Python: T3_Env",
            "type": "python",
            "request": "launch",
            "program": "~/Code/T3/T3.py",
            "console": "integratedTerminal",
            "justMyCode": true,
            "args": ["${input:pickDir}/input.yml"]
        }
    ],
    "inputs": [
        {
            "id": "pickDir",
            "type": "command",
            "command": "extension.commandvariable.file.pickFile",
            "args":{
                "include":"**/*",
                "display": "fileName",
                "description": "Subdirectory to process",
                "showDirs": true,
                "fromFolder":{"fixed":"PATH/TO/WHERE/INPUT/FILES/ARE/LOCATED"}
            }
        }
    ]
}
```
