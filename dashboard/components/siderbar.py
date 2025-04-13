# components/sidebar.py
from dash import html

def create_sidebar():
    """Crée le composant de la barre latérale."""
    return html.Div([
        html.H2("Suivi Déforestation"), 
        html.Label(
            "Tableau de bord pour visualiser l'évolution de la couverture végétale "
            "dans différentes forêts classées.",
            style={'color': 'rgb(33 36 35)'}
        ),
        html.Hr(),
        html.P("Sélectionnez une forêt et une année pour afficher la carte NDVI classifiée et les statistiques associées."),
        
        html.Div(id='sidebar-info')
    ], className='side_bar') 
