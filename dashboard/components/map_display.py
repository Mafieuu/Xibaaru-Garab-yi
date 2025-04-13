# components/map_display.py
from dash import dcc, html
import dash_bootstrap_components as dbc 

def create_map_display():
    """Crée la zone d'affichage pour la carte NDVI et les statistiques."""
    return html.Div([
        html.Div([
             html.H4(id='map-title', style={'text-align': 'center'}), 
             dcc.Loading( 
                 type="default",
                 children=dcc.Graph(id='ndvi-map', config={'scrollZoom': True}) 
             ),
             html.P("Carte NDVI classifiée. Les couleurs représentent différentes classes de végétation.",
                    style={'font-size': 'small', 'text-align': 'center'})
        ], className='box', style={'width': '65%', 'padding': '15px', 'margin-right': '10px'}), 

        html.Div([
             html.H5("Statistiques de Couverture"),
             dcc.Loading(
                 type="default",
                 children=html.Div(id='vegetation-stats-display') 
            ),
             html.P("Surface en hectares (ha) et pourcentage (%) de couverture pour chaque classe.",
                     style={'font-size': 'small'})
        ], className='box', style={'width': '30%', 'padding': '15px'}) 

    ], className='row', style={'display': 'flex', 'margin': '10px 0'}) 

