from dash import dcc, html
import dash_bootstrap_components as dbc

def create_analysis_selector():
    """Crée le sélecteur de mode d'analyse (style RadioItems original)."""
    return dbc.RadioItems(
        id='analysis-mode-selector',
        className='radio', 
        options=[
            {'label': 'Instantané Annuel', 'value': 'snapshot'},
            {'label': 'Comparaison Annuelle', 'value': 'comparison'},
        ],
        value='snapshot', 
        inline=True 
    )

def create_forest_selector(forest_options):
    """Crée le sélecteur de forêt."""
    default_forest = forest_options[0] if forest_options else None
    return html.Div([
        html.Label("Forêt:", style={'margin-right': '10px'}), 
        dcc.Dropdown(
            id='forest-selector',
            options=[{'label': f, 'value': f} for f in forest_options],
            value=default_forest,
            clearable=False,
            style={'width': '250px', 'display': 'inline-block', 'vertical-align': 'middle'}, 
            disabled=not forest_options
        )
    ])

def create_year_selectors(year_options):
    """Crée les sélecteurs d'année (conditionnels pour comparaison)."""
    default_year = year_options[0] if year_options else None
    default_year2 = year_options[1] if len(year_options) > 1 else default_year

    return html.Div([
        # Sélecteur Année 1 (toujours visible)
        html.Div([
            html.Label("Année:", style={'margin-right': '10px'}),
            dcc.Dropdown(
                id='year-selector-1',
                options=[{'label': y, 'value': y} for y in year_options],
                value=default_year,
                clearable=False,
                 style={'width': '120px', 'display': 'inline-block', 'vertical-align': 'middle'},
                disabled=not year_options
            )
        ], id='year-selector-1-container', style={'display': 'inline-block', 'margin-right': '20px'}),

        # Sélecteur Année 2 (pour comparaison, initialement caché)
        html.Div([
            html.Label("Comparer avec:", style={'margin-right': '10px'}),
            dcc.Dropdown(
                id='year-selector-2',
                options=[{'label': y, 'value': y} for y in year_options],
                value=default_year2,
                clearable=False,
                 style={'width': '120px', 'display': 'inline-block', 'vertical-align': 'middle'},
                disabled=not year_options or len(year_options) < 2
            )
        ], id='year-selector-2-container', style={'display': 'none'}) # Caché par défaut
    ])

