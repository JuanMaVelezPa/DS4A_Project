from dash_html_components.P import P
from numpy.lib.type_check import asfarray
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
from datetime import date as dt

indicators_general = [
    dbc.Col([
        
        dbc.Row([
            dbc.Col([
                    html.H4('Historico de ventas'),
                    dcc.Graph(id='historic_sales_money', figure={})
                ],
                className='graph-chunk'
            ),

            dbc.Col([
                    html.H4('Promedio de ventas'),
                    dcc.Graph(id='historic_sales_mean', figure={})
                ],
                className='graph-chunk halved'
            ),
        ]),

        dbc.Col([
                html.H4('Mapa de referencias por cantidad y valor vendidos'),
                dcc.Graph(id='sales_map', figure={}),
            ],
            className='graph-chunk'
        ),
    ]),
]

indicators_features = [
    dbc.Col([
        dbc.Row([
                html.H3("Indicadores por característica", className='title'),
            ],
            className = 'flexy-row'
        ),
        html.Hr(),

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
    ]),
]

ind_content = html.Div(className='content-data',id='indicators-container',children=indicators_general)

indicators_container = [
    ind_content
]

# Initial callback for content display
@app.callback(
    [Output("indicators-container", "children")],
    [Input("url", "pathname")]
)
def render_indicators_content(pathname):
    if pathname == '/' or pathname == '/indicadores' or pathname == '/indicadores/general':
        return indicators_general
    elif pathname == '/indicadores/caracteristicas':
        return indicators_features
    else:
        return [html.Div()]

dateMin = DataManager().sales_prod["FECHA"].min()
dateMax = DataManager().sales_prod["FECHA"].max()

## ---------------------------------------------------------------------- ##
## ------------------------ GENERAL CALLBACKS --------------------------- ##
## ---------------------------------------------------------------------- ##


## --------------------------- CALLBACK STORE --------------------------- ##
@app.callback(
    Output('dropdown_category', 'options'),
    Output('dropdown_category', 'value'),
    Input('dropdown_tienda', 'value'),
    prevent_initial_call=True
)
def update_on_store(store):
    data = get_filtered(DataManager().sales_prod,'store',store)

    cats = data['CATEGORIA'].unique()
    return [{'label': i, 'value': i} for i in cats], ''


## ------------------------- CALLBACK CATEGORIA ------------------------- ##
@app.callback(
    Output('dropdown_subcategory', 'options'),
    Output('dropdown_subcategory', 'value'),
    Input('dropdown_category', 'value'),
    State('dropdown_tienda', 'value')
)
def update_on_cat(cat, state_store):
    data = DataManager().sales_prod

    if(len(state_store) > 0):
        data = get_filtered(data,'store',state_store)
    if(len(cat) > 0):
        data = get_filtered(data,'cat',cat)

    subcats = data['SUBCATEGORIA_POS'].unique()

    return [{'label': i, 'value': i} for i in subcats], ''


## ----------------------- CALLBACK SUBCATEGORIA ----------------------- ##
@app.callback(
    Output('historic_sales_money', 'figure'),
    Output('historic_sales_mean', 'figure'),
    Output('sales_map', 'figure'),
    [
        Input('dropdown_subcategory', 'value'), 
        Input('calendar', 'start_date'),
        Input('calendar', 'end_date')
    ],
    State('dropdown_tienda', 'value'),
    State('dropdown_category', 'value')
)
def update_on_subcat(subcat, start_date, end_date, state_store, state_cat):
    data = DataManager().sales_prod

    if(len(state_store) > 0):
        data = get_filtered(data,'store',state_store)
    if(len(state_cat) > 0):
        data = get_filtered(data,'cat',state_cat)
    if(len(subcat) > 0):
        data = data.query('SUBCATEGORIA_POS == @subcat')

    graph_1 = update_historic_sales_money_graph(data, start_date, end_date)
    graph_2 = update_historic_sales_mean_graph(data, start_date, end_date)
    graph_3 = update_map_graph(data, start_date, end_date)

    return graph_1, graph_2, graph_3


def get_filtered(data, column, l):
    print('Iniciando filtro')

    if(column == 'store'):
        return data.query('TIENDA == @l')
    elif(column == 'cat'):
        return data.query('CATEGORIA == @l')


def update_historic_sales_money_graph(data, start_date, end_date):
    
    mask = (data['FECHA'] >= start_date) & (data['FECHA'] <= end_date)
    data = data.loc[mask].groupby(['ANIO','MES'])['TOTAL'].sum().to_frame().reset_index()
    
    fig = go.Figure()

    fig = px.line(data, x="MES", y="TOTAL", color='ANIO', 
        labels = {'TOTAL':'Total ($)','MES':'Mes','ANIO':'',1:"Ene",2:"Feb",3:"Mar",4:"Abr",5:"May",6:"Jun",7:"Jul",8:"Ago",9:"Sep",10:"Oct",11:"Nov",12:"Dic"},
        height = 250,
        width = 500,
        color_discrete_sequence=px.colors.qualitative.Vivid,
        markers=True
    )
    fig.update_layout(
        font_size = 10,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        margin=dict(t=20, l=10, r=10, b=10, pad=0),
        paper_bgcolor = '#c8c8c8'
    )
    return fig

def update_historic_sales_mean_graph(data,start_date,end_date):
    mask = (data['FECHA'] >= start_date) & (data['FECHA'] <= end_date)
    data = data.loc[mask].groupby(['ANIO','MES'])['TOTAL'].sum().to_frame().reset_index()
    data['ANIO'] = data['ANIO'].astype("category")
    
    fig = px.bar(data, x="MES", y="TOTAL", color='ANIO',barmode='group',
        labels = {'TOTAL':'Total ($)','MES':'Mes','ANIO':''},
        height = 250,
        width = 400,
        color_discrete_sequence=px.colors.qualitative.Vivid
    )
    fig.update_layout(
        font_size = 10,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        margin=dict(t=20, l=10, r=10, b=10, pad=0),
        paper_bgcolor = '#c8c8c8'
    )
    return fig

def update_map_graph(data,start_date,end_date):
    mask = (data['FECHA'] >= start_date) & (data['FECHA'] <= end_date)
    data = data.loc[mask]
        
    fig = px.scatter(data,
        labels = {'TOTAL':'Valor vendido ($)','CANTIDAD':'Cantidad vendida','SUBCATEGORIA':'Subcategoría'},
        x="CANTIDAD",
        y="TOTAL",
        color="SUBCATEGORIA",
        hover_data=['REF', 'DESC_LARGA','CATEGORIA'],
        color_discrete_sequence=px.colors.qualitative.Vivid
    )
    fig.update_layout(
        font_size=12,
        margin=dict(t=20, l=10, r=10, b=10),
        paper_bgcolor = '#c8c8c8'
    )
    return fig

## ---------------------------------------------------------------------- ##
## ----------------------- FEATURES CALLBACKS --------------------------- ##
## ---------------------------------------------------------------------- ##

@app.callback(
    Output('heatmap_amount', 'figure'),
    [Input('main_variable', 'value'),
    Input('second_variable', 'value'),
    Input('calendar2', 'start_date'),
    Input('calendar2', 'end_date')])

def update_features_graph1(value1,value2,start_date,end_date):
    if (len(value1)>0 and len(value2)>0):
        data = DataManager().sales_prod
        x_values = data[value1].unique()
        y_values = data[value2].unique()
        if(len(x_values)<len(y_values)):
            x_values, y_values = y_values, x_values
            z_values = pd.crosstab(data[value1], data[value2]).values.tolist()
        else:
            z_values = pd.crosstab(data[value2], data[value1]).values.tolist()
        fig1 =  go.Figure(data=go.Heatmap(
                z=z_values,
                x=x_values,
                y=y_values,
                hoverongaps = False),layout=go.Layout( title=f"{value1} VS {value2} (Unidades vendidas)"))
    else:
        data = DataManager().sales_prod
        x_values = data["SUBCATEGORIA_POS"].unique()
        y_values = data["CATEGORIA"].unique()
        z_values = pd.crosstab(data["CATEGORIA"], data["SUBCATEGORIA_POS"]).values.tolist()
        fig1 =  go.Figure(data=go.Heatmap(
                z=z_values,
                x=x_values,
                y=y_values,
                hoverongaps = False),layout=go.Layout( title="CATEGORIA VS SUBCATEGORIA_POS (Unidades vendidas)"))
    return fig1

@app.callback(
    Output('heatmap_money', 'figure'),
    [Input('main_variable', 'value'),
    Input('second_variable', 'value'),
    Input('calendar2', 'start_date'),
    Input('calendar2', 'end_date')])

def update_features_graph2(value1,value2,start_date,end_date):
    if (len(value1)>0 and len(value2)>0):
        data = DataManager().sales_prod
        x_values = data[value1].unique()
        y_values = data[value2].unique()
        if(len(x_values)<len(y_values)):
            x_values, y_values = y_values, x_values
            z_values2 = data.groupby([value1, value2]).TOTAL.sum().unstack(fill_value=0).values.tolist()
        else:
            z_values2 = data.groupby([value2, value1]).TOTAL.sum().unstack(fill_value=0).values.tolist()
        fig2 = go.Figure(data=go.Heatmap(
                z=z_values2,
                x=x_values,
                y=y_values,
                hoverongaps = False),layout=go.Layout( title=f"{value1} VS {value2} ($)"))
    else:
        data = DataManager().sales_prod
        x_values = data["SUBCATEGORIA_POS"].unique()
        y_values = data["CATEGORIA"].unique()
        z_values2 = data.groupby(['CATEGORIA', 'SUBCATEGORIA_POS']).TOTAL.sum().unstack(fill_value=0).values.tolist()
        fig2 = go.Figure(data=go.Heatmap(
                z=z_values2,
                x=x_values,
                y=y_values,
                hoverongaps = False),layout=go.Layout( title="CATEGORIA VS SUBCATEGORIA_POS ($)"))

    return fig2
