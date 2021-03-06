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
            html.H3("Predicción de Demanda"),
            dbc.Row([
                    dbc.Col([
                            dcc.Graph(id='graph_prediction', figure={})
                        ],
                        width = 8
                    ),
                    dbc.Col([
                        html.H6('Detalle de las cantidades predichas para cada referencia por tienda, categoria, subcategoria y fecha'),
                        html.Hr(),
                        dbc.Col([
                                dbc.Button(
                                    'Predicción', id='modal-open', 
                                    color='dark', outline=True, block=True, n_clicks=0
                                ),
                            ],
                            className = 'buttons-panel flexy-col start'
                        ),
                    ])
                ],
                className = 'graph-chunk'
            )
        ],
        className='classificators-content content-data'
    ),

    dbc.Modal([
            dbc.ModalHeader([], id='modal-header'),
            dbc.ModalBody([
                    html.H6('Productos pronosticados:'),
                    html.Hr(),
                    dbc.Row([
                        html.Div(id='prediction-table')
                    ]),
                    dbc.Row([
                        dbc.Button("Descargar csv",id="download_predictor", outline=True, color="dark", block=True, n_clicks=0,),           
                        dcc.Download(id='download_predictor')
                    ]),
                ], 
                id = 'modal-body'
            ),
            dbc.ModalFooter(
                dbc.Button(
                    "Close", id="modal-close-pred", color='dark', outline=True, n_clicks=0
                )
            ),
        ],
        id = "modal-pred",
        size = 'lg',
        is_open = False,
        centered = True,
        scrollable = True,
        contentClassName = 'round'
    ),
]

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
    Output('prediction-table', 'children'),
    Input('dropdown_ref', 'value'),
    State('dropdown_category_pred', 'value'),
    State('dropdown_subcategory_pred', 'value'),
)
def update_on_refs(ref, categoria, subcategoria):
    data_type = 3
    if(data_type == 1):
        data = DataManager().all_data()
        data_fut = DataManager().data_forecasting_2021()
        data = np.concat(data,data_fut,index=0)
    elif(data_type == 2):
        data = DataManager().all_data_lag()
        data_fut = DataManager().data_forecasting_2021_lag()
        np.concat(data,data_fut,index=0)
    elif(data_type == 3):
        data, index = DataManager().all_data_future_lag()
        data_fut = data[-index:]

    indexes, predicted = ModelManager(data_type,2,True,12,3,2).get_data()
    index, date_index, date_before, date_after = indexes

    ##futuro
    data['PREDICTED'] = predicted
    
    past = data[:-index]
    train = past[:int(len(past)*0.75)]
    test = past[int(len(past)*0.75):]
    fut = data[-index:]

    table_predictor = fut.copy()

    if (len(categoria)>0):
        past = past.query('CATEGORIA == @categoria')
        fut = fut.query('CATEGORIA == @categoria')
        train = train.query('CATEGORIA == @categoria')
        test = test.query('CATEGORIA == @categoria')
    if  (len(subcategoria)>0):
        past = past.query('SUBCATEGORIA_POS== @subcategoria')
        fut = fut.query('SUBCATEGORIA_POS== @subcategoria')
        train = train.query('SUBCATEGORIA_POS == @subcategoria')
        test = test.query('SUBCATEGORIA_POS == @subcategoria')
    if (len(ref)>0):
        past = past.query('REF == @ref')
        fut = fut.query('REF == @ref')
        train = train.query('REF == @ref')
        test = test.query('REF == @ref')

    past = past.groupby(['DATE']).sum().reset_index()
    fut = fut.groupby(['DATE']).sum().reset_index()
    past['PREDICTED'] = past['PREDICTED']#.round()
    fut['PREDICTED'] = fut['PREDICTED']#.round()
    res_train = train.groupby(['REF','DATE']).sum().reset_index()
    res_test = test.groupby(['REF','DATE']).sum().reset_index()
    
    fig = go.Figure()
    fig.add_scatter(x=past['DATE'], y=past['PREDICTED'], mode='lines+markers', name='Valores predichos', line_width=2, line_dash="dot")
    fig.add_scatter(x=past['DATE'], y=past['CANTIDAD'], mode='lines+markers', name='Valores reales')
    fig.add_scatter(x=fut['DATE'], y=fut['PREDICTED'], mode='lines+markers', name='Valores futuros', line_width=2, line_dash="dash", line_color="green")
    
    fig.add_vline(
        x = date_index, 
        line_width = 3, 
        line_dash = "dot", 
        line_color = "orange", 
        y0 = 0, 
        y1 = 1
    )
    fig.add_vrect( 
        x0 = date_index, 
        x1 = past['DATE'].sort_values(ascending=False).unique()[0],
        fillcolor = 'orange', 
        opacity = 0.1, 
        layer = "below", 
        line_width = 0
    )

    fig.add_annotation(
        x='-'.join([date_after,'10']), 
        y = 0.95, 
        yref="paper",
        text="Test",
        font=dict(family="Courier New, monospace",size=16,color="black"),
        showarrow=True,
        arrowhead=1,
        ax = 35,
        ay = 0,
        xanchor="center",
        yanchor="middle"
    )
    fig.add_annotation(
        x='-'.join([date_before,'25']), 
        y = 0.95, 
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
        y = 0.93, 
        yref="paper",
        text="RMSE:<br>{:.2f}".format(mse(res_test.PREDICTED,res_test.CANTIDAD,squared=False)),
        font=dict(family="Courier New, monospace",size=16,color="black"),
        showarrow=False,
        ax=35,
        ay=0,
    )
    fig.add_annotation(
        x='-'.join([date_before,'1']), 
        y = 0.93, 
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
        height = 450,
        font_size = 10,
        margin=dict(t=25, l=10, r=10, b=10, pad=0),
        paper_bgcolor = '#c8c8c8',
        legend = dict(
            orientation="h",
            yanchor="bottom",
            y=1.04,
            xanchor="right",
            x=1,
        ),
        yaxis_title = "Número de ventas",
    )
    fig.update_xaxes(tickangle=270)

    table_predictor = table_predictor.groupby(['REF','DATE','CATEGORIA','SUBCATEGORIA_POS','COLOR_POS','MATERIAL_POS','ACABADO','ORIGEN','AREA','ALTO','PUESTOS']).sum().reset_index()
    table_predictor['PREDICTED_ROUND'] = table_predictor['PREDICTED'].round()
    table_predictor = table_predictor[['REF','DATE','PREDICTED','PREDICTED_ROUND','CATEGORIA','SUBCATEGORIA_POS','COLOR_POS','MATERIAL_POS','ACABADO','ORIGEN','AREA','ALTO','PUESTOS']].sort_values(by=['DATE','PREDICTED_ROUND'], ascending=[True,False])
    print(table_predictor['CATEGORIA'].unique())
    exportTable = dash_table.DataTable(
        id = 'prediction-table',
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

@app.callback(
    Output("modal-pred", "is_open"),
    [
        Input('modal-open', "n_clicks"), 
        Input("modal-close-pred", "n_clicks")
    ],
    State("modal-pred", "is_open"),
    prevent_initial_call = True,
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

## FileDownload_Predictor
@app.callback(Output("download_predictor", "data"),
            Input("download_predictor", "n_clicks"),
            prevent_initial_call=True,)

def generate_csv(n_nlicks):
    df = DataManager().all_incorporated_lag()
    column_predicted = ModelManager().get_data()[1]
    max_index_known = df.tail(1).index[0]
    data_future = DataManager().data_forecasting_2021_lag()
    data_future['CANTIDAD'] = np.nan
    df=pd.concat([df,data_future],axis=0)
    df['PREDICTED'] = column_predicted
    df_future = df[max_index_known+1:]

    return dcc.send_data_frame(df_future.to_csv, filename="pronostico.csv")
