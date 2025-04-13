from dash import dcc, html

from components.selectors import create_timeseries_filter

def create_primary_chart_area():

     return html.Div([
         html.Div([
             html.Label(id='primary-chart-title'),
             dcc.Loading(type="default", children=dcc.Graph(id='primary-chart')),
             html.Div([dcc.Markdown(id='primary-comment')], className='box_comment')
         ], className='box', style={'padding-bottom':'15px', 'min-height': '450px'}),
     ], style={'width': '40%'}) 

def create_secondary_chart_area():
     """ Zone graphique secondaire (gauche, sous le premier) """
     return html.Div([
         html.Div([
             html.Label(id='secondary-chart-title'),
             dcc.Loading(type="default", children=dcc.Graph(id='secondary-chart')),
             
             create_timeseries_filter(), 
         ], className='box', style={'padding-bottom':'15px', 'margin-top': '20px', 'min-height':'400px'})
     ], id='secondary-chart-container', style={'width': '20%', 'display':'none'}) # Caché initialement, prend la largeur du parent

def create_tertiary_chart_area():
     """ Zone pour un troisième graphique ou infos textuelles (droite, sous les stats?) """
     return html.Div([
         html.Div([
             html.Label(id='tertiary-area-title'),
             dcc.Loading(type="default", children=html.Div(id='tertiary-content')),
             dcc.Markdown(id='tertiary-comment', style={'margin-top':'10px'})
         ], className='box', style={'margin-top': '20px'})
     ], id='tertiary-chart-container', style={'width': '100%'}) # Prend toute la largeur de la colonne droite
