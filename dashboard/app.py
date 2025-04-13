# app.py
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from components.siderbar import create_sidebar
import data_loader as dl
from components.selectors import create_analysis_selector, create_forest_selector, create_year_selectors
from components.main_view_components import create_primary_chart_area, create_map_area
from components.footer import create_footer
from callbacks.main_callback import register_main_callback
import plotly.graph_objects as go 


try:
    initial_forests, initial_years = dl.get_initial_data()
    if not initial_forests: print("ERREUR critique: Aucune forêt trouvée.")
    if not initial_years: print("AVERTISSEMENT: Aucune année trouvée.")
except Exception as e:
    print(f"ERREUR critique chargement initial: {e}")
    initial_forests, initial_years = [], []

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Dashboard Suivi Forêts"
app.config.suppress_callback_exceptions = True # Nécessaire car on cache/affiche des outputs

initial_fig = go.Figure()
initial_fig.update_layout(xaxis={"visible": False}, yaxis={"visible": False},
                           annotations=[{"text": "Sélectionnez...", "xref": "paper", "yref": "paper", "showarrow": False}])

app.layout = html.Div([
    create_sidebar(), 

    html.Div([ 
        html.Div([
            html.Div([ 
                html.Label("Mode d'Analyse:", style={'margin-right': '10px'}),
                create_analysis_selector()
            ], style={'display': 'inline-block', 'margin-right': '30px'}),
            html.Div([ 
                 create_forest_selector(initial_forests)
            ], style={'display': 'inline-block', 'margin-right': '30px'}),

             html.Div([ 
                 create_year_selectors(initial_years)
             ], style={'display': 'inline-block'}),

        ], className='box', style={'margin': '10px', 'padding': '15px'}), 

        
        html.Div([
            create_primary_chart_area(), 
            create_map_area(),           
        ], className='row'), 


        create_footer(),

    ], className='main') 
])

register_main_callback(app)


if __name__ == '__main__':
    app.run(debug=True) 