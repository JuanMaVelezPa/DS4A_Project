import numpy as np
import pandas as pd
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from sklearn.metrics import mean_squared_error as mse

from mainDash import *
from managers.modelManager import ModelManager
from managers.dataManager import DataManager
import dash_table

predictor = [
        dbc.Col([
            html.H3("Prediccion de Demanda"),
            dbc.Row([
                    dbc.Col(dcc.Graph(id='graph_prediction', figure={}),xs=12,sm=12,md=12,lg=12,xl=12)
                ],
                className = 'graph-chunk'
            ),
        ],
        className = 'predictor-content content-data'
    ),
]

## Callback used to graph demand prediction accuracy graph
@app.callback(
    Output('graph_prediction', 'figure'),
    [Input('dropdown_category_pred', 'value'),
     Input('dropdown_subcategory_pred', 'value'),
     Input('dropdown_ref', 'value'),],
    prevent_initial_call=False
)
        
def graph_model(categoria,subcategoria,ref):
    df = DataManager().all_incorporated_lag()
    indexes, column_predicted = ModelManager().get_data()
    index, date_index, date_before, date_after = indexes
    ##recuperar datos
    max_index_known=df.tail(1).index[0]
    max_date_known=df.tail(1)['DATE']
    ##futuro
    data_future=DataManager().data_forecasting_2021_lag()
    data_future['CANTIDAD'] = np.nan
    df=pd.concat([df,data_future],axis=0)
    df['PREDICTED'] = column_predicted
    res_train = df[:index]
    res_test = df[index:max_index_known+1]
    #res_future=df[max_index_known+1:]

    if (len(categoria)>0):
        df = df.query('CATEGORIA == @categoria')
        #res_train = res_train.query('CATEGORIA == @categoria')
        #res_test = res_test.query('CATEGORIA == @categoria')
    if  (len(subcategoria)>0):
        df = df.query('SUBCATEGORIA_POS== @subcategoria')
        #res_train = res_train.query('SUBCATEGORIA_POS == @subcategoria')
        #res_test = res_test.query('SUBCATEGORIA_POS == @subcategoria')
    if (len(ref)>0):
        df = df.query('REF == @ref')
        #res_train = res_train.query('REF == @ref')
        #res_test = res_test.query('REF == @ref')

    df = df.groupby(['DATE']).sum().reset_index()
    
    fig = go.Figure()
    
    fig.add_scatter(x=df['DATE'], y=df['PREDICTED'], mode='lines+markers', name='Valores predichos')
    fig.add_scatter(x=df['DATE'], y=df['CANTIDAD'], mode='lines+markers', name='Valores reales')
    
    fig.add_vline(x=date_index, line_width=3, line_dash="dot", line_color="green", y0=0, y1=1.25)
    
    fig.add_annotation(
        x='-'.join([date_after,'10']), 
        y=1, 
        yref="paper",
        text="Test",
        font=dict(family="Courier New, monospace",size=16,color="black"),
        showarrow=True,
        arrowhead=1,
        ax=35,
        ay=0,
        xanchor="center",
        yanchor="middle"
    )
    fig.add_annotation(
        x='-'.join([date_before,'25']), 
        y=1, 
        yref="paper",
        text="Train",
        font=dict(family="Courier New, monospace",size=16,color="black"),
        showarrow=True,
        arrowhead=1,
        ax=-40,
        ay=0,
        xanchor="center",
        yanchor="middle"
    )
    fig.add_annotation(
        x='-'.join([date_after,'31']), 
        y=0.99, 
        yref="paper",
        text="RMSE:<br>{:.2f}".format(mse(res_test.PREDICTED,res_test.CANTIDAD,squared=False)),
        font=dict(family="Courier New, monospace",size=16,color="black"),
        showarrow=False,
        ax=35,
        ay=0,
    )
    fig.add_annotation(
        x='-'.join([date_before,'1']), 
        y=0.99, 
        yref="paper",
        text="RMSE:<br>{:.2f}".format(mse(res_train.PREDICTED,res_train.CANTIDAD,squared=False)),
        font=dict(family="Courier New, monospace",size=16,color="black"),
        showarrow=False,
        arrowhead=1,
        ax=-40,
        ay=0,
        xanchor="center"
    )
    fig.update_layout(
        width = 900,
        height = 400,
        font_size = 10,
        margin=dict(t=25, l=10, r=10, b=10, pad=0),
        paper_bgcolor = '#c8c8c8',

        yaxis_title = "Número de ventas",
    )

    fig.update_layout(
    )

    return fig