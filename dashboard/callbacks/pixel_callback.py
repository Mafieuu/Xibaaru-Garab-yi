# actuellement abandonee ---------------------------
#
#



from dash import Output, Input, State, html, dcc, no_update, callback # Importer callback explicitement
import plotly.express as px
import data_loader as dl
from callbacks.main_callback import create_empty_figure # Réutiliser helper figure vide
import pandas as pd

def register_pixel_callback(app):

    @callback( # Utiliser @callback au lieu de @app.callback si dans fichier séparé
        Output('pixel-evolution-chart', 'figure'),
        Input('ndvi-map-leaflet', 'click_lat_lng'),
        State('forest-selector', 'value'), # Besoin de savoir quelle forêt regarder
        prevent_initial_call=True
    )
    def update_pixel_evolution(click_data, forest):
        if click_data is None or forest is None:
            return no_update # Ne rien faire si pas de clic ou pas de forêt

        lat = click_data['latlng']['lat']
        lon = click_data['latlng']['lng']
        print(f"Pixel Callback: Clicked at {lat}, {lon} in forest {forest}")

        # Appeler la fonction du data_loader
        pixel_data = dl.get_pixel_evolution(forest, lat, lon)

        if pixel_data:
            # Créer un DataFrame pour Plotly
            df_pixel = pd.DataFrame(pixel_data, columns=['Year', 'Value'])
            df_pixel = df_pixel.dropna() # Enlever les années où la lecture a échoué

            if not df_pixel.empty:
                 # Créer le graphique
                 fig = px.line(df_pixel.sort_values('Year'), x='Year', y='Value',
                              markers=True, title=f"Évolution Pixel ({lat:.4f}, {lon:.4f})")
                 fig.update_layout(margin=dict(t=50, b=10, l=10, r=10), height=200)
                 # Adapter le nom de l'axe Y selon ce que vous lisez (NDVI, Classe ?)
                 fig.update_yaxes(title_text="Valeur Pixel (NDVI ou Classe?)")
                 return fig
            else:
                 return create_empty_figure(f"Aucune donnée de pixel valide trouvée pour ({lat:.4f}, {lon:.4f})")
        else:
            # La fonction get_pixel_evolution a retourné None ou a échoué
            return create_empty_figure(f"Impossible de lire l'évolution du pixel pour ({lat:.4f}, {lon:.4f})")