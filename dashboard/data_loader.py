import glob
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))) # Pas nécessaire si exécuté depuis la racine
import utils.constantes as constantes
import rasterio
import numpy as np
import pandas as pd 
import geopandas as gpd
from rasterio.warp import  transform_geom
from rasterio.enums import Resampling
from rasterio.errors import RasterioIOError


def get_forest_names():
    """ Obtient la liste unique et triée des noms de forêts. """
    search_path = os.path.join( constantes.DATA_DIR, "Foret_Classee_de_*.tif")
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
    """ Obtient les années disponibles filtrées par forêt. """
    if forest_name:
         pattern = os.path.join( constantes.DATA_DIR, f"Foret_Classee_de_{forest_name}_*.tif")
    else:
         pattern = os.path.join( constantes.DATA_DIR, "Foret_Classee_de_*.tif")

    files = glob.glob(pattern)
    if not files:
        print(f" Aucun fichier trouvé pour  {pattern}")
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
                 print(f" Format d'année non reconnu dans {basename}")
        except IndexError:
            print(f" Impossible d'extraire l'année de {basename}")
            continue
    return sorted(list(years), reverse=True)  # le plus recent en premier

# Fonction pour trouver le chemin du fichier pour une forêt et une année donnée
def get_file_path(forest_name, year):
    """ Trouve le chemin du fichier pour une forêt et une année données. """
    pattern = os.path.join( constantes.DATA_DIR, f"Foret_Classee_de_{forest_name}_*-{year}.tif")
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
            #  les bandes Rouge3) et NIR 4
            red_band = src.read(3).astype(np.float32)
            nir_band = src.read(4).astype(np.float32)

            # pour éviter la division par zéro
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

def read_rgb_bands(image_path, max_size=1000):
    """
    Lit les bandes RGB d'un TIF source dans data/.
    Redimensionne si l'image est trop grande pour l'affichage.
    Retourne une matrice NumPy 
    """
    try:
        with rasterio.open(image_path) as src:
            # Vérifier si au moins 3 bandes existent
            if src.count < 3:
                print(f"ERREUR: Moins de 3 bandes dans {image_path}, impossible de lire RGB.")
                return None, None

            # Lire les 3 premières bandes (supposées R, G, B - A ADAPTER SI NECESSAIRE)
            # Définir les index réels si différents
            band_r_idx, band_g_idx, band_b_idx = 1, 2, 3
            print(f"Lecture bandes RGB : R={band_r_idx}, G={band_g_idx}, B={band_b_idx}")

            # Redimensionner si trop grand pour éviter de saturer la mémoire
            height, width = src.height, src.width
            if max(height, width) > max_size:
                scale = max_size / max(height, width)
                new_height = int(height * scale)
                new_width = int(width * scale)
                print(f"Redimensionnement RGB: ({height}x{width}) -> ({new_height}x{new_width})")
                # Lire en redimensionnant
                rgb_bands = src.read(
                    [band_r_idx, band_g_idx, band_b_idx],
                    out_shape=(3, new_height, new_width),
                    resampling=Resampling.bilinear # Méthode de rééchantillonnage
                )
            else:
                # Lire à la résolution originale
                rgb_bands = src.read([band_r_idx, band_g_idx, band_b_idx])


            rgb_image = np.moveaxis(rgb_bands, 0, -1)
            
            

            

            return rgb_image, src.profile

    except RasterioIOError as e:
        print(f"Erreur Rasterio ouverture/lecture RGB {image_path}: {e}")
        return None, None
    except IndexError:
         print(f"ERREUR: Index de bande RGB ({band_r_idx},{band_g_idx},{band_b_idx}) invalide pour {image_path}")
         return None, None
    except Exception as e:
        print(f"Erreur inattendue lecture RGB {image_path}: {e}")
        return None, None
#  pour calculer les statistiques par classe NDVI

def calcul_class_stats(ndvi_class_map):
    """ Calcule les statistiques (nombre de pixels, surface en ha, et  %) pour chaque classe NDVI. """
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
        how='outer'
    ).fillna(0)

    # Récupérer le 'Classe Label' depuis df_new 
    label_map = pd.concat([stats_df_new[['Classe Index', 'Classe Label']], stats_df_old[['Classe Index', 'Classe Label']]]).drop_duplicates(subset=['Classe Index']).set_index('Classe Index')
    merged_stats['Classe Label'] = merged_stats['Classe Index'].map(label_map['Classe Label'])


    # Vérifier que les colonnes pour le calcul existent AVANT de calculer
    surf_col_new = f'Surface (ha)_{year_new}'
    surf_col_old = f'Surface (ha)_{year_old}'
    perc_col_new = f'% Couverture_{year_new}'
    perc_col_old = f'% Couverture_{year_old}'

    if surf_col_new not in merged_stats.columns: merged_stats[surf_col_new] = 0
    if surf_col_old not in merged_stats.columns: merged_stats[surf_col_old] = 0
    if perc_col_new not in merged_stats.columns: merged_stats[perc_col_new] = 0
    if perc_col_old not in merged_stats.columns: merged_stats[perc_col_old] = 0


    merged_stats['Différence Surface (ha)'] = merged_stats[surf_col_new] - merged_stats[surf_col_old]
    merged_stats['Différence % Couverture'] = merged_stats[perc_col_new] - merged_stats[perc_col_old]

    # Sélectionner les colonnes pour le retour
    diff_df = merged_stats[[
        'Classe Label',
        surf_col_new,
        surf_col_old,
        'Différence Surface (ha)',
        'Différence % Couverture'
    ]].round(2)

    return diff_df


# ------------------------------------------------ pour GeoJSON - Actuellement abandonner mais peut toujours servir dans le future
def get_geojson_path(forest_name, year):
    """ Trouve le chemin du fichier GeoJSON pour une forêt et une année données. """
    pattern = os.path.join( constantes.DATA_DIR, f"Foret_Classee_de_{forest_name}_*-{year}.geojson")
    
    matching_files = glob.glob(pattern)
    print(f"Recherche GeoJSON avec le pattern : {pattern}")
    print("Fichiers GeoJSON trouvés :", matching_files)
    if matching_files:
        return matching_files[0]
    else:
        print(f"Avertissement : Aucun fichier GeoJSON trouvé pour {forest_name} en {year} avec le pattern {pattern}")
        return None


def load_geojson(geojson_path):
    """ Charge un fichier GeoJSON dans un GeoDataFrame. """
    if not geojson_path or not os.path.exists(geojson_path):
        print(f"Erreur: Chemin GeoJSON invalide ou fichier inexistant: {geojson_path}")
        return None
    try:
        gdf = gpd.read_file(geojson_path)
        #  le système de coordonnées  WGS84 / EPSG:4326 pour Mapbox
        if gdf.crs is None:
            print("pas de CRS , nous prennons  EPSG:4326")
            gdf.set_crs("EPSG:4326", inplace=True)
        elif gdf.crs.to_epsg() != 4326:
            print(f"Conversion du CRS de {gdf.crs} vers EPSG:4326.")
            gdf = gdf.to_crs("EPSG:4326")


        potential_class_cols = ['class_index', 'class_id', 'CLASS_ID', 'Class', 'NDVI_Class', 'label']
        class_col = None
        for col in potential_class_cols:
             if col in gdf.columns:
                 class_col = col
                 break
        if not class_col:
             print(f"ERREUR: Colonne de classe NDVI non trouvée dans {geojson_path}. Colonnes présentes: {gdf.columns.tolist()}")

             # Tenter une conversion si une colonne numérique existe (dernier recours)
             numeric_cols = gdf.select_dtypes(include=np.number).columns
             if len(numeric_cols) > 0:
                  print(f"Tentative d'utilisation de la première colonne numérique '{numeric_cols[0]}' comme class_index.")
                  gdf.rename(columns={numeric_cols[0]: 'class_index'}, inplace=True)
                  class_col = 'class_index' # Mise à jour de la variable
             else:
                  return None # Impossible de continuer sans colonne de classe

        
        #  renommer en 'class_index' pour la cohérence
        if class_col != 'class_index':
             gdf.rename(columns={class_col: 'class_index'}, inplace=True)

        try:
            gdf['class_index'] = gdf['class_index'].astype(int)
        except ValueError as e:
             print(f"ERREUR: Impossible de convertir la colonne 'class_index' en entier dans {geojson_path}: {e}. Vérifiez les valeurs.")
             # Afficher les valeurs problématiques
             print("Valeurs uniques dans la colonne 'class_index':", gdf['class_index'].unique())
             return None

        # Ajouter le label textuel pour l'affichage hover
        gdf['class_label'] = gdf['class_index'].map(lambda idx: constantes.INDEX_TO_LABEL.get(idx, "Inconnue"))

        return gdf

    except Exception as e:
        print(f"Erreur lors du chargement ou traitement du GeoJSON {geojson_path}: {e}")
        return None




# --------------------------------------  Fonction pour charger TOUTES les stats annuelles (calcule à partir des TIFs)
def load_all_year_stats(forest_name):
    available_years = get_available_years(forest_name)
    all_stats = []
    print(f"Calcul des stats annuelles pour {forest_name}, années: {available_years}")
    for year in available_years:
        print(f"  Année {year}:")
        image_path = get_file_path(forest_name, year)
        stats_df_year = pd.DataFrame() # Init vide pour l'année
        # code impropre ....
        if image_path:
            ndvi_matrix, _ = calcul_ndvi(image_path) # Calculer NDVI
            if ndvi_matrix is not None:
                ndvi_class_map = classify_ndvi(ndvi_matrix) # Classifier
                if ndvi_class_map is not None:
                    stats_df_year = calcul_class_stats(ndvi_class_map) # Calculer stats
                    if not stats_df_year.empty:
                        stats_df_year['Year'] = year # Ajouter colonne Année
                        all_stats.append(stats_df_year)
                        print(f"    -> Stats calculées.")
                    else: print(f"    ->  Stats vides après classification.")
                else: print(f"    -> Erreur: Classification NDVI échouée.")
            else: print(f"    -> Erreur: Calcul NDVI échoué.")
        else: print(f"    -> Erreur: Fichier TIF non trouvé.")

    if not all_stats: return pd.DataFrame()
    full_stats_df = pd.concat(all_stats, ignore_index=True)
    return full_stats_df

# --- Fonction pour l'évolution pixel ---
# actuellement abandonee ---------------------------
def get_pixel_evolution(forest_name, lat, lon):
    """
    Récupère la valeur du pixel aux coordonnées (lat, lon) pour toutes les années disponibles.
    Lit directement depuis les fichiers TIF (peut être lent).
    Retourne une liste de tuples (année, valeur) ou None en cas d'erreur.
    """
    available_years = get_available_years(forest_name)
    if not available_years:
        print(f"Aucune année trouvée pour {forest_name}")
        return None

    pixel_values = []
    transform = None
    crs = None
    target_crs = "EPSG:4326"

    # Essayer de lire les métadonnées d'un fichier pour obtenir la transformation
    for year in available_years:
        image_path = get_file_path(forest_name, year)
        if image_path:
            try:
                with rasterio.open(image_path) as src:
                    transform = src.transform
                    crs = src.crs
                    break # Métadonnées trouvées
            except  :
                print("Erreur ouverture {image_path} pour métadonnées: ")
                continue # Essayer l'année suivante
    
    if transform is None or crs is None:
         print(f"Impossible d'obtenir les métadonnées de géoréférencement pour {forest_name}")
         return None

    # Convertir les coordonnées du clic (lat/lon) en coordonnées du raster
    try:
        # Créer un point GeoJSON pour la transformation
        point_geom = {'type': 'Point', 'coordinates': (lon, lat)}
        # Transformer les coordonnées du CRS cible (EPSG:4326) vers le CRS du raster
        coords_raster = transform_geom(target_crs, crs, point_geom, precision=6)
        raster_x, raster_y = coords_raster['coordinates']
        # Obtenir les indices row/col du pixel
        row, col = rasterio.transform.rowcol(transform, raster_x, raster_y)
        print(f"Clic ({lat:.4f}, {lon:.4f}) -> Raster ({raster_x:.2f}, {raster_y:.2f}) -> Pixel ({row}, {col})")
    except Exception as e:
        print(f"Erreur lors de la conversion des coordonnées ou obtention row/col: {e}")
        return None

    # Lire la valeur pour chaque année
    for year in available_years:
        image_path = get_file_path(forest_name, year)
        if image_path:
            try:
                with rasterio.open(image_path) as src:
                    # S'assurer que row/col sont dans les limites
                    if 0 <= row < src.height and 0 <= col < src.width:
                        # Lire le NDVI (supposons bande 4 pour NIR, 3 pour Red)
                        # Ou lire la classe si c'est un raster classifié (supposons bande 1)
                        # Adaptez ceci à la structure de VOS TIFs
                        # Exemple: Lire la première bande (classe ?)
                        # Assurez-vous que la fenêtre est valide
                        window = rasterio.windows.Window(col, row, 1, 1)
                        # Lire une seule valeur pour la première bande
                        value = src.read(1, window=window)[0, 0]
                        
                        # Tenter de lire NDVI si les bandes existent
                        # try:
                        #    red_band = src.read(3, window=window).astype(np.float32)
                        #    nir_band = src.read(4, window=window).astype(np.float32)
                        #    denominator = nir_band + red_band
                        #    if denominator != 0:
                        #       value = (nir_band - red_band) / denominator
                        #    else: value = 0 # ou np.nan
                        # except IndexError:
                        #    print(f"Avertissement: Bandes NDVI non trouvées pour {year}, utilise bande 1.")

                        pixel_values.append((year, float(value))) # Assurer float
                    else:
                         print(f"Avertissement: Coordonnées ({row}, {col}) hors limites pour {year} ({src.height}x{src.width})")
                         pixel_values.append((year, np.nan)) # Marquer comme non disponible

            except:
                print("Erreur I/O lecture pixel {year}")
                pixel_values.append((year, np.nan))
        else:
            pixel_values.append((year, np.nan)) # Fichier non trouvé pour cette année

    # Trier par année
    pixel_values.sort(key=lambda item: item[0])
    return pixel_values

# --- Fonction pour calculer la tendance ---
def calculate_trend(stats_df, class_label):
    """Calcule la tendance linéaire de la surface pour une classe donnée."""
    if stats_df is None or stats_df.empty:
        return None, "Données manquantes"
    
    class_stats = stats_df[stats_df['Classe Label'] == class_label].dropna(subset=['Year', 'Surface (ha)'])
    if len(class_stats) < 2:
        return None, f"Pas assez de données pour {class_label}"

    years = class_stats['Year'].values
    surface = class_stats['Surface (ha)'].values

    # Calculer la régression linéaire pente
    try:
        coeffs = np.polyfit(years, surface, 1) # Degré 1 pour linéaire
        slope = coeffs[0] # Pente
        
        # Interpréter la tendance
        if abs(slope) < 0.1: # Seuil arbitraire pour considérer comme stable
             trend_text = "Stable"
        elif slope > 0:
             trend_text = f"Hausse ({slope:+.1f} ha/an)"
        else:
             trend_text = f"Baisse ({slope:+.1f} ha/an)"
        return slope, trend_text
    except Exception as e:
        print(f"Erreur calcul tendance pour {class_label}: {e}")
        return None, "Erreur calcul"
