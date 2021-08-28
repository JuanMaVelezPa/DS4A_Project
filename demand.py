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
import dash_table

button_demand = dbc.Row([
        dbc.Button("Clasificador de Demanda", href="/demanda/clasificador", outline=True, color="secondary", className="mr-1"),
        dbc.Button("Prediccion Demanda", href="/demanda/prediccion", outline=True, color="secondary", className="mr-1"),
    ])

demand_classificator = [
        dbc.Row([
            dbc.Col([
                button_demand,
                html.Hr(),
                html.H3("Clasificador de Demanda", style=TEXT_TITLE),
                html.Hr(),
            ]),
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(id='graph_classificator_1', figure={}),xs=12,sm=12,md=12,lg=12,xl=12)
        ]),
        dbc.Row([
            dbc.Col(html.H6('Por favor seleccionar el producto para mirar su clasificacion:\n'),xs=6,sm=6,md=6,lg=6,xl=6),
        ]),
        dbc.Row([
            dbc.Col(html.H6('INTERMITEENT'),xs=6,sm=6,md=3,lg=3,xl=3),
            dbc.Col(html.H6('LUMPY'),xs=6,sm=6,md=3,lg=3,xl=3),
            dbc.Col(html.H6('SMOOTH'),xs=6,sm=6,md=3,lg=3,xl=3),
            dbc.Col(html.H6('ERRATIC'),xs=6,sm=6,md=3,lg=3,xl=3),
        ]),
        dbc.Row([
            dbc.Col(dcc.Dropdown(id='dropdown_demand_1',
                options=[],value=[],
                placeholder='Please select...',
                multi=True,),xs=6,sm=6,md=3,lg=3,xl=3),
           dbc.Col(dcc.Dropdown(id='dropdown_demand_2',
                options=[],value=[],
                placeholder='Please select...',
                multi=True,),xs=6,sm=6,md=3,lg=3,xl=3),
           dbc.Col(dcc.Dropdown(id='dropdown_demand_3',
                options=[],value=[],
                placeholder='Please select...',
                multi=True,),xs=6,sm=6,md=3,lg=3,xl=3),
           dbc.Col(dcc.Dropdown(id='dropdown_demand_4',
                options=[],value=[],
                placeholder='Please select...',
                multi=True,),xs=6,sm=6,md=3,lg=3,xl=3),
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(id='graph_classificator_2', figure={},style={"margin-left": "0"}),xs=12,sm=12,md=6,lg=6,xl=6),
            dbc.Col(dcc.Graph(id='graph_classificator_3', figure={},style={"margin-left": "0"}),xs=12,sm=12,md=6,lg=6,xl=6),
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(id='graph_classificator_4', figure={},style={"margin-left": "0"}),xs=12,sm=12,md=6,lg=6,xl=6),
            dbc.Col(dcc.Graph(id='graph_classificator_5', figure={},style={"margin-left": "0"}),xs=12,sm=12,md=6,lg=6,xl=6),
        ]),
        dbc.Row([
            html.H5('Productos a descontinuar:'),
        ]),
        dbc.Row([
            dbc.Col(html.Hr()),
        ]),
        dbc.Row([
            dbc.Col(html.Div(id='datatable1'),xs=6,sm=6,md=6,lg=6,xl=6)
        ]),
]

demand_predictor = [
        button_demand,
        html.Hr(),
        html.H3("Prediccion de Demanda", style=TEXT_TITLE),
        html.Hr(),
    ]

#DemandClassificator
@app.callback(
    Output('graph_classificator_1', 'figure'),
    Output('datatable1', 'children'),
    Output('dropdown_demand_1', 'value'),
    Output('dropdown_demand_2', 'value'),
    Output('dropdown_demand_3', 'value'),
    Output('dropdown_demand_4', 'value'),
    Output('dropdown_demand_1', 'options'),
    Output('dropdown_demand_2', 'options'),
    Output('dropdown_demand_3', 'options'),
    Output('dropdown_demand_4', 'options'),
    [Input('dropdown_category', 'value'),
     Input('dropdown_subcategory', 'value'),
     Input('calendar', 'start_date'),
     Input('calendar', 'end_date')])

def update_graph(value1,value2,start_date,end_date):
    demand2, discontinued, smooth, intermittent, erratic, lumpy = DataManager().demand_data(value1,value2,start_date,end_date)

    fig = px.scatter(demand2,
            x="CV2", y="ADI", color="SUBCATEGORIA_POS",
            hover_data=['CATEGORIA','SUBCATEGORIA_POS','PROD_REF', 'DESCRIPCION',],
            title="\t DEMAND CLASIFICATION")

    fig.add_hline(y=1.32, line_dash="dot", line_width=2,  line_color="black")
    fig.add_vline(x=0.49, line_dash="dot", line_width=2,  line_color="black")
    fig.add_annotation(text="INTERMITTENT", x=0.1, y=round(demand2['ADI'].max()+2), showarrow=False)
    fig.add_annotation(text="LUMPY", x=2, y=round(demand2['ADI'].max()+2), showarrow=False)
    fig.add_annotation(text="SMOOTH", x=0.1, y=0.5, showarrow=False)
    fig.add_annotation(text="ERRATIC", x=2, y=0.5, showarrow=False)

    options1=[{'label':opt, 'value':opt} for opt in intermittent['PROD_REF'].unique()]
    options2=[{'label':opt, 'value':opt} for opt in lumpy['PROD_REF'].unique()]
    options3=[{'label':opt, 'value':opt} for opt in smooth['PROD_REF'].unique()]
    options4=[{'label':opt, 'value':opt} for opt in erratic['PROD_REF'].unique()]

    return fig, dash_table.DataTable(id='datatable1',data= discontinued.to_dict('records'),
                                    columns=[{'id': x, 'name': x} for x in discontinued.columns],
                                    style_as_list_view=True,
                                    style_header={'backgroundColor': 'rgb(30, 30, 30)',
                                                'color':'white'},
                                    style_cell={
                                        'backgroundColor': 'white',
                                        'color': 'black'},
                                    style_cell_conditional=[{'textAlign': 'left'}],
                                    ), [],[],[],[], options1, options2, options3, options4

#Intermittent
@app.callback(
    Output('graph_classificator_2', 'figure'),
    [Input('dropdown_demand_1', 'value')],
    prevent_initial_call=True,)

def update_drown(value):
    intermittent= DataManager().intermittent

    if (len(value)>0):
        intermittent = intermittent[intermittent['PROD_REF'].isin(value)]

    fig = px.bar(intermittent, y='YY_MM',x='CANTIDAD',
       hover_data=['PROD_REF','CATEGORIA','SUBCATEGORIA_POS','DESCRIPCION'], 
       labels={'YY_MM':'FECHA'},
       title="INTERMITTENT")

    return fig

#Lumpy
@app.callback(
    Output('graph_classificator_3', 'figure'),
    [Input('dropdown_demand_2', 'value')],
    prevent_initial_call=True,)

def update_drown(value):
    lumpy= DataManager().lumpy

    if (len(value)>0):
        lumpy = lumpy[lumpy['PROD_REF'].isin(value)]

    fig = px.bar(lumpy, y='YY_MM',x='CANTIDAD',
       hover_data=['PROD_REF','CATEGORIA','SUBCATEGORIA_POS','DESCRIPCION'], 
       labels={'YY_MM':'FECHA'},
       title="LUMPY")

    return fig

#Smooth
@app.callback(
    Output('graph_classificator_4', 'figure'),
    [Input('dropdown_demand_3', 'value')],
    prevent_initial_call=True,)

def update_drown(value):
    smooth= DataManager().smooth

    if (len(value)>0):
        smooth = smooth[smooth['PROD_REF'].isin(value)]

    fig = px.bar(smooth, y='YY_MM',x='CANTIDAD',
       hover_data=['PROD_REF','CATEGORIA','SUBCATEGORIA_POS','DESCRIPCION'], 
       labels={'YY_MM':'FECHA'},
       title="SMOOTH")

    return fig

#Erratic
@app.callback(
    Output('graph_classificator_5', 'figure'),
    [Input('dropdown_demand_4', 'value')],
    prevent_initial_call=True,)

def update_drown(value):
    erratic= DataManager().erratic

    if (len(value)>0):
        erratic = erratic[erratic['PROD_REF'].isin(value)]

    fig = px.bar(erratic, y='YY_MM',x='CANTIDAD',
       hover_data=['PROD_REF','CATEGORIA','SUBCATEGORIA_POS','DESCRIPCION'], 
       labels={'YY_MM':'FECHA'},
       title="ERRATIC")

    return fig