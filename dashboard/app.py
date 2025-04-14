from dash import Dash, html
import dash_bootstrap_components as dbc
import sys
import os
sys.path.append(os.path.dirname(__file__))

import aws_data_loader 

from components.siderbar import create_sidebar
from components.selectors import (create_analysis_selector, create_forest_selector,
                                 create_year_slider, create_year_selectors,
                                 create_view_type_selector, 
                                 create_timeseries_filter)

from components.charts import create_secondary_chart_area 
from components.map_display import create_map_area
from components.footer import create_footer 


from callbacks.main_callback import register_main_callback

try:
    initial_forests, initial_years = aws_data_loader.get_initial_data()
    if not initial_forests: print(" Aucune forêt trouvée.")
    if not initial_years: print(" Aucune année trouvée.")
except Exception as e:
    print(f"ERREUR chargement initial: {e}")
    initial_forests, initial_years = [], []


app = Dash(__name__, external_stylesheets=[dbc.themes.PULSE]) # Thème Pulse
app.title = "Dashboard Suivi Forêts classé du Sénégal"
app.config.suppress_callback_exceptions = True


app.layout = dbc.Container(fluid=True, children=[
    dbc.Row([
        dbc.Col(create_sidebar(), width=12, lg=2, className="side_bar bg-light"), # Utilise classe CSS

        dbc.Col([
            # Ligne 1: Titre et Sélecteurs
            dbc.Card(dbc.CardBody([
                html.H4("Tableau de Bord de suivi de la déforestation - Sénégal", className="card-title text-center"),
                dbc.Row([
                    dbc.Col(create_analysis_selector(), width=12, md=6, lg=3),
                    dbc.Col(create_forest_selector(initial_forests), width=12, md=6, lg=3),
                    dbc.Col(create_view_type_selector(), width=12, md=6, lg=3),
                    dbc.Col(create_year_selectors(initial_years), width=12, md=6, lg=3)
                ], className="align-items-center"),
                dbc.Row([
                    dbc.Col(create_year_slider(initial_years), width=12, lg=12)
                ], className="mt-3"),
            ]), className="mb-4",
    style={"background-color": "#f1faee"}),

            # Ligne 2: Graphique Temporel / Affichage Raster/Stats/Infos
            dbc.Row([
                # Colonne Gauche: Graphique Temporel seulement
                dbc.Col([
                     dbc.Card(dbc.CardBody([
                        html.Div(id='secondary-chart-wrapper', children=[
                            create_secondary_chart_area(),
                            create_timeseries_filter()
                        ])
                     ]), id='secondary-chart-container')
                ], width=12, lg=4), # Largeur Colonne Gauche

                # Colonne Droite: Affichage Raster, Stats Combinées, Infos Tertiaires
                dbc.Col(
                    # create_map_area retourne  la structure dbc.Col  pour cette zone
                    create_map_area(),
                    width=12, lg=8 
                ),
            ]),
                        # Ajout du pied de page
            create_footer()

        ], width=12, lg=10, style={'padding': '25px'})
    ], style={'min-height': '100vh'})
])


register_main_callback(app)

server = app.server
if __name__ == '__main__':
    app.run(debug=True)