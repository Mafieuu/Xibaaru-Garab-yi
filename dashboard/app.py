from dash import Dash, html, dcc, page_container
import dash_bootstrap_components as dbc
import dash
from utils.csv_data_loader import load_data
import json


data_dict = load_data()


# juste après le chargement de data_dict
for key, df in data_dict.items():
    if hasattr(df, "to_json"):  # Vérifie si c'est un DataFrame
        data_dict[key] = df.to_json(orient='split')  # ou 'records' selon ton usage



app = Dash(__name__, use_pages=True, suppress_callback_exceptions=True)

app.layout = html.Div([
    # Store pour partager les données entre les pages
    dcc.Store(id='store-data', data=data_dict),
    
    # Navigation entre les pages
    html.Div([
        html.Div([
            dcc.Link(
                html.Button(page['name'], 
                            id=f"btn-{page['name'].lower()}", 
                            className=f"nav-btn {'active' if page['path'] == '/' else ''}"),
                href=page["path"]
            ) for page in dash.page_registry.values()
        ], className='nav-buttons')
    ], className='nav-container'),
    
    # Conteneur pour le contenu des pages
    page_container
])

if __name__ == '__main__':
    app.run(debug=True)
