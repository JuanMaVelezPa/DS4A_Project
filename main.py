import plotly
plotly.io.templates.default = 'plotly'

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from mainDash import *

from layout.menus import top_menu, sidebar_menu
from layout.controls import *

from views.indicators import *
from views.features import *
from views.demand import *

from dataManager import *


## ---------------------------------------------------------------------- ##
## --------------------------- DASH COMPONENTS -------------------------- ##
## ---------------------------------------------------------------------- ##

## ----------------------------- CONTAINER ------------------------------ ##
content = html.Div( id='page-content', children=[])

## ------------------------------- LAYOUT ------------------------------- ##
app.layout = html.Div(
    [
        dcc.Location(id="url"),
        top_menu,
        sidebar_menu,
        content,
    ],
    className='site-content'
)


## ---------------------------------------------------------------------- ##
## -------------------------- SITE CALLBACKS ---------------------------- ##
## ---------------------------------------------------------------------- ##

## ------------------------- INITIAL CALLBACK --------------------------- ##
@app.callback(
    [ Output("sidebar_container", "children"),
    Output("page-content", "children")],
    [Input("url", "pathname")]
)
def render_page_content(pathname):
    print('START')
    if pathname == '/' or pathname == '/indicadores' or pathname == '/indicadores/general':
        return indicators_controls, indicators
    elif pathname == '/indicadores/caracteristicas':
        return features_controls, features
    elif pathname == '/demanda' or pathname == '/demanda/clasificador':
        return demand_controls, demand_container
    elif pathname == '/demanda/prediccion':
        return predict_controls, demand_container
    else:
        return [], dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ])

## --------------------------- SERVER RUN ----------------------------- ##
if __name__ == '__main__':
    app.run_server(debug=True,use_reloader=True,dev_tools_hot_reload=False)
