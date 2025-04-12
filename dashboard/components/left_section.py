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

def create_emissions_display():

    return html.Div([
        html.Label('Emissions measured as kg of CO2 per kg of product', style={'font-size': 'medium'}),
        html.Br(),
        html.Br(),
        html.Div([
            html.Div([
                html.H4('Land use', style={'font-weight':'normal'}),
                html.H3(id='land_use')
            ], className='box_emissions'),

            html.Div([
                html.H4('Animal Feed', style={'font-weight':'normal'}),
                html.H3(id='animal_feed')
            ], className='box_emissions'),
        
            html.Div([
                html.H4('Farm', style={'font-weight':'normal'}),
                html.H3(id='farm')
            ], className='box_emissions'),

            html.Div([
                html.H4('Processing', style={'font-weight':'normal'}),
                html.H3(id='processing')
            ], className='box_emissions'),
        
            html.Div([
                html.H4('Transport', style={'font-weight':'normal'}),
                html.H3(id='transport')
            ], className='box_emissions'),

            html.Div([
                html.H4('Packaging', style={'font-weight':'normal'}),
                html.H3(id='packging')
            ], className='box_emissions'),
        
            html.Div([
                html.H4('Retail', style={'font-weight':'normal'}),
                html.H3(id='retail')
            ], className='box_emissions'),
        ], style={'display': 'flex'}),
    ], className='box', style={'heigth':'10%'})

def create_left_img(app):
    img_url = app.get_asset_url('Food.png')
    print("URL de l'image :", img_url)  # Vérification
    return html.Div([
        html.Img(src=img_url, style={'width': '100%', 'position': 'relative', 'opacity': '80%'})
    ])