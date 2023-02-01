# Flux diagram
This script simulates your Shock Tube system through different time intervals and creates flux diagrams with species molecule images.

- Clone these scripts to a new folder: `Flux diagram`  <br><br>
- In the Cantera environment in terminal, install `conda install -c conda-forge pdf2image` <br><br>
- Copy from your RMG run the Cantera output `chem_annotated.cti` and paste it in the folder, (the given file is for running a test, so you can just rename it). <br><br>
- Same with the species dictionary `species_dictionary.txt`, (the given file is for running a test, so you can just rename it).<br><br>
- In the first code block in `cte_replace_labels_to_smiles v2.ipynb` change the 4 paths to your files' location. <br><br>
- Change the initial operating conditions of your Shock Tube system in the first code block in `cte_replace_labels_to_smiles v2.ipynb`.<br><br>
- Put attention to your system's elements. Cantera lables them as one thing and Smiles as another thing, you should consider that in the code itself.<br><br>
For instance, Argon's label in `cti` file is `Ar`, but in Smiles its label is `[Ar]`. For elements, you should consider Cantera's notation. Two cases are considered in the script: `Ar` and `Ne`.<br><br>
- Run the script `cte_replace_labels_to_smiles v2.ipynb` under Cantera environmemt.

## Output:<br>
Ignition delay time plot in the folder:<br><br>
![Idt](idt_plot.png)<br><br>

11 folder for 11 different times intervals: 
0.5tau, 0.6tau...tau, 1.1tau,...1.5tau<br>
In each folder you will find a `png` file which contains the flux diagram specified in theat time. <br><br>
For example:<br><br> 
![rxn_diagram_tau](ReactionPathDiagram.png)<br><br>
