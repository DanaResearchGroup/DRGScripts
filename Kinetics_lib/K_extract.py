from rmgpy.species import Species
from rmgpy.reaction import Reaction
from rmgpy.data.kinetics.library import KineticsLibrary, LibraryReaction
from rmgpy.kinetics.arrhenius import Arrhenius
from rmgpy.data.base import Entry
import pandas as pd
import numpy as np
import os


def create_smiles_dict(smiles_csv):
    """Get df of label vs smiles, 
    return dict: {label (str): smiles(str)}
    """
    df_smiles = pd.read_csv(smiles_csv,index_col=None)
    smiles_dict = {} 
    for row in range(len(df_smiles.index)):
        smiles_dict[df_smiles.iloc[row]['Label']]=df_smiles.iloc[row]['Smiles']
    return smiles_dict

def get_kinetics(rxn_label):
    label_splits = rxn_label.split(' <=> ')
    reactants = label_splits[0].split(' + ')
    products = label_splits[1].split(' + ')
    reactants = [Species(label=label, smiles=smiles_dict[label]) for label in reactants]
    products = [Species(label=label, smiles=smiles_dict[label]) for label in products]
    #Get A units according to rxn order
    A_units = ['', 's^-1', 'cm^3/(mol*s)', 'cm^6/(mol^2*s)']
    rxn_order = len(reactants)
    return A_units[rxn_order],reactants, products

def create_kinetics_dict(kinetics_csv):
    """Get df of kinetics of rxns in different T[K], 
    Tdata and Kdata should be the same length
    Return a list of Kinetics of all rxns
    """
    rxns=[]
    df_kinetics = pd.read_csv(kinetics_csv,index_col=None)
    Tdata = np.array(df_kinetics[0:len(df_kinetics.index)]['T(K)'])
    avogadro_num=6.02214076e23 
    for rxn_label in df_kinetics.columns[1:]:
        Kdata = df_kinetics[rxn_label]
        kunits=get_kinetics(rxn_label)[0]
        #k is given in 1/s or cm^3/molecule/s. Avogadro number is used for conversion of molecule to mol
        #bimolecular rxn:
        if kunits == 'cm^3/(mol*s)':
            Kdata = [k * avogadro_num for k in Kdata]
        #Reaction order 3:
        elif kunits == 'cm^6/(mol^2*s)':
            Kdata = [k * (avogadro_num**2) for k in Kdata]
        elif kunits not in ['','s^-1']:
            raise ValueError("The reaction's order is higher than 3, script should be adjusted")
        Kdata = np.array(Kdata)
        arrhenius = Arrhenius().fit_to_data(Tdata, Kdata, kunits=kunits, three_params=True)
        rxns.append(LibraryReaction(reactants=get_kinetics(rxn_label)[1],
        products=get_kinetics(rxn_label)[2],
        kinetics=(arrhenius)))
    return rxns

def create_kinetic_library(rxns_list,path,kinetic_lib_name,short_desc_kinetic_lib,long_desc_kinetic_lib):
    """Create kinetic library non Pdep based A,n,Ea from the literature"""
    lib = KineticsLibrary(name=kinetic_lib_name,
                        short_desc = short_desc_kinetic_lib,
                        long_desc = long_desc_kinetic_lib,)
    for index, rxn in enumerate(rxns_list):
        lib.entries[index] = Entry(
                    index=index,
                    label=' <=> '.join([' + '.join([reactant.label for reactant in rxn.reactants]),
                                        ' + '.join([product.label for product in rxn.products])]),
                    item=rxn,
                    data=rxn.kinetics,
                )
    lib.save(path=path)

#Edit paths and files:
base_dir='/home/nelly/Code/scripts/Kinetics/files'
smiles_csv = 'smiles_csv.csv'
kinetics_csv = 'kinetics_csv.csv'
kinetics_path= os.path.join(base_dir,'reactions.py')

#Edit Kinetic library detailes:
kinetic_lib_name = 'Furfuryl_OH'
short_desc_kinetic_lib="Ab initio kinetics of OH-initiated reactions of 2-furfuryl alcohol, 2023"
long_desc_kinetic_lib="DOI: 10.1016/j.fuel.2022.127325"
smiles_dict = create_smiles_dict(os.path.join(base_dir,smiles_csv)) 
rxns_list = create_kinetics_dict(os.path.join(base_dir,kinetics_csv)) 
create_kinetic_library(rxns_list,kinetics_path,kinetic_lib_name,short_desc_kinetic_lib,long_desc_kinetic_lib)
