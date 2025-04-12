from dash import Input, Output, callback
from utils.csv_data_loader import load_data

def update_slider(product):
    data_dict = load_data()
    """
    Logique du callback
    """
    year = data_dict['productions'][data_dict['productions']['Item'] == product]['Year'].max()
    return year, year

def register_slider_callbacks():
    """
    Quand l'utilisateur choisit un produit dans drop_map,
    le slider est automatiquement réglé sur l'année la plus récente (année max) où ce produit est disponible
    """
    @callback(
        [
            Output('slider_map', 'max'),
            Output('slider_map', 'value'),
        ],
        [
            Input('drop_map', 'value')
        ]
    )
    def wrapper(product):
        return update_slider(product)