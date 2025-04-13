
from dash import dcc, html

def create_primary_chart_area():
     """ Crée la zone pour le graphique principal gauche et le commentaire."""
     return html.Div([
         html.Div([
             html.Label(id='primary-chart-title', style={'font-weight':'bold'}),
             dcc.Loading(type="default", children=dcc.Graph(id='primary-chart')),
             html.Div([html.P(id='primary-comment')], className='box_comment') 
         ], className='box', style={'padding-bottom':'15px', 'height': '450px'}), 

         html.Div(id='secondary-chart-area', children=[
              html.Div([
                   html.Label(id='secondary-chart-title', style={'font-weight':'bold'}),
                   dcc.Loading(type="default", children=dcc.Graph(id='secondary-chart'))
              ], className='box', style={'padding-bottom':'15px', 'margin-top': '15px'}) # Ajout marge
         ], style={'display': 'block'}) 

     ], style={'width': '40%'}) 

def create_map_area():
    """ Crée la zone pour la carte droite et les contrôles/stats."""
    return html.Div([
        html.Div([
             html.Label(id='map-title', style={'font-weight':'bold', 'margin': '10px'}),
        ], className='box'),

        html.Div([
             html.Div([
                dcc.Loading(type="default", children=dcc.Graph(id='ndvi-map', style={'height': '400px'})) 
             ], style={'width': '60%', 'display': 'inline-block', 'vertical-align': 'top'}),

             html.Div([
                  html.H5("Statistiques Détaillées"),
                  dcc.Loading(type="default", children=html.Div(id='stats-display', style={'height': '380px', 'overflow-y': 'auto'})) # Hauteur et scroll
             ], style={'width': '38%', 'display': 'inline-block', 'vertical-align': 'top', 'padding-left': '2%'})

        ], style={'margin-top': '10px'})

    ], style={'width': '60%'}) 
