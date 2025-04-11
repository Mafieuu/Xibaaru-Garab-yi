# ====================================================================================
#
# ===================== Test unitaires des getters ==============================
#
# le dossier DATA_DIR sera simuler par le package tempfile
# car les .tif ne sont pas partagé dans le repertoire Github
# ref : https://docs.pytest.org/en/stable/how-to/monkeypatch.html
#
# ====================================================================================

import os
import tempfile
import numpy as np
import sys
# si python ne parviens pas a acceder au dossier dashboard:l'ajouter au path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dashboard")))

from utils.data_loader import get_forest_names, get_available_years, get_file_path
from utils.constantes import DATA_DIR
print(DATA_DIR)
# ====================================================================================

def test_get_forest_names(monkeypatch):
    print("Début du test : test_get_forest_names")

    # Simuler le dossier "data" temporairement

    with tempfile.TemporaryDirectory() as tmpdir: 
       

        # remplace temporairement la valeur de DATA_DIR par tmpdir

        monkeypatch.setattr("utils.constantes.DATA_DIR", tmpdir)
        print(f"Dossier temporaire créé : {tmpdir}")
        file1 = os.path.join(tmpdir, "Foret_Classee_de_Mbao_01-01-01-02-2020.tif")
        file2 = os.path.join(tmpdir, "Foret_Classee_de_Richard-Toll_01-01-01-02-2021.tif")
        open(file1, "a").close()
        open(file2, "a").close()
        print(f"Fichiers créés :\n- {file1}\n- {file2}")
        forests = get_forest_names()
        assert "Mbao" in forests
        assert "Richard-Toll" in forests
# ====================================================================================
def test_get_available_years(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setattr("utils.constantes.DATA_DIR", tmpdir)
        # Pendant ce test, fais comme si la variable DATA_DIR dans utils.constantes valait tmpdir
        open(os.path.join(tmpdir, "Foret_Classee_de_X_01-01-01-02-2019.tif"), "a").close()
        open(os.path.join(tmpdir, "Foret_Classee_de_Y_01-01-01-02-2020.tif"), "a").close()

        years = get_available_years()
        assert "2019" in years
        assert "2020" in years
# ====================================================================================
def test_get_file_path(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setattr("utils.constantes.DATA_DIR", tmpdir)
        filename = "Foret_Classee_de_Test_01-01-01-02-2022.tif"
        path = os.path.join(tmpdir, filename)
        open(path, "a").close()

        assert get_file_path("Test", "2022") == path