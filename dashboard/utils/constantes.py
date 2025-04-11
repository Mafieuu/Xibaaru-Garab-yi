DATA_DIR = "data"  # A modifier si stockage dans AWS 
NDVI_MIN = -1
NDVI_MAX = 1
NDVI_CLASSES = {
    "Eau ": [-1, 0.2],
    "Végétation clair": [0.2, 0.4],
    "Végétation moyenne": [0.4, 0.6],
    "Végétation dense": [0.6, 1]
}
pixel_surface_m2=10*10 # pour le calcul des stats des classes de NDVI