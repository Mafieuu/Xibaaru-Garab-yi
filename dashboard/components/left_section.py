from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.express as px

# -------------------------------------------------------------------------
def create_emissions_sunburst(global_emissions_data):
    """Diagramme en sunburst de la repartition des émmisions de CO2 dans l'alimentation
        param :
    global_emissions_data : pandas.DataFrame 
    """
    fig_gemissions = px.sunburst(
        global_emissions_data, 
        path=['Emissions', 'Group', 'Subgroup'], 
        values='Percentage of food emissions', 
        color='Group', 
        color_discrete_sequence=px.colors.sequential.Peach_r
    ).update_traces(
        hovertemplate='%{label}<br>Global Emissions: %{value}%', 
        textinfo="label + percent entry"
    )
    
    fig_gemissions.update_layout({
        'margin': dict(t=0, l=0, r=0, b=10),
        'paper_bgcolor': '#F9F9F8',
        'font_color': '#363535'
    })
    
    return html.Div([
        html.Label(
            "3. Global greenhouse gas emissions from food production, in percentage", 
            style={'font-size': 'medium'}
        ),
        html.Br(),
        html.Label('Click on it to know more!', style={'font-size':'9px'}),
        html.Br(), 
        html.Br(), 
        dcc.Graph(figure=fig_gemissions)
    ], className='box', style={'width': '40%'})

# -------------------------------------------------------------------------
# def create_emissions_display():
#
# n'avais pas sa place ici,voir right_section.py

#------------------------------------------------------------------------
def create_left_img(app):
    img_url = app.get_asset_url('Food.png')
    print("URL de l'image :", img_url)  # Vérification
    return html.Div([
        html.Img(src=img_url, style={'width': '100%', 'position': 'relative', 'opacity': '80%'})
    ])