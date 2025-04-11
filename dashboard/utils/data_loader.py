# -----------------------------------------------------------------------------
#
# Ce script postule que nous continuons avec la notation du style  Foret_Classee_de_Richard-Toll_01-01-01-02-2019.tif
# et qu'on télécharge toujours des images composites entre le 01 janvier et le 01 fevrier
# -----------------------------------------------------------------------------

import glob
import os
from constantes import *
import rasterio
import numpy as np


def get_forest_names():
    """
     obtenir les noms des forêts à partir des noms de fichiers
    """
    files = glob.glob(os.path.join(DATA_DIR, "Foret_Classee_de_*.tif"))
    forest_names = set()
    for file in files:
        basename = os.path.basename(file)
        # Extraire le nom entre "Foret_Classee_de_" et le premier "_01-01"
        #TODO: faire du regex pour ne pas mentionner _01-01 (pour version systeme d'alerte ...)
        try:
            forest_name = basename.split("Foret_Classee_de_")[1].split("_01-01")[0]
            forest_names.add(forest_name)
        except IndexError:
            continue
    return sorted(list(forest_names))
def get_available_years():
    '''
    obtenir les années disponibles
    '''
    files = glob.glob(os.path.join(DATA_DIR, "*.tif"))
    years = set()
    for file in files:
        basename = os.path.basename(file)
        try:
            # Extraire l'année juste avant le '.tif '
            year = basename.split("-")[-1].split(".")[0]
            years.add(year)
        except IndexError:
            continue
    return sorted(list(years))


def get_file_path(forest_name, year):
    """
    trouver le fichier correspondant à une forêt et une année
    """
    pattern = os.path.join(DATA_DIR, f"Foret_Classee_de_{forest_name}_01-01-01-02-{year}.tif")
    matching_files = glob.glob(pattern)
    if matching_files:
        return matching_files[0]
    return None

def calcul_ndvi(image_path):
    with rasterio.open(image_path) as src:
        red_band = src.read(3) 
        nir_band = src.read(4) 
        ndvi = (nir_band.astype(float) - red_band.astype(float)) / (nir_band.astype(float) + red_band.astype(float))
        
        return ndvi

def classify_ndvi(ndvi_matrix):
    # init d'un zero_array de meme dimension que ndvi_array
    ndvi_class_map = np.zeros_like(ndvi_matrix)
    category_counter = 1  # indice 1 pour la premiére classe 

    for category_label, (lower_bound, upper_bound) in NDVI_CLASSES.items():
        category_mask = (ndvi_matrix >= lower_bound) & (ndvi_matrix <= upper_bound) # Un tableau booléen
        ndvi_class_map[category_mask] = category_counter # remplace les 0 par le numero de la classe NDVI
        category_counter += 1  
    return ndvi_class_map 

def calcul_class_stats(ndvi_class_map):
    """
    Calcule les statistiques des classes NDVI.
    
    Retourne un dictionnaire dont les clés sont les étiquettes de classes
    et les valeurs sont des dictionnaires contenant :
        - "pixel_count" : nombre de pixels dans la classe
        - "area_ha" : superficie en hectares
        - "pourcentage_couverture" : pourcentage de couverture par rapport au nombre total de pixels
    """
    # trouve les classes presents et compte son occurence en terme de pixel 
    unique_classes, pixel_counts = np.unique(ndvi_class_map, return_counts=True) # is array
    
    # un dict associant chaque classe  à son nombre de pixels.

    dict_class_pixel_count = dict(zip(unique_classes, pixel_counts))
    
    total_pixels = np.sum(pixel_counts) # is integer
    stats = {}
    
    for class_index, class_label in NDVI_CLASSES.items():
        # nombre de pixels pour la classe actuelle
        pixel_count = dict_class_pixel_count.get(class_index, 0)

        total_surface_m2 = pixel_count * pixel_surface_m2
        total_surface_ha = total_surface_m2 / 10000  # conversion en hectare

        pourcentage_couverture = (pixel_count / total_pixels * 100) if total_pixels > 0 else 0

        class_stats[class_label] = {
            "pixel_count": pixel_count,
            "area_ha": total_surface_ha,
            "pourcentage_couverture": pourcentage_couverture
        }

    return class_stats