import numpy as np
import os
import sys
# si python ne parviens pas a acceder au dossier dashboard:l'ajouter au path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dashboard")))

from utils.data_loader import calcul_ndvi, classify_ndvi
# -------------------------------------------------------------------------------------------
# def test_calcul_ndvi(image_path):
    # pas necessaire
# -------------------------------------------------------------------------------------------
def test_classify_ndvi():
    ndvi_fake = np.array([
        [-0.5, 0.1, 0.3, 0.5, 0.7]
    ])
    class_map = classify_ndvi(ndvi_fake)
    # rappelons que:
    # NDVI_CLASSES = {
    # "Eau ": [-1, 0.2],
    # "Végétation clair": [0.2, 0.4],
    # "Végétation moyenne": [0.4, 0.6],
    # "Végétation dense": [0.6, 1]
    #    }
    expected = [1, 1, 2, 3, 4] 
    assert class_map.tolist()[0] == expected
