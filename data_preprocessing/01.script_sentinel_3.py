import os
import numpy as np
import geopandas as gpd
import rasterio
from rasterio.mask import mask
from rasterio.features import shapes
from shapely.geometry import mapping, shape
import pandas as pd
from datetime import datetime
from pathlib import Path
import warnings
import matplotlib.pyplot as plt
from io import BytesIO
import json

# Imports pour OAuth2
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from datetime import datetime, timedelta


# Supprimer les avertissements pour plus de clarté
warnings.filterwarnings("ignore")


# Variables globales pour stocker le token entre les appels
_token = None
_oauth_session = None
_expires_at = None

def get_oauth_token(force_refresh=False):
    """
    Obtient un token OAuth2 pour l'API Sentinel Hub et gère son renouvellement automatique.
    
    Args:
        force_refresh (bool): Force le renouvellement du token même s'il n'est pas expiré
    
    Returns:
        tuple: (session OAuth2, token d'accès) ou (None, None) en cas d'erreur
    """
    global _token, _oauth_session, _expires_at
    
    # Identifiants d'accès à l'API
    #client_id = 
    # client_secret = remplir
    token_url = 'https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token'
    
    current_time = datetime.now()
    
    # Vérifier si le token existe et s'il est encore valide
    if not force_refresh and _token and _oauth_session and _expires_at:
        # Ajouter une marge de sécurité de 5 minutes
        if current_time + timedelta(minutes=5) < _expires_at:
            return _oauth_session, _token
    
    try:
        # Création du client OAuth2 et de la session
        client = BackendApplicationClient(client_id=client_id)
        _oauth_session = OAuth2Session(client=client)
        
        # Récupération du token d'accès
        _token = _oauth_session.fetch_token(
            token_url=token_url,
            client_secret=client_secret,
            include_client_id=True
        )
        
        # Calcul de la date d'expiration
        if 'expires_at' in _token:
            _expires_at = datetime.fromtimestamp(_token['expires_at'])
        else:
            # Si pas d'information d'expiration, on suppose 1 heure
            _expires_at = current_time + timedelta(hours=1)
        
        print(f"Token d'authentification obtenu avec succès (expire le {_expires_at})")
        return _oauth_session, _token
    except Exception as e:
        print(f"Erreur lors de l'obtention du token: {e}")
        _token = None
        _oauth_session = None
        _expires_at = None
        return None, None
    

"""
def get_oauth_token():

    # Identifiants d'accès à l'API
    client_id = 'sh-3794e51b-81ec-44b6-b862-e66f890ca138'
    client_secret = '7pZTvLfmx8ZZ0Mf6A9bpfXcblbDfA77T'
    token_url = 'https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token'
    
    try:
        # Création du client OAuth2 et de la session
        client = BackendApplicationClient(client_id=client_id)
        oauth = OAuth2Session(client=client)
        
        # Récupération du token d'accès
        token = oauth.fetch_token(
            token_url=token_url,
            client_secret=client_secret,
            include_client_id=True
        )
        
        print("Token d'authentification obtenu avec succès")
        return oauth, token
    except Exception as e:
        print(f"Erreur lors de l'obtention du token: {e}")
        return None, None
"""

def get_evalscript_calibrated():
    """
    Définit un script d'évaluation amélioré pour Sentinel Hub.
    """
    return """
    //VERSION=3
    function setup() {
        return {
            input: [{
                bands: ["B02", "B03", "B04", "B08"],
                units: "REFLECTANCE"
            }],
            output: {
                bands: 5,
                sampleType: "FLOAT32"
            }
        };
    }

    function normalizeValues(val, min, max) {
        return Math.max(0, Math.min(1, (val - min) / (max - min)));
    }

    function evaluatePixel(sample) {
        // Calcul du NDVI
        let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
        
        // Valeurs typiques min/max pour la normalisation
        const minReflR = 0.0;
        const maxReflR = 0.3;
        const minReflG = 0.0;
        const maxReflG = 0.3;
        const minReflB = 0.0;
        const maxReflB = 0.3;
        
        // Normalisation des bandes pour une meilleure cohérence entre images
        let r_norm = normalizeValues(sample.B04, minReflR, maxReflR);
        let g_norm = normalizeValues(sample.B03, minReflG, maxReflG);
        let b_norm = normalizeValues(sample.B02, minReflB, maxReflB);
        
        return [r_norm, g_norm, b_norm, sample.B08, ndvi];
    }
    """

def check_and_convert_shapefile(shapefile_path):
    """
    Vérifie et convertit le shapefile en WGS 84 (EPSG:4326) si nécessaire.
    """
    gdf = gpd.read_file(shapefile_path)
    print(f"CRS du shapefile original: {gdf.crs}")
    
    # Vérifier si le CRS est déjà WGS 84
    if gdf.crs != "EPSG:4326":
        print(f"Conversion du CRS {gdf.crs} vers WGS84 (EPSG:4326)...")
        gdf = gdf.to_crs("EPSG:4326")
    
    return gdf

def get_sentinel_data_direct(oauth_session, token, geometry, start_date, end_date, resolution=10):
    """
    Télécharge les données Sentinel-2 pour la période spécifiée.
    """
    # URL de l'API Process
    process_api_url = "https://sh.dataspace.copernicus.eu/api/v1/process"
    
    # Extraire les limites de la géométrie
    minx, miny, maxx, maxy = geometry.bounds
    bbox = [minx, miny, maxx, maxy]
    
    # Calcul approximatif des dimensions
    earth_radius = 6371000  # rayon moyen de la Terre en mètres
    width_m = abs(maxx - minx) * (np.pi/180) * earth_radius * np.cos((miny + maxy) * np.pi/360)
    height_m = abs(maxy - miny) * (np.pi/180) * earth_radius
    
    # Calcul des dimensions en pixels selon la résolution demandée
    width = max(int(width_m / resolution), 10)
    height = max(int(height_m / resolution), 10)
    
    # Standardisation des dimensions pour éviter des images trop grandes
    max_dimension = 2048
    if width > max_dimension or height > max_dimension:
        ratio = max(width, height) / max_dimension
        width = int(width / ratio)
        height = int(height / ratio)
    
    # Formatage des dates pour l'API
    time_range = {
        "from": f"{start_date}T00:00:00Z",
        "to": f"{end_date}T23:59:59Z"
    }
    
    # Préparation du payload de la requête
    payload = {
        "input": {
            "bounds": {
                "bbox": bbox,
                "properties": {
                    "crs": "http://www.opengis.net/def/crs/EPSG/0/4326"
                }
            },
            "data": [{
                "dataFilter": {
                    "timeRange": time_range,
                    "mosaickingOrder": "leastCC",
                    "maxCloudCoverage": 30
                },
                "type": "sentinel-2-l2a"
            }]
        },
        "output": {
            "width": width,
            "height": height,
            "responses": [{
                "identifier": "default",
                "format": {
                    "type": "image/tiff"
                }
            }]
        },
        "evalscript": get_evalscript_calibrated()
    }
    
    # En-têtes avec le token d'authentification
    headers = {
        "Authorization": f"Bearer {token['access_token']}",
        "Content-Type": "application/json"
    }
    
    try:
        # Envoi de la requête
        print(f"Envoi de la requête à Sentinel Hub pour {width}x{height} pixels...")
        response = oauth_session.post(process_api_url, json=payload, headers=headers)
        
        # Vérification de la réponse
        if response.status_code == 200:
            # Charger les données depuis la réponse
            with BytesIO(response.content) as bio:
                with rasterio.open(bio) as src:
                    # Vérifier le nombre de bandes
                    band_count = src.count
                    
                    # Lire toutes les bandes
                    data = src.read()
                    # Obtenir les métadonnées pour la géoréférence
                    profile = src.profile
            
            print(f"Données téléchargées avec succès: {data.shape} (bandes, hauteur, largeur)")
            
            return data, profile
        else:
            print(f"Erreur {response.status_code}: {response.text}")
            return None, None
    except Exception as e:
        print(f"Erreur lors du téléchargement des données: {e}")
        return None, None

def clip_raster_to_polygon(data, profile, geometry):
    """
    Découpe le raster selon la forme exacte du polygone.
    """
    try:
        # Création d'un raster virtuel en mémoire avec les données téléchargées
        with rasterio.io.MemoryFile() as memfile:
            with memfile.open(**profile) as src:
                # Écrire les données dans le fichier virtuel
                src.write(data)
                
                # Préparer la géométrie pour le masquage
                geoms = [mapping(geometry)]
                
                # Appliquer le masque et obtenir les données découpées
                out_image, out_transform = mask(src, geoms, crop=True, all_touched=False, nodata=None)
                
                # Copier et mettre à jour le profil du raster
                out_profile = src.profile.copy()
                out_profile.update({
                    "height": out_image.shape[1],
                    "width": out_image.shape[2],
                    "transform": out_transform,
                    "nodata": None
                })
            
        return out_image, out_profile
    
    except Exception as e:
        print(f"Erreur lors du découpage du raster: {e}")
        return None, None

def save_multiband_raster(data, profile, output_path):
    """
    Sauvegarde un raster multi-bandes (RGB, NIR, et NDVI) dans un seul fichier GeoTIFF.
    """
    if data is None:
        print("Pas de données à sauvegarder")
        return False
    
    try:
        # Mise à jour du profil pour le fichier de sortie
        out_profile = profile.copy()
        out_profile.update({
            'count': 5,
            'dtype': rasterio.float32,
            'driver': 'GTiff',
            'compress': 'lzw',
            'nodata': None
        })
        
        # Création du fichier de sortie
        with rasterio.open(output_path, 'w', **out_profile) as dst:
            # Écriture de toutes les bandes
            for i in range(data.shape[0]):
                dst.write(data[i], i+1)
            
            # Ajout des descriptions de bandes
            dst.set_band_description(1, "Rouge (B4) - normalisé")
            dst.set_band_description(2, "Vert (B3) - normalisé")
            dst.set_band_description(3, "Bleu (B2) - normalisé")
            dst.set_band_description(4, "Proche Infrarouge (B8)")
            dst.set_band_description(5, "NDVI")
        
        print(f"Raster multi-bandes sauvegardé: {output_path}")
        return True
    
    except Exception as e:
        print(f"Erreur lors de la sauvegarde du raster: {e}")
        return False

def create_quick_rgb_preview(data, output_path, percentile_clip=(2, 98)):
    """
    Crée une image RGB de prévisualisation rapide avec amélioration de contraste.
    """
    try:
        # Extraire les trois premières bandes (RGB)
        rgb = data[0:3, :, :]
        
        # Transposer pour obtenir le format attendu par matplotlib
        rgb = np.transpose(rgb, (1, 2, 0))
        
        # Appliquer l'étirement du contraste par percentile
        for i in range(3):
            p_low, p_high = np.percentile(rgb[:,:,i], percentile_clip)
            rgb[:,:,i] = np.clip((rgb[:,:,i] - p_low) / (p_high - p_low), 0, 1)
        
        # Créer la figure
        plt.figure(figsize=(10, 10))
        plt.imshow(rgb)
        plt.axis('off')
        plt.tight_layout()
        
        # Sauvegarder l'image
        plt.savefig(output_path, dpi=150, bbox_inches='tight', pad_inches=0)
        plt.close()
        
        print(f"Aperçu RGB sauvegardé: {output_path}")
        return True
    
    except Exception as e:
        print(f"Erreur lors de la création de l'aperçu RGB: {e}")
        return False

def create_ndvi_classified_raster(raster_path, output_path):
    """
    Crée un raster classifié basé sur la bande NDVI avec 5 classes prédéfinies.
    
    Classes:
    1: Très faible végétation (NDVI < 0.1)
    2: Faible végétation (0.1 <= NDVI < 0.3)
    3: Végétation modérée (0.3 <= NDVI < 0.5)
    4: Végétation dense (0.5 <= NDVI < 0.7)
    5: Végétation très dense (NDVI >= 0.7)
    """
    try:
        # Ouvrir le raster source
        with rasterio.open(raster_path) as src:
            # Vérifier que le raster a au moins 5 bandes (la bande NDVI est la 5ème)
            if src.count < 5:
                print(f"Le raster {raster_path} ne contient pas de bande NDVI")
                return False
            
            # Lire la bande NDVI (5ème bande)
            ndvi = src.read(5)
            
            # Créer un nouveau raster pour les classes
            classified = np.zeros_like(ndvi, dtype=np.uint8)
            
            # Définir les seuils et classes
            classified[(ndvi >= -1) & (ndvi < 0.1)] = 1               # Très faible végétation
            classified[(ndvi >= 0.1) & (ndvi < 0.3)] = 2  # Faible végétation
            classified[(ndvi >= 0.3) & (ndvi < 0.5)] = 3  # Végétation modérée
            classified[(ndvi >= 0.5) & (ndvi < 0.7)] = 4  # Végétation dense
            classified[(ndvi >= 0.7)& (ndvi <= 1)] = 5              # Végétation très dense
            
            # Copier et adapter le profil pour le raster classifié
            profile = src.profile.copy()
            profile.update({
                'count': 1,
                'dtype': rasterio.uint8,
                'nodata': None
            })
            
            # Sauvegarder le raster classifié
            with rasterio.open(output_path, 'w', **profile) as dst:
                dst.write(classified, 1)
                
                # Ajouter des métadonnées sur la classification
                dst.set_band_description(1, "Classes NDVI (1:très faible, 2:faible, 3:modérée, 4:dense, 5:très dense)")
                dst.update_tags(
                    CLASSIFICATION_VALUES="1,2,3,4,5",
                    CLASSIFICATION_NAMES="Très faible végétation,Faible végétation,Végétation modérée,Végétation dense,Végétation très dense",
                    CLASSIFICATION_NDVI_RANGES="<0.1,0.1-0.3,0.3-0.5,0.5-0.7,>=0.7"
                )
            
            print(f"Raster classifié sauvegardé: {output_path}")
            return True
    
    except Exception as e:
        print(f"Erreur lors de la création du raster classifié: {e}")
        return False

def create_geojson_from_classified(classified_raster_path, output_geojson_path):
    """
    Crée un fichier GeoJSON à partir du raster classifié.
    Chaque classe de NDVI devient une entité distincte dans le GeoJSON.
    """
    try:
        # Ouvrir le raster classifié
        with rasterio.open(classified_raster_path) as src:
            # Lire la bande classifiée
            class_data = src.read(1)
            
            # Préparer les classes à vectoriser
            unique_classes = np.unique(class_data)
            unique_classes = unique_classes[unique_classes > 0]  # Ignorer les zones sans données (0)
            
            # Vectoriser chaque classe
            features = []
            for class_value in unique_classes:
                # Créer un masque pour la classe actuelle
                mask = class_data == class_value
                
                # Convertir les pixels connectés en polygones
                class_polygons = list(shapes(mask.astype(np.uint8), mask=mask, transform=src.transform))
                
                # Obtenir le nom de la classe
                if class_value == 1:
                    class_name = "Très faible végétation"
                elif class_value == 2:
                    class_name = "Faible végétation"
                elif class_value == 3:
                    class_name = "Végétation modérée"
                elif class_value == 4:
                    class_name = "Végétation dense"
                elif class_value == 5:
                    class_name = "Végétation très dense"
                else:
                    class_name = f"Classe {class_value}"
                
                # Ajouter les polygones à la liste des entités
                for polygon, value in class_polygons:
                    feature = {
                        "type": "Feature",
                        "properties": {
                            "class_value": int(class_value),
                            "class_name": class_name
                        },
                        "geometry": polygon
                    }
                    features.append(feature)
            
            # Créer le GeoJSON
            geojson = {
                "type": "FeatureCollection",
                "features": features
            }
            
            # Écrire le GeoJSON dans un fichier
            with open(output_geojson_path, 'w') as f:
                json.dump(geojson, f)
                
            print(f"GeoJSON créé avec succès: {output_geojson_path}")
            return True
            
    except Exception as e:
        print(f"Erreur lors de la création du GeoJSON: {e}")
        return False

def process_polygon(oauth_session, token, gdf_row, year, output_dir, shapefile_dir):
    """
    Traite un polygone forestier pour une année spécifique en saison sèche uniquement.
    """
    polygon_name = gdf_row['NOM']
    polygon_geom = gdf_row['geometry']
    
    # Créer les dossiers de sortie
    polygon_output_dir = os.path.join(output_dir, f"{polygon_name}")
    os.makedirs(polygon_output_dir, exist_ok=True)
    
    # Définir la période pour la saison sèche (Janvier-Février)
    dry_season_start = f"{year}-01-01"
    dry_season_end = f"{year}-02-01"
    
    print(f"Téléchargement des données pour {polygon_name}, saison sèche {year}...")
    
    # Télécharger les données Sentinel
    data, profile = get_sentinel_data_direct(oauth_session, token, polygon_geom, dry_season_start, dry_season_end)
    
    if data is None:
        print(f"Aucune donnée disponible pour {polygon_name} en saison sèche {year}")
        return False
    
    # Découper le raster selon le polygone exact
    print(f"Découpage du raster selon le polygone {polygon_name}...")
    clipped_data, clipped_profile = clip_raster_to_polygon(data, profile, polygon_geom)
    
    if clipped_data is None:
        print(f"Échec du découpage pour {polygon_name} en saison sèche {year}")
        return False
    
    # Définir les chemins de sortie
    output_filename = f"{polygon_name}_dry_{year}"
    raster_output_path = os.path.join(polygon_output_dir, f"{output_filename}.tif")
    preview_output_path = os.path.join(polygon_output_dir, f"{output_filename}_preview.png")
    
    # Sauvegarder le raster multi-bandes
    if not save_multiband_raster(clipped_data, clipped_profile, raster_output_path):
        return False
    
    # Créer un aperçu RGB pour vérification visuelle rapide
    create_quick_rgb_preview(clipped_data, preview_output_path)
    
    # Créer le raster classifié par NDVI
    classified_output_path = os.path.join(polygon_output_dir, f"class_{output_filename}.tif")
    if not create_ndvi_classified_raster(raster_output_path, classified_output_path):
        return False
    
    # Créer le GeoJSON à partir du raster classifié
    os.makedirs(shapefile_dir, exist_ok=True)
    geojson_output_path = os.path.join(shapefile_dir, f"class_{output_filename}.geojson")
    if not create_geojson_from_classified(classified_output_path, geojson_output_path):
        return False
    
    print(f"Traitement terminé pour {polygon_name} en saison sèche {year}")
    return True

# Point d'entrée principal du script
if __name__ == "__main__":
    # Paramètres
    shapefile_path = "C:/Users/LENOVO/Desktop/hackathon_stat/Data_hackathon_stat/shapefile/class_forest.shp" 
    output_base_dir = "C:/Users/LENOVO/Desktop/hackathon_stat/Data_hackathon_stat/data_raster" 
    shapefile_output_dir = "C:/Users/LENOVO/Desktop/hackathon_stat/Data_hackathon_stat/shapefile"
    start_year = 2017  # Année de début
    end_year = 2023    # Année de fin
    
    print("\n=== EXTRACTION DE DONNÉES SENTINEL-2 POUR L'ANALYSE FORESTIÈRE ===")
    print("Ce script simplifié télécharge uniquement les images de saison sèche")
    print("et génère des classifications par NDVI avec GeoJSON correspondant.")
    
    # Obtention du token OAuth2
    print("\n== ÉTAPE 1: AUTHENTIFICATION ==")
    oauth_session, token = get_oauth_token()
    if oauth_session is None or token is None:
        print("Erreur critique d'authentification. Arrêt du script.")
        exit(1)
    
    # Charger le shapefile des polygones forestiers
    print("\n== ÉTAPE 2: CHARGEMENT DES POLYGONES ==")
    gdf = check_and_convert_shapefile(shapefile_path)
    print(f"Nombre de polygones à traiter: {len(gdf)}")
    
    # Vérifier et créer le dossier de sortie
    os.makedirs(output_base_dir, exist_ok=True)
    
    # Traiter chaque polygone pour chaque année
    print("\n== ÉTAPE 3: TRAITEMENT DES DONNÉES PAR POLYGONE ET ANNÉE ==")
    years = range(start_year, end_year + 1)
    
    for year in years:
        print(f"\nTraitement de l'année {year}...")
        
        for idx, row in gdf.iterrows():
            print(f"\nTraitement du polygone {idx+1}/{len(gdf)}: {row['NOM']}")
            
            # Traiter le polygone (uniquement saison sèche)
            process_polygon(oauth_session, token, row, year, output_base_dir, shapefile_output_dir)
    
    print("\nTraitement terminé pour toutes les années!")