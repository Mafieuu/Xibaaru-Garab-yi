from dash import dcc, html
import dash_bootstrap_components as dbc

from utils import constantes


def create_analysis_selector():
    return dbc.RadioItems(
        id='analysis-mode-selector',
        className='radio',
        options=[
            {'label': html.Span(["📊 ", "Instantané Annuel"], style={'color': '#007bff', 'fontWeight': 'bold'}),
             'value': 'snapshot'},
            {'label': html.Span(["🔄 ", "Comparaison Annuelle"], style={'color': '#28a745', 'fontWeight': 'bold'}),
             'value': 'comparison'}
        ],
        value='snapshot',
        inline=True,
        labelStyle={
            'marginRight': '15px',
            'cursor': 'pointer',
            'padding': '6px 10px',
            'borderRadius': '6px',
            'transition': 'background-color 0.3s ease-in-out'
        },
        labelCheckedStyle={
            'backgroundColor': '#f8f9fa',
            'border': '1px solid #007bff',
            'color': '#007bff',
            'fontWeight': 'bold',
            'padding': '6px 12px',
            'borderRadius': '6px'
        }
    )
def create_forest_selector(forest_options):
    """Crée le sélecteur de forêt."""
    default_forest = forest_options[0] if forest_options else None
    return html.Div([html.Label("Forêt:", style={'margin-right': '10px'}), dcc.Dropdown(id='forest-selector', options=[{'label': f, 'value': f} for f in forest_options], value=default_forest, clearable=False, style={'width': '250px', 'display': 'inline-block', 'vertical-align': 'middle'}, disabled=not forest_options)])

def create_year_selectors(year_options):
    """le sélecteur d'année 2 pour comparaison entre deux dates."""
    default_year2 = year_options[1] if len(year_options) > 1 else (year_options[0] if year_options else None)
    return html.Div([
        html.Div([
            html.Label("Comparer avec Année:", style={'margin-right': '10px'}),
            dcc.Dropdown(id='year-selector-2', options=[{'label': y, 'value': y} for y in year_options], value=default_year2, clearable=False, style={'width': '120px', 'display': 'inline-block', 'vertical-align': 'middle'}, disabled=not year_options or len(year_options) < 2)
        ], id='year-selector-2-container', style={'display': 'none'}) # Caché par défaut
    ])

def create_timeseries_filter():
     """ Crée des checkboxes pour filtrer les classes sur le graphique temporel. """
     # Options basées sur les labels des classes NDVI
     class_options = [{'label': details['label'], 'value': details['label']}
                      for _, details in constantes.NDVI_CLASSES.items() if details['label'] != 'Eau'] # Exclure l'eau par défaut?

     return html.Div([
       html.Label("Selectionnez les  classes à afficher:", style={'margin-top':'10px'}),
       dcc.Checklist(
           id='timeseries-class-filter',
           options=class_options,
           value=[opt['value'] for opt in class_options], # Tout coché par défaut
           inline=True,
           className='checkbox'
       )
   ], id='timeseries-filter-container', style={'display': 'none', 'margin-top':'15px'})
def create_year_slider(year_options):
    if not year_options:
        return html.Div("Pas d'années disponibles")

    min_year = min(year_options)
    max_year = max(year_options)
    default_year = max(year_options) # Commencer par l'année la plus récente

    # Créer les marques pour le slider
    marks = {year: str(year) for year in year_options if year % 2 == 0 or year == min_year or year == max_year} # Afficher tous les 2 ans + extrêmes

    return html.Div([
        html.Label("Année Sélectionnée:", style={'margin-right': '10px'}),
        dcc.Slider(
            id='year-slider',
            min=min_year,
            max=max_year,
            step=1,
            value=default_year,
            marks=marks,
            tooltip={"placement": "bottom", "always_visible": True}
        )
    ], style={'width': '80%', 'display': 'inline-block', 'padding': '10px 20px'})


def create_view_type_selector():
    return html.Div([
        html.Label("Type de Vue:", style={'margin-right': '10px', 'font-weight': 'bold', 'color': '#2c3e50'}),

        dbc.RadioItems(
            id='view-type-selector',
            options=[
                {'label': html.Span(["🌿 ", "NDVI"], style={'color': '#28a745', 'fontWeight': 'bold'}),
                 'value': 'ndvi'},
                {'label': html.Span(["🖼️ ", "RGB"], style={'color': '#007bff', 'fontWeight': 'bold'}),
                 'value': 'rgb'}
            ],
            value='ndvi',  # Valeur par défaut sur NDVI
            inline=True, 
            className='radio',
            labelStyle={
                'marginRight': '15px',
                'cursor': 'pointer',
                'padding': '6px 10px',
                'borderRadius': '6px',
                'transition': 'background-color 0.3s ease-in-out'
            },
            labelCheckedStyle={
                'backgroundColor': '#f8f9fa',
                'border': '1px solid #007bff',
                'color': '#007bff',
                'fontWeight': 'bold',
                'padding': '6px 12px',
                'borderRadius': '6px'
            }
        )
    ])