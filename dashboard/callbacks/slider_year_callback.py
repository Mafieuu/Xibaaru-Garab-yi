from dash import Input, Output

def update_slider(product, data_dict):
    """
    Logique du callback
    """
    year = data_dict['productions'][data_dict['productions']['Item'] == product]['Year'].max()
    return year, year

def slide_year_callback(app, data_dict):
    """
    Quand l'utilisateur choisit un produit dans drop_map,
    le slider est automatiquement réglé sur l'année la plus récente (année max) où ce produit est disponible
"""
    
    @app.callback(
        [
            Output('slider_map', 'max'),
            Output('slider_map', 'value'),
        ],
        [
            Input('drop_map', 'value')
        ]
    )
    def wrapper(product):
        return update_slider(product, data_dict) 