import pandas as pd
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go

import dash  # (version 1.12.0) pip install dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from styles import *

button_demand = dbc.Row([
        dbc.Button("Clasificador de Demanda", href="/demanda/clasificador", outline=True, color="secondary", className="mr-1"),
        dbc.Button("Prediccion Demanda", href="/demanda/prediccion", outline=True, color="secondary", className="mr-1"),
    ])

demand_classificator = [
        button_demand,
        html.Hr(),
        html.H3("Clasificador de Demanda", style=TEXT_TITLE),
        html.Hr(),
    ]

demand_predictor = [
        button_demand,
        html.Hr(),
        html.H3("Prediccion de Demanda", style=TEXT_TITLE),
        html.Hr(),
    ]