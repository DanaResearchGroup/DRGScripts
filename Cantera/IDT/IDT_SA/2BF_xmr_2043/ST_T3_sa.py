import os
import shutil

from arc.common import read_yaml_file
from t3 import T3
from t3.simulate.cantera_IDT import (CanteraIDT, get_idt_per_phi_p_condition,
                                     get_t_and_p_lists,
                                     plot_idt_vs_temperature)
from t3.utils.fix_cantera import fix_cantera

import re
import yaml
import arc.rmgdb as rmgdb
from arc.common import save_yaml_file
from arc.reaction import ARCReaction
import rmgpy.data.kinetics.family as family
from rmgpy.chemkin import load_chemkin_file, load_species_dictionary
from rmgpy.data.rmg import RMGDatabase
from rmgpy.reaction import Reaction
from rmgpy.species import Species

from matplotlib.offsetbox import AnnotationBbox, OffsetImage
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
# Import plotting modules and define plotting preference
plt.rcParams["axes.labelsize"] = 14
plt.rcParams["xtick.labelsize"] = 12
plt.rcParams["ytick.labelsize"] = 12
plt.rcParams["legend.fontsize"] = 10
plt.rcParams["figure.figsize"] = (8, 6)
plt.rcParams["figure.dpi"] = 120
# Get the best of both ggplot and seaborn
plt.style.use("ggplot")
plt.style.use("seaborn-deep")
plt.rcParams["figure.autolayout"] = True
#---------------------------------------------------------------

#Edit your IDT project name and iteration number
project_name = "2BF_xmr_2043"
restart_dir_name = 'xmr_2043_restart'
iteration_num = 1
T_list = [850, 1000, 1400, 1800] #K #the experimental range is 700-1990 K
P = 20 #bar
equivalence_ratio = [ 1, ]
#-----------------------INPUT FILES-----------------------------
chemkin_path = os.path.join(os.getcwd(),'data',project_name,f'iteration_{iteration_num}','RMG','cantera','chem_annotated.inp')
SIM_DIR = os.path.join(os.getcwd(),f'data/{project_name}')
FIG_DIR_IDT = os.path.join(SIM_DIR,f'iteration_{iteration_num}/Figures/')
dict_path = os.path.join(SIM_DIR,f'iteration_{iteration_num}','RMG','cantera','species_dictionary.txt')
restart_path = '/home/nellymitnik/Code/RMG-database/input' #rmgdb path on ZEUS!

#----------------------OUTPUT FILES--------------------------------------------------------------------
csv_path = os.path.join(SIM_DIR,f'iteration_{iteration_num}','csv_files')
imgs_path = os.path.join(SIM_DIR,f'iteration_{iteration_num}','images')
plots_path = os.path.join(SIM_DIR,f'iteration_{iteration_num}','plots')
if not os.path.exists(plots_path):
    os.makedirs(plots_path)
summary_yaml_path = os.path.join(SIM_DIR,f'iteration_{iteration_num}','summary.yml')
#------------------------------------------------------------------------------------------------------

#-----------------------------------Functions-----------------------------------------------------------
def find_rxn_lib_in_restart(restart_lib, rmg_rxn):
    rxn_lib = ""
    for rxn in restart_lib.get_library_reactions():
        if rmg_rxn.is_isomorphic(rxn):
            rxn_lib = rxn.library
    return rxn_lib

def check_same_rxn(from_ct_rxn, reactants, products):
    return Reaction.matches_species(from_ct_rxn, reactants, products)

def extract_pattern(text):
    # patterns of library or family from rxn note string in cantera output file
    library_pattern = r"Library reaction:\s*(.*)"
    family_pattern_1 = r"family:\s*(.*)"
    family_pattern_2 = r"Template reaction:\s*(.*)" 
    pdep_pattern = r"PDep reaction:\s*(.*)" 

    match = re.search(library_pattern, text)
    if match:
        return match.group(1).strip()
    match = re.search(family_pattern_1, text)
    if match:
        return match.group(1).strip()
    match = re.search(family_pattern_2, text)
    if match:
        return match.group(1).strip()
    match = re.search(pdep_pattern, text)
    if match:
        return match.group(1).strip()
    return "None"

def fix_stoich(reactants):
    i = 0
    while i < len(reactants):
        if reactants[i].isdigit():  
            multiplier = int(reactants[i]) 
            if i + 1 < len(reactants):  
                reactant = reactants[i + 1]
                repeated_reactant = [reactant] * (multiplier-1) #since one occurance already exists
                reactants[i + 1:i + 1] = repeated_reactant
            del reactants[i]
        else:
            i += 1
    return(reactants)

def get_rxn_dict(rxns, species, label_adj_dict ,T, gas):
    '''
    example:
    rxns_dict = {'rxn_label': {'rmg_rxn': rxn_rmg, 'family': rxn_rmg', 'img_path' = img_output_path}}
    summary_dict ={i: rxn_eq, 'source': 'H_Abstraction'}
    '''
    rxns_dict = {}
    summary_dict = {}
    for i,rxn in enumerate(rxns):
        index = gas.reaction_equations().index(rxn)
        text = gas.reactions()[index].input_data["note"]
        rmg_rxn, extracted_text = get_rxn(rxn, label_adj_dict, text)
        img_output_path = os.path.join(imgs_path,species, T,f"rxn_{i+1}.png")
        os.makedirs(os.path.dirname(img_output_path), exist_ok=True)
        rxns_dict [rxn] = {'rmg_rxn': rmg_rxn, 'source': extracted_text, 'img_path':img_output_path }
        rmg_rxn.draw(img_output_path)
        summary_dict[i+1] = {'reaction': rxn, 'source': extracted_text}
    return rxns_dict, summary_dict

def get_rxn(rxn_label, label_adj_dict, text=None):
    try:
        if ' <=> ' in rxn_label:
            label_splits = rxn_label.split(' <=> ')
        elif ' => ' in rxn_label:
            label_splits = rxn_label.split(' => ')
    except:
        raise ValueError("Invalid reaction format: must contain '=> ' or '<=> '")
    reactants = label_splits[0].split(' + ')
    reactants = [i.split(' ') for i in reactants]
    reactants = [value for sublist in reactants for value in sublist]
    reactants = fix_stoich(reactants)
    products = label_splits[1].split(' + ')
    products = [i.split(' ') for i in products]
    products = [value for sublist in products for value in sublist]
    products = fix_stoich(products)
    reactants = [label_adj_dict[label] for label in reactants if label != '(+M)']
    products = [label_adj_dict[label] for label in products if label != '(+M)']
    rxn_rmg = Reaction(reactants=reactants , products=products)
    if text is not None:
        extracted_text = extract_pattern(text)
        if extracted_text == "restart":
            rst_lib = find_rxn_lib_in_restart(restart_lib, rxn_rmg)
            if rst_lib != restart_dir_name and rst_lib != "":
                extracted_text = rst_lib
                print(rxn_rmg," restart lib is:", rst_lib)
    else: 
        extracted_text = None
    return rxn_rmg, extracted_text

def add_images_to_plot(ax, top_reactions, rxns_dict):
    # Load image for each reaction in top_reactions
    for i, reaction in enumerate(top_reactions):
        img_path = rxns_dict[reaction]['img_path']
        img = plt.imread(img_path)

        imagebox = OffsetImage(img, zoom=0.4)  
        ab = AnnotationBbox(imagebox, (-0.35, i+0.5), frameon=False, xycoords=('axes fraction', 'data'))

        # Add image to plot
        ax.add_artist(ab)

        # Add title as annotation text with smaller font size and above the image
        title_text = rxns_dict[reaction]['source']
        ax.annotate(title_text, xy=(1, i), xycoords=('axes fraction', 'data'),
                    xytext=(5,0), textcoords='offset points', fontsize=8,
                    color='black', va='center', ha='left')
#------------------------End Functions--------------------------------------------------------------------------                    

#--------------Load chemkin file and species dictionary----------------------------------------------------------
label_adj_dict = load_species_dictionary(dict_path)
#Do not change the Chemkin file from RMG, just copy paste it
species, reactions = load_chemkin_file(path=chemkin_path,
                                       dictionary_path=dict_path,
                                       check_duplicates=False,
                                       use_chemkin_names=True,
                                      )
#------------------------------------------------------------------------------------------------------------------

#-------------------------Load restart kinetics library-------------------------------------------------------------
restart_lib__path = os.path.join(restart_path,'kinetics','libraries', restart_dir_name)
restart_lib = ""
if os.path.exists(restart_lib__path):
    #load rmg restart library from rmgdb
    database = RMGDatabase()
    database.load(path=restart_path,
                thermo_libraries=[],
                reaction_libraries=[restart_dir_name],
                seed_mechanisms=[],
                kinetics_families=[])
    restart_lib = database.kinetics.libraries[restart_dir_name]
#--------------------------------------------------------------------------------------------------------------------

for T in T_list:
    #Load T3 input file of your project into a dictionairy
    yaml_file_path = os.path.join(SIM_DIR,'input.yml')
    input_dict = read_yaml_file(yaml_file_path)

    #print the T3 input file dictionairy:
    for k,v in input_dict.items():
        print(k,v)

    #create a t3 object from your T3 run:
    rmg_args = input_dict["rmg"]
    t3_args = input_dict["t3"]
    qm_args = input_dict["qm"]

    t3 = T3(project=project_name,
            t3=t3_args,
            rmg=rmg_args,
            qm=qm_args,
            )

    t3.iteration = iteration_num

    t3.project_directory = SIM_DIR
    t3.set_paths()
    t3.rmg['reactors'] = [{'type': 'gas batch constant T P',
                            'T': T, 'P': P,
                            'termination_rate_ratio': 0.01},
                            ]
    t3.rmg['species'] = [{'label': '2BF', 'smiles': 'CCCCC1=CC=CO1', 'concentration': 0, 'role': 'fuel',
                            'equivalence_ratios': equivalence_ratio},
                            {'label': 'O2', 'smiles': '[O][O]', 'concentration': 0, 'role': 'oxygen'},
                            {'label': 'N2', 'smiles': 'N#N', 'concentration': 0, 'role': 'nitrogen'}]
    ct_adapter = CanteraIDT(t3=t3.t3,
                            rmg=t3.rmg,
                            paths=t3.paths,
                            logger=t3.logger,
                            atol=t3.rmg['model']['atol'],
                            rtol=t3.rmg['model']['rtol'],
                            )

    sa_dict = ct_adapter.get_sa_coefficients(dk = 1e-2, T= T, P=P)
    print("sa_dict:",sa_dict)

    observables = ct_adapter.radical_label
    import pandas as pd

    sensitivities = pd.DataFrame(index=ct_adapter.model.reaction_equations(), columns=[T])
    for rxn_indx in sa_dict['kinetics'][observables].keys():
        rxn_str = ct_adapter.model.reaction_equation(rxn_indx)
        sensitivities.loc[rxn_str, T] = sa_dict['kinetics'][observables][rxn_indx]

    # Build the directory path
    dir_path = os.path.join(SIM_DIR, f'iteration_{iteration_num}', str(observables))
    # Create the directory if it doesn't exist
    os.makedirs(dir_path, exist_ok=True)
    # Build the file path
    file_path = os.path.join(dir_path, f"{T}_sa_results_final.csv")

    # Save the DataFrame to CSV
    sensitivities.to_csv(file_path)
    
    top_n = 20  # Number of top values to consider (double the number in case there is a duplicate to each rxn)
    dict_summary = {}

    dict_T_top10rxns = {}
    file_name = os.path.join(SIM_DIR,f'iteration_{iteration_num}', observables ,'sa_results_final.csv')
    if os.path.exists(file_name):
        sensitivities = pd.read_csv(file_name, index_col=0) #rxns equesions are the rows IDs
        temperatures = sensitivities.columns  # column indices
        for T in temperatures:
            sensitivities_T = sensitivities.loc[:, T]
            # Sort absolute values and select top 10
            top_sensitivities = sensitivities_T.abs().nlargest(top_n).drop_duplicates(keep='first')
            top_sensitivities = top_sensitivities.head(int(top_n/2))
            # Get rxns equations (meaning, the rows' indices of the top sensitivities)
            top_reactions = top_sensitivities.index
            rxns_dict = get_rxn_dict(top_reactions, observables, label_adj_dict, T, ct_adapter.model)[0]
            dict_T_top10rxns[T] = get_rxn_dict(top_reactions, observables, label_adj_dict, T, ct_adapter.model)[1]
            fig, ax = plt.subplots(figsize= (10,6))
            sensitivities_subset = sensitivities.loc[top_reactions, T].drop_duplicates(keep='first')
            sensitivities_subset.plot.barh(ax=ax, title=f"Top Sensitivities for {T} K", legend=None)
            ax.set_yticks(range(len(top_reactions)))
            ax.set_yticklabels(top_reactions, fontsize=9)
            ax.invert_yaxis()
            ax.set_xlabel(f"Sensitivity: $\\frac{{\\partial\\:\\ln{{C_{{{observables}}}}}}}{{\\partial\\:\\ln{{k}}}}$")
            add_images_to_plot(ax, top_reactions, rxns_dict)
            formatter = ScalarFormatter(useMathText=True)
            formatter.set_scientific(True)
            formatter.set_powerlimits((-2, 2))
            ax.xaxis.set_major_formatter(formatter)
            plt.tight_layout()
            plot_path = os.path.join(plots_path, f"{observables}_{T}K_sa_top10.png")
            plt.savefig(plot_path, dpi=300)
    dict_summary[observables]= dict_T_top10rxns

    rxn_distinct_list =[]
    for obsrv in dict_summary.keys():
        for T in dict_summary[obsrv]:
            for i in dict_summary[obsrv][T].keys(): #iterate over indicies
                rxn_distinct_list.append(dict_summary[obsrv][T][i]['reaction'])

    rxn_distinct_list = list(dict.fromkeys(rxn_distinct_list)) #remove duplicate rxns

    ct_chemkin_dict ={}
    for ct_rxn in rxn_distinct_list:
        rxn_rmg = get_rxn(ct_rxn, label_adj_dict)[0]
        reactants = rxn_rmg.reactants
        products = rxn_rmg.products
        for rxn in reactions:
            if check_same_rxn(rxn, reactants, products):
                ct_chemkin_dict[ct_rxn] = rxn

    new_yaml_data = {}
    for obsrv in dict_summary.keys():
        T_dict={}
        for T in dict_summary[obsrv]:
            rxn_dict={}
            for i in dict_summary[obsrv][T].keys():
                source = dict_summary[obsrv][T][i]['source']
                reaction = dict_summary[obsrv][T][i]['reaction']
                kinetics = ct_chemkin_dict[reaction].kinetics
                rxn_dict[i] ={'reaction': reaction, "source":source, "kinetics": str(kinetics)}
            T_dict[T] = rxn_dict
        new_yaml_data[obsrv]=T_dict

    save_yaml_file(path=summary_yaml_path,
                content=new_yaml_data,
                )
