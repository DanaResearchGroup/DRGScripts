# User specific aliases and functions


# RMG-Py
export rmgpy_path='~/Code/RMG-Py/'
export rmgdb_path='~/Code/RMG-Py/'
export PYTHONPATH=$PYTHONPATH:~/Code/RMG-Py/

# ARC
export arc_path='~/Code/ARC/'
export PYTHONPATH=$PYTHONPATH:~/Code/ARC/

# T3
export t3_path='~/Code/T3/'
export PYTHONPATH=$PYTHONPATH:~/Code/T3/

# g09
source /usr/local/g09/setup.sh


# aliases

alias rmge='conda activate rmg_env'
alias arce='conda activate arc_env'
alias t3e='conda activate t3_env'
alias deact='conda deactivate'
alias rc='source ~/.bashrc'
alias erc='nano ~/.bashrc'
alias rce='nano ~/.bashrc'
alias rmgcode='cd $rmgpy_path'
alias dbcode='cd $rmgdb_path'
alias arcode='cd $arc_path'
alias t3code='cd $t3_path'
alias runs='cd ~/runs'
alias rmg='python-jl $rmgpy_path/rmg.py input.py  > >(tee -a stdout.log) 2> >(tee -a stderr.log >&2)'
alias sb='qsub submit.sh'
alias st='qstat -u $USER'
