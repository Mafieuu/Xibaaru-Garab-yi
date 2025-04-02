# **********************************************************************************************************
# Ce script permet de merger tous les fichiers geojson present dans le dossier to_merge
#
# **************************************************************************************************************
import geojson
import os
import glob

def merge_geojson_files(input_dir="to_merge", output_file="merged_output.geojson"):
    
    if not os.path.exists(input_dir) or not os.path.isdir(input_dir):
        print(f"Le dossier {input_dir} n'existe pas ")
        return
    
    # Chercher tous les fichiers GeoJSON dans le dossier
    files = glob.glob(os.path.join(input_dir, "*.geojson"))
    
    if not files:
        print(f"Aucun fichier GeoJSON trouvé dans le dossier {input_dir}")
        return None
    
    # Liste pour stocker toutes les features
    all_features = []
    
    # Lire chaque fichier et extraire les features
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = geojson.load(f)
                
                # Vérifier si c'est un GeoJSON valide 
                if hasattr(data, 'features'):
                    all_features.extend(data.features)
                else:
                    print(f"Attention: {file_path} ne contient pas de 'features'")
        except Exception as e:
            print(f"Erreur lors de la lecture de {file_path}: {str(e)}")
    
    # Créer le GeoJSON résultant
    merged_geojson = geojson.FeatureCollection(all_features)
    
    # Écrire le résultat dans un nouveau fichier
    with open(output_file, 'w', encoding='utf-8') as f:
        geojson.dump(merged_geojson, f)
    
    print(f"{len(files)} fichiers fusionnés avec un total de {len(all_features)} features")
    print(f"Résultat enregistré dans {output_file}")
    
    return merged_geojson

if __name__ == "__main__":
    merge_geojson_files()