import pandas as pd
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go

import dash  # (version 1.12.0) pip install dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from styles import *

button_indicators = dbc.Row([
        dbc.Button("General", href="/indicadores/general", outline=True, color="secondary", className="mr-1"),
        dbc.Button("Caracteristicas", href="/indicadores/caracteristicas", outline=True, color="secondary", className="mr-1"),
    ])  

indicators_general = dbc.Container([
        dbc.Row([
            dbc.Col([
                button_indicators,
                html.Hr(),
                html.H3("Indicadores", style=TEXT_TITLE),
                html.Hr(),
            ]),
        ]),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='graph_general_1', figure={})
            ]),
            dbc.Col([
                dcc.Graph(id='graph_general_2', figure={})
            ])
        ]),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='graph_general_3', figure={})
            ]),
            dbc.Col([
                dcc.Graph(id='graph_general_4', figure={})
            ])
        ]),
])


indicators_features = dbc.Container([
         dbc.Row([
            dbc.Col([
                button_indicators,
                html.Hr(),
                html.H3("Caracteristicas", style=TEXT_TITLE),
                html.Hr(),
            ]),
        ]),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='graph_features_1', figure={})
            ]),
            dbc.Col([
                dcc.Graph(id='graph_features_2', figure={})
            ])
        ])
    ])