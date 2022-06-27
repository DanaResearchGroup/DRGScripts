# ADD these lines to youe .bashrc file on your LOCAL computer. Don't delete any of the existing lines in the .bashrc file.
# Don't forget to replace all ocurrences of "[username]" with your actual username on Atlas (also delete the brackets, "[" and "]").
# You may delete these three lines.


# RMG-Py
export rmgpy_path='~/Code/RMG-Py/'
export rmgdb_path='~/Code/RMG-database/'
export PYTHONPATH=$PYTHONPATH:~/Code/RMG-Py/

# ARC
export arc_path='~/Code/ARC/'
export PYTHONPATH=$PYTHONPATH:~/Code/ARC/
export PYTHONPATH=$PYTHONPATH:~/Code/AutoTST/
export PYTHONPATH=$PYTHONPATH:~/Code/KinBot/
export PYTHONPATH=$PYTHONPATH:~/Code/TS-GCN/

# T3
export t3_path='~/Code/T3/'
export PYTHONPATH=$PYTHONPATH:~/Code/T3/

# TCKDB
export tckdb_path='~/Code/TCKDB/'
export PYTHONPATH=$PYTHONPATH:~/Code/TCKDB/

# RMS
export PATH="$HOME/julia/bin:$PATH"


# Servers
alias atlas='ssh [username]@tech-ui02.hep.technion.ac.il'


# personalized aliases

alias rc='source ~/.bashrc'
alias rce='nano ~/.bashrc'
alias erc='nano ~/.bashrc'

alias rmge='conda activate rmg_env'
alias arce='conda activate arc_env'
alias tcke='conda activate tck_env'
alias t3e='conda activate t3_env'
alias rmse='conda activate rms_env'
alias deact='conda deactivate'

alias rmgcode='cd $rmgpy_path'
alias dbcode='cd $rmgdb_path'
alias arcode='cd $arc_path'
alias t3code='cd $t3_path'
alias tckcode='cd $tckdb_path'

alias j='cd ~Code/scripts && jupyter notebook'

alias rmg='python $rmgpy_path/rmg.py input.py'
alias arkane='python $rmgpy_path/Arkane.py input.py'
alias arc='python $arc_path/ARC.py input.yml'
alias t3='python $t3_path/T3.py input.yml'

alias tst='pytest -ra -vv'

alias gv='bash ~/Software/gview/gview.sh'  # You can change this path if you installed GaussView at a different location


