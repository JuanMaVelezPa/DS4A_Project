import pandas as pd
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go

import dash  # (version 1.12.0) pip install dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from styles import *

cards_demand = dbc.Row([
    dbc.Nav([
        dbc.Col(
            dbc.Card(
                [
                    dbc.NavLink("Clasificador", href="/demanda/clasificador", active="exact", style=CARD_TEXT_STYLE)
                ]
            ),
        ),
        dbc.Col(
            dbc.Card(
                [
                    dbc.NavLink("Prediccion Demanda", href="/demanda/prediccion", active="exact", style=CARD_TEXT_STYLE)
                ]
            ),
    )])
])

demand_classificator = [
        cards_demand,
        html.H1("Demanda Clasificador", style={'text-align': 'left'}),
        html.Hr(),
    ]

demand_predictor = [
        cards_demand,
        html.H1("Prediccion demanda", style={'text-align': 'left'}),
        html.Hr(),
    ]