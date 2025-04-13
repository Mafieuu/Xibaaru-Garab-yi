
from dash import html

def create_footer():
     """Crée le pied de page."""
     # Repris de l'original
     return html.Footer("Dashboard Suivi Forêts | Données NDVI | ENSAE 2025",
                       style={'text-align':'center', 'padding':'20px', 'color':'grey'})