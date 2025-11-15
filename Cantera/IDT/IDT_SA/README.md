# IDT script

This script is using the Cantera_IDT.py in T3: [Cantera_IDT](https://github.com/ReactionMechanismGenerator/T3/blob/idt_sa/t3/simulate/cantera_IDT.py)
<br>
<br>
In `data` folder, open your project folder (for example: `2BF_xmr_2043`).
<br>
Inside that folder, open another folder of your RMG iteration number, in convention of: iteration_num (for example: `iteration_1`).
<br>
Put your T3 input file inside the project folder.
<br>
Then, open `RMG` folder, and inside the latter, open `cantera` folder.
<br>
Then put there your `chem_annotated.yaml` file.
<br>
### Pay attention to how the radicals (OH + H) are written in chem_annotated.yaml and ,chem_annotated.inp and species_dictionary.txt: if they are written in a different convention than `OH(index_num)` or `H(index_num)`, then replace all the appearances to the mentioned convention.
<br>
Edit the project name and the iteration number inside the script.
Also copy the restart folder from rmg to rmgdb kinetics libraries in server
<br>
Edit T_list, P, equivalence_ratio
<br>
<br>
![example](/2BF_xmr_2043/data/2BF_xmr_2043/iteration_1/plots/OH(18)_1400K_sa_top10.png)
