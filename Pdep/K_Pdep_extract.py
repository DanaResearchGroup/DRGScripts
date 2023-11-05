from rmgpy.species import Species
from rmgpy.reaction import Reaction
from rmgpy.data.kinetics.library import KineticsLibrary, LibraryReaction
from rmgpy.kinetics.arrhenius import Arrhenius
from rmgpy.kinetics import PDepArrhenius
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

def reshape_matrix(matrix):
    """Get a numpy matrix which contains string values of scientific values and empty cells
    which are marked as '/'. Return a sliced matrix of all columns, with minimal row number 
    that dont contain '/'.
    """
    col_len_list=[]
    rows,cols = np.shape(matrix)
    for col in range(cols):
        col_filtered_data = [value for value in matrix[:,col] if value != '/']
        col_len_list.append(len(col_filtered_data))
    min_len = min(col_len_list)
    new_matrix = matrix[0:min_len,:]
    return new_matrix

def create_Pdep_kinetics_list(Pdep_kinetics_csv):
    """Get df of Pdep kinetics of rxns in different T[K] and P[atm], 
    Tdata and Kdata should be in the same length
    Return a list of Pdep Kinetics for all rxns
    """
    rxns=[]
    df_kinetics = pd.read_csv(Pdep_kinetics_csv,index_col=None)
    T_full_range = np.array(df_kinetics.iloc[:,0])
    T_full_range = [item for item in T_full_range if item != 'T(K)']
    avogadro_num = 6.02214076e23 
    num_pressures = len(P_range) 
    #Go over the rxns
    for col in range(1,len(df_kinetics.columns),num_pressures):
        rxn_label = df_kinetics.columns[col]
        print(rxn_label)
        K_matrix = df_kinetics.to_numpy()[1: , col:col+4]
        K_filtered = reshape_matrix(K_matrix)
        #create a temp numpy array of T range according to the rows in k_filtered matrix
        #convert pressures in atm to Pa
        rows = np.shape(K_filtered)[0]
        T_filtered = T_full_range[0:rows]
        T_filtered = np.array([float(value) for value in T_filtered])
        P_array = np.array([p * 101325 for p in P_range])
        kunits, reactants, products = get_kinetics(rxn_label)
        #k is given in 1/s or cm^3/molecule/s. Avogadro number is used for conversion of molecule to mol
        #bimolecular rxn:
        if kunits == 'cm^3/(mol*s)':
            # K_filtered = K_filtered * avogadro_num
            K_filtered = np.array([[float(cell) * avogadro_num for cell in row] for row in K_filtered])
        #Reaction order 3:
        elif kunits == 'cm^6/(mol^2*s)':
                K_filtered = np.array([[float(cell) * (avogadro_num**2) for cell in row] for row in K_filtered])
        elif kunits not in ['','s^-1']:
            raise ValueError("The reaction's order is higher than 3, script should be adjusted")
        kinetics=PDepArrhenius().fit_to_data(T_filtered, P_array, K_filtered, kunits=kunits)
        rxns.append(LibraryReaction(reactants=reactants,
                            products=products,
                            kinetics=kinetics
                            ))
    return rxns

def create_kinetic_library(rxns_list,path,kinetic_lib_name,short_desc_kinetic_lib,long_desc_kinetic_lib):
    """Create Pdep kinetic library based A,n,Ea from the literature"""
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
base_dir='/home/nelly/Code/scripts/Pdep/files'
smiles_csv = 'smiles.csv'
Pdep_kinetics_csv = 'kinetics.csv'
#Assumption: K is given for some constant pressures for each rxn
P_range=[0.001,0.1,1,10] #atm

#Edit Pdep kinetic lib parameters:
kinetic_lib_name="Pdep Kientic Library Furfuryl and OH 2023"
short_desc_kinetic_lib="Ab initio kinetics of OH-initiated reactions of 2-furfuryl alcohol"
long_desc_kinetic_lib="DOI: 10.1016/j.fuel.2022.127325"
kinetics_path = os.path.join(base_dir,'reactions.py')

smiles_dict = create_smiles_dict(os.path.join(base_dir,smiles_csv)) 
rxns_list = create_Pdep_kinetics_list(os.path.join(base_dir,Pdep_kinetics_csv)) 
create_kinetic_library(rxns_list,kinetics_path,kinetic_lib_name,short_desc_kinetic_lib,long_desc_kinetic_lib)
