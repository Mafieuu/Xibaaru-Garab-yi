from dash import html
import sys,os
# si Python ne parviens pas a acceder au dossier dashboard:l'ajouter au path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dashboard")))

def create_sidebar():
    return html.Div([
        html.H2("Suivi Forêts"), 
        html.P( 
            "Analyse de l'évolution de la couverture végétale via NDVI.",
            style={'color': 'rgb(33 36 35)'}
        ),
        html.Hr(),
        html.Div(id='sidebar-dynamic-content', children=[
             html.Img(src='assets/supply_chain.png', 
                      style={ 
                          'position': 'relative',
                          'width': '100%', 
                          'padding': '10px',
                          #'left': '-83px',
                          #'top': '-20px'
                      })
        ]),
        html.Hr(),
         html.P("Sélectionnez un mode, une forêt et une/des année(s).", style={'font-size': 'small'}),
    ], className='side_bar') 

