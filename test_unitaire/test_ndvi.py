import numpy as np
import os
import sys
# si python ne parviens pas a acceder au dossier dashboard:l'ajouter au path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dashboard")))

from utils.data_loader import calcul_ndvi, classify_ndvi, calcul_class_stats
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
# -------------------------------------------------------------------------------------------
def test_calcul_class_stats(monkeypatch):
    ndvi_class_map = np.array([
        [1, 1, 2, 2],
        [3, 3, 3, 4]
    ])
    
   
    monkeypatch.setattr("utils.data_loader.constantes.pixel_surface_m2", 100) 
    fake_classes = {
        1: "Eau ",
        2: "Végétation clair",
        3: "Végétation moyenne",
        4: "Végétation dense"
    }
    monkeypatch.setattr("utils.data_loader.constantes.NDVI_CLASSES", fake_classes)
    stats_to_test = calcul_class_stats(ndvi_class_map)
    total_pixels = 8
    pixel_surface_m2 = 100
    for class_index, class_label in fake_classes.items():
        compteur_pixels_true = np.sum(ndvi_class_map == class_index) # is int
        area_ha_true = (compteur_pixels_true * pixel_surface_m2) / 10000
        pourcentage_couverture_true = (compteur_pixels_true / total_pixels) * 100

        assert stats_to_test[class_label]["pixel_count"] == compteur_pixels_true
        assert stats_to_test[class_label]["area_ha"] == area_ha_true
        assert stats_to_test[class_label]["pourcentage_couverture"] == pourcentage_couverture_true