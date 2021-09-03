import plotly.express as px 
import plotly.graph_objects as go

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from mainDash import *
from managers.dataManager import *

## ---------------------------------------------------------------------- ##
## ------------------------------- LAYOUT ------------------------------- ##
## ---------------------------------------------------------------------- ##

indicators = [
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
        ],
        className='indicators-content content-data'
    ),
]

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


## ---------------------------------------------------------------------- ##
## ------------------------------ METHODS ------------------------------- ##
## ---------------------------------------------------------------------- ##

## ------------------------- GET FILTERED DATA -------------------------- ##
def get_filtered(data, column, l):
    print('Iniciando filtro')

    if(column == 'store'):
        return data.query('TIENDA == @l')
    elif(column == 'cat'):
        return data.query('CATEGORIA == @l')

## ------------------------- UPDATE SALES GRAPH -------------------------- ##
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

## ------------------------- UPDATE MEAN GRAPH ------------------------- ##
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

## ------------------------- UPDATE MAP GRAPH -------------------------- ##
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
