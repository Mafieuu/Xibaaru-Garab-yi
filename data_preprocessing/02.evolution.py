import boto3
import rasterio
import os
import io
import numpy as np
import argparse
from botocore.exceptions import NoCredentialsError

# Configuration AWS
    # Identifiants d'accès à l'API
    #client_id = 
    # client_secret = remplir
region_name = 'us-east-1'
bucket_name = 'hackaton-stat'

# Dossiers de travail
input_folder = 'data_raster/'
output_folder = 'data_evolution/'

# Connexion à S3
s3_client = boto3.client(
    's3',
        # Identifiants d'accès à l'API
    #client_id = 
    # client_secret = remplir
    region_name=region_name
)

def check_raster_exists(bucket, key):
    """Vérifie si un raster existe à l'emplacement spécifié"""
    try:
        s3_client.head_object(Bucket=bucket, Key=key)
        return True
    except:
        return False

def load_raster_from_s3(bucket, key):
    """Charge un fichier raster depuis S3 dans un objet rasterio"""
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        raster_bytes = response['Body'].read()
        return rasterio.open(io.BytesIO(raster_bytes))
    except Exception as e:
        print(f"Erreur lors du chargement de {key}: {e}")
        return None

def check_output_exists(bucket, output_key):
    """Vérifie si le fichier de sortie existe déjà dans S3"""
    try:
        s3_client.head_object(Bucket=bucket, Key=output_key)
        return True
    except:
        return False

def calculate_difference(raster1, raster2):
    """Calcule la différence entre deux rasters"""
    # Lire les données des rasters
    data1 = raster1.read(1)  # Lecture de la première bande
    data2 = raster2.read(1)  # Lecture de la première bande
    
    # Calculer la différence (raster2 - raster1)
    diff_data = data2.astype(float) - data1.astype(float)
    
    return diff_data, raster1.profile

def save_raster_to_s3(data, profile, bucket, output_key):
    """Sauvegarde un raster dans S3"""
    try:
        # Créer un fichier temporaire en mémoire
        with io.BytesIO() as memfile:
            # Mettre à jour le profil pour le nouveau raster
            profile.update(
                dtype=rasterio.float32,
                count=1,
                compress='lzw'
            )
            
            # Écrire le raster dans le fichier mémoire
            with rasterio.open(memfile, 'w', **profile) as dst:
                dst.write(data.astype(rasterio.float32), 1)
            
            # Retourner au début du fichier mémoire
            memfile.seek(0)
            
            # Téléverser vers S3
            s3_client.upload_fileobj(memfile, bucket, output_key)
            
        print(f"Raster de différence sauvegardé avec succès: {output_key}")
        return True
    except Exception as e:
        print(f"Erreur lors de la sauvegarde du raster: {e}")
        return False

def process_rasters(raster1_path, raster2_path):
    """Traite deux rasters en calculant leur différence"""
    # Construire les chemins complets des rasters
    raster1_key = input_folder + raster1_path
    raster2_key = input_folder + raster2_path
    
    # Vérifier si les rasters existent
    if not check_raster_exists(bucket_name, raster1_key):
        print(f"Le raster {raster1_key} n'existe pas.")
        return False
        
    if not check_raster_exists(bucket_name, raster2_key):
        print(f"Le raster {raster2_key} n'existe pas.")
        return False
    
    # Extraire juste les noms de fichiers (sans le chemin)
    raster1_filename = os.path.basename(raster1_path)
    raster2_filename = os.path.basename(raster2_path)
    
    # Créer le nom du fichier de sortie (concaténation des noms des deux rasters)
    output_name = f"{os.path.splitext(raster1_filename)[0]}_{os.path.splitext(raster2_filename)[0]}_diff.tif"
    output_key = output_folder + output_name
    
    # Vérifier si le fichier de sortie existe déjà
    if check_output_exists(bucket_name, output_key):
        print(f"Le fichier {output_key} existe déjà. Traitement ignoré.")
        return False
    
    # Charger les rasters
    print(f"Chargement de {raster1_key}...")
    raster1 = load_raster_from_s3(bucket_name, raster1_key)
    
    print(f"Chargement de {raster2_key}...")
    raster2 = load_raster_from_s3(bucket_name, raster2_key)
    
    if raster1 is None or raster2 is None:
        print("Impossible de charger les rasters. Arrêt du traitement.")
        return False
    
    # Calculer la différence
    print("Calcul de la différence entre les rasters...")
    diff_data, profile = calculate_difference(raster1, raster2)
    
    # Sauvegarder le résultat
    print(f"Sauvegarde du résultat dans {output_key}...")
    success = save_raster_to_s3(diff_data, profile, bucket_name, output_key)
    
    # Fermer les fichiers
    raster1.close()
    raster2.close()
    
    return success

def main():
    """Fonction principale"""
    # Configuration de l'analyseur d'arguments
    parser = argparse.ArgumentParser(description='Calcul de différence entre deux rasters')
    parser.add_argument('raster1', type=str, help='Chemin relatif du premier fichier raster à partir de data_raster/')
    parser.add_argument('raster2', type=str, help='Chemin relatif du deuxième fichier raster à partir de data_raster/')
    
    args = parser.parse_args()
    
    # Traiter les rasters spécifiés
    process_rasters(args.raster1, args.raster2)

if __name__ == "__main__":
    main()
