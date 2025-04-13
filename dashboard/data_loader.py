import glob
import os
import sys
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))) # Pas nécessaire si exécuté depuis la racine
import utils.constantes as constantes
import rasterio
import numpy as np
import pandas as pd 

# Fonction pour obtenir les noms uniques des forêts
def get_forest_names():
    """ Obtient la liste unique et triée des noms de forêts. """
    search_path = os.path.join("dashboard", constantes.DATA_DIR, "Foret_Classee_de_*.tif")
    files = glob.glob(search_path)
    if not files:
        print(f"Avertissement : Aucun fichier trouvé dans {search_path}")
        return []
    forest_names = set()
    for file in files:
        basename = os.path.basename(file)
        try:
            # Extraction du nom de la forêt : on prend tout ce qui se trouve entre "Foret_Classee_de_" et le premier "_01-01"
            forest_name = basename.split("Foret_Classee_de_")[1].split("_01-01")[0]
            forest_names.add(forest_name)
        except IndexError:
            print(f"Avertissement : Impossible d'extraire le nom de forêt de {basename}")
            continue
    return sorted(list(forest_names))

def get_available_years(forest_name=None):
    """ Obtient les années disponibles, potentiellement filtrées par forêt. """
    if forest_name:
         pattern = os.path.join("dashboard", constantes.DATA_DIR, f"Foret_Classee_de_{forest_name}_*.tif")
    else:
         pattern = os.path.join("dashboard", constantes.DATA_DIR, "Foret_Classee_de_*.tif")

    files = glob.glob(pattern)
    if not files:
        print(f"Avertissement : Aucun fichier trouvé pour le pattern {pattern}")
        return []
    years = set()
    for file in files:
        basename = os.path.basename(file)
        try:
            # Extraction de l'année : la dernière partie avant l'extension .tif
            year = basename.split(".tif")[0].split("-")[-1]
            if year.isdigit():
                 years.add(int(year))  # Conversion en int pour le tri
            else:
                 print(f"Avertissement : Format d'année non reconnu dans {basename}")
        except IndexError:
            print(f"Avertissement : Impossible d'extraire l'année de {basename}")
            continue
    return sorted(list(years), reverse=True)  # le plus recent en premier

# Fonction pour trouver le chemin du fichier pour une forêt et une année donnée
def get_file_path(forest_name, year):
    """ Trouve le chemin du fichier pour une forêt et une année données. """
    pattern = os.path.join("dashboard", constantes.DATA_DIR, f"Foret_Classee_de_{forest_name}_*-{year}.tif")
    matching_files = glob.glob(pattern)
    print(f"Recherche avec le pattern : {pattern}")
    print("Fichiers trouvés :", matching_files)
    if matching_files:
        return matching_files[0]
    else:
        print(f"Erreur : Aucun fichier trouvé pour {forest_name} en {year} avec le pattern {pattern}")
        return None

# Fonction pour calculer la matrice NDVI à partir d'un fichier TIF
def calcul_ndvi(image_path):
    """ Calcule la matrice NDVI à partir d'un fichier TIF. """
    try:
        with rasterio.open(image_path) as src:
            if src.count < 4:
                 raise ValueError(f"Le fichier {image_path} a moins de 4 bandes ")
            #  les bandes Rouge (index 3) et NIR (index 4)
            red_band = src.read(3).astype(np.float32)
            nir_band = src.read(4).astype(np.float32)

            # Masquage pour éviter la division par zéro
            np.seterr(divide='ignore', invalid='ignore')
            denominator = nir_band + red_band
            ndvi = np.where(denominator == 0, 0, (nir_band - red_band) / denominator)
            ndvi = np.clip(ndvi, constantes.NDVI_MIN, constantes.NDVI_MAX)

            return ndvi, src.profile

    except rasterio.RasterioIOError as e:
        print(f"Erreur Rasterio lors de l'ouverture/lecture de {image_path}: {e}")
        return None, None
    except ValueError as e:
         print(f"Erreur lors du calcul NDVI pour {image_path}: {e}")
         return None, None
    except Exception as e:
        print(f"Erreur inattendue lors du calcul NDVI pour {image_path}: {e}")
        return None, None

# Fonction pour classifier la matrice NDVI selon les seuils définis dans constantes
def classify_ndvi(ndvi_matrix):
    """ Classifie la matrice NDVI selon les seuils définis dans constantes. """
    if ndvi_matrix is None:
        return None
    ndvi_class_map = np.zeros_like(ndvi_matrix, dtype=np.uint8)

    for class_index, details in constantes.NDVI_CLASSES.items():
        lower_bound, upper_bound = details["range"]
        # Appliquer un masque pour assigner l'index de la classe
        if class_index == min(constantes.NDVI_CLASSES.keys()):
            mask = (ndvi_matrix >= lower_bound) & (ndvi_matrix <= upper_bound)
        else:
            mask = (ndvi_matrix > lower_bound) & (ndvi_matrix <= upper_bound)

        ndvi_class_map[mask] = class_index

    return ndvi_class_map

#  pour calculer les statistiques par classe NDVI
def calcul_class_stats(ndvi_class_map):
    """ Calcule les statistiques (nombre de pixels, surface en ha, %) pour chaque classe NDVI. """
    if ndvi_class_map is None:
        return pd.DataFrame()

    unique_classes, pixel_counts = np.unique(ndvi_class_map, return_counts=True)
    dict_class_pixel_count = dict(zip(unique_classes, pixel_counts))

    valid_pixels = np.sum([count for class_id, count in dict_class_pixel_count.items() if class_id in constantes.NDVI_CLASSES])
    if valid_pixels == 0:
         print("Avertissement : Aucun pixel valide trouvé dans ndvi_class_map pour le calcul des stats.")
         return pd.DataFrame()

    stats_list = []
    for class_index, details in constantes.NDVI_CLASSES.items():
        pixel_count = dict_class_pixel_count.get(class_index, 0)
        total_surface_m2 = pixel_count * constantes.PIXEL_SURFACE_M2
        total_surface_ha = total_surface_m2 / 10000
        pourcentage_couverture = (pixel_count / valid_pixels * 100) if valid_pixels > 0 else 0

        stats_list.append({
            "Classe Index": class_index,
            "Classe Label": details["label"],
            "Pixel Count": pixel_count,
            "Surface (ha)": np.round(total_surface_ha, 2),
            "% Couverture": np.round(pourcentage_couverture, 2)
        })

    stats_df = pd.DataFrame(stats_list)
    return stats_df

# Fonction pour encapsuler le chargement et le traitement d'une image
def load_and_process_image(forest_name, year):
    """ Charge, calcule le NDVI, classifie et calcule les stats pour une forêt/année. """
    image_path = get_file_path(forest_name, year)
    if not image_path:
        return None, None, pd.DataFrame()  # Image non trouvée

    ndvi_matrix, profile = calcul_ndvi(image_path)
    if ndvi_matrix is None:
        return None, None, pd.DataFrame()  # Erreur lors du calcul du NDVI

    ndvi_class_map = classify_ndvi(ndvi_matrix)
    if ndvi_class_map is None:
        return ndvi_matrix, None, pd.DataFrame()  # Erreur de classification

    stats_df = calcul_class_stats(ndvi_class_map)
    # return la carte classifiée
    return ndvi_class_map, profile, stats_df

def get_initial_data():
     """ Charge les listes initiales pour les sélecteurs. """
     forests = get_forest_names()
     initial_years = get_available_years(forests[0]) if forests else get_available_years()
     return forests, initial_years


def calculate_stats_difference(stats_df_new, stats_df_old, year_new, year_old):
    """ Calcule la différence de surface et de pourcentage entre deux DataFrames de statistiques. """
    if stats_df_new.empty or stats_df_old.empty:
        return pd.DataFrame()

    # Fusionner les dataframes sur l'index ou le label de classe
    merged_stats = pd.merge(
        stats_df_new[['Classe Index', 'Classe Label', 'Surface (ha)', '% Couverture']],
        stats_df_old[['Classe Index', 'Surface (ha)', '% Couverture']],
        on='Classe Index',
        suffixes=(f'_{year_new}', f'_{year_old}'),
        how='outer' # Garder toutes les classes même si elles n'existent que dans 
    ).fillna(0) # Remplacer NaN par 0 si une classe manque une année

    # Calculer les différences
    merged_stats[f'Différence Surface (ha)'] = merged_stats[f'Surface (ha)_{year_new}'] - merged_stats[f'Surface (ha)_{year_old}']
    merged_stats[f'Différence % Couverture'] = merged_stats[f'% Couverture_{year_new}'] - merged_stats[f'% Couverture_{year_old}']

    # Sélectionner et renommer les colonnes pertinentes pour l'affichage
    diff_df = merged_stats[[
        'Classe Label',
        f'Surface (ha)_{year_new}',
        f'Surface (ha)_{year_old}',
        f'Différence Surface (ha)',
        f'Différence % Couverture'
    ]].round(2) 

    return diff_df

def calculate_diff_map(map_new, map_old):
     """ Calcule une carte de différence simple (pixel par pixel). Peut être bruité. """
     if map_new is None or map_old is None or map_new.shape != map_old.shape:
         return None
     # Simple différence, les valeurs peuvent être négatives, positives ou nulles
     diff_map = map_new.astype(np.int8) - map_old.astype(np.int8)
     return diff_map