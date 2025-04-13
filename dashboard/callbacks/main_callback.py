import dash
from dash import Output, Input, State, html, dcc, no_update
import plotly.graph_objects as go
import plotly.express as px
import data_loader as dl
import utils.constantes as constantes
import numpy as np
import pandas as pd
import dash_bootstrap_components as dbc

# Helper pour créer un tableau de stats 
def create_stats_table(df, title="Statistiques"):
     if df.empty:
         return html.P("Aucune statistique disponible.")
     return html.Div([
         html.H6(title, style={'text-align':'center'}),
         dbc.Table.from_dataframe(
            df, striped=True, bordered=True, hover=True, responsive=True, className="table-sm"
         )
     ])

# Helper pour créer une figure vide 
def create_empty_figure(message="Aucune donnée"):
     fig = go.Figure()
     fig.update_layout(
         xaxis={"visible": False}, yaxis={"visible": False},
         annotations=[{"text": message, "xref": "paper", "yref": "paper", "showarrow": False, "font": {"size": 16}}]
     )
     return fig

def register_main_callback(app):
    @app.callback(
        [# --- Sorties pour la zone "Graphique Principal" (gauche) ---
         Output('primary-chart-title', 'children'),
         Output('primary-chart', 'figure'),
         Output('primary-comment', 'children'),
         # --- Sorties pour la zone "Graphique Secondaire" (gauche) ---
         Output('secondary-chart-area', 'style'), # Pour cacher/afficher
         Output('secondary-chart-title', 'children'),
         Output('secondary-chart', 'figure'),
         # --- Sorties pour la zone "Carte" (droite) ---
         Output('map-title', 'children'),
         Output('ndvi-map', 'figure'),
         # --- Sorties pour la zone "Stats" (droite) ---
         Output('stats-display', 'children'),
         # --- Sorties pour les sélecteurs d'année (interaction) ---
         Output('year-selector-1', 'options'),
         Output('year-selector-1', 'value'),
         Output('year-selector-2-container', 'style'), # Pour cacher/afficher année 2
         Output('year-selector-2', 'options'),
         Output('year-selector-2', 'value'),
        ],
        [# --- Inputs ---
         Input('analysis-mode-selector', 'value'),
         Input('forest-selector', 'value'),
         Input('year-selector-1', 'value'),
         Input('year-selector-2', 'value'), # Utilisé seulement en mode comparaison
        ],
        [# --- States (pour éviter re-calculs inutiles) ---
         State('year-selector-1', 'options'),
         State('year-selector-2', 'options')
        ]
    )
    def update_dashboard(mode, forest, year1, year2, year1_opts_state, year2_opts_state):

        ctx = dash.callback_context
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else 'initial load'

        # --- la mise à jour des années disponibles si la forêt change ---
        current_year1_opts = year1_opts_state
        current_year2_opts = year2_opts_state
        selected_year1 = year1
        selected_year2 = year2

        if triggered_id == 'forest-selector' and forest:
            available_years = dl.get_available_years(forest)
            new_year_opts = [{'label': y, 'value': y} for y in available_years]

            # Mettre à jour les options et sélectionner la plus récente pour année 1
            current_year1_opts = new_year_opts
            selected_year1 = available_years[0] if available_years else None

            # Mettre à jour les options et sélectionner la 2e plus récente pour année 2 si existe
            current_year2_opts = new_year_opts
            if len(available_years) > 1:
                 selected_year2 = available_years[1]
            elif available_years:
                 selected_year2 = available_years[0]
            else:
                 selected_year2 = None
        elif triggered_id == 'initial load' and not forest :
             # Ne rien faire au chargement initial si aucune forêt n'est sélectionnée
             # Retourner des valeurs vides partout
             placeholder_fig = create_empty_figure("Sélectionnez une forêt")
             no_data_msg = html.P("Veuillez sélectionner une forêt et une année.")
             hidden_style = {'display': 'none'}
             visible_style = {'display': 'block'} 

             return ("Titre Graphique", placeholder_fig, "Commentaire...", # Zone Graphe Primaire
                     hidden_style, "Titre Graphique 2", placeholder_fig, # Zone Graphe Secondaire (caché)
                     "Carte NDVI", placeholder_fig, # Zone Carte
                     no_data_msg, # Zone Stats
                     current_year1_opts, selected_year1, # Selecteurs Annee 1
                     hidden_style, current_year2_opts, selected_year2) # Selecteurs Annee 2 (caché)


        # ---  Logique de visibilité 
        hide_secondary_chart = True
        show_year2_selector = False
        if mode == 'snapshot':
            hide_secondary_chart = False # On affiche le pie chart en mode snapshot
            show_year2_selector = False
        elif mode == 'comparison':
             hide_secondary_chart = True # On cache le pie chart en mode comparaison
             show_year2_selector = True

        year2_selector_style = {'display': 'inline-block', 'margin-left': '20px'} if show_year2_selector else {'display': 'none'}
        secondary_chart_style = {'display': 'none'} if hide_secondary_chart else {'display': 'block', 'margin-top':'15px'}

        # Validation des inputs ---
        if not forest or not selected_year1 or (mode == 'comparison' and not selected_year2):
            placeholder_fig = create_empty_figure("Sélection manquante")
            error_msg = html.P("Veuillez sélectionner une forêt et la/les année(s) requise(s).")
            return ("Erreur", placeholder_fig, "Sélection incomplète.", # Graphe Primaire
                    secondary_chart_style, "", placeholder_fig, # Graphe Secondaire
                    "Erreur", placeholder_fig, # Carte
                    error_msg, # Stats
                    current_year1_opts, selected_year1, year2_selector_style, current_year2_opts, selected_year2)

        if mode == 'comparison' and selected_year1 == selected_year2:
            placeholder_fig = create_empty_figure("Années identiques")
            error_msg = html.P("Veuillez sélectionner deux années différentes pour la comparaison.")
            # On affiche quand même la vue snapshot pour l'année sélectionnée
            mode = 'snapshot' # Forcer le mode snapshot
            year2_selector_style = {'display': 'none'}
            secondary_chart_style = {'display': 'block', 'margin-top':'15px'}
            # Pas d'erreur , mais un avertissement implicite
            print("Avertissement: Années identiques sélectionnées pour comparaison, affichage en mode snapshot.")


        #  Chargement et Traitement des Données 
        print(f"Mode: {mode}, Forêt: {forest}, Année1: {selected_year1}, Année2: {selected_year2}")
        ndvi_map1, profile1, stats_df1 = dl.load_and_process_image(forest, selected_year1)

        if ndvi_map1 is None: # Erreur chargement année 1
             error_fig = create_empty_figure(f"Erreur: {selected_year1}")
             error_msg = html.P(f"Impossible de charger les données pour {forest} en {selected_year1}.")
             return ("Erreur", error_fig, f"Erreur chargement {selected_year1}.",
                     secondary_chart_style, "", error_fig,
                     "Erreur", error_fig, error_msg,
                     current_year1_opts, selected_year1, year2_selector_style, current_year2_opts, selected_year2)

        # ---  Génération des Figures et stats
        if mode == 'snapshot':
            # --- Mode Instantané ---
            primary_chart_title = f"Distribution Surface (ha) - {selected_year1}"
            # Graphique Principal: Bar chart
            bar_colors = [constantes.NDVI_CLASSES.get(idx, {"color": "#cccccc"})['color'] for idx in stats_df1['Classe Index']]
            fig_bar = go.Figure(go.Bar(
                 x=stats_df1['Classe Label'], y=stats_df1['Surface (ha)'], marker_color=bar_colors,
                 text=stats_df1['% Couverture'].apply(lambda x: f'{x:.1f}%'), textposition='auto'
            ))
            fig_bar.update_layout(title=f'Surface par Classe (ha)', yaxis_title="Surface (ha)", margin=dict(t=30, b=10), height=350)
            primary_chart_fig = fig_bar

            try:
                dense_veg_stats = stats_df1[stats_df1['Classe Label'] == "Végétation Dense"].iloc[0]
                comment = f"Végétation Dense: {dense_veg_stats['Surface (ha)']} ha ({dense_veg_stats['% Couverture']:.1f}%) en {selected_year1}."
            except: comment = f"Statistiques pour {selected_year1}."

            # Graphique Secondaire: Pie chart
            secondary_chart_title = f"Distribution Pourcentage (%) - {selected_year1}"
            fig_pie = go.Figure(go.Pie(
                 labels=stats_df1['Classe Label'], values=stats_df1['% Couverture'],
                 marker_colors=bar_colors, hole=0.3 # Donut chart
            ))
            fig_pie.update_layout(title=f'% Couverture par Classe', margin=dict(t=50, b=20, l=20, r=20), height=300)
            secondary_chart_fig = fig_pie

            # Carte
            map_title = f"Classification NDVI - {forest} ({selected_year1})"
            # Utiliser la colormap définie dans les constantes
            colorscale = [[i / (len(constantes.NDVI_CLASSES)), constantes.NDVI_CLASSES[idx]['color']]
                          for i, idx in enumerate(sorted(constantes.NDVI_CLASSES.keys()))]
            colorscale.append([1.0, colorscale[-1][1]]) # Répéter la dernière couleur pour la borne sup

            fig_map = px.imshow(ndvi_map1, color_continuous_scale=colorscale, aspect='equal',
                                zmin=min(constantes.NDVI_CLASSES.keys()), zmax=max(constantes.NDVI_CLASSES.keys()))
            fig_map.update_layout(margin=dict(l=10, r=10, t=30, b=10), xaxis_visible=False, yaxis_visible=False)
            fig_map.update_coloraxes(showscale=False) # Cacher la colorbar par défaut

            # Stats
            stats_display = create_stats_table(stats_df1[['Classe Label', 'Surface (ha)', '% Couverture']], f"Stats {selected_year1}")

        elif mode == 'comparison':
            ndvi_map2, profile2, stats_df2 = dl.load_and_process_image(forest, selected_year2)

            if ndvi_map2 is None: # Erreur chargement année 2
                 error_fig = create_empty_figure(f"Erreur: {selected_year2}")
                 error_msg = html.P(f"Impossible de charger les données pour {forest} en {selected_year2}.")
                 # Afficher quand même les données de l'année 1
                 primary_chart_title = f"Données {selected_year1} (Erreur {selected_year2})"
                 primary_chart_fig = fig_bar # Réutiliser le bar chart de l'année 1 (calculé plus haut)
                 comment = f"Impossible de charger les données pour {selected_year2}."
                 secondary_chart_title = ""
                 secondary_chart_fig = create_empty_figure()
                 map_title = f"Classification NDVI - {forest} ({selected_year1}) (Erreur {selected_year2})"
                 fig_map = fig_map # Réutiliser la carte de l'année 1
                 stats_display = create_stats_table(stats_df1[['Classe Label', 'Surface (ha)', '% Couverture']], f"Stats {selected_year1} (Erreur {selected_year2})")

            else:
                 # Calculer la différence
                 diff_stats_df = dl.calculate_stats_difference(stats_df1, stats_df2, selected_year1, selected_year2)

                 # Graphique Principal: Bar chart des différences de surface
                 primary_chart_title = f"Changement de Surface (ha) entre {selected_year2} et {selected_year1}"
                 diff_colors = ['#2ca02c' if x > 0 else '#d62728' if x < 0 else '#7f7f7f' for x in diff_stats_df['Différence Surface (ha)']] # Vert=Gain, Rouge=Perte
                 fig_diff_bar = go.Figure(go.Bar(
                      x=diff_stats_df['Classe Label'], y=diff_stats_df['Différence Surface (ha)'],
                      marker_color=diff_colors,
                      text=diff_stats_df['Différence Surface (ha)'].apply(lambda x: f'{x:+.1f} ha'), textposition='auto'
                 ))
                 fig_diff_bar.update_layout(title=f'Différence Surface (ha) = {selected_year1} - {selected_year2}', yaxis_title="Différence (ha)", margin=dict(t=30, b=10), height=350)
                 primary_chart_fig = fig_diff_bar

                 # Commentaire sur le changement
                 try:
                     dense_veg_diff = diff_stats_df[diff_stats_df['Classe Label'] == "Végétation Dense"]['Différence Surface (ha)'].iloc[0]
                     dense_veg_perc_diff = diff_stats_df[diff_stats_df['Classe Label'] == "Végétation Dense"]['Différence % Couverture'].iloc[0]
                     comment = f"Changement Vég. Dense ({selected_year1} vs {selected_year2}): {dense_veg_diff:+.1f} ha ({dense_veg_perc_diff:+.1f}%)."
                 except: comment = f"Comparaison entre {selected_year1} et {selected_year2}."

                 # Pas de graphique secondaire en mode comparaison
                 secondary_chart_title = ""
                 secondary_chart_fig = create_empty_figure()

                 # Carte: Afficher l'année la plus récente (année 1)
                 map_title = f"Classification NDVI - {forest} ({selected_year1}) (Comparé à {selected_year2})"
                 colorscale = [[i / (len(constantes.NDVI_CLASSES)), constantes.NDVI_CLASSES[idx]['color']]
                               for i, idx in enumerate(sorted(constantes.NDVI_CLASSES.keys()))]
                 colorscale.append([1.0, colorscale[-1][1]])
                 fig_map = px.imshow(ndvi_map1, color_continuous_scale=colorscale, aspect='equal',
                                     zmin=min(constantes.NDVI_CLASSES.keys()), zmax=max(constantes.NDVI_CLASSES.keys()))
                 fig_map.update_layout(margin=dict(l=10, r=10, t=30, b=10), xaxis_visible=False, yaxis_visible=False)
                 fig_map.update_coloraxes(showscale=False)

                 # Stats: Afficher le tableau des différences
                 stats_display = create_stats_table(diff_stats_df, f"Comparaison {selected_year1} vs {selected_year2}")

        # --- 6. Retourner toutes les sorties ---
        return (primary_chart_title, primary_chart_fig, comment,
                secondary_chart_style, secondary_chart_title, secondary_chart_fig,
                map_title, fig_map,
                stats_display,
                current_year1_opts, selected_year1,
                year2_selector_style, current_year2_opts, selected_year2)