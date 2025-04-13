from dash import dcc, html
import dash_bootstrap_components as dbc 


def create_map_area():
    """ Zone affichage Raster + Zone Tertiaire + Stats/Chart combinés """

    return dbc.Col([ 
        dbc.Row([
            dbc.Col(html.H4(id='map-title', className="text-center"), width=12)
        ]),
        # --- Affichage Raster (px.imshow) ---
        dbc.Row([
            dbc.Col(
                 dcc.Loading(type="default", children=dcc.Graph(
                     id='raster-display-graph', figure={}, config={'scrollZoom': True}
                 )),
                 width=12
            )
        ], className="mb-3"),

        # --- Zone Tertiaire d'abord 
        dbc.Row([
             dbc.Col(
                 html.Div([
                    html.H5(id='tertiary-area-title', className="text-center"),
                    dcc.Loading(type="default", children=html.Div(id='tertiary-content'))
                 ]),
                 id='tertiary-chart-container',
                 width=12
              )
         ], className="mb-3"), 

        # --- Zone pour Graphique/Stats Combinés 
        dbc.Row([
            dbc.Col(
                 html.Div([
                    html.H5("Distribution & Statistiques Année", className="text-center"),
                     dcc.Loading(type="default", children=html.Div(
                         id='combined-stats-chart-display',
                     ))
                 ]),
                width=12
             )
        ]),

    ]) 