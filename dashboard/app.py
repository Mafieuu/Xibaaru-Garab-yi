from dash import html,dcc,Dash
from callbacks.bar_callback import bar_callbacks
from callbacks.carte_callback import map_callback
from callbacks.slider_year_callback import slide_year_callback
from components.bar_nav import create_origin_selector
from components.display_footer import create_footer
from components.siderbar import create_sidebar
from components.left_section import create_emissions_sunburst, create_left_img
from components.right_section import create_drop_map, create_map_controls, create_water_sunburst,create_emissions_display
from utils.csv_data_loader import create_dropdown_options, load_data

data_dict = load_data()
dropdown_options = create_dropdown_options(data_dict)

#------------------------------------------------------ APP ------------------------------------------------------ 

app = Dash(__name__)


app.layout = html.Div([

    create_sidebar(),

    html.Div([
        html.Div([
# --------------------------------------------------------- La bar nav
                html.Div([
                    html.Label("Choose the Product's Origin:"), 
                    html.Br(),
                    html.Br(),
                    create_origin_selector()
                ], className='box', style={'margin': '10px', 'padding-top':'15px', 'padding-bottom':'15px'}),
# ---------------------------------------------------------  Le left_img  puis [le drop_map et [emission_display et le map_controler]]
            html.Div([
                html.Div([
                    
                    html.Div([    
                        html.Label(id='title_bar'),           
                        dcc.Graph(id='bar_fig'), 
                        html.Div([              
                            html.P(id='comment')
                        ], className='box_comment'),
                    ], className='box', style={'padding-bottom':'15px'}),
                    create_left_img(app),

                ], style={'width': '40%'}),


                html.Div([

                    html.Div([
                    html.Label(id='choose_product', style= {'margin': '10px'}),
                    create_drop_map(),
                    ], className='box'),

                    html.Div([
                        create_emissions_display(),
                        create_map_controls(), 
                    ]),
                ], style={'width': '60%'}),           
            ], className='row'),
# ---------------------------------------------------------  Les deux sunburst
            html.Div([
                create_emissions_sunburst(data_dict['global_emissions']), 
                create_water_sunburst(data_dict["water"]), 
            ], className='row'),
# ---------------------------------------------------------  Le pied de page           
            create_footer(),
        ], className='main'),
    ]),
])


#------------------------------------------------------ Callbacks ------------------------------------------------------
#---------------------------------------------- Callback de 1. et 2.
bar_callbacks(app, data_dict, dropdown_options)
#---------------------------------------------- Callback ajustement du slider year de la carte
slide_year_callback(app,data_dict)
# --------------------------------------------

#---------------------------------------------- Callback de Choroplet Plot (la carte ) 
map_callback(app, data_dict)

if __name__ == '__main__':
    app.run(debug=True)
