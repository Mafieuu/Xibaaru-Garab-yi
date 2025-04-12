from dash import Output, Input, callback
import plotly.graph_objs as go
from dash import html
from utils.csv_data_loader import create_dropdown_options, load_data

def register_bar_callbacks():
    data_dict = load_data()
    dropdown_options = create_dropdown_options(data_dict)
    
    @callback(
        [
            Output('title_bar', 'children'),
            Output('bar_fig', 'figure'),
            Output('comment', 'children'),
            Output('drop_map', 'options'),
            Output('drop_map', 'value'),
            Output('choose_product', 'children')
        ],
        [
            Input('ani_veg', 'value')
        ],
    )
    def update_bar_chart(top10_select):
        # Force la valeur à 0 pour la page animal
        top10_select = 0
        
        # ------------------------------------------------- 1) Top10 Plot
        title = '1. Greenhouse emissions (kg CO2 per kg of product)'
        bar_options = [data_dict['top8_animal'], data_dict['top10_vegetal'], data_dict['top10']]
        bar_colors = ['#ebb36a', '#6dbf9c']
        df = bar_options[top10_select]
        
        bar_fig = dict(
            type='bar',
            x=df.Total_emissions,
            y=df["Food product"],
            orientation='h',
            marker_color=bar_colors[top10_select]
        )

        # ------------------------------------------------- 2) Dropdown Bar
        options_return = dropdown_options['animal']
        product_chosen = "2. Choose an animal product:"
        comment = [
            "Look at the beef production emissions! Each kilogram of beef produces almost 60 kg of CO2.",
            html.Br(),
            html.Br()
        ]
        
        figure = go.Figure(
            data=bar_fig,
            layout=dict(
                height=300,
                font_color='#363535',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=30, b=20),
                margin_pad=10
            )
        )
        return title, figure, comment, options_return, options_return[0]['value'], product_chosen