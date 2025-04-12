from dash import Input, Output, State, callback
import plotly.graph_objects as go
import numpy as np
from utils.csv_data_loader import load_data

def register_map_callbacks():
    data_dict = load_data()
    
    @callback(
        [
            Output('land_use', 'children'),
            Output('animal_feed', 'children'),
            Output('farm', 'children'),
            Output('processing', 'children'),
            Output('transport', 'children'),
            Output('packging', 'children'),
            Output('retail', 'children'),
            Output('title_map', 'children'),
            Output('map', 'figure')
        ],
        [
            Input('drop_map', 'value'),
            Input('slider_map', 'value'),
            Input('drop_continent', 'value')
        ],
        [State("drop_map", "options")]
    )
    def update_map(drop_map_value, year, continent, opt):
        # ################## Emissions datset ##################
        the_label = [x['label'] for x in opt if x['value'] == drop_map_value]
        data_emissions = data_dict['emissions'][data_dict['emissions']["Food product"] == the_label[0]]
        land_use_str = str(np.round(data_emissions["Land use change"].values[0], 2))
        animal_feed_str = str(np.round(data_emissions["Animal Feed"].values[0], 2))
        farm_str = str(np.round(data_emissions["Farm"].values[0], 2))
        processing_str = str(np.round(data_emissions["Processing"].values[0], 2))
        transport_str = str(np.round(data_emissions["Transport"].values[0], 2))
        packging_str = str(np.round(data_emissions["Packging"].values[0], 2))
        retail_str = str(np.round(data_emissions["Retail"].values[0], 2))
        
        # Choroplet Plot (la carte) ##################
        prod1 = data_dict['productions'][
            (data_dict['productions']['Item'] == drop_map_value) &
            (data_dict['productions']['Year'] == year)
        ]
        title = 'Production quantities of {}, by country'.format(prod1['Item'].unique()[0])
        data_slider = []
        data_each_yr = dict(type='choropleth',
                            locations=prod1['Area'],
                            locationmode='country names',
                            autocolorscale=False,
                            z=np.log(prod1['Value'].astype(float)),
                            zmin=0,
                            zmax=np.log(data_dict['productions'][data_dict['productions']['Item'] == drop_map_value]['Value'].max()),
                            colorscale=["#ffe2bd", "#006837"],
                            marker_line_color='rgba(0,0,0,0)',
                            colorbar={'title': 'Tonnes (log)'},  # Tonnes in logscale
                            colorbar_lenmode='fraction',
                            colorbar_len=0.8,
                            colorbar_x=1,
                            colorbar_xanchor='left',
                            colorbar_y=0.5,
                            name='')
        data_slider.append(data_each_yr)
        layout = dict(geo=dict(scope=continent,
                               projection={'type': 'natural earth'},
                               bgcolor='rgba(0,0,0,0)'),
                      margin=dict(l=0,
                                  r=0,
                                  b=0,
                                  t=30,
                                  pad=0),
                      paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)')
        fig_choropleth = go.Figure(data=data_slider, layout=layout)
        fig_choropleth.update_geos(showcoastlines=False, showsubunits=False, showframe=False)
        return land_use_str, \
               animal_feed_str, \
               farm_str, \
               processing_str, \
               transport_str, \
               packging_str, \
               retail_str, \
               title, \
               fig_choropleth