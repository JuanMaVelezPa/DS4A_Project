import numpy as np
import pandas as pd
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from sklearn.metrics import mean_squared_error as mse

from mainDash import *
from managers.modelManager import ModelManager
from managers.dataManager import DataManager
import dash_table

predictor = [
    dbc.Col([
        html.H3("Prediccion de Demanda", className='title'),
        dbc.Row([
                dbc.Col(dcc.Graph(id='graph_prediction', figure={}),xs=12,sm=12,md=12,lg=12,xl=12),
            ],
            className = 'graph-chunk'
        ),
        html.Hr(),
        html.H6('Productos pronosticados:'),
        dbc.Row([
            dbc.Col(html.Div(id='datatable2'),xs=12,sm=12,md=12,lg=12,xl=12)
        ]),
        dbc.Row([
            dbc.Button("Descargar csv",id="download_predictor", outline=True, color="dark", block=True, n_clicks=0,),           
            dcc.Download(id='download_predictor')
        ]),
    ],
    className='classificators-content content-data'),
]


dbc.Col([
            html.H6('Productos sugeridos a descontinuar:'),
            dbc.Button('Productos', id={'type': 'modal_button', 'index': 5}, color='dark', outline=True, block=True)
        ],
        className = 'discontinued-panel'
    )


## ------------------------- CALLBACK CATEGORIA ------------------------- ##
@app.callback(
    Output('dropdown_subcategory_pred', 'options'),
    Output('dropdown_subcategory_pred', 'value'),
    Input('dropdown_category_pred', 'value'),
    prevential_initial_call=True,
)
def update_on_cat(cat):
    data = DataManager().sales_prod.query('CATEGORIA == @cat')

    subcats = data['SUBCATEGORIA_POS'].unique()
    return [{'label': i, 'value': i} for i in subcats], ''


## ----------------------- CALLBACK SUBCATEGORIA ----------------------- ##
@app.callback(
    Output('dropdown_ref', 'options'),
    Output('dropdown_ref', 'value'),
    Input('dropdown_subcategory_pred', 'value'),
    State('dropdown_category_pred', 'value')
)
def update_on_subcat(subcat, cat):
    data = DataManager().sales_prod

    if(len(cat) > 0):
        data = data.query('CATEGORIA == @cat')
    if(len(subcat) > 0):
        data = data.query('SUBCATEGORIA_POS == @subcat')

    refs = data['REF'].unique()
    return [{'label': i, 'value': i} for i in refs], ''

## ----------------------- CALLBACK REFERENCIA  ----------------------- ##
@app.callback(
    Output('graph_prediction', 'figure'),
    Output('datatable2', 'children'),
    Input('dropdown_ref', 'value'),
    State('dropdown_category_pred', 'value'),
    State('dropdown_subcategory_pred', 'value'),
)
def update_on_refs(ref, categoria, subcategoria):
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

    df1 = df[:max_index_known+1]
    df2 = df[max_index_known+1:]
    table_predictor = df2.copy()

    if (len(categoria)>0):
        df1 = df1.query('CATEGORIA == @categoria')
        df2 = df2.query('CATEGORIA == @categoria')
        res_train = res_train.query('CATEGORIA == @categoria')
        res_test = res_test.query('CATEGORIA == @categoria')
    if  (len(subcategoria)>0):
        df1 = df1.query('SUBCATEGORIA_POS== @subcategoria')
        df2 = df2.query('SUBCATEGORIA_POS== @subcategoria')
        res_train = res_train.query('SUBCATEGORIA_POS == @subcategoria')
        res_test = res_test.query('SUBCATEGORIA_POS == @subcategoria')
    if (len(ref)>0):
        df1 = df1.query('REF == @ref')
        df2 = df2.query('REF == @ref')
        res_train = res_train.query('REF == @ref')
        res_test = res_test.query('REF == @ref')

    df1 = df1.groupby(['DATE']).sum().reset_index()
    df2 = df2.groupby(['DATE']).sum().reset_index()
    df1['PREDICTED'] = df1['PREDICTED'].round()
    df2['PREDICTED'] = df2['PREDICTED'].round()
    res_train = res_train.groupby(['REF','DATE']).sum().reset_index()
    res_test = res_test.groupby(['REF','DATE']).sum().reset_index()
    
    fig = go.Figure()
    fig.add_scatter(x=df1['DATE'], y=df1['PREDICTED'], mode='lines+markers', name='Valores predichos')
    fig.add_scatter(x=df1['DATE'], y=df1['CANTIDAD'], mode='lines+markers', name='Valores reales')
    fig.add_scatter(x=df2['DATE'], y=df2['PREDICTED'], mode='lines+markers', name='Valores futuros', line_width=2, line_dash="dash", line_color="green")
    
    fig.add_vline(
        x = date_index, 
        line_width = 3, 
        line_dash = "dot", 
        line_color = "orange", 
        y0=0, 
        y1=1.25
    )
    fig.add_vrect( 
        x0 = date_index, 
        x1 = df1['DATE'].sort_values(ascending=False).unique()[0],
        fillcolor = 'orange', 
        opacity = 0.1, 
        layer = "below", 
        line_width = 0
    )

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
    fig.update_xaxes(tickangle=270)

    table_predictor = table_predictor.groupby(['REF','DATE','CATEGORIA','SUBCATEGORIA_POS','COLOR_POS','MATERIAL_POS','ACABADO','ORIGEN','AREA','ALTO','PUESTOS']).sum().reset_index()
    table_predictor['PREDICTED_ROUND'] = table_predictor['PREDICTED'].round()
    table_predictor = table_predictor[['REF','DATE','PREDICTED','PREDICTED_ROUND','CATEGORIA','SUBCATEGORIA_POS','COLOR_POS','MATERIAL_POS','ACABADO','ORIGEN','AREA','ALTO','PUESTOS']].sort_values(by=['DATE','PREDICTED_ROUND'], ascending=[True,False])
        
    exportTable = dash_table.DataTable(
        id = 'datatable2',
        data = table_predictor.to_dict('records'),
        columns = [{'id': x, 'name': x} for x in table_predictor.columns],
        sort_action = 'native',
        page_size = 20,
        style_table = {'height': '300px', 'overflowY': 'auto'},
        style_as_list_view = True,
        style_header = {
            'backgroundColor': 'rgb(30, 30, 30)',
            'color':'white',
            'fontWeight': 'bold',
            'font_size':13,
            'textAlign': 'center'
        },
        style_cell = {
            'backgroundColor': 'white',
            'color': 'black',
            'border': '1px solid grey',
            'font_size':11
        },
        style_cell_conditional = [{'textAlign': 'left'}],
        style_data = {'border':'1px solid grey'},
    )               

    return fig, exportTable

## FileDownload_Predictor
@app.callback(Output("download_predictor", "data"),
            [Input("download_predictor", "n_clicks")],
            prevent_initial_call=True,)

def generate_csv(n_nlicks):
    return dcc.send_data_frame(DataManager().discontinued.to_csv, filename="pronostico.csv")
