import pandas as pd
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go

import dash  # (version 1.12.0) pip install dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

# Styles
from styles import *
from indicators import *
from demand import *
from inventory import *
from static import sidebar, cards

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

content = html.Div( id='page-content', children=[], style=CONTENT_STYLE)

app.layout = html.Div([
    dcc.Location(id="url"),
    sidebar, 
    cards,
    content,
])

@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")]
)

def render_page_content(pathname):
    if pathname == '/' or pathname == '/indicadores' or pathname == '/indicadores/general':
        return indicators_general
    elif pathname == '/indicadores/caracteristicas':
        return indicators_features
    elif pathname == '/demanda' or pathname == '/demanda/clasificador':
        return demand_classificator
    elif pathname == '/demanda/prediccion':
        return demand_predictor
    elif pathname == '/inventario':
        return inventory
    else:
        return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )

"""
@app.callback(Output("download", "data"), [Input("btn", "n_clicks")],prevent_initial_call=True,)
def generate_csv(n_nlicks):
    #return dcc.send_data_frame(df.to_csv, filename="prediction.csv")
    return dcc.send_data_frame(pd.DataFrame().to_csv, filename="prediction.csv")
"""

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)