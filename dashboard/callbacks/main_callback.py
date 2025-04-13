from dash import Output, Input, State, html, no_update
import dash
import plotly.graph_objects as go
import plotly.express as px
import data_loader as dl 
import utils.constantes as constantes
import numpy as np
import dash_bootstrap_components as dbc # Pour formater le tableau de stats

# Helper function pour créer la légende de la carte manuellement
def create_manual_legend():
    legend_items = []
    for index, details in constantes.NDVI_CLASSES.items():
        legend_items.append(
            html.Div([
                html.Span(style={'background-color': details['color'], 'width': '15px', 'height': '15px', 'display': 'inline-block', 'margin-right': '5px'}),
                html.Span(f"{details['label']} ({details['range'][0]} à {details['range'][1]})")
            ], style={'margin-bottom': '5px'})
        )
    return html.Div(legend_items, style={'padding': '10px', 'border': '1px solid #ccc', 'border-radius': '5px', 'margin-top': '10px'})


def register_main_callback(app):
    @app.callback(
        [Output('ndvi-map', 'figure'),
         Output('map-title', 'children'),
         Output('vegetation-stats-display', 'children'),
         Output('vegetation-distribution-bar', 'figure'),
         Output('stats-comment', 'children'),
         Output('year-selector', 'options'), # Mettre à jour les années si la forêt change
         Output('year-selector', 'value')], # Mettre à jour la valeur année si nécessaire
        [Input('forest-selector', 'value'),
         Input('year-selector', 'value')],
        [State('year-selector', 'options')] # Pour ne pas recharger si l'année est déjà la bonne
    )
    def update_visualizations(selected_forest, selected_year, current_year_options):

        # --- 1. Gestion des changements de sélection ---
        ctx = dash.callback_context
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else 'No trigger'

        # Si la forêt change, mettre à jour la liste des années disponibles pour cette forêt
        new_year_options_list = []
        new_year_value = selected_year # Garder l'année sélectionnée par défaut
        if trigger_id == 'forest-selector':
            available_years = dl.get_available_years(selected_forest)
            new_year_options_list = [{'label': y, 'value': y} for y in available_years]
            # Si l'année actuelle n'est plus dispo, prendre la plus récente
            if available_years and selected_year not in available_years:
                new_year_value = available_years[0] # Prend la plus récente
            elif not available_years:
                 new_year_value = None # Aucune année dispo
                 print(f"Aucune année trouvée pour la forêt {selected_forest}")
            # Si les options n'ont pas changé, ne pas mettre à jour pour éviter boucle infinie
            if new_year_options_list == current_year_options:
                new_year_options_output = no_update
            else:
                new_year_options_output = new_year_options_list

        else: # Si l'année change ou c'est le chargement initial
            new_year_options_output = no_update # Ne pas changer les options si seule l'année change

        # Si aucune forêt ou année n'est sélectionnée (cas initial ou erreur)
        if not selected_forest or not new_year_value:
            print("Callback déclenché sans forêt ou année valide.")
            empty_fig = go.Figure()
            empty_fig.update_layout(
                xaxis = {"visible": False},
                yaxis = {"visible": False},
                annotations = [{
                    "text": "Sélectionnez une forêt et une année",
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {"size": 16}
                }]
            )
            no_data_message = html.P("Aucune donnée à afficher. Sélectionnez une forêt et une année.")
            # Retourner des sorties vides ou des messages d'attente
            return empty_fig, "Carte NDVI", no_data_message, empty_fig, "", new_year_options_output, new_year_value


        # --- 2. Charger et traiter les données ---
        print(f"Chargement des données pour : Forêt={selected_forest}, Année={new_year_value}")
        ndvi_class_map, profile, stats_df = dl.load_and_process_image(selected_forest, new_year_value)

        # Gérer le cas où les données ne sont pas chargées correctement
        if ndvi_class_map is None or stats_df.empty:
            print(f"Erreur lors du chargement/traitement pour {selected_forest} - {new_year_value}")
            error_fig = go.Figure()
            error_fig.update_layout(
                 annotations=[{"text": f"Données indisponibles pour {selected_forest} en {new_year_value}", "showarrow": False}]
            )
            error_message = html.P(f"Impossible de charger ou traiter les données pour {selected_forest} en {new_year_value}.")
            return error_fig, f"Erreur Données - {selected_forest} ({new_year_value})", error_message, error_fig, "", new_year_options_output, new_year_value

        # --- 3. Créer la carte NDVI avec Plotly ---
        # Utiliser imshow pour afficher la matrice classifiée
        # Créer une colormap discrète basée sur nos classes
        num_classes = len(constantes.NDVI_CLASSES)
        colors = [constantes.COLOR_MAP.get(i, '#FFFFFF') for i in range(num_classes + 1)] # +1 pour inclure 0 (si existe)
        color_scale = px.colors.qualitative.Pastel 
        custom_color_scale = []
        bounds = sorted(list(constantes.NDVI_CLASSES.keys()))
        for i in range(len(bounds)):
             norm_val_start = i / len(bounds)
             norm_val_end = (i + 1) / len(bounds)
             color = constantes.NDVI_CLASSES[bounds[i]]['color']
             custom_color_scale.extend([[norm_val_start, color], [norm_val_end, color]])


        fig_map = px.imshow(
            ndvi_class_map,
            color_continuous_scale=custom_color_scale,
            # zmin=min(constantes.NDVI_CLASSES.keys()), # ID min de classe
            # zmax=max(constantes.NDVI_CLASSES.keys()), # ID max de classe
            aspect='equal' # Conserver les proportions des pixels
        )

        # Supprimer la colorbar par défaut (car on peut afficher une légende manuelle)
        fig_map.update_coloraxes(showscale=False)
        fig_map.update_layout(
            margin=dict(l=10, r=10, t=30, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis_visible=False, # Cacher les axes pour une carte nette
            yaxis_visible=False,
        )
        map_title = f"Classification NDVI - {selected_forest} ({new_year_value})"
        # Ajouter une légende manuelle ( car les couleurs sont maintenant dans le bar chart)
        # map_legend = create_manual_legend()

        # ---  Créer le tableau des statistiques ---
        stats_table = dbc.Table.from_dataframe(
            stats_df[['Classe Label', 'Surface (ha)', '% Couverture']],
            striped=True,
            bordered=True,
            hover=True,
            responsive=True, 
            className="table-sm" 
        )
        stats_display = html.Div([stats_table]) 

        # --- le graphique à barres de distribution ---
        # Utiliser les couleurs définies dans les constantes
        bar_colors = [constantes.NDVI_CLASSES[idx]['color'] for idx in stats_df['Classe Index']]

        fig_bar = go.Figure(go.Bar(
            x=stats_df['Classe Label'],
            y=stats_df['Surface (ha)'],
            marker_color=bar_colors, # Appliquer les couleurs par classe
            text=stats_df['% Couverture'].apply(lambda x: f'{x:.1f}%'), # Afficher le % sur les barres
            textposition='auto'
        ))
        fig_bar.update_layout(
            title=f'Répartition par Surface (ha)',
            xaxis_title="Classe NDVI",
            yaxis_title="Surface (ha)",
            height=300, 
            font_color='#363535', 
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=40, b=20),
            margin_pad=10
        )

        try:
            dense_veg_stats = stats_df[stats_df['Classe Label'] == "Végétation Dense"].iloc[0]
            comment = f"La classe 'Végétation Dense' couvre {dense_veg_stats['Surface (ha)']} ha ({dense_veg_stats['% Couverture']:.1f}%) de la zone analysée pour {selected_forest} en {new_year_value}."
        except (IndexError, KeyError):
            comment = f"Statistiques pour {selected_forest} en {new_year_value} affichées."


        return fig_map, map_title, stats_display, fig_bar, comment, new_year_options_output, new_year_value