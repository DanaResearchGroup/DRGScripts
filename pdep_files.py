import os
import re

# iterate over files in that directory. Return list of paths and list of files names
def getListPathsNames (directory):
    list_files_paths=[]
    list_files_names=[]
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        # checking if it is a file
        if os.path.isfile(f):
            list_files_paths.append(f)
            list_files_names.append(filename)
    return list_files_paths, list_files_names

#return from file name, the Pdep num by REGEX. For example: from "network5_1.py" --> returns 5
def get_PDEPnum (file_name):
    pdep_num= re.findall("(?!network)(\d*)(?=_)",file_name)[0]
    #print (pdep_num)
    return pdep_num

#return from file name, the Isomers num by REGEX. For example: from "network5_1.py" --> returns 1
def get_Isomers_num (file_name):
    isomers_num=re.findall("(?<=_)(\d*)",file_name)[0]
    #print (isomers_num)
    return isomers_num

#returns a dict of keys as PDEP num and values as list of num of isomers
def get_Pdep_and_Isomers_nums(list_files_names):
    isomers_num=""
    pdep_num = ""
    pdep_isomers_dict = {}
    for file_name in list_files_names:
        pdep_num = int(get_PDEPnum(file_name))
        isomers_num = int(get_Isomers_num(file_name))
        if pdep_num in pdep_isomers_dict:
            pdep_isomers_dict[pdep_num].append(isomers_num)
        else:
            pdep_isomers_dict[pdep_num] = [isomers_num]
        pdep_num=""
        isomers_num=""
    return pdep_isomers_dict

#return a dict of pdep num as a key and a num of max isomers as a value
def max_Isomernum_in_Pdep(pdep_isomers_dict):
    for pdep in pdep_isomers_dict.keys():
        list_isomers_num=pdep_isomers_dict[pdep]
        max_value_isomers=max(list_isomers_num)
        pdep_isomers_dict[pdep]=max_value_isomers
        max_value_isomers = 0
    return pdep_isomers_dict

#comment:Casting the dictionary items to list creates a list of its items, so you can iterate over it and avoid the RuntimeError
#return a dict of pdep:isomers_num only above the treshold
def max_isomers_above_treshold(treshold,pdep_isomers_max_dict):
    for pdep,isomer_max in list(pdep_isomers_max_dict.items()):
        if isomer_max < treshold:
            del pdep_isomers_max_dict[pdep]
    return pdep_isomers_max_dict

#returns a list of paths to pdep files which are max and above the user's treshold
def create_paths_to_pdep(pdep_isomers_max_dict,directory):
    lists_paths=[]
    for pdep in pdep_isomers_max_dict.keys():
        file_path = os.path.join(directory, "network"+str(pdep)+"_"+str(pdep_isomers_max_dict[pdep])+".py")
        lists_paths.append(file_path)
    return lists_paths

#This Method uses all the above methods. It gets a directory and returns a list of relevant string paths of pdep files/
#For example: ['/home/nelly/Desktop/xmr2001_try_script/pdep/network28_64.py',
# '/home/nelly/Desktop/xmr2001_try_script/pdep/network123_29.py', '/home/nelly/Desktop/xmr2001_try_script/pdep/network57_26.py']
def get_list_of_paths(directory):
    list_files_paths = []
    list_files_names = []
    list_files_paths, list_files_names = getListPathsNames(directory)
    dict_pdepnum_isomernum = get_Pdep_and_Isomers_nums(list_files_names)
    pdep_isomers_max_dict = max_Isomernum_in_Pdep(dict_pdepnum_isomernum)
    pdep_isomers_above_treshold = max_isomers_above_treshold(treshold_num_isomers, pdep_isomers_max_dict)
    lists_paths = create_paths_to_pdep(pdep_isomers_above_treshold, directory)
    return lists_paths

if __name__ == "__main__":
    """Edit the directory to a locally copied directory of pdep from RMG run on server"""
    directory = '/home/nelly/Desktop/xmr2001_try_script/pdep/'

    #The user can edit the treshold number of isomers number. Above that, an input file for ARC will be created
    """Edit the treshold_num_isomers"""
    treshold_num_isomers=25

    list_relevant_paths = get_list_of_paths(directory)
