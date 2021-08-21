from numpy.lib.type_check import asfarray
import pandas as pd
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go

import dash  # (version 1.12.0) pip install dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from datetime import date
from dash.dependencies import Input, Output, State
from styles import *
from dataManager import *
from mainDash import *

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
                html.Div(id='prueba', children=['Colores más vendidos']),
            ]),
        ]),

        dbc.Row([
            dbc.Col([
                dcc.Graph(id='graph_general_1', figure={})
            ])
        ]),
        
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='graph_general_2', figure={})
            ]),
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

@app.callback(
    Output('graph_general_2', 'figure'),
    [Input('dropdown_category', 'value'),
     Input('dropdown_subcategory', 'value'),
     Input('dropdown_tienda', 'value'),
     Input('calendar', 'start_date'),
     Input('calendar', 'end_date')])

def update_graph(value1,value2,value3,start_date,end_date):

    if(value3 == []):
        temp = DataManager().sales_prod
    else:
        temp = DataManager().sales_prod.query("TIENDA==@value3")

    if (value1 == [] and value2 == []):
        sales_prod = temp
    elif (value1 != [] and value2 == []):
        sales_prod = temp.query("CATEGORIA==@value1")
    elif (value1 == [] and value2 != []):
        sales_prod = temp.query("SUBCATEGORIA==@value2")
    else:
        sales_prod = temp.query("CATEGORIA==@value1")
        sales_prod = temp.query("SUBCATEGORIA==@value2")
    mask = (sales_prod['FECHA'] >= start_date) & (sales_prod['FECHA'] <= end_date)
    sales_prod = sales_prod.loc[mask]
    fig = px.scatter(sales_prod,
        x="CANTIDAD",
        y="TOTAL",
        color="SUBCATEGORIA",
        hover_data=['REF', 'DESC_LARGA','CATEGORIA'],
        title="\t Sales Subategories | Money vs Units"
        )
    return fig

@app.callback(
    Output('graph_general_1', 'figure'),
    [Input('dropdown_category', 'value'),
     Input('dropdown_subcategory', 'value'),
     Input('dropdown_tienda', 'value'),
     Input('calendar', 'start_date'),
     Input('calendar', 'end_date')])

def update_graph(value1,value2,value3,start_date,end_date):

    if(value3 == []):
        temp = DataManager().sales_prod
    else:
        temp = DataManager().sales_prod.query("TIENDA==@value3")

    if (value1 == [] and value2 == []):
        sales_prod = temp
    elif (value1 != [] and value2 == []):
        sales_prod = temp.query("CATEGORIA==@value1")
    elif (value1 == [] and value2 != []):
        sales_prod = temp.query("SUBCATEGORIA==@value2")
    else:
        sales_prod = temp.query("CATEGORIA==@value1")
        sales_prod = temp.query("SUBCATEGORIA==@value2")
    mask = (sales_prod['FECHA'] >= start_date) & (sales_prod['FECHA'] <= end_date)
    sales_prod = sales_prod.loc[mask]
    
    df = sales_prod.groupby(['COLOR_POS'])['CANTIDAD'].sum()
    colors = ["#FFFF00","#0000FF","#e4e4a1","#FFFFFF","#A52A2A", "#9999ff","#808080","#FFA500","#000000", 
    "#0f3c14", "#ff0000" ]
    
    fig = go.Figure(data=[go.Bar(
        x= df.index,
        y= df,
        marker_color=colors # marker color can be a single color value or an iterable
        )])
    
    return fig









    