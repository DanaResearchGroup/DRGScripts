import os
import yaml

from pdf2image import convert_from_path


def convert_pdf_2_png(smiles, pdf_path):
    """
    Cairo2D in RMG supports PDF (higher resolution than svg/png) 
    BUT, Graphiz DOT in Cantera doesnt support PDF
    SO, converting PDF image to png image results in better resolution than original png
    """
    pdf = convert_from_path(pdf_path, 300)
    pdf[0].save(f'{smiles}.png')


def pdf_smiles_2_png(species_output_dict, flux_diagram_folder_path):
    """
    This func goes over the pdf images in images folder, and converts each pdf image to png image
    """
    os.chdir(flux_diagram_folder_path+'/images')
    for smiles in species_output_dict.values():
        if smiles in ['[Ne]', '[He]', '[Ar]']:
            convert_pdf_2_png(smiles[1:3], os.path.join(flux_diagram_folder_path, 'images', f'{smiles[1:3]}.pdf'))
        else:
            convert_pdf_2_png(smiles, os.path.join(flux_diagram_folder_path, 'images', f'{smiles}.pdf'))


def insert_smiles_image_path_into_dot_file(label, smiles, content, work_dir): 
    """
    This func gets a smiles label and the modified dot file content.
    Each variable in content list is a line from the modified dot file content
    It updates the content with the path to the smiles png image and returns it
    """
    for i, line in enumerate(content):
        if f'"{label}"' in line:
            index=line.find('label="')
            new_line=line[:index]+'label=""'+f' , image="{work_dir}/images/{smiles}.png"];\n'
            content[i]=new_line              
    return content


def smiles_images_to_dot(work_dir):
    """
    This func reads the original dot file. All lines are in content variable (list).
    It goes over all the smiles and each smiles sends it to be modified and updated with the png image path in
    insert_smiles_image_path_into_dot_file func
    """
    with open(os.path.join(work_dir, "ReactionPathDiagram.dot"), "r") as f:
        content = f.readlines()
    with open(os.path.join(work_dir, 'output.yml'), 'r') as f:
        species_output_dict = yaml.load(stream=f, Loader=yaml.FullLoader)
    for label, smiles in species_output_dict.items():
        content=insert_smiles_image_path_into_dot_file(label,
                                                       smiles,
                                                       content,
                                                       work_dir,
                                                      )
    with open(os.path.join(work_dir, "ReactionPathDiagramModified.dot"), 'w') as outfile:
        outfile.writelines(content)


