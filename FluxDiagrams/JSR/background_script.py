import argparse
import os
import yaml
import shutil

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
    dir_name=os.path.dirname(path_species_dict)
    species_dict=load_species_dictionary(path_species_dict)
    dict_label_smiles={species.label: species.molecule[0].to_smiles() for species in species_dict.values()}

    path_output_yml=os.path.join(dir_name, "output.yml")
    yaml_str = yaml.dump(data=dict_label_smiles)
    with open(path_output_yml, 'w') as f:
        f.write(yaml_str)

    images_path = os.path.join(dir_name, 'images')
    shutil.rmtree(images_path, ignore_errors=True)
    os.mkdir(images_path)
    print(f"the images path: {images_path}")

    for specie in species_dict.values():
        smiles = specie.molecule[0].to_smiles() 
        if smiles == "[Ne]":
            MoleculeDrawer().draw(specie.molecule[0], file_format='pdf', target=os.path.join(images_path, 'Ne.pdf'))
        elif smiles == '[Ar]':
            MoleculeDrawer().draw(specie.molecule[0], file_format='pdf', target=os.path.join(images_path, 'Ar.pdf'))
        elif smiles == '[He]':
            MoleculeDrawer().draw(specie.molecule[0], file_format='pdf', target=os.path.join(images_path, 'He.pdf'))
        else:
            MoleculeDrawer().draw(specie.molecule[0], file_format='pdf', target=os.path.join(images_path, f'{smiles}.pdf'))


def main():
    """
    The main executable function
    """
    args = parse_command_line_arguments()
    dict_species(args.file)


if __name__ == '__main__':
    main()
