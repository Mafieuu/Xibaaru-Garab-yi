import dash
from dash import Output, Input, State, html, dcc, no_update
import plotly.graph_objects as go
import plotly.express as px
import data_loader as dl
import utils.constantes as constantes
import numpy as np
import pandas as pd
import dash_bootstrap_components as dbc


def create_stats_table(df, title="Statistiques"):
    if df.empty: return html.P("Aucune statistique disponible.")
    df_display = df.copy();
    for col in df_display.select_dtypes(include=np.number).columns:
        if 'Index' not in col and 'Year' not in col:
            try: df_display[col] = df_display[col].round(2)
            except TypeError: pass
    return html.Div([html.H6(title, style={'text-align':'center', 'margin-bottom':'10px'}), dbc.Table.from_dataframe(df_display, striped=True, bordered=True, hover=True, responsive=True, className="table-sm")])



def create_empty_figure(message="Aucune donnée"):
    fig = go.Figure(); fig.update_layout(xaxis={"visible": False}, yaxis={"visible": False}, annotations=[{"text": message, "xref": "paper", "yref": "paper", "showarrow": False, "font": {"size": 16}}], height=300)
    return fig


def register_main_callback(app):

    @app.callback(
        [# --- Graphes Gauche (Seulement Temporel) ---
         Output('secondary-chart-container', 'style'), Output('secondary-chart-title', 'children'), Output('secondary-chart', 'figure'),
         Output('timeseries-filter-container', 'style'),
         # --- Affichage Raster Droite ---
         Output('map-title', 'children'), # Titre pour le graphique imshow
         Output('raster-display-graph', 'figure'), # NOUVEAU: Figure pour px.imshow
         # --- Stats/Chart Combinés Droite ---
         Output('combined-stats-chart-display', 'children'),
         # --- Zone Tertiaire Droite ---
         Output('tertiary-chart-container', 'style'), Output('tertiary-area-title', 'children'),
         Output('tertiary-content', 'children'),
         # --- Sélecteurs Année ---
         Output('year-slider', 'min'), Output('year-slider', 'max'), Output('year-slider', 'marks'), Output('year-slider', 'value'),
         Output('year-selector-2-container', 'style'),
         Output('year-selector-2', 'options'), Output('year-selector-2', 'value'),
        ],
        [# --- Inputs ---
         Input('analysis-mode-selector', 'value'),
         Input('forest-selector', 'value'),
         Input('view-type-selector', 'value'), # Type de vue (ndvi/rgb)
         Input('year-slider', 'value'),        # Année 1 via slider
         Input('year-selector-2', 'value'),    # Année 2 via dropdown
         Input('timeseries-class-filter', 'value'),
        ],
        [# --- States ---
         State('year-selector-2', 'options'),
         State('year-slider', 'min'), State('year-slider', 'max'), State('year-slider', 'marks')
        ],
        prevent_initial_call=False
    )
    def update_dashboard(mode, forest, view_type, selected_year1_slider, selected_year2_dropdown,
                         selected_classes,
                         year2_opts_state,
                         slider_min_state, slider_max_state, slider_marks_state):

        ctx = dash.callback_context
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else 'No trigger'
        print(f"Main Callback triggered by: {triggered_id}")
        print(f"Inputs: Mode={mode}, Forest={forest}, View={view_type}, Year1={selected_year1_slider}, Year2={selected_year2_dropdown}")

        selected_year1 = selected_year1_slider
        selected_year2 = selected_year2_dropdown

        # --- 1. Gestion Mise à Jour Années/Slider si Forêt Change 
        current_slider_min = slider_min_state; current_slider_max = slider_max_state; current_slider_marks = slider_marks_state
        current_slider_value = selected_year1; current_year2_opts = year2_opts_state; current_year2_value = selected_year2
        if triggered_id == 'forest-selector' and forest:
            available_years = dl.get_available_years(forest) # Lit depuis data/
            if available_years:
                 new_year_opts = [{'label': str(y), 'value': y} for y in available_years]
                 current_year2_opts = new_year_opts
                 current_slider_min = min(available_years); current_slider_max = max(available_years)
                 current_slider_marks = {year: str(year) for year in available_years if year % 2 == 0 or year == current_slider_min or year == current_slider_max}
                 current_slider_value = max(available_years) if selected_year1 not in available_years else selected_year1
                 current_year2_value = available_years[1] if len(available_years) > 1 and selected_year2 not in available_years else selected_year2
                 if len(available_years) > 1 and current_year2_value == current_slider_value: current_year2_value = available_years[0] if available_years[0] != current_slider_value else available_years[1]
                 selected_year1 = current_slider_value; selected_year2 = current_year2_value
            else:
                 current_year2_opts = []; current_slider_min = 0; current_slider_max = 0; current_slider_marks = {}; current_slider_value = 0; selected_year1 = None; selected_year2 = None
        slider_outputs = (current_slider_min, current_slider_max, current_slider_marks, current_slider_value)
        year2_outputs = (no_update, current_year2_opts, current_year2_value)


        # --- 2. Logique Visibilité et Validation Inputs 
        is_snapshot = (mode == 'snapshot'); is_comparison = (mode == 'comparison')
        secondary_style = {'display': 'block'} if is_snapshot else {'display': 'none'}
        tertiary_style = {'display': 'block'}
        year2_selector_style_calc = {'display': 'inline-block'} if is_comparison else {'display': 'none'}
        timeseries_filter_style = {'display': 'block'} if is_snapshot else {'display': 'none'}
        if triggered_id == 'forest-selector': year2_outputs = (year2_selector_style_calc, current_year2_opts, current_year2_value)
        if not forest or not selected_year1 or (is_comparison and not selected_year2):
            
            placeholder_raster_fig = create_empty_figure("Sélection manquante")
            placeholder_combined = html.Div([html.H6("Distribution & Stats", style={'text-align':'center'}), create_empty_figure("Sélection manquante")])
            return (secondary_style, "Évolution", create_empty_figure(), timeseries_filter_style, # 4
                    "Erreur Sélection", placeholder_raster_fig,                               # 2 (Titre Raster, Fig Raster)
                    placeholder_combined,                                                  # 1
                    tertiary_style, "Infos", html.P("Sélection incomplète."),             # 3
                    *slider_outputs,                                                       # 4
                    year2_selector_style_calc, current_year2_opts, current_year2_value)    # 3 -> Total 17

        if is_comparison and selected_year1 == selected_year2:
             # ... (Forcer mode snapshot 
             mode = 'snapshot'; is_snapshot = True; is_comparison = False
             secondary_style = {'display': 'block'}; year2_selector_style_calc = {'display': 'none'}; timeseries_filter_style = {'display': 'block'}


        # --- 3. Chargement TIF SOURCE Année 1 & Préparation Affichage ---
        print(f"Recherche TIF source: Forêt={forest}, Année1={selected_year1} dans data/")
        image_path1 = dl.get_file_path(forest, selected_year1) # Chemin vers TIF dans data/
        raster_fig = create_empty_figure(f"Données non trouvées pour {selected_year1}") # Fig par défaut
        stats_df1 = pd.DataFrame()
        map_title = f"Erreur Chargement {selected_year1}"

        if image_path1:
            print(f"TIF Source trouvé: {image_path1}. Génération vue {view_type.upper()}...")
            if view_type == 'ndvi':
                ndvi_matrix, profile = dl.calcul_ndvi(image_path1)
                if ndvi_matrix is not None:
                    # Créer figure px.imshow pour NDVI
                    raster_fig = px.imshow(ndvi_matrix, color_continuous_scale='RdYlGn', aspect='equal')
                    raster_fig.update_layout(coloraxis_colorbar_title_text='NDVI', margin=dict(l=0, r=0, t=30, b=0))
                    map_title = f"Vue NDVI - {forest} ({selected_year1})"
                    # Calculer stats pour NDVI
                    ndvi_class_map = dl.classify_ndvi(ndvi_matrix)
                    if ndvi_class_map is not None:
                        stats_df1 = dl.calcul_class_stats(ndvi_class_map)
                        if not stats_df1.empty: stats_df1['Year'] = selected_year1
                else: map_title = f"Erreur Calcul NDVI - {selected_year1}"

            elif view_type == 'rgb':
                # Lire les bandes RGB (depuis TIF dans data/)
                rgb_image, profile = dl.read_rgb_bands(image_path1)
                if rgb_image is not None:
                     # Créer figure px.imshow pour RGB
                     raster_fig = px.imshow(rgb_image, aspect='equal')
                     raster_fig.update_layout(margin=dict(l=0, r=0, t=30, b=0))
                     raster_fig.update_coloraxes(showscale=False) # Pas d'échelle de couleur pour RGB
                     map_title = f"Vue RGB - {forest} ({selected_year1})"
                     # Pas de calcul de stats NDVI ici, stats_df1 reste vide
                     print("Affichage RGB: Statistiques NDVI non calculées.")
                else: map_title = f"Erreur Lecture RGB - {selected_year1}"
            else: # Type de vue inconnu
                 map_title = f"Type de vue '{view_type}' non supporté."
                 raster_fig = create_empty_figure(map_title)

        else: print(f"Fichier TIF source non trouvé pour {selected_year1} dans data/")


        # --- 4. Logique par Mode ---
        combined_stats_chart_content = html.Div("Chargement...")
        tertiary_title = "Infos Add."
        tertiary_content = html.P("Chargement...")
        secondary_title = "Évolution Temporelle"; secondary_fig = create_empty_figure()

        if is_snapshot:
            # --- Mode Instantané ---
            # map_title et raster_fig sont déjà définis

            # Graphe Secondaire (Temporel) 
       
            secondary_title = f"Évolution Temporelle Surface (ha) - {forest}"
            all_stats_df = dl.load_all_year_stats(forest) # Lit TIFs sources de data/
            if not all_stats_df.empty:
                 if not selected_classes: secondary_fig = create_empty_figure("Sélectionnez des classes")
                 else:
                     filtered_stats = all_stats_df[all_stats_df['Classe Label'].isin(selected_classes)]
                     if filtered_stats.empty: secondary_fig = create_empty_figure("Aucune donnée temporelle")
                     else:
                          fig_line = px.line(filtered_stats.sort_values('Year'), x='Year', y='Surface (ha)', color='Classe Label', markers=True, color_discrete_map={details['label']: details['color'] for _, details in constantes.NDVI_CLASSES.items()})
                          fig_line.update_layout(margin=dict(t=30, b=10, l=10, r=10), height=350, legend_title_text='Classe')
                          secondary_fig = fig_line
            else: secondary_fig = create_empty_figure("Données temporelles indisponibles")

            # Contenu Combiné Graphique/Stats (utilise stats_df1)

            if not stats_df1.empty: # Seulement si stats NDVI ont été calculées
                 fig_bar = go.Figure(go.Bar(x=stats_df1['Classe Label'], y=stats_df1['Surface (ha)'], marker_color=[constantes.NDVI_CLASSES.get(idx, {"color": "#cccccc"})['color'] for idx in stats_df1['Classe Index']], text=stats_df1['% Couverture'].apply(lambda x: f'{x:.1f}%'), textposition='outside'))
                 fig_bar.update_layout(yaxis_title="Surface (ha)", margin=dict(t=20, b=10, l=10, r=10), height=300)
                 stats_table_component = create_stats_table(stats_df1[['Classe Label', 'Surface (ha)', '% Couverture']], f"Statistiques {selected_year1}")
                 combined_stats_chart_content = html.Div([dcc.Graph(figure=fig_bar), html.Hr(), stats_table_component])
            elif view_type == 'rgb': # Si vue RGB, pas de stats/graph NDVI
                 combined_stats_chart_content = html.P("Statistiques NDVI non disponibles en vue RGB.", className="text-center fst-italic")
            else: # Si erreur chargement ou stats vides
                 combined_stats_chart_content = html.Div([html.H6("Distribution & Stats", style={'text-align':'center'}), create_empty_figure(f"Stats manquantes pour {selected_year1}")])

            # Zone Tertiaire: Légende et Tendance  (utilise all_stats_df)
          
            tertiary_title = "Légende & Tendances Générales"
            legend_items = [html.Li(f"{details['label']}: {details['range'][0]} à {details['range'][1]}", style={'color': details['color'], 'fontWeight': 'bold'}) for _, details in constantes.NDVI_CLASSES.items()]
            trend_content = [];
            if not all_stats_df.empty:
                slope_dense, trend_text_dense = dl.calculate_trend(all_stats_df, 'Végétation Dense'); slope_bare, trend_text_bare = dl.calculate_trend(all_stats_df, 'Végétation Modérée')
                trend_content = [html.Hr(),html.P(f"Tendance Vég. Dense: {trend_text_dense}"), html.P(f"Tendance Végétation Modérée: {trend_text_bare}")]
            tertiary_content = html.Div([html.H6("Légende Classes NDVI"), html.Ul(legend_items, style={'padding-left': '10px'}), *trend_content])


        elif is_comparison:
            # --- Mode Comparaison ---
            # map_title et raster_fig (pour année 1) sont déjà définis
            map_title = f"Comparaison {selected_year1} vs {selected_year2} - {forest} (Vue: {view_type.upper()})"

            # Charger TIF source et calculer stats pour année 2 (depuis data/)
            print(f"Recherche TIF source: Forêt={forest}, Année2={selected_year2} dans data/")
            image_path2 = dl.get_file_path(forest, selected_year2)
            stats_df2 = pd.DataFrame()
            if image_path2:
                 # Calculer stats pour comparaison (seulement si vue NDVI ou si stats nécessaires)
                 # Pour simplifier, on calcule toujours les stats NDVI pour la comparaison, même si la vue est RGB
                 # On accepte ce probleme en attendant de trouver une solution
                 print(f"TIF Source trouvé: {image_path2}. Calcul des stats NDVI pour comparaison...")
                 ndvi_matrix2, _ = dl.calcul_ndvi(image_path2)
                 if ndvi_matrix2 is not None:
                     ndvi_class_map2 = dl.classify_ndvi(ndvi_matrix2)
                     if ndvi_class_map2 is not None:
                         stats_df2 = dl.calcul_class_stats(ndvi_class_map2)
                         if not stats_df2.empty: stats_df2['Year'] = selected_year2
            else: print(f"Fichier TIF source non trouvé pour {selected_year2} dans data/")

            # Gérer erreur chargement/calcul stats année 2
            if stats_df1.empty or stats_df2.empty: # Comparaison impossible si l'une des stats manque
                 error_msg = html.P(f"Impossible de calculer les stats NDVI pour {selected_year1} ou {selected_year2}. Comparaison impossible.\n Pour l'image RGB pas de comparaison annuelle ")
                 secondary_title = ""; secondary_fig = create_empty_figure()
                 # Afficher fallback (graphique stats/barres Année 1 si dispo)
                 if not stats_df1.empty:
                     fig_bar1 = go.Figure(go.Bar(x=stats_df1['Classe Label'], y=stats_df1['Surface (ha)'], marker_color=[constantes.NDVI_CLASSES.get(idx, {"color": "#cccccc"})['color'] for idx in stats_df1['Classe Index']]))
                     fig_bar1.update_layout(yaxis_title="Surface (ha)", margin=dict(t=20, b=10, l=10, r=10), height=300)
                     stats_table1 = create_stats_table(stats_df1[['Classe Label', 'Surface (ha)', '% Couverture']], f"Stats {selected_year1} (Erreur Comparaison)")
                     combined_stats_chart_content = html.Div([dcc.Graph(figure=fig_bar1), html.Hr(), stats_table1])
                 else: combined_stats_chart_content = error_msg # Si même année 1 vide
                 tertiary_title = "Erreur Comparaison"; tertiary_content = error_msg

            else:
                 # --- Comparaison possible ---
                 diff_stats_df = dl.calculate_stats_difference(stats_df1, stats_df2, selected_year1, selected_year2)

                 # Affichage combiné -> Tableau des différences
                 if not diff_stats_df.empty:
                     combined_stats_chart_content = create_stats_table(diff_stats_df, f"Comparaison Stats {selected_year1} vs {selected_year2}")
                 else:
                     combined_stats_chart_content = html.P("Impossible d'afficher les différences statistiques.")

                 # Graphe Secondaire (Caché)
                 secondary_title = ""; secondary_fig = create_empty_figure()

                 # Contenu Tertiaire: Résumé des changements 
                 tertiary_title = f"Changements Nets ({selected_year1} vs {selected_year2})"
                 if not diff_stats_df.empty:
                     items = []
                     diff_stats_df_sorted = diff_stats_df.sort_values('Classe Label')
                     for index, row in diff_stats_df_sorted.iterrows():
                         change_ha = row['Différence Surface (ha)']; label = row['Classe Label']
                         color = "secondary"; icon = ""
                         if change_ha > 0.1: color = "success"; icon = "▲ "
                         elif change_ha < -0.1: color = "danger"; icon = "▼ "
                         items.append(dbc.ListGroupItem(f"{icon}{label}: {change_ha:+.1f} ha", color=color, className="d-flex justify-content-between align-items-center"))
                     tertiary_content = dbc.ListGroup(items, flush=True)
                 else: tertiary_content = html.P("Calcul des différences impossible.")

        # --- 6. Retour des Outputs ---
        year2_outputs_final = (year2_selector_style_calc, current_year2_opts, current_year2_value)

        # Retourner toutes les valeurs dans le bon ordre 17 items
        return (secondary_style, secondary_title, secondary_fig, timeseries_filter_style, # 4
                map_title, raster_fig,                                                 # 2
                combined_stats_chart_content,                                          # 1
                tertiary_style, tertiary_title, tertiary_content,                        # 3
                *slider_outputs,                                                       # 4
                *year2_outputs_final)                                                  # 3 -> Total 17