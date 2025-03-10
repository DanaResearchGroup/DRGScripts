

# User specific aliases and functions. APPEND this to youe existing .bashrc file
# Note: Change the <user> keyword of the last "st" command to your own username (without the "<" and ">)


# RMG-Py
export rmgpy_path=~/Code/RMG-Py/
export rmgdb_path=~/Code/RMG-database/
export PYTHONPATH=$PYTHONPATH:~/Code/RMG-Py/

# ARC
export arc_path=~/Code/ARC/
export PYTHONPATH=$PYTHONPATH:~/Code/ARC/

# T3
export t3_path=~/Code/T3/
export PYTHONPATH=$PYTHONPATH:~/Code/T3/


# personalized aliases
alias rc='source ~/.bashrc'
alias rce='nano ~/.bashrc'
alias erc='nano ~/.bashrc'

alias rmge='conda activate rmg_env'
alias arce='conda activate arc_env'
alias t3e='conda activate t3_env'
alias cte='conda activate ct_env'
alias deact='conda deactivate'

alias rmgcode='cd $rmgpy_path'
alias dbcode='cd $rmgdb_path'
alias arcode='cd $arc_path'
alias t3code='cd $t3_path'

alias j='cd ~/scripts && jupyter notebook'

alias rmg='python-jl $rmgpy_path/rmg.py input.py  > >(tee -a stdout.log) 2> >(tee -a stderr.log >&2)'
alias arkane='python-jl $rmgpy_path/Arkane.py input.py  > >(tee -a stdout.log) 2> >(tee -a stderr.log >&2)'
alias arc='python $arc_path/ARC.py input.yml  > >(tee -a stdout.log) 2> >(tee -a stderr.log >&2)'
alias arcrestart='python $arc_path/ARC.py restart.yml  > >(tee -a stdout.log) 2> >(tee -a stderr.log >&2)'
alias t3='python $t3_path/T3.py input.yml  > >(tee -a stdout.log) 2> >(tee -a stderr.log >&2)'

alias runs='cd ~/runs'
alias rmg='python-jl $rmgpy_path/rmg.py input.py  > >(tee -a stdout.log) 2> >(tee -a stderr.log >&2)'
