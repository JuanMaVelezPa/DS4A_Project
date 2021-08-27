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
            dbc.Col([
                dcc.Graph(id='graph_classificator_1', figure={})
            ])
        ]),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='graph_classificator_2', figure={})
            ]),
        ]),
]

demand_predictor = [
        button_demand,
        html.Hr(),
        html.H3("Prediccion de Demanda", style=TEXT_TITLE),
        html.Hr(),
    ]

@app.callback(
    Output('graph_classificator_1', 'figure'),
    [Input('dropdown_category', 'value'),
     Input('dropdown_subcategory', 'value'),
     Input('calendar', 'start_date'),
     Input('calendar', 'end_date')])

def update_graph(value1,value2,start_date,end_date):
    if (value1 == [] and value2 == []):
        sales_prod = DataManager().sales_prod
    elif (value1 != [] and value2 == []):
        sales_prod = DataManager().sales_prod.query("CATEGORIA==@value1")
    elif (value1 == [] and value2 != []):
        sales_prod = DataManager().sales_prod.query("SUBCATEGORIA==@value2")
    else:
        sales_prod = DataManager().sales_prod.query("CATEGORIA==@value1")
        sales_prod = DataManager().sales_prod.query("SUBCATEGORIA==@value2")

    mask = (sales_prod['FECHA'] > start_date) & (sales_prod['FECHA'] <= end_date)
    sales_prod = sales_prod.loc[mask]


    demand = sales_prod[sales_prod['VIGENCIA']!='DESCONTINUADO'].copy()

    demand['YY_MM'] = demand['FECHA'].dt.strftime('%y-%m')

    dicts = {}
    for i,j in enumerate(demand['YY_MM'].sort_values().unique()):
        dicts[i] = j
    
    demand = demand.groupby(['PROD_REF','YY_MM'])['CANTIDAD'].sum().reset_index()
    demand = demand.pivot(index='PROD_REF',columns='YY_MM').fillna(0)
    demand['N_LAST'] = demand.apply(lambda x: np.where(x)[0][-1] ,axis=1)
    demand['LAST'] = demand['N_LAST'].map(dicts)
    demand['N_FIRST'] = demand.apply(lambda x: np.where(x)[0][0] ,axis=1)
    demand['FIRST'] = demand['N_FIRST'].map(dicts)
    demand['PER_LAST-FIRST'] = demand['N_LAST']-demand['N_FIRST']+1
    demand['PER_SIN_INFO'] = len(demand.columns[0:-5])-demand['N_LAST']-1

    v0 = demand[demand.columns[0:-5]].values
    v1 = np.where(v0 > 0, v0, np.nan)
    demand['DEMAND_BUCKETS'] = np.count_nonzero(v1>0, axis=1)-1
    demand['TOTAL_PER'] = np.count_nonzero(v1, axis=1)-1-demand['N_FIRST']
    demand['ADI'] = demand['TOTAL_PER']/demand['DEMAND_BUCKETS']
    demand['CV2'] = (np.nanstd(v1, axis=1)/np.nanmean(v1, axis=1))**2

    demand2 = demand.set_axis(demand.columns.map(''.join), axis=1, inplace=False).reset_index()
    demand2 = demand2[['PROD_REF','N_LAST','LAST','N_FIRST','FIRST','PER_LAST-FIRST','PER_SIN_INFO','DEMAND_BUCKETS','TOTAL_PER','ADI','CV2']]
    groupby_sales = DataManager().products
    demand2 = demand2.merge(groupby_sales, how='left',left_on='PROD_REF',right_on='REF')

    fig = px.scatter(demand2,
            x="CV2", y="ADI", color="SUBCATEGORIA_POS",
            hover_data=['PROD_REF', 'DESC_LARGA','CATEGORIA','SUBCATEGORIA_POS',])

    # add two horizontal lines
    fig.add_hline(y=1.32, line_dash="dot", line_width=2,  line_color="black")
    fig.add_vline(x=0.49, line_dash="dot", line_width=2,  line_color="black")

    fig.add_annotation(text="INTERMITTENT", x=0.1, y=20, showarrow=False)
    fig.add_annotation(text="LUMPY", x=2, y=20, showarrow=False)
    fig.add_annotation(text="SMOOTH", x=0.1, y=0.5, showarrow=False)
    fig.add_annotation(text="ERRATIC", x=2, y=0.5, showarrow=False)

    return fig