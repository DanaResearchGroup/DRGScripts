# Don't forget to replace all ocurrences of "[username]" with your actual username on Atlas (also delete the brackets, [ and ]). You may delete this line now.

# >>> conda initialize >>>
__conda_setup="$('/Local/ce_dana/anaconda3/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/Local/ce_dana/anaconda3/etc/profile.d/conda.sh" ]; then
        . "/Local/ce_dana/anaconda3/etc/profile.d/conda.sh"
    else
        export PATH="/Local/ce_dana/anaconda3/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<


# RMG-Py
export rmgpy_path='/Local/ce_dana/Code/RMG-Py/'
export rmgdb_path='/Local/ce_dana/Code/RMG-database/'
export PYTHONPATH=$PYTHONPATH:/Local/ce_dana/Code/RMG-Py/

# ARC
export arc_path='/Local/ce_dana/Code/ARC/'
export PYTHONPATH=$PYTHONPATH:/Local/ce_dana/Code/ARC/
export PYTHONPATH=$PYTHONPATH:/Local/ce_dana/Code/AutoTST/
export PYTHONPATH=$PYTHONPATH:/Local/ce_dana/Code/KinBot/
export PYTHONPATH=$PYTHONPATH:/Local/ce_dana/Code/TS-GCN/

# T3
export t3_path='/Local/ce_dana/Code/T3/'
export PYTHONPATH=$PYTHONPATH:/Local/ce_dana/Code/T3/

# TCKDB
export tckdb_path='/Local/ce_dana/Code/TCKDB/'
export PYTHONPATH=$PYTHONPATH:/Local/ce_dana/Code/TCKDB/

# RMS
export PATH="$HOME/julia/bin:$PATH"

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

alias rmg='python $rmgpy_path/rmg.py input.py'
alias arkane='python $rmgpy_path/Arkane.py input.py'
alias arc='python $arc_path/ARC.py input.yml'
alias t3='python $t3_path/T3.py input.yml'

alias tst='pytest -ra -vv'

alias sb='condor_submit submit.sub'
alias st='condor_q -cons "Member(Jobstatus,{1,2})" -af:j "{\"0\",\"P\",\"R\",\"X\",\"C\",\"H\",\">\",\"S\"}[JobStatus]" RequestCpus RequestMemory JobName "(Time() - EnteredCurrentStatus)"'
alias runs='cd /storage/ce_dana/[username]/runs'

