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


inventory = [
        html.H2("Inventario", style=TEXT_TITLE),
        html.Hr(),
    ]