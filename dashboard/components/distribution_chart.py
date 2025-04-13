from dash import dcc, html

def create_distribution_chart():
    """Crée la zone pour le graphique de distribution des classes."""
    return html.Div([
        html.Div([
            html.H4("Distribution des Classes NDVI"),
            dcc.Loading(
                 type="default",
                 children=dcc.Graph(id='vegetation-distribution-bar')
            ),
             html.Div(id='stats-comment') 
        ], className='box', style={'padding': '15px'})
    ], style={'margin-top': '20px'})