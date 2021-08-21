import pandas as pd
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go

import dash  # (version 1.12.0) pip install dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from styles import *
from dataManager import *
from mainDash import *

button_demand = dbc.Row([
        dbc.Button("Clasificador de Demanda", href="/demanda/clasificador", outline=True, color="secondary", className="mr-1"),
        dbc.Button("Prediccion Demanda", href="/demanda/prediccion", outline=True, color="secondary", className="mr-1"),
    ])

demand_classificator = dbc.Container([
        dbc.Row([
            dbc.Col([
                button_demand,
                html.Hr(),
                html.H3("Clasificador de Demanda", style=TEXT_TITLE),
                html.Hr(),
            ]),
        ]),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='graph_classificator_1', figure={})
            ])
        ]),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='graph_classificator_2', figure={})
            ]),
        ]),
])

demand_predictor = [
        button_demand,
        html.Hr(),
        html.H3("Prediccion de Demanda", style=TEXT_TITLE),
        html.Hr(),
    ]

@app.callback(
    Output('graph_classificator_1', 'figure'),
    [Input('dropdown_category', 'value'),
     Input('calendar', 'start_date'),
     Input('calendar', 'end_date')])

def update_graph(value,start_date,end_date):
    if (value == []):
        sales_prod = DataManager().sales_prod
    else:
        sales_prod = DataManager().sales_prod.query("CATEGORIA==@value")
    mask = (sales_prod['FECHA'] > start_date) & (sales_prod['FECHA'] <= end_date)
    sales_prod = sales_prod.loc[mask]
    fig = px.scatter(sales_prod,
        x="CANTIDAD",
        y="TOTAL",
        color="SUBCATEGORIA",
        hover_data=['REF', 'DESC_LARGA','CATEGORIA'],
        title="\t Sales Subategories | Money vs Units"
        )
    return fig