from arkane.input import load_input_file
from arc import ARC
from arc.species import ARCSpecies
from arc.common import read_yaml_file

network_path = '/home/nelly/Desktop/xmr2001_try_script/network28_64.py'
arc_path='/home/nelly/Desktop/xmr2001_try_script/input.yml'
project_name_arc_input="pdep_28"

"""load_input_file returns a tuple of dicts. The 3rd dict is species_dict & the 4th dict is network_dict"""
tuple_from_input_file = load_input_file(network_path)
species_dict = tuple_from_input_file[2]
network_dict = tuple_from_input_file[4]
pdep_network_name = list(network_dict.keys())[0]
pdep_isomers = network_dict[pdep_network_name].isomers #configuration object
pdep_isomers=[str(isomer) for isomer in pdep_isomers] #list of isomer strings
labels_adj_dict=dict()

for species in species_dict.values():
    """ Sometimes RMG doesn't have a library thermo for a radical species, but it does have library thermo for 
        the corresponding non-radical structure.
        So it takes the library value and adds a radical correction to it. Sometimes it's good, other times less. 
        In this case, the thermo comment would be: "LibraryName + radical(groupName)". """
    if species.label in pdep_isomers and ('Thermo group additivity estimation:' in species.thermo.comment or 'radical(' in species.thermo.comment):
        """the method to_adjacency_list return a string of label in first line and adj in rest
        Keep the adj only by removing the first string line"""
        print(species.to_adjacency_list().split('\n', 1)[1])
        labels_adj_dict[species.label]=species.to_adjacency_list().split('\n', 1)[1]

print(f'\nGot {len(list(labels_adj_dict.keys()))} isomers with group additivity in thermo in this network.')

"""create an input file for ARC with RMG library as an output"""

def adj_to_arc( smiles, adjc):
    try:
        print( " good adjc_list: ", smiles, "\n", adjc)
        return (ARCSpecies(label=smiles, adjlist=adjc))

    except Exception:
        print(i, " bad adjc_list: ", smiles, "\n", adjc)
        pass

arc_1 = ARC(project=project_name_arc_input,
            level_of_theory='CBS-QB3',
            # adjc list to ARC
            species=list([adj_to_arc(key, labels_adj_dict[key]) for key in labels_adj_dict.keys()]),
            allow_nonisomorphic_2d=False,
            compute_thermo=True,
            job_types={'opt': True, 'fine': False, 'freq': False, 'rotors': False, 'sp': False},
            ess_settings={'gaussian': 'local'},
            # trsh_ess_jobs=False,
            )
arc_1.write_input_file(arc_path)

