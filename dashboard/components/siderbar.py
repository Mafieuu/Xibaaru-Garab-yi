from dash import html, dcc
import sys,os
# si Python ne parviens pas a acceder au dossier dashboard:l'ajouter au path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dashboard")))

def create_sidebar():
    
    return html.Div([
        html.H2("GeoForestGuardian"),
        html.P("Analyse de l'évolution de la dégradation des forêts dégradé du Sénégal", style={'color': 'rgb(33 36 35)'}),
        html.Hr(),
        html.Img(src='assets/forest_icon.png', 
                 style={'width': '60%', 'display':'block', 'margin':'auto', 'padding':'5px'}),
        html.Hr(),
        html.Div(id='sidebar-info-text', children=[
             dcc.Markdown("""
             **Bienvenue !**
             Ce tableau de bord permet de :
             * Visualiser la classification NDVI pour une année donnée.
             * Comparer les changements entre deux années.
             * Suivre l'évolution temporelle des classes de végétation (...)

             *Sélectionnez un mode, une forêt et une/des année(s).*
             """)
        ]),
        html.Hr(),
        html.Div(id='sidebar-dynamic-content')
    ], className='side_bar')
