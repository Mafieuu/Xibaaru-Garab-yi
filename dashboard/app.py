# app.py
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc # Nécessaire si on utilise des composants bootstrap (ex: Table)
from components.map_display import create_map_display
from components.selectors import create_selectors
from components.siderbar import create_sidebar
import data_loader as dl

from components.distribution_chart import create_distribution_chart
from callbacks.main_callback import register_main_callback


try:
    initial_forests, initial_years = dl.get_initial_data()
    if not initial_forests:
         print("ERREUR critique: Aucune forêt trouvée au démarrage. Vérifiez DATA_DIR et les fichiers.")
    if not initial_years:
         print("AVERTISSEMENT: Aucune année trouvée au démarrage.")

except Exception as e:
     print(f"ERREUR critique lors du chargement des données initiales: {e}")
     initial_forests, initial_years = [], []


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Dashboard Suivi Déforestation" # Titre de l'onglet navigateur


app.layout = html.Div([
    create_sidebar(), 

    html.Div([ 
        # Sélecteurs en haut
        create_selectors(initial_forests, initial_years),

        # Ligne avec Carte NDVI à gauche et Stats à droite
        create_map_display(),

        # Graphique de distribution en dessous
        create_distribution_chart(),

        # Pied de page 
        html.Footer([
            html.P("Projet de Suivi de Déforestation - Inspiré du Hackathon ENSAE"),

        ], style={'text-align': 'center', 'margin-top': '20px', 'color': 'grey'})

    ], className='main') 
])

register_main_callback(app)

if __name__ == '__main__':
    app.run(debug=True)