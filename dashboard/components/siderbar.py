from dash import html

def create_sidebar():
    """Create the sidebar component"""
    return html.Div([
        html.H1(children='HACKATON ENSAE'),
        html.Label(
            'We are interested in investigating the food products that have the biggest '
            'impact on environment. Here you can understand which are the products whose '
            'productions emit more greenhouse gases and associate this with each supply '
            'chain step, their worldwide productions, and the water use.',
            style={'color':'rgb(33 36 35)'}
        ), 
        html.Img(
            src='assets/supply_chain.png', 
            style={
                'position': 'relative', 
                'width': '180%', 
                'left': '-83px', 
                'top': '-20px'
            }
        ),
    ], className='side_bar')