import pandas as pd
import plotly.graph_objects as go

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from mainDash import *
from managers.dataManager import *

## ---------------------------------------------------------------------- ##
## ------------------------------- LAYOUT ------------------------------- ##
## ---------------------------------------------------------------------- ##

features = [
    dbc.Col([
            html.P('Mapas de calor de la relación existente entre la categorias o subcategorias y las diferentes características de los muebles'),
            html.Hr(),
            dbc.Row([
                dbc.Col([
                        html.H6('Unidades vendidas'),
                        dcc.Graph(id='heatmap_amount', figure={})
                    ],className='graph-chunk'
                ),
                dbc.Col([
                        html.H6('Ventas ($)'),
                        dcc.Graph(id='heatmap_money', figure={})
                    ],
                    className='graph-chunk'
                )
            ])
        ],
        className = 'features-content content-data'
    ),
]

## ---------------------------------------------------------------------- ##
## ----------------------- FEATURES CALLBACKS --------------------------- ##
## ---------------------------------------------------------------------- ##

@app.callback(
    Output('heatmap_amount', 'figure'),
    Output('heatmap_money', 'figure'),
    [
        Input('filter', 'value'),
        Input('feature', 'value'),
        Input('calendar2', 'start_date'),
        Input('calendar2', 'end_date')
    ]
)
def update(filter, feature, start_date, end_date):
    data = DataManager().sales_prod

    x = 'SUBCATEGORIA_POS'
    y = 'CATEGORIA'

    if(len(filter) > 0):
        x = filter
    if(len(feature) > 0):
        y = feature

    if(len(x)<len(y)):
        x, y = y, x
    
    x_values = data[x]
    y_values = data[y]
    
    cross_tab = pd.crosstab(x_values, y_values).transpose()
    cross_tab[cross_tab == 0] = np.nan
    group_by = data.groupby([x, y])[['TOTAL']].sum().unstack().transpose()
    
    x_names = cross_tab.columns
    y_names = cross_tab.index

    map_amount = update_map_amount(x_names, y_names, cross_tab)
    map_money = update_map_money(x_names, y_names, group_by)
    
    return map_amount, map_money

def update_map_amount(x_names, y_names, cross_tab):
    fig =  go.Figure(
        data = go.Heatmap(
            z = cross_tab,
            x = x_names,
            y = y_names,
            hoverongaps = False,
        ),
    )
    fig.update_xaxes(
        tickangle = 270,
    )
    fig.update_layout(
        width = 450,
        height = max(300,len(y_names) * 40),
        font_size = 10,
        margin=dict(t=20, l=10, r=10, b=10, pad=0),
        paper_bgcolor = '#c8c8c8'
    )
    return fig

def update_map_money(x_names, y_names, z):
    fig = go.Figure(
        data = go.Heatmap(
            z = z,
            x = x_names,
            y = y_names,
            hoverongaps = False,
        ),
    )
    fig.update_xaxes(
        tickangle = 270,
    )
    fig.update_layout(
        width = 450,
        height = max(300,len(y_names) * 40),
        font_size = 10,
        margin=dict(t=20, l=10, r=10, b=10, pad=0),
        paper_bgcolor = '#c8c8c8'
    )

    return fig