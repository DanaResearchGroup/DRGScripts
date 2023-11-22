import os
import yaml
import shutil
from pdf2image import convert_from_path
from rmgpy.chemkin import load_species_dictionary
from rmgpy.molecule.draw import MoleculeDrawer
import pydot

def generate_pdf_files(dict_path):
    """
    Create file inside 'models' folder, named 'output_imgs.yaml', in which the keys are cantera species' labels and smiles labels are the values.
    Create a folder of images of all species in pdf format (high resolution)
    The names of the images follows: {smiles}.pdf
    Return specie_dict
    """
    dir_models_path = os.path.dirname(dict_path)
    print("models_dir_name: ",dir_models_path)
    species_dict = load_species_dictionary(dict_path)
    dict_label_smiles={species.label: species.molecule[0].to_smiles() for species in species_dict.values()}
    
    #create a yaml file of species_dict ({ct_label:smiles_label})
    path_output_yml=os.path.join(dir_models_path, "output_imgs.yml")
    yaml_str = yaml.dump(data=dict_label_smiles)
    with open(path_output_yml, 'w') as f:
        f.write(yaml_str)

    #create a folder for species images
    images_path = os.path.join(dir_models_path, 'images')
    if os.path.exists(images_path):
        #if folder exists, remove its content and create a new folder
        #this is to avoid previous unrelated files
        shutil.rmtree(images_path, ignore_errors=True)

    os.mkdir(images_path)
    
    #Create pdf files for each specie
    for specie in species_dict.values():
        smiles = specie.molecule[0].to_smiles() 
        #Elements in cantera yaml are represented as symbols, BUT in smiles they should be put in squared parenthesis
        if smiles == "[Ne]":
            MoleculeDrawer().draw(specie.molecule[0], file_format='pdf', target=os.path.join(images_path, 'Ne.pdf'))
        elif smiles == '[Ar]':
            MoleculeDrawer().draw(specie.molecule[0], file_format='pdf', target=os.path.join(images_path, 'Ar.pdf'))
        elif smiles == '[He]':
            MoleculeDrawer().draw(specie.molecule[0], file_format='pdf', target=os.path.join(images_path, 'He.pdf'))
        else:
            MoleculeDrawer().draw(specie.molecule[0], file_format='pdf', target=os.path.join(images_path, f'{smiles}.pdf'))
    
    return dict_label_smiles

def convert_pdf_2_png(smiles, pdf_path):
    """
    Cairo2D in RMG supports PDF (higher resolution than svg/png)
    BUT, Graphiz DOT (.dot file) doesnt support PDF
    SO, converting PDF image to png image results in better resolution than using originally png
    """
    pdf = convert_from_path(pdf_path, 300)
    pdf[0].save(f"{smiles}.png")


def Iterate_pdf_2_png(dict_species, notebook_directory):
    """
    Go over pdf files in 'images' folder, and converts pdf to png image
    """
    imgs_path = os.path.join(notebook_directory,'models', 'images')
    #changes current directory location to 'images' folder
    os.chdir(imgs_path)
    for smiles in dict_species.values():
        #special cases for elements
        if smiles in ["[Ne]", "[He]", "[Ar]"]:
            smiles_label = smiles[1:3] #cut out the squared parenthesis
            convert_pdf_2_png(
                smiles_label,
                os.path.join(imgs_path, f"{smiles_label}.pdf"),
            )
        else:
            convert_pdf_2_png(
                smiles,
                os.path.join(imgs_path, f"{smiles}.pdf"),
            )
    #changes current directory location back to main folder
    os.chdir(notebook_directory)

def add_images_to_nodes(dict_species, dot_file_path, image_folder_path):
    """Go over the dot files in FD and recreate modified dot files with 
    images of the molecular structures inside the nodes"""
    # Read the original .dot file
    with open(dot_file_path, 'r') as f:
        dot_content = f.read()

    # Create a PyDot graph from the .dot content
    graph = pydot.graph_from_dot_data(dot_content)[0]

    # Get the current attributes of the graph
    graph_attributes = graph.get_attributes()
    # Change the font size (it's the title of the graph in the bottom)
    #graph_attributes['fontsize'] = '30'  # Set the desired font size
    # Update the attributes
    graph.set('fontsize', "30")

    # Iterate over all edges and change the fontsize
    for edge in graph.get_edges():
        edge.set('fontsize', "28")

    # Iterate over nodes and add images
    for node in graph.get_nodes():
        # Assume node names are enclosed in double quotes
        node_name = node.get_name().strip('"')
        if node_name != r'\n':
            # Check if the node has xlabel attribute
            if 'xlabel' in node.get_attributes():
                # Get the current attributes
                attributes = node.get_attributes()
                # Increase the font size (modify other attributes as needed)
                #attributes['fontsize'] = '26'  # Set the desired font size
                # Update the attributes
                node.set('fontsize', "26")
                
            if node_name in ["[Ne]", "[He]", "[Ar]"]:
                node_name = node[1:3] #cut out the squared parenthesis
            else:
                smiles = dict_species[node_name]

            image_path = os.path.join(image_folder_path, f"{smiles}.png")
        # Add the image to the node
        if os.path.exists(image_path):
            node.set_image(image_path)
            node.set_label('')

    # Save the new .dot file
    modified_dot_path = os.path.join(os.path.dirname(dot_file_path),'flux_diagram_2.0_s_modified.dot')
    graph.write(modified_dot_path, format='raw', prog='dot')
    modified_png_path = os.path.join(os.path.dirname(dot_file_path),'flux_diagram_2.0_s_modified.png')
    graph.write_png(modified_png_path)

