import argparse
import os
import yaml

from rmgpy.chemkin import load_species_dictionary
from rmgpy.molecule.draw import MoleculeDrawer

def parse_command_line_arguments(command_line_args=None):
    """
    Parse command-line arguments.

    Args:
        command_line_args: The command line arguments.

    Returns:
        The parsed command-line arguments by key words.
    """

    parser = argparse.ArgumentParser(description='desc')
    parser.add_argument('file', metavar='FILE', type=str, nargs=1,
                        help='a file describing the job to execute')

    args = parser.parse_args(command_line_args)
    args.file = args.file[0]

    return args


def dict_species(path_species_dict):
    """
    This fucn creates an output.yml file of cantera_labels as keys
    and smiles as values.
    After that, it creates a folder of images of the species of pdf format (high resolution)
    The name of the images are {smiles}.pdf
    """
    #######output.yml#######
    dir_name=os.path.dirname(path_species_dict)
    species_dict=load_species_dictionary(path_species_dict)
    #generate_resonance_structures=False)
    dict_label_smiles={species.label: species.molecule[0].to_smiles() for species in species_dict.values()}

    path_output_yml=os.path.join(dir_name,"output.yml")
    yaml_str = yaml.dump(data=dict_label_smiles)
    with open(path_output_yml, 'w') as f:
        f.write(yaml_str)
    
    #######species images#######
    if not os.path.exists(os.path.join(os.path.abspath(''),"images")): #check whether images folder exists
        images_path=os.path.join(os.path.abspath(''),'images')
        os.mkdir(images_path)
        os.chdir(images_path)
        
    else: #images folder exists
        if "images" not in os.getcwd(): #can be Flux diagram folder or species_dictionary.txt file inside Flux folder -> check the 2 options
            if "species_dictionary" in os.getcwd():
                os.chdir(os.path.join(os.chdir("../"),"images"))
            else:
                os.chdir(os.path.join(os.getcwd(),"images"))
        else:
            pass #we are probably in the right filder of images
                
    print("the images path: ",os.path.abspath(''))

    for specie in species_dict.values():
        molecule=specie.molecule[0]
        smiles=molecule.to_smiles() 
        if smiles != "[Ne]" and smiles != "[Ar]": #avoid parenthesis for elements - keep convention with Cantera
            MoleculeDrawer().draw(molecule, file_format='pdf', target=f'{smiles}.pdf')
        else:
            if smiles=="[Ne]":
                MoleculeDrawer().draw(molecule, file_format='pdf', target='Ne.pdf')
            else:
                MoleculeDrawer().draw(molecule, file_format='pdf', target='Ar.pdf')


def main():
    """
    The main ARC executable function
    """
    args = parse_command_line_arguments()
    
    if "images" in os.getcwd():
        os.chdir("../") #go back one folder back in current working dir path
    
    path=os.path.normpath(os.getcwd() )
    path_species_dict = os.path.join(path,'species_dictionary.txt')

    dict_species(path_species_dict)
   
if __name__ == '__main__':
    main()
