import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from components.siderbar import create_sidebar
from components.left_section import create_emissions_sunburst, create_left_img
from components.right_section import create_drop_map, create_map_controls, create_water_sunburst, create_emissions_display
from components.display_footer import create_footer
from components.bar_nav import create_origin_selector

# Enregistrement de la page
dash.register_page(
    __name__,
    path='/vegetal',
    name='Vegetal',
    title='Food Footprint - Vegetal Products'
)

# Définition de la mise en page
layout = html.Div([
    create_sidebar(),
    html.Div([
        html.Div([
            # Sélection d'origine cachée (pour maintenir la cohérence avec les callbacks)
            html.Div([
                create_origin_selector(),
            ], style={'display': 'none'}),  # Masqué car la navigation est maintenant gérée par le système de pages
            
            # Contenu principal
            html.Div([
                html.Div([
                    html.Div([
                        html.Label(id='title_bar'),
                        dcc.Graph(id='bar_fig'),
                        html.Div([
                            html.P(id='comment')
                        ], className='box_comment'),
                    ], className='box', style={'padding-bottom':'15px'}),
                    
                    # Image spécifique aux produits végétaux
                    html.Div([
                        html.Img(src=dash.get_asset_url('vegetal_products.png'), 
                               style={'width': '100%', 'position':'relative', 'opacity':'80%'}),
                    ]),
                ], style={'width': '40%'}),
                
                html.Div([
                    html.Div([
                        html.Label(id='choose_product', style={'margin': '10px'}),
                        create_drop_map(),
                    ], className='box'),
                    
                    html.Div([
                        create_emissions_display(),
                        create_map_controls(),
                    ]),
                ], style={'width': '60%'}),
            ], className='row'),
            
            # Sunburst charts spécifiques aux produits végétaux - Utilisation du Store pour récupérer les données
            html.Div([
                # Nous allons utiliser un callback pour filtrer les données par origine
                dcc.Store(id='vegetal-emissions-data'),
                dcc.Store(id='vegetal-water-data'),
                html.Div(id='emissions-sunburst-container', className='box', style={'width': '40%'}),
                html.Div(id='water-sunburst-container', className='box', style={'width': '60%'})
            ], className='row'),
            
            # Footer
            create_footer(),
        ], className='main'),
    ]),
])

# Importation des callbacks
from callbacks.vegetal_page_callbacks.bar_callback import register_bar_callbacks
from callbacks.vegetal_page_callbacks.slider_year_callback import register_slider_callbacks
from callbacks.vegetal_page_callbacks.carte_callback import register_map_callbacks
from dash.dependencies import Input, Output
from dash import callback

# Enregistrement des callbacks pour cette page
register_bar_callbacks()
register_slider_callbacks()
register_map_callbacks()

# Nouveaux callbacks pour filtrer les données par origine
@callback(
    Output('vegetal-emissions-data', 'data'),
    Input('store-data', 'data')
)
def filter_emissions_data(data_dict):
    # Cette fonction sera implémentée pour filtrer les données de emissions par origine 'Vegetal'
    # Vous devrez adapter cette logique en fonction de votre structure de données
    return data_dict  # Filtrez ici selon votre structure

@callback(
    Output('vegetal-water-data', 'data'),
    Input('store-data', 'data')
)
def filter_water_data(data_dict):
    # Cette fonction sera implémentée pour filtrer les données de water par origine 'Vegetal'
    # Vous devrez adapter cette logique en fonction de votre structure de données
    return data_dict  # Filtrez ici selon votre structure

@callback(
    Output('emissions-sunburst-container', 'children'),
    Input('vegetal-emissions-data', 'data')
)
def update_emissions_sunburst(filtered_data):
    # Utilisez les données filtrées pour créer le sunburst
    return create_emissions_sunburst(filtered_data)

@callback(
    Output('water-sunburst-container', 'children'),
    Input('vegetal-water-data', 'data')
)
def update_water_sunburst(filtered_data):
    # Utilisez les données filtrées pour créer le sunburst
    return create_water_sunburst(filtered_data)