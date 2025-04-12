from dash import html
def create_footer():
    return html.Div([
                html.Div([
                    html.P(['GroupV', html.Br(),'Ana Carrelha (20200631), Inês Melo (20200624), Inês Roque (20200644), Ricardo Nunes(20200611)'], style={'font-size':'12px'}),
                ], style={'width':'60%'}), 
                html.Div([
                    html.P(['Sources ', html.Br(), html.A('Our World in Data', href='https://ourworldindata.org/', target='_blank'), ', ', html.A('Food and Agriculture Organization of the United Nations', href='http://www.fao.org/faostat/en/#data', target='_blank')], style={'font-size':'12px'})
                ], style={'width':'37%'}),
            ], className = 'footer', style={'display':'flex'})