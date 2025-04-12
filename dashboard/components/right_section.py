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