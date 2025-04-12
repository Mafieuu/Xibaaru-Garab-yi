from dash import html, dcc
import dash_daq as daq
import plotly.express as px

# -------------------------------------------------------------------------
def create_water_sunburst(water_data):
    """
    Diagramme en sunburst de la répartition de l'eau 
    param :
    water_data : pandas.DataFrame 

    """
    fig_water = px.sunburst(
        water_data, 
        path=['Origin', 'Category', 'Product'], 
        values='Water Used', 
        color='Category', 
        color_discrete_sequence=px.colors.sequential.haline_r
    ).update_traces(hovertemplate='%{label}<br>' + 'Water Used: %{value} L')

    fig_water.update_layout({
        'margin': dict(t=0, l=0, r=0, b=10),
        'paper_bgcolor': '#F9F9F8',
        'font_color': '#363535'
    })

    return html.Div([
        html.Label("4. Freshwater withdrawals per kg of product, in Liters", style={'font-size': 'medium'}),
        html.Br(),
        html.Label('Click on it to know more!', style={'font-size':'9px'}),
        html.Br(), 
        html.Br(), 
        dcc.Graph(figure=fig_water)
    ], className='box', style={'width': '63%'})

# -------------------------------------------------------------------------
def create_map_controls():

    """
    Crée les contrôles de la carte, le menu déroulant des continents et le curseur d'années
    """
    return html.Div([ 
        html.Div([
            html.Div([
                html.Br(),
                html.Label(id='title_map', style={'font-size':'medium'}), 
                html.Br(),
                html.Label(
                    'These quantities refer to the raw material used to produce the product selected above', 
                    style={'font-size':'9px'}
                ),
            ], style={'width': '70%'}),
            html.Div([], style={'width': '5%'}),
            html.Div([
                dcc.Dropdown(
                    id='drop_continent',
                    clearable=False, 
                    searchable=False, 
                    options=[
                        {'label': 'World', 'value': 'world'},
                        {'label': 'Europe', 'value': 'europe'},
                        {'label': 'Asia', 'value': 'asia'},
                        {'label': 'Africa', 'value': 'africa'},
                        {'label': 'North america', 'value': 'north america'},
                        {'label': 'South america', 'value': 'south america'}
                    ],
                    value='world', 
                    style={'margin': '4px', 'box-shadow': '0px 0px #ebb36a', 'border-color': '#ebb36a'}
                ), 
                html.Br(),
                html.Br(), 
            ], style={'width': '25%'}),
        ], className='row'),
        
        dcc.Graph(id='map', style={'position':'relative', 'top':'-50px'}), 
        
        html.Div([
            daq.Slider(
                id='slider_map',
                handleLabel={"showCurrentValue": True, "label": "Year"},
                marks={str(i): str(i) for i in [1990, 1995, 2000, 2005, 2010, 2015]},
                min=1990,
                size=450, 
                color='#4B9072'
            )
        ], style={'margin-left': '15%', 'position':'relative', 'top':'-38px'}),
    ], className='box', style={'padding-bottom': '0px'})
# -----------------------------------------------------------------------
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

def create_drop_map():
    """
    Le dropdown 2. , ses options dependent de la valeur de create_origin_selector dans les callbacks
    """
    return dcc.Dropdown(
        id = 'drop_map',
        clearable=False,
        searchable=False, 
        style= {'margin': '4px', 'box-shadow': '0px 0px #ebb36a', 'border-color': '#ebb36a'}        
    )