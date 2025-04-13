DATA_DIR = "data"  
NDVI_MIN = -1
NDVI_MAX = 1
NDVI_CLASSES = {
    1: {"label": "Eau", "range": [-1, 0.2], "color": "#007bff"},        
    2: {"label": "Sol Nu / Urbain", "range": [0.2, 0.3], "color": "#d2b48c"}, 
    3: {"label": "Végétation éparse", "range": [0.3, 0.5], "color": "#90ee90"}, 
    4: {"label": "Végétation Modérée", "range": [0.5, 0.7], "color": "#3cb371"}, 
    5: {"label": "Végétation Dense", "range": [0.7, 1], "color": "#006400"}     
}
# Mapping inverse pour retrouver le label à partir de l'index numérique
INDEX_TO_LABEL = {index: details["label"] for index, details in NDVI_CLASSES.items()}
# Mapping des couleurs pour le graphique imshow
COLOR_MAP = {index: details["color"] for index, details in NDVI_CLASSES.items()}
PIXEL_SURFACE_M2 = 10*10