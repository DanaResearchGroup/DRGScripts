# IDT script

This script is using the Cantera_IDT.py in T3: [Cantera_IDT](https://github.com/ReactionMechanismGenerator/T3/blob/idt/t3/simulate/cantera_IDT.py)
<br>
<br>
In `data` folder, open your project folder (for example: `2BF_xmr_2038`).
<br>
Inside that folder, open another folder of your RMG iteration number, in convention of: iteration_num (for example: `iteration_2`).
<br>
Put your T3 input file inside the project folder.
<br>
Then, open `RMG` folder, and inside the latter, open `cantera` folder.
<br>
Then put there your `chem_annotated.yaml` file.
<br>
## Pay attention how the radical (OH/H) is written in chem_annotated.yaml: if it's written in a different convention than `OH(index_num)` or `H(index_num)`, then replace all the appearances to the mentioned convention.
<br>
Edit the project name and the iteration number inside the script.
<br>
Edit your reactor parameters and species in the last code block.
<br>
<br>

### Results:
<br>After simulating an IDT, you wil get a `Figures` folder in which there will be two types of graphs.
<br>
![IDT](/data/2BF_xmr_2038/iteration_2/Figures/IDTs/R0_0.5_1.0bar_700.0K.png)
<br>
<br>
![IDT_vs_T](/data/2BF_xmr_2038/iteration_2/Figures/IDTs/IDT_vs_T/R0_0.5_1.0bar.png)
<br>
