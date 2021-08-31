import pandas as pd
import plotly
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go
plotly.io.templates.default = 'plotly'

import dash  # (version 1.12.0) pip install dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from mainDash import *

from views.indicators import *
from views.demand import *
from views.inventory import *

from dataManager import *

from layout.menus import top_menu, sidebar_menu
from layout.controls import *

content = html.Div( className='page-content', id='content', children=[])

app.layout = html.Div(
    [
        dcc.Location(id="url"),
        top_menu,
        sidebar_menu,
        content,
    ],
    className='site-content'
)

@app.callback(
    [ Output("sidebar_container", "children"),
    Output("content", "children")],
    [Input("url", "pathname")]
)
def render_page_content(pathname):
    print('START')
    if pathname == '/' or pathname == '/indicadores' or pathname == '/indicadores/general':
        return indicators_controls, indicators_container
    elif pathname == '/indicadores/caracteristicas':
        return features_controls, indicators_container
    elif pathname == '/demanda' or pathname == '/demanda/clasificador':
        return demand_controls, demand_container
    elif pathname == '/demanda/prediccion':
        return predict_controls, demand_container
    elif pathname == '/inventario':
        return inventory_controls, inventory
    else:
        return [], dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ])


"""
@app.callback(Output("download", "data"), [Input("btn", "n_clicks")],prevent_initial_call=True,)
def generate_csv(n_nlicks):
    #return dcc.send_data_frame(df.to_csv, filename="prediction.csv")
    return dcc.send_data_frame(pd.DataFrame().to_csv, filename="prediction.csv")
"""

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True,use_reloader=True,dev_tools_hot_reload=False)
