import io         # Pour lire les objets S3 en mémoire
import os
import sys
import boto3
import rasterio
import numpy as np
import pandas as pd
import geopandas as gpd
from rasterio.warp import transform_geom
from rasterio.enums import Resampling
from rasterio.errors import RasterioIOError
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

# --- Configuration AWS (depuis .env ou variables d'environnement) ---
aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_region = os.getenv("AWS_REGION")

# --- Configuration S3 (à adapter) ---
BUCKET_NAME = 'hackaton-stat' # Nom de ton bucket S3
S3_PREFIX = 'Data_hackathon_stat_data_raster/'

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import utils.constantes as constantes

# --- Initialisation du client S3 ---
s3_client = None
if aws_access_key_id and aws_secret_access_key and aws_region:
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=aws_region
        )
        print("Client S3 initialisé avec succès.")
    except Exception as e:
        print(f"ERREUR: Impossible d'initialiser le client S3: {e}")
        # Gérer l'erreur comme il convient (ex: arrêter l'app)
else:
    print("ERREUR: Variables d'environnement AWS manquantes (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION).")
    # Gérer l'erreur

# --- Fonctions utilitaires S3 ---

def _list_s3_objects(bucket, prefix):
    """Liste toutes les clés d'objets S3 pour un préfixe donné (gère la pagination)."""
    if not s3_client:
        print("Erreur: Client S3 non initialisé.")
        return []

    keys = []
    paginator = s3_client.get_paginator('list_objects_v2')
    try:
        pages = paginator.paginate(Bucket=bucket, Prefix=prefix)
        for page in pages:
            if 'Contents' in page:
                for obj in page['Contents']:
                    keys.append(obj['Key'])
        return keys
    except Exception as e:
        print(f"Erreur lors du listage des objets S3 (Bucket: {bucket}, Prefix: {prefix}): {e}")
        return []

def _read_s3_object_to_bytesio(bucket, key):
    """Lit un objet S3 et le retourne comme un objet BytesIO."""
    if not s3_client:
        print("Erreur: Client S3 non initialisé.")
        return None
    try:
        s3_object = s3_client.get_object(Bucket=bucket, Key=key)
        return io.BytesIO(s3_object['Body'].read())
    except s3_client.exceptions.NoSuchKey:
        print(f"Erreur: Clé S3 non trouvée (Bucket: {bucket}, Key: {key})")
        return None
    except Exception as e:
        print(f"Erreur lors de la lecture de l'objet S3 (Bucket: {bucket}, Key: {key}): {e}")
        return None

# --- Adaptation des fonctions de data_loader.py ---

def get_forest_names():
    """ Obtient la liste unique et triée des noms de forêts depuis S3. """
    all_keys = _list_s3_objects(BUCKET_NAME, S3_PREFIX)
    tiff_keys = [key for key in all_keys if key.lower().endswith('.tif')]

    if not tiff_keys:
        print(f"Avertissement : Aucun fichier .tif trouvé dans S3 Bucket '{BUCKET_NAME}' avec le préfixe '{S3_PREFIX}'")
        return []

    forest_names = set()
    for key in tiff_keys:
        # Utiliser os.path.basename pour obtenir le nom du fichier depuis la clé S3
        basename = os.path.basename(key)
        try:
            # La logique d'extraction reste la même, mais appliquée au basename de la clé
            forest_name = basename.split("Foret_Classee_de_")[1].split("_01-01")[0]
            forest_names.add(forest_name)
        except IndexError:
            print(f"Avertissement : Impossible d'extraire le nom de forêt de la clé S3 {key} (basename: {basename})")
            continue
    return sorted(list(forest_names))

def get_available_years(forest_name=None):
    """ Obtient les années disponibles filtrées par forêt depuis S3. """
    # Construire le préfixe S3 basé sur le nom de la forêt si fourni
    search_prefix = S3_PREFIX
    if forest_name:
        # Attention: list_objects_v2 ne gère pas les wildcards comme glob.
        # On liste tout sous le préfixe principal et on filtre ensuite.
        # Si la structure est S3_PREFIX/Foret_Classee_de_XXX_..., on peut affiner le préfixe:
        # search_prefix = f"{S3_PREFIX}Foret_Classee_de_{forest_name}" # Si la structure S3 le permet
        pass # Gardons le préfixe large et filtrons après pour plus de robustesse

    all_keys = _list_s3_objects(BUCKET_NAME, search_prefix)
    # Filtrer pour ne garder que les .tif
    tiff_keys = [key for key in all_keys if key.lower().endswith('.tif')]

    # Filtrer par nom de forêt si spécifié (si on n'a pas pu affiner le préfixe)
    if forest_name:
         # Attention à la correspondance exacte du nom dans la clé
         pattern_part = f"Foret_Classee_de_{forest_name}_"
         tiff_keys = [key for key in tiff_keys if pattern_part in os.path.basename(key)]


    if not tiff_keys:
        if forest_name:
             print(f"Aucune clé .tif trouvée pour la forêt '{forest_name}' dans S3 (Bucket: {BUCKET_NAME}, Prefix: {search_prefix})")
        else:
             print(f"Aucune clé .tif trouvée dans S3 (Bucket: {BUCKET_NAME}, Prefix: {search_prefix})")
        return []

    years = set()
    for key in tiff_keys:
        basename = os.path.basename(key)
        try:
            
            year_str = basename.split(".tif")[0].split("-")[-1]
            if year_str.isdigit():
                years.add(int(year_str))
            else:
                print(f"Format d'année non reconnu dans la clé S3 {key} (basename: {basename})")
        except IndexError:
            print(f"Impossible d'extraire l'année de la clé S3 {key} (basename: {basename})")
            continue
    return sorted(list(years), reverse=True) # Le plus récent en premier

def get_file_path(forest_name, year):
    """
    Trouve la clé S3 pour une forêt et une année données, 
    """
    search_prefix = S3_PREFIX # Préfixe large où chercher
    all_keys = _list_s3_objects(BUCKET_NAME, search_prefix)

    # Construire les motifs de début et de fin attendus
    # Utiliser os.path.basename pour s'assurer qu'on cherche dans le nom de fichier et non le chemin S3 complet
    expected_start_part = f"Foret_Classee_de_{forest_name}_"
    expected_end_part = f"-{year}.tif"

    matching_keys = []
    for key in all_keys:
        # Extraire le nom de fichier de la clé complète
        basename = os.path.basename(key)
        # Vérifier si le nom de fichier commence par la bonne partie ET se termine par la bonne année/extension
        if basename.startswith(expected_start_part) and basename.endswith(expected_end_part):
             matching_keys.append(key) # Ajouter la clé S3 complète si ça correspond

    # Log de débogage mis à jour
    print(f"Recherche S3 pour forêt '{forest_name}', année {year}. Pattern: start='{expected_start_part}', end='{expected_end_part}'")
    print("Clés S3 correspondantes trouvées:", matching_keys)

    if matching_keys:
        # S'il y a plusieurs correspondances (peu probable si l'année est unique),
        # on prend la première trouvée. On pourrait ajouter une logique si nécessaire.
        return matching_keys[0]
    else:
        print(f"Erreur : Aucune clé S3 trouvée pour {forest_name} en {year} avec le pattern start='{expected_start_part}' et end='{expected_end_part}'")
        return None
    
# --- Modification des fonctions de lecture Rasterio ---

def calcul_ndvi(s3_key): # Prend la clé S3 en entrée
    """ Calcule la matrice NDVI à partir d'un fichier TIF lu depuis S3. """
    file_like_object = _read_s3_object_to_bytesio(BUCKET_NAME, s3_key)
    if file_like_object is None:
        return None, None # Erreur lors de la lecture S3

    try:
        # Rasterio peut lire directement depuis l'objet bytes en mémoire
        with rasterio.open(file_like_object) as src:
            if src.count < 4:
                raise ValueError(f"Le fichier dans S3 ({s3_key}) a moins de 4 bandes")

            # Les indices des bandes restent les mêmes (à adapter si besoin)
            red_band = src.read(3).astype(np.float32)
            nir_band = src.read(4).astype(np.float32)

            # La logique de calcul NDVI reste identique
            np.seterr(divide='ignore', invalid='ignore')
            denominator = nir_band + red_band
            ndvi = np.where(denominator == 0, 0, (nir_band - red_band) / denominator)
            ndvi = np.clip(ndvi, constantes.NDVI_MIN, constantes.NDVI_MAX)

            return ndvi, src.profile # Retourne le profil si nécessaire

    except RasterioIOError as e:
        print(f"Erreur Rasterio lors de l'ouverture/lecture de l'objet S3 {s3_key}: {e}")
        return None, None
    except ValueError as e:
        print(f"Erreur lors du calcul NDVI pour l'objet S3 {s3_key}: {e}")
        return None, None
    except Exception as e:
        print(f"Erreur inattendue lors du calcul NDVI pour l'objet S3 {s3_key}: {e}")
        return None, None
    finally:
        # Fermer l'objet BytesIO s'il a été ouvert
        if file_like_object:
            file_like_object.close()


def read_rgb_bands(s3_key, max_size=1000): 
    """ Lit les bandes RGB d'un TIF sur S3. """
    file_like_object = _read_s3_object_to_bytesio(BUCKET_NAME, s3_key)
    if file_like_object is None:
        return None, None

    try:
        with rasterio.open(file_like_object) as src:
            if src.count < 3:
                print(f"ERREUR: Moins de 3 bandes dans l'objet S3 {s3_key}, impossible de lire RGB.")
                return None, None

            
            band_r_idx, band_g_idx, band_b_idx = 1, 2, 3
            print(f"Lecture bandes RGB depuis S3 {s3_key}: R={band_r_idx}, G={band_g_idx}, B={band_b_idx}")

            
            height, width = src.height, src.width
            if max(height, width) > max_size:
                scale = max_size / max(height, width)
                new_height = int(height * scale)
                new_width = int(width * scale)
                print(f"Redimensionnement RGB: ({height}x{width}) -> ({new_height}x{new_width})")
                rgb_bands = src.read(
                    [band_r_idx, band_g_idx, band_b_idx],
                    out_shape=(3, new_height, new_width),
                    resampling=Resampling.bilinear
                )
            else:
                rgb_bands = src.read([band_r_idx, band_g_idx, band_b_idx])

           
            rgb_image = np.moveaxis(rgb_bands, 0, -1)
           
            return rgb_image, src.profile

    except RasterioIOError as e:
        print(f"Erreur Rasterio ouverture/lecture RGB objet S3 {s3_key}: {e}")
        return None, None
    except IndexError:
        print(f"ERREUR: Index de bande RGB ({band_r_idx},{band_g_idx},{band_b_idx}) invalide pour objet S3 {s3_key}")
        return None, None
    except Exception as e:
        print(f"Erreur inattendue lecture RGB objet S3 {s3_key}: {e}")
        return None, None
    finally:
        if file_like_object:
            file_like_object.close()


def classify_ndvi(ndvi_matrix):
    """ Classifie la matrice NDVI (logique inchangée). """
    if ndvi_matrix is None: return None
    ndvi_class_map = np.zeros_like(ndvi_matrix, dtype=np.uint8)
    for class_index, details in constantes.NDVI_CLASSES.items():
        lower_bound, upper_bound = details["range"]
        if class_index == min(constantes.NDVI_CLASSES.keys()):
            mask = (ndvi_matrix >= lower_bound) & (ndvi_matrix <= upper_bound)
        else:
            mask = (ndvi_matrix > lower_bound) & (ndvi_matrix <= upper_bound)
        ndvi_class_map[mask] = class_index
    return ndvi_class_map

def calcul_class_stats(ndvi_class_map):
    """ Calcule les statistiques par classe NDVI (logique inchangée). """
    if ndvi_class_map is None: return pd.DataFrame()
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
            "Pixel Count": pixel_count, # Garder le compte pixel peut être utile
            "Surface (ha)": np.round(total_surface_ha, 2),
            "% Couverture": np.round(pourcentage_couverture, 2)
        })
    stats_df = pd.DataFrame(stats_list)
    return stats_df

def calculate_stats_difference(stats_df_new, stats_df_old, year_new, year_old):
     """ Calcule la différence entre deux DataFrames de statistiques (logique inchangée). """
     if stats_df_new.empty or stats_df_old.empty: return pd.DataFrame()
     merged_stats = pd.merge(
         stats_df_new[['Classe Index', 'Classe Label', 'Surface (ha)', '% Couverture']],
         stats_df_old[['Classe Index', 'Surface (ha)', '% Couverture']],
         on='Classe Index',
         suffixes=(f'_{year_new}', f'_{year_old}'),
         how='outer'
     ).fillna(0)
     label_map = pd.concat([stats_df_new[['Classe Index', 'Classe Label']], stats_df_old[['Classe Index', 'Classe Label']]]).drop_duplicates(subset=['Classe Index']).set_index('Classe Index')
     merged_stats['Classe Label'] = merged_stats['Classe Index'].map(label_map['Classe Label'])
     surf_col_new = f'Surface (ha)_{year_new}'; surf_col_old = f'Surface (ha)_{year_old}'
     perc_col_new = f'% Couverture_{year_new}'; perc_col_old = f'% Couverture_{year_old}'
     if surf_col_new not in merged_stats.columns: merged_stats[surf_col_new] = 0
     if surf_col_old not in merged_stats.columns: merged_stats[surf_col_old] = 0
     if perc_col_new not in merged_stats.columns: merged_stats[perc_col_new] = 0
     if perc_col_old not in merged_stats.columns: merged_stats[perc_col_old] = 0
     merged_stats['Différence Surface (ha)'] = merged_stats[surf_col_new] - merged_stats[surf_col_old]
     merged_stats['Différence % Couverture'] = merged_stats[perc_col_new] - merged_stats[perc_col_old]
     diff_df = merged_stats[[
         'Classe Label', surf_col_new, surf_col_old,
         'Différence Surface (ha)', 'Différence % Couverture'
     ]].round(2)
     return diff_df

def calculate_trend(stats_df, class_label):
    """Calcule la tendance linéaire (logique inchangée)."""
    if stats_df is None or stats_df.empty: return None, "Données manquantes"
    class_stats = stats_df[stats_df['Classe Label'] == class_label].dropna(subset=['Year', 'Surface (ha)'])
    if len(class_stats) < 2: return None, f"Pas assez de données pour {class_label}"
    years = class_stats['Year'].values; surface = class_stats['Surface (ha)'].values
    try:
        coeffs = np.polyfit(years, surface, 1); slope = coeffs[0]
        if abs(slope) < 0.1: trend_text = "Stable"
        elif slope > 0: trend_text = f"Hausse ({slope:+.1f} ha/an)"
        else: trend_text = f"Baisse ({slope:+.1f} ha/an)"
        return slope, trend_text
    except Exception as e:
        print(f"Erreur calcul tendance pour {class_label}: {e}")
        return None, "Erreur calcul"


def get_initial_data():
    """ Charge les listes initiales pour les sélecteurs depuis S3. """
    if not s3_client: return [], [] 
    forests = get_forest_names()
    
    initial_years = get_available_years(forests[0]) if forests else get_available_years()
    return forests, initial_years

def load_all_year_stats(forest_name):
    """ Charge TOUTES les stats annuelles depuis S3 (calcule à partir des TIFs S3). """
    if not s3_client: return pd.DataFrame()
    available_years = get_available_years(forest_name)
    all_stats = []
    print(f"Calcul des stats annuelles depuis S3 pour {forest_name}, années: {available_years}")
    for year in available_years:
        print(f"  Année {year}:")
        s3_key = get_file_path(forest_name, year) 
        stats_df_year = pd.DataFrame()
        if s3_key:
            ndvi_matrix, _ = calcul_ndvi(s3_key) 
            if ndvi_matrix is not None:
                ndvi_class_map = classify_ndvi(ndvi_matrix)
                if ndvi_class_map is not None:
                    stats_df_year = calcul_class_stats(ndvi_class_map)
                    if not stats_df_year.empty:
                        stats_df_year['Year'] = year
                        all_stats.append(stats_df_year)
                        print(f"    -> Stats calculées depuis S3.")
                    else: print(f"    -> Stats vides après classification.")
                else: print(f"    -> Erreur: Classification NDVI échouée.")
            else: print(f"    -> Erreur: Calcul NDVI depuis S3 échoué.")
        else: print(f"    -> Erreur: Clé S3 non trouvée pour {year}.")

    if not all_stats: return pd.DataFrame()
    full_stats_df = pd.concat(all_stats, ignore_index=True)
    return full_stats_df
