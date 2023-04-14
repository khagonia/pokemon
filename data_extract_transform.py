import pandas as pd
from bs4 import BeautifulSoup
import os
import requests

#########################
### POKEMON DATA  #######
#########################

poke_df = pd.read_csv(os.path.join(os.getcwd(), 'pokemon/pokemon.csv'))

poke_df['id'] = ["0" * (4 - len(str(x))) + str(x) for x in poke_df['id']]


abilities = poke_df['abilities']
ability_1 = []
ability_2 = []
for a in abilities:
    a_list = eval(a)
    ability_1.append(a_list[0])
    ability_2.append(a_list[1] if len(a_list) > 1 else None)
    
poke_df['ability_1'] = ability_1
poke_df['ability_2'] = ability_2

poke_df.drop(columns = ["abilities", "japanese_name", "pokedex_number"], inplace=True)
poke_df.rename(columns={"classfication": "classification"}, inplace=True)

#########################
### TYPES DATA  #########
#########################

type_df = pd.read_csv(os.path.join(os.getcwd(), 'pokemon/pokemon_types.csv'))


#########################
### EVOLUTION DATA ######
#########################

response = requests.get("https://pokemondb.net/evolution")
page = BeautifulSoup(response.text, "html.parser")

# get the all 'infocard-list-evo' divs from a block. each div is a single evolution tree.
# a single block can contain multiple evolution trees.
def get_list_evo(block):
    return block.find_all("div", class_="infocard-list-evo", recursive=False)

# get all evolution paths in an evolution tree (single infocard-list-evo div). 
# a tree can split into different branches, leading to multiple evolution paths
def get_evolution_paths(tree):
    children = tree.findChildren(recursive=False)
    list = []
    
    for child in children:
        if(not(child.has_attr('class'))): continue
        if(child['class'][0] == 'infocard' and len(child['class']) == 1):
            list.append(extract_id_form(child))

        if(child['class'][0] == 'infocard-evo-split'):
            split_paths = get_list_evo(child)
            
            branch_list = []
            for split in split_paths:
                branch_list.append(list + get_evolution_paths(split))
            
            list = branch_list
                
        
    return list

# extract id and regional form from an 'infocard' div, which is a single
# node / pokemon in an evolution path.
def extract_id_form(tag):
    #extract information
    info = {}
    small_text = tag.find_all("small", limit=2)

    #extract regional form
    if (int(small_text[0].text[1:]) < 801):
        # get id
        info['id'] = small_text[0].text[1:].strip()

        # get form
        if "Alolan" in small_text[1].text:
            info['regional_form'] = "Alolan"
        elif "Galarian" in small_text[1].text:
            info['regional_form'] = "Galarian"
        elif "Hisuian" in small_text[1].text:
            info['regional_form'] = "Hisuian"
        elif "Paldean" in small_text[1].text:
            info['regional_form'] = "Paldean"
        else:
            info['regional_form'] = "Default"
    else:
        info['id'] = None
        info['regional_form'] = None

    return info

evo_df = pd.DataFrame(columns = ["evo_1_id", "evo_1_form", "evo_2_id", "evo_2_form", "evo_3_id", "evo_3_form"])

evolution_set = page.find_all("div", class_="infocard-filter-block")

for evolution_block in evolution_set:
    evolutions = get_list_evo(evolution_block)
    for evolution in evolutions:
        paths = get_evolution_paths(evolution)
        # print(paths)
        paths = [paths] if "id" in paths[0] else paths
        
        path_transformed = {}
        for path in paths:
            try:
                for i in range(3):
                    match i:
                        case 0:
                            path_transformed['evo_1_id'] = path[i]['id']
                            path_transformed['evo_1_form'] = path[i]['regional_form']
                        case 1:
                            path_transformed['evo_2_id'] = path[i]['id']
                            path_transformed['evo_2_form'] = path[i]['regional_form']
                        case 2:
                            path_transformed['evo_3_id'] = path[i]['id']
                            path_transformed['evo_3_form'] = path[i]['regional_form']           
            except:
                pass

            new_row = pd.Series(path_transformed).to_frame().T
            evo_df = pd.concat([evo_df, new_row], ignore_index=True)


evo_df.to_csv(os.path.join(os.getcwd(), 'pokemon/evolutions.csv'), index_label="id")
