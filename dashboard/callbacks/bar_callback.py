from dash import Output, Input, State
import plotly.graph_objs as go
from dash import html

def bar_callbacks(app, data_dict, dropdown_options):
    @app.callback(
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
    # ------------------------------------------------- 1) Top10 Plot
        title = '1. Greenhouse emissions (kg CO2 per kg of product)'
        bar_options = [data_dict['top8_animal'], data_dict['top10_vegetal'], data_dict['top10']]
        bar_colors = ['#ebb36a', '#6dbf9c']
        df = bar_options[top10_select]

        if top10_select == 2:
            bar_fig = dict(
                type='bar',
                x=df.Total_emissions,
                y=df["Food product"],
                orientation='h',
                marker_color=['#ebb36a' if x=='Animal' else '#6dbf9c' for x in df.Origin]
            )
        else:
            bar_fig = dict(
                type='bar',
                x=df.Total_emissions,
                y=df["Food product"],
                orientation='h',
                marker_color=bar_colors[top10_select]
            )

    # ------------------------------------------------- 2) Dropdown Bar
        if top10_select == 0:
            options_return = dropdown_options['animal']
            product_chosen = "2. Choose an animal product:" 
            comment = [
                "Look at the beef production emissions! Each kilogram of beef produces almost 60 kg of CO2.", 
                html.Br(), 
                html.Br()
            ]
        elif top10_select == 1:
            options_return = dropdown_options['vegetal']
            product_chosen = "2. Choose a vegetal product:" 
            comment = [
                "Did you know that dark chocolate and coffee are the vegetal-based products that emit more gases?", 
                html.Br(), 
                html.Br()
            ]
        else:
            options_return = dropdown_options['total']
            product_chosen = "2. Choose an animal or vegetal product:" 
            comment = "Check the difference between animal and vegetal-based products! Beef (top1 animal-based emitter) produces around 3 times more emissions than dark chocolate (top1 plant-based emitter)."

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