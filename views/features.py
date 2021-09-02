from numpy.lib.type_check import asfarray
import pandas as pd
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from styles import *
from dataManager import *
from mainDash import *
from datetime import date as dt

## ---------------------------------------------------------------------- ##
## ------------------------------- LAYOUT ------------------------------- ##
## ---------------------------------------------------------------------- ##

features = [
    dbc.Col([
            html.P('Mapas de calor de la relación existente entre la categorias o subcategorias y las diferentes características de los muebles'),
            dbc.Row([
                    dbc.Col([
                        dcc.Graph(id='heatmap_amount', figure={})
                    ]),
                    dbc.Col([
                        dcc.Graph(id='heatmap_money', figure={})
                    ])
                ],
                className='graph-chunk'
            )
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
    x_names = x_values.unique()
    y_names = y_values.unique()
    
    cross_tab = pd.crosstab(x_values, y_values).values.tolist()
    group_by = data.groupby([x, y]).TOTAL.sum().unstack(fill_value=0).values.tolist()

    map_amount = update_map_amount(x_names, y_names, cross_tab)
    map_money = update_map_money(x_names, y_names, group_by)
    return map_amount, map_money

def update_map_amount(x_values, y_values, z_values):
    fig =  go.Figure(
        data = go.Heatmap(
            z = z_values,
            x = x_values,
            y = y_values,
            hoverongaps = False
        ),
    )
    fig.update_layout(
        font_size = 10,
        margin=dict(t=20, l=10, r=10, b=10, pad=0),
        paper_bgcolor = '#c8c8c8'
    )
    return fig

def update_map_money(x_values, y_values, z):
    fig = go.Figure(
        data = go.Heatmap(
            z = z,
            x = x_values,
            y = y_values,
            hoverongaps = False
        ),
    )

    return fig