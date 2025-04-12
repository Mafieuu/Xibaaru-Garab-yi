import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
from components.siderbar import create_sidebar
from components.left_section import create_emissions_sunburst, create_left_img
from components.right_section import create_drop_map, create_map_controls, create_water_sunburst, create_emissions_display
from components.display_footer import create_footer
from components.bar_nav import create_origin_selector

# Enregistrement de la page
dash.register_page(
    __name__,
    path='/',
    name='Total',
    title='Food Footprint - All Products'
)

layout = html.Div([
    create_sidebar(),
    html.Div([
        html.Div([
            # Sélection d'origine masqué 
            html.Div([
                create_origin_selector(),
            ], style={'display': 'none'}),  # Masqué car la navigation est maintenant gérée par le système de pages
            
            
            html.Div([
                html.Div([
                    html.Div([
                        html.Label(id='title_bar'),
                        dcc.Graph(id='bar_fig'),
                        html.Div([
                            html.P(id='comment')
                        ], className='box_comment'),
                    ], className='box', style={'padding-bottom':'15px'}),
                    
                    # Image spécifique aux produits animaux
                    html.Div([
                        html.Img(src=dash.get_asset_url('animal_products.png'), 
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
            
            # Sunburst charts - Utilisation du Store pour récupérer toutes les données
            html.Div([
                # Nous allons utiliser un callback pour les données complètes
                dcc.Store(id='total-emissions-data'),
                dcc.Store(id='total-water-data'),
                html.Div(id='emissions-sunburst-container', className='box', style={'width': '40%'}),
                html.Div(id='water-sunburst-container', className='box', style={'width': '60%'})
            ], className='row'),
            
            # Footer
            create_footer(),
        ], className='main'),
    ]),
])

# ----------------------------------------------------------------------------------
from callbacks.total_page_callbacks.bar_callback import register_bar_callbacks
from callbacks.total_page_callbacks.slider_year_callback import register_slider_callbacks
from callbacks.total_page_callbacks.carte_callback import register_map_callbacks
from dash.dependencies import Input, Output

# Enregistrement des callbacks pour cette page
register_bar_callbacks()
register_slider_callbacks()
register_map_callbacks()

# Callbacks pour les données totales (sans filtrage par origine)
@callback(
    Output('total-emissions-data', 'data'),
    Input('store-data', 'data')
)
def prepare_emissions_data(data_dict):
    # Pas besoin de filtrer les données pour la page Total
    return data_dict

@callback(
    Output('total-water-data', 'data'),
    Input('store-data', 'data')
)
def prepare_water_data(data_dict):
    # Pas besoin de filtrer les données pour la page Total
    return data_dict

@callback(
    Output('emissions-sunburst-container', 'children'),
    Input('total-emissions-data', 'data')
)
def update_emissions_sunburst(data):
    # Utilisez les données complètes pour créer le sunburst
    return create_emissions_sunburst(data)

@callback(
    Output('water-sunburst-container', 'children'),
    Input('total-water-data', 'data')
)
def update_water_sunburst(data):
    # Utilisez les données complètes pour créer le sunburst
    return create_water_sunburst(data)