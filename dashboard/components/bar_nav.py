import dash_bootstrap_components as dbc
def create_origin_selector():
    """Create radio button for selecting product origin"""
    return dbc.RadioItems(
        id='ani_veg', 
        className='radio',
        options=[
            dict(label='Animal', value=0), 
            dict(label='Vegetal', value=1), 
            dict(label='Total', value=2)
        ],
        value=2, 
        inline=True
    )
# -------------------------------------------------------------------------