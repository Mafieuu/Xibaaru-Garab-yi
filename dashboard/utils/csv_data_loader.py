import pandas as pd

def load_data():
    path = 'https://raw.githubusercontent.com/InesRoque3/GroupV_project2/main/data/'
    
    emissions = pd.read_csv(path + "emissions_with_origin.csv")
    productions = pd.read_csv(path + "productions.csv")
    water = pd.read_csv(path + "water_use.csv")
    global_emissions = pd.read_csv(path + "Global_Emissions.csv")
    
    # Prétraitement
    top10 = emissions.sort_values("Total_emissions")[-10:]
    top10_vegetal = emissions[emissions.Origin=='Vegetal'].sort_values("Total_emissions")[-10:]
    top8_animal = emissions[emissions.Origin=='Animal'].sort_values("Total_emissions")
    
    return {
        'emissions': emissions,
        'productions': productions,
        'water': water,
        'global_emissions': global_emissions,
        'top10': top10,
        'top10_vegetal': top10_vegetal,
        'top8_animal': top8_animal
    }

def get_product_mapping():
    """
    Return un dict qui etablie une correspondance entre 
    produit alimentaire et matiére premiére (return le contenu initial de  dict_)
    """
    return {
        'Apples':'Apples', 'Bananas':'Bananas', 'Barley':'Barley', 'Beet Sugar':'Sugar beet', 
        'Berries & Grapes':'Berries & Grapes', 'Brassicas':'Brassicas', 'Cane Sugar':'Sugar cane', 
        'Cassava':'Cassava', 'Citrus Fruit':'Citrus', 'Coffee':'Coffee beans', 'Groundnuts':'Groundnuts',
        'Maize':'Maize', 'Nuts':'Nuts', 'Oatmeal':'Oats', 'Olive Oil':'Olives', 
        'Onions & Leeks':'Onions & Leeks', 'Palm Oil':'Oil palm fruit', 'Peas':'Peas', 
        'Potatoes':'Potatoes', 'Rapeseed Oil':'Rapeseed', 'Rice':'Rice', 
        'Root Vegetables':'Roots and tubers', 'Soymilk':'Soybeans', 'Sunflower Oil':'Sunflower seed', 
        'Tofu':'Soybeans', 'Tomatoes':'Tomatoes', 'Wheat & Rye':'Wheat & Rye', 
        'Dark Chocolate':'Cocoa, beans', 'Milk': 'Milk', 'Eggs': 'Eggs',
        'Poultry Meat': 'Poultry Meat', 'Pig Meat': 'Pig Meat', 
        'Seafood (farmed)': 'Seafood (farmed)', 'Cheese': 'Cheese', 
        'Lamb & Mutton': 'Lamb & Mutton', 'Beef (beef herd)': 'Beef (beef herd)'
    }

def create_dropdown_options(data_dict):
    """Génére la liste des options dispo en fonction des options de create_origin_selector().
    return un dict
     """
    
    product_mapping = get_product_mapping()
    
    options_veg = [dict(label=key, value=product_mapping[key]) 
                  for key in data_dict['top10_vegetal']['Food product'].tolist()[::-1] 
                  if key in product_mapping.keys()]
    
    options_an = [dict(label=val, value=val) 
                 for val in data_dict['top8_animal']["Food product"].tolist()[::-1]]
    
    options_total = [dict(label=key, value=product_mapping[key]) 
                    for key in data_dict['top10']['Food product'].tolist()[::-1] 
                    if key in product_mapping.keys()]
    
    return {
        'vegetal': options_veg,
        'animal': options_an,
        'total': options_total
    }