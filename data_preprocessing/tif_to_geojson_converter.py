import os
import glob
import sys
import numpy as np
import rasterio
from rasterio import features
import geopandas as gpd
from shapely.geometry import shape
import utils.constantes as constantes
import argparse
import time
from tqdm import tqdm

def get_all_tif_files(data_dir=None):
    """Récupère tous les fichiers TIF dans le répertoire de données."""
    if data_dir is None:
        data_dir = os.path.join("dashboard", constantes.DATA_DIR)
    
    search_path = os.path.join(data_dir, "Foret_Classee_de_*.tif")
    files = glob.glob(search_path)
    
    if not files:
        print(f"Aucun fichier TIF trouvé dans {search_path}")
        return []
        
    return files

def check_geojson_exists(tif_path):
    """Vérifie si un fichier GeoJSON correspondant existe déjà."""
    geojson_path = tif_path.replace('.tif', '.geojson')
    return os.path.exists(geojson_path)

def extract_forest_name_and_year(tif_path):
    """Extrait le nom de la forêt et l'année à partir du chemin du fichier TIF."""
    basename = os.path.basename(tif_path)
    try:
        forest_name = basename.split("Foret_Classee_de_")[1].split("_01-01")[0]
        year = basename.split(".tif")[0].split("-")[-1]
        return forest_name, year
    except IndexError:
        print(f"Impossible d'extraire le nom de forêt et l'année de {basename}")
        return None, None

def calcul_ndvi(image_path):
    """Calcule la matrice NDVI à partir d'un fichier TIF."""
    try:
        with rasterio.open(image_path) as src:
            if src.count < 4:
                raise ValueError(f"Le fichier {image_path} a moins de 4 bandes")
            
            # Lire les bandes Rouge (index 3) et NIR (index 4)
            red_band = src.read(3).astype(np.float32)
            nir_band = src.read(4).astype(np.float32)

            # Masquage pour éviter la division par zéro
            np.seterr(divide='ignore', invalid='ignore')
            denominator = nir_band + red_band
            ndvi = np.where(denominator == 0, 0, (nir_band - red_band) / denominator)
            ndvi = np.clip(ndvi, constantes.NDVI_MIN, constantes.NDVI_MAX)

            return ndvi, src
    except rasterio.RasterioIOError as e:
        print(f"Erreur Rasterio lors de l'ouverture/lecture de {image_path}: {e}")
        return None, None
    except ValueError as e:
        print(f"Erreur lors du calcul NDVI pour {image_path}: {e}")
        return None, None
    except Exception as e:
        print(f"Erreur inattendue lors du calcul NDVI pour {image_path}: {e}")
        return None, None

def classify_ndvi(ndvi_matrix):
    """Classifie la matrice NDVI selon les seuils définis dans constantes."""
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

def create_geojson_from_classified_ndvi(ndvi_class_map, src, output_path):
    """
    Crée un fichier GeoJSON à partir d'une carte NDVI classifiée.
    Utilise la vectorisation de rasterio pour créer des polygones.
    """
    if ndvi_class_map is None:
        print(f"Erreur: Carte NDVI classifiée invalide pour {output_path}")
        return False
    
    try:
        # Créer des masques et des polygones pour chaque classe NDVI
        shapes = []
        for class_index in constantes.NDVI_CLASSES:
            # Créer un masque binaire pour cette classe
            mask = ndvi_class_map == class_index
            if not np.any(mask):
                continue  # Passer si la classe n'est pas présente
                
            # Vectoriser les pixels contigus de cette classe
            class_shapes = features.shapes(
                mask.astype(np.uint8),
                mask=mask,
                transform=src.transform
            )
            
            # Ajouter l'attribut de classe à chaque forme
            for geom, _ in class_shapes:
                shapes.append({
                    'geometry': geom,
                    'properties': {'class_index': int(class_index)}
                })
        
        if not shapes:
            print(f"Avertissement: Aucune forme générée pour {output_path}")
            return False
            
        # Créer un GeoDataFrame à partir des formes
        gdf = gpd.GeoDataFrame(
            [{'geometry': shape(item['geometry']), 'class_index': item['properties']['class_index']} for item in shapes],
            crs=src.crs
        )
        
        # Ajouter le label textuel pour chaque classe
        gdf['class_label'] = gdf['class_index'].map(lambda idx: constantes.INDEX_TO_LABEL.get(idx, "Inconnue"))
        
        # Convertir au CRS WGS84 (EPSG:4326) pour compatibilité
        if gdf.crs is None:
            gdf.set_crs("EPSG:4326", inplace=True)
        elif gdf.crs.to_epsg() != 4326:
            gdf = gdf.to_crs("EPSG:4326")
        
        # Simplifier les géométries pour réduire la taille des fichiers (optionnel)
        gdf['geometry'] = gdf['geometry'].simplify(tolerance=0.00001)
        
        # Sauvegarder en GeoJSON
        gdf.to_file(output_path, driver='GeoJSON')
        print(f"GeoJSON créé avec succès: {output_path}")
        return True
        
    except Exception as e:
        print(f"Erreur lors de la création du GeoJSON {output_path}: {e}")
        return False

def convert_tif_to_geojson(tif_path, force=False):
    """Convertit un fichier TIF en GeoJSON s'il n'existe pas déjà."""
    geojson_path = tif_path.replace('.tif', '.geojson')
    
    if os.path.exists(geojson_path) and not force:
        print(f"GeoJSON existe déjà: {geojson_path}, ignoré.")
        return False
    
    forest_name, year = extract_forest_name_and_year(tif_path)
    if not forest_name or not year:
        print(f"Impossible de traiter {tif_path}, nom de forêt ou année manquant.")
        return False
    
    print(f"Traitement de {forest_name} ({year})...")
    
    # Calculer NDVI
    ndvi_matrix, src = calcul_ndvi(tif_path)
    if ndvi_matrix is None or src is None:
        print(f"Échec du calcul NDVI pour {tif_path}")
        return False
    
    # Classifier NDVI
    ndvi_class_map = classify_ndvi(ndvi_matrix)
    if ndvi_class_map is None:
        print(f"Échec de la classification NDVI pour {tif_path}")
        return False
    
    # Créer GeoJSON
    result = create_geojson_from_classified_ndvi(ndvi_class_map, src, geojson_path)
    return result

def process_all_tifs(data_dir=None, force=False):
    """Traite tous les fichiers TIF qui n'ont pas de GeoJSON correspondant."""
    tif_files = get_all_tif_files(data_dir)
    
    if not tif_files:
        print("Aucun fichier TIF à traiter.")
        return
    
    start_time = time.time()
    success_count = 0
    skip_count = 0
    error_count = 0
    
    print(f"Début du traitement de {len(tif_files)} fichiers TIF...")
    
    for tif_path in tqdm(tif_files, desc="Conversion TIF → GeoJSON"):
        if not force and check_geojson_exists(tif_path):
            skip_count += 1
            continue
            
        try:
            result = convert_tif_to_geojson(tif_path, force)
            if result:
                success_count += 1
            else:
                error_count += 1
        except Exception as e:
            print(f"Erreur lors du traitement de {tif_path}: {e}")
            error_count += 1
    
    elapsed_time = time.time() - start_time
    
    print("\n===== Rapport de conversion =====")
    print(f"Temps total: {elapsed_time:.2f} secondes")
    print(f"Fichiers traités avec succès: {success_count}")
    print(f"Fichiers ignorés (GeoJSON existe déjà): {skip_count}")
    print(f"Fichiers en erreur: {error_count}")
    print("=================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convertit les fichiers TIF en GeoJSON.')
    parser.add_argument('--data-dir', help='Répertoire contenant les données (par défaut: dashboard/data)')
    parser.add_argument('--force', action='store_true', help='Force la conversion même si le GeoJSON existe déjà')
    parser.add_argument('--single', help='Convertit un seul fichier TIF spécifié')
    
    args = parser.parse_args()
    
    if args.single:
        if not os.path.exists(args.single):
            print(f"Erreur: Le fichier {args.single} n'existe pas.")
            sys.exit(1)
        
        print(f"Conversion du fichier unique: {args.single}")
        convert_tif_to_geojson(args.single, force=args.force)
    else:
        process_all_tifs(args.data_dir, force=args.force)