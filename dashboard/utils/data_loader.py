import glob
import os
from constantes import *


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

