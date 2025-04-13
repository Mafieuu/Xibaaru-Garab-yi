from dash import dcc, html

def create_selectors(forest_options, year_options):
    """Crée les sélecteurs pour la forêt et l'année."""
    # Vérifier si les listes sont vides et fournir des valeurs par défaut/désactivées
    default_forest = forest_options[0] if forest_options else None
    default_year = year_options[0] if year_options else None # Prend l'année la plus récente par défaut

    return html.Div([
        html.Label("Choisir la Forêt Classée:"),
        dcc.Dropdown(
            id='forest-selector',
            options=[{'label': f, 'value': f} for f in forest_options],
            value=default_forest,
            clearable=False,
            disabled=not forest_options # Désactiver si aucune forêt n'est trouvée
        ),
        html.Br(),
        html.Label("Choisir l'Année:"),
        dcc.Dropdown(
            id='year-selector',
            options=[{'label': y, 'value': y} for y in year_options],
            value=default_year,
            clearable=False,
            disabled=not year_options # Désactiver si aucune année n'est trouvée
        ),
    ], className='box', style={'margin': '10px', 'padding': '15px'}) # Style repris

