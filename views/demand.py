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

demand_classificator = [
    dbc.Col([
        dbc.Row([
                html.H3("Clasificador de Demanda",className='title'),
                html.A(html.I("I"),
                    id="auto-toast-toggle",
                    n_clicks=0,
                    className='btn btn-outline-dark info-btn flexy-row',
                ),
            ],
            className='flexy-row'
        ),
        html.Hr(),

        dbc.Row([
            dbc.Col([
                html.Div([
                    dbc.Toast([
                            html.Div([ 
                                html.H6('Para determinar la previsibilidad de un producto, aplicamos dos coeficientes:'),
                                html.Div('- The Average Demand Interval (ADI): Mide la regularidad de la demanda en el tiempo calculando el intervalo promedio entre dos demandas.'),
                                html.Div('El historial de la demanda muestra muy poca variacion en la cantidad de demanda, pero una gran variacion en el intervalo entre dos demandas. Aunque los metodos de pronostico especificos abordan las demandas intermitentes, el margen de error de pronostico es considerablemente mayor.'),
                                html.H6('- the square of the Coefficient of Variation (CV2): Es la medida de la variacion en cantidades'),
                                html.Hr(),
                                html.H6('- Smooth demand(ADI> = 1,32 y CV2 <0,49)'),
                                html.Div('El historial de la demanda muestra muy poca variacion en la cantidad de demanda, pero una gran variacion en el intervalo entre dos demandas. Aunque los metodos de pronostico especificos abordan las demandas intermitentes, el margen de error de pronostico es considerablemente mayor.'),
                                html.Br(),
                                html.H6('- Intermittent demand (ADI <1,32 y CV2 <0,49)'),
                                html.Div('La demanda es muy regular en tiempo y cantidad. Por lo tanto, es facil de pronosticar y no tendra problemas para alcanzar un nivel de error de pronostico bajo.'),
                                html.Br(),
                                html.H6('- Erratic demand (ADI> = 1,32 y CV2> = 0,49)'),
                                html.Div('La demanda se caracteriza por una gran variacion en cantidad y en el tiempo. En realidad, es imposible producir un pronostico confiable, independientemente de las herramientas de pronostico que utilice. Este tipo particular de patron de demanda es imprevisible.'),
                                html.Br(),
                                html.H6('- Lumpy demand (ADI <1,32 y CV2 <0,49)'),
                                html.Div('La demanda es muy regular en tiempo y cantidad. Por lo tanto, es facil de pronosticar y no tendra problemas para alcanzar un nivel de error de pronostico bajo.'),
                            ], className="mb-0",style={'color': 'black', 'fontSize': 14}),],
                                    id="auto-toast",
                                    header="Con base en estas 2 dimensiones, la literatura clasifica los perfiles de demanda en 4 categorias diferentes:",
                                    icon="dark",
                                    style={"maxWidth": "80%"},
                                    is_open=False,
                                    dismissable=True,
                                ),
                ])
            ]),
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(id='graph_classificator_1', figure={}),xs=12,sm=12,md=12,lg=12,xl=12)
        ]),
        dbc.Row([
            dbc.Col(html.H6('Por favor seleccionar producto para mirar detalle de clasificacion:\n'),xs=12,sm=12,md=12,lg=12,xl=12),
        ]),
        dbc.Row([
            html.Br(),
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
            dbc.Col(dcc.Graph(id='graph_classificator_2', figure={},style={"marginLeft": "0"}),xs=12,sm=12,md=6,lg=6,xl=6),
            dbc.Col(dcc.Graph(id='graph_classificator_3', figure={},style={"marginLeft": "0"}),xs=12,sm=12,md=6,lg=6,xl=6),
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(id='graph_classificator_4', figure={},style={"marginLeft": "0"}),xs=12,sm=12,md=6,lg=6,xl=6),
            dbc.Col(dcc.Graph(id='graph_classificator_5', figure={},style={"marginLeft": "0"}),xs=12,sm=12,md=6,lg=6,xl=6),
        ]),
        dbc.Row([
            dbc.Col(html.Hr()),
        ]),
        dbc.Row([
            html.H5('Productos propuestos a descontinuar:'),
        ]),
        dbc.Row([
            html.Br(),
        ]),
        dbc.Row([
            dbc.Button("Descargar csv",id="download_discontinued",outline=True, color="dark",n_clicks=0,),
            dcc.Download(id='download')
        ]),
        dbc.Row([
            html.Br(),
        ]),
        dbc.Row([
            dbc.Col(html.Div(id='datatable1'),xs=6,sm=6,md=5,lg=5,xl=5)
        ]),
    ])
]

demand_predictor = [
    dbc.Col([
        dbc.Row([
                html.H3("Prediccion de Demanda", className='title'),
            ],
            className = 'flexy-row'
        ),
        html.Hr(),

        dbc.Row([
            dbc.Col(dcc.Graph(id='graph_prediction', figure={}),xs=12,sm=12,md=12,lg=12,xl=12),
        ]),
        dbc.Row([
            dbc.Col(html.Hr()),
        ]),
        dbc.Row([
            html.H5('Pronostico:'),
        ]),
        dbc.Row([
            html.Br(),
        ]),
        dbc.Row([
            dbc.Button("Descargar csv",id="download_predictor",outline=True, color="dark",n_clicks=0,),
            dcc.Download(id='download_predictor')
        ]),
        dbc.Row([
            html.Br(),
        ]),
        dbc.Row([
            dbc.Col(html.Div(id='datatable2'),xs=12,sm=12,md=12,lg=12,xl=12)
        ]),
    ]),
]

demd_content = html.Div(className='content-data',id='demand-container',children=demand_classificator)

demand_container = [
    demd_content
]

@app.callback(
    [Output("demand-container", "children")],
    [Input("url", "pathname")]
)
def render_indicators_content(pathname):
    if pathname == '/demanda' or pathname == '/demanda/clasificador':
        return demand_classificator
    elif pathname == '/demanda/prediccion':
        return demand_predictor
    else:
        return [html.Div()]


## DemandClassificator
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
    demand2, discontinued, demand_classificator, classifier = DataManager().demand_data(start_date,end_date,True)
    smooth = demand_classificator.query("CLASSIFIER == 'Smooth'")
    intermittent = demand_classificator.query("CLASSIFIER == 'Intermittent'")
    lumpy = demand_classificator.query("CLASSIFIER == 'Lumpy'")
    erratic = demand_classificator.query("CLASSIFIER == 'Erratic'")
    if len(value1)>0:
        demand2=demand2.query('CATEGORIA == @value1')
        discontinued=discontinued.query('CATEGORIA == @value1')
        smooth=smooth.query('CATEGORIA == @value1')
        intermittent=intermittent.query('CATEGORIA == @value1')
        erratic=erratic.query('CATEGORIA == @value1')
        lumpy=lumpy.query('CATEGORIA == @value1')
    if len(value2)>0:
        demand2=demand2.query('SUBCATEGORIA_POS== @value2')
        discontinued=discontinued.query('SUBCATEGORIA_POS == @value2')
        smooth=smooth.query('SUBCATEGORIA_POS == @value2')
        intermittent=intermittent.query('SUBCATEGORIA_POS == @value2')
        erratic=erratic.query('SUBCATEGORIA_POS == @value2')
        lumpy=lumpy.query('SUBCATEGORIA_POS == @value2')
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

    options1=[{'label':opt, 'value':opt} for opt in intermittent.sort_values('DEMAND_BUCKETS',ascending=False)['PROD_REF'].unique()]
    options2=[{'label':opt, 'value':opt} for opt in lumpy.sort_values('DEMAND_BUCKETS',ascending=False)['PROD_REF'].unique()]
    options3=[{'label':opt, 'value':opt} for opt in smooth.sort_values('DEMAND_BUCKETS',ascending=False)['PROD_REF'].unique()]
    options4=[{'label':opt, 'value':opt} for opt in erratic.sort_values('DEMAND_BUCKETS',ascending=False)['PROD_REF'].unique()]

    return fig, dash_table.DataTable(id='datatable1',data= discontinued.to_dict('records'),
                                    columns=[{'id': x, 'name': x} for x in discontinued.columns],
                                    sort_action='native',
                                    page_size=20,
                                    style_table={'height': '300px', 'overflowY': 'auto'},
                                    style_as_list_view=True,
                                    style_header={'backgroundColor': 'rgb(30, 30, 30)',
                                                'color':'white',
                                                'fontWeight': 'bold',
                                                'font_size':13,
                                                'textAlign': 'center'},
                                    style_cell={
                                        'backgroundColor': 'white',
                                        'color': 'black',
                                        'border': '1px solid grey',
                                        'font_size':11},
                                    style_cell_conditional=[{'textAlign': 'left'}],
                                    style_data={ 'border': '1px solid grey', },
                                    ), [],[],[],[], options1, options2, options3, options4

## Intermittent
@app.callback(
    Output('graph_classificator_2', 'figure'),
    [Input('dropdown_demand_1', 'value')],
    prevent_initial_call=True,)

def update_drown(value):
    intermittent= DataManager().demand_classifier.query("CLASSIFIER=='Intermittent'").sort_values('DEMAND_BUCKETS',ascending=False)

    if (len(value)>0):
        intermittent = intermittent[intermittent['PROD_REF'].isin(value)]

    fig = px.bar(intermittent, y='YY_MM',x='CANTIDAD',
       hover_data=['PROD_REF','CATEGORIA','SUBCATEGORIA_POS','DESCRIPCION'], 
       labels={'YY_MM':'FECHA'},
       title="INTERMITTENT")

    return fig

## Lumpy
@app.callback(
    Output('graph_classificator_3', 'figure'),
    [Input('dropdown_demand_2', 'value')],
    prevent_initial_call=True,)

def update_drown(value):
    lumpy= DataManager().demand_classifier.query("CLASSIFIER=='Lumpy'").sort_values('DEMAND_BUCKETS',ascending=False)

    if (len(value)>0):
        lumpy = lumpy[lumpy['PROD_REF'].isin(value)]

    fig = px.bar(lumpy, y='YY_MM',x='CANTIDAD',
       hover_data=['PROD_REF','CATEGORIA','SUBCATEGORIA_POS','DESCRIPCION'], 
       labels={'YY_MM':'FECHA'},
       title="LUMPY")

    return fig

## Smooth
@app.callback(
    Output('graph_classificator_4', 'figure'),
    [Input('dropdown_demand_3', 'value')],
    prevent_initial_call=True,)

def update_drown(value):
    smooth= DataManager().demand_classifier.query("CLASSIFIER=='Smooth'").sort_values('DEMAND_BUCKETS',ascending=False)

    if (len(value)>0):
        smooth = smooth[smooth['PROD_REF'].isin(value)]

    fig = px.bar(smooth, y='YY_MM',x='CANTIDAD',
       hover_data=['PROD_REF','CATEGORIA','SUBCATEGORIA_POS','DESCRIPCION'], 
       labels={'YY_MM':'FECHA'},
       title="SMOOTH")

    return fig

## Erratic
@app.callback(
    Output('graph_classificator_5', 'figure'),
    [Input('dropdown_demand_4', 'value')],
    prevent_initial_call=True,)

def update_drown(value):
    erratic= DataManager().demand_classifier.query("CLASSIFIER=='Erratic'").sort_values('DEMAND_BUCKETS',ascending=False)

    if (len(value)>0):
        erratic = erratic[erratic['PROD_REF'].isin(value)]

    fig = px.bar(erratic, y='YY_MM',x='CANTIDAD',
       hover_data=['PROD_REF','CATEGORIA','SUBCATEGORIA_POS','DESCRIPCION'], 
       labels={'YY_MM':'FECHA'},
       title="ERRATIC")

    return fig

## Info
@app.callback(
    Output("auto-toast", "is_open"), [Input("auto-toast-toggle", "n_clicks")],prevent_initial_call=True,)
def open_toast(n):
    if n:
        return True
    return False
    
## FileDownload_Discontinued
@app.callback(Output("download", "data"),
            [Input("download_discontinued", "n_clicks")],
            prevent_initial_call=True,)

def generate_csv(n_nlicks):
    return dcc.send_data_frame(DataManager().discontinued.to_csv, filename="descontinuados.csv")


## Callback used to graph demand prediction accuracy graph
@app.callback(
    Output('graph_prediction', 'figure'),
    Output('datatable2', 'children'),
    [Input('dropdown_category', 'value'),
     Input('dropdown_subcategory', 'value'),
     Input('dropdown_ref', 'value'),],
    prevent_initial_call=True
)
        
def graph_model(categoria,subcategoria,ref):
    df = DataManager().all_incorporated()
    indexes, column_predicted = ModelManager().get_data()
    index, date_index, date_before, date_after = indexes
    ##recuperar datos
    max_index_known=df.tail(1).index[0]
    max_date_known=df.tail(1)['DATE']
    ##futuro
    data_future=DataManager().data_forecasting_2021()
    data_future['CANTIDAD'] = np.nan
    df=pd.concat([df,data_future],axis=0)
    a = 'Pronostico General'
    df['PREDICTED'] = column_predicted
    res_train = df[:index]
    res_test = df[index:max_index_known+1]

    df1 = df[:max_index_known+1]
    df2 = df[max_index_known+1:]
    df2['PREDICTED'] = df2['PREDICTED'].round()
    table_predictor = df2.copy()

    if (len(categoria)>0):
        a = 'Pronostico por Categoria'
        df1 = df1.query('CATEGORIA == @categoria')
        df2 = df2.query('CATEGORIA == @categoria')
        res_train = res_train.query('CATEGORIA == @categoria')
        res_test = res_test.query('CATEGORIA == @categoria')
    if  (len(subcategoria)>0):
        a = 'Pronostico por Subcategoria'
        df1 = df1.query('SUBCATEGORIA_POS== @subcategoria')
        df2 = df2.query('SUBCATEGORIA_POS== @subcategoria')
        res_train = res_train.query('SUBCATEGORIA_POS == @subcategoria')
        res_test = res_test.query('SUBCATEGORIA_POS == @subcategoria')
    if (len(ref)>0):
        a = 'Pronostico por Referencia'
        df1 = df1.query('REF == @ref')
        df2 = df2.query('REF == @ref')
        res_train = res_train.query('REF == @ref')
        res_test = res_test.query('REF == @ref')
   
    df1 = df1.groupby(['DATE']).sum().reset_index()
    df2 = df2.groupby(['DATE']).sum().reset_index()

    fig = go.Figure()
    fig.add_scatter(x=df1['DATE'], y=df1['PREDICTED'], mode='lines+markers', name='Valores predichos')
    fig.add_scatter(x=df1['DATE'], y=df1['CANTIDAD'], mode='lines+markers', name='Valores reales')
    fig.add_scatter(x=df2['DATE'], y=df2['PREDICTED'], mode='lines+markers', name='Valores futuros', 
                    line_width=2, line_dash="dash", line_color="green")

    fig.add_vline(x=date_index, line_width=3, line_dash="dot", line_color="green", y0=0, y1=1.25)

    # Add shape regions
    fig.add_vrect(
        x0=date_index, x1=df1['DATE'].sort_values(ascending=False).unique()[0],
        fillcolor='rgb(184, 247, 212)', opacity=0.5, layer="below", line_width=0,
    ),


    fig.add_annotation(x='-'.join([date_after,'5']), y=1.18, yref="paper",
                text="Test",
                font=dict(family="Courier New, monospace",size=16,color="black"),
                showarrow=True,
                arrowhead=1,
                ax=35,
                ay=0,
                xanchor="center",
                yanchor="middle",)
    fig.add_annotation(x='-'.join([date_before,'25']), y=1.18, yref="paper",
                text="Train",
                font=dict(family="Courier New, monospace",size=16,color="black"),
                showarrow=True,
                arrowhead=1,
                ax=-40,
                ay=0,
                xanchor="center",
                yanchor="middle",)

    fig.add_annotation(x='-'.join([date_after,'31']), y=1.15, yref="paper",
                text="RMSE:<br>{:.2f}".format(mse(res_test.CANTIDAD,res_test.PREDICTED,squared=False)),
                font=dict(family="Courier New, monospace",size=16,color="black"),
                showarrow=False,
                ax=35,
                ay=0,
                )
    fig.add_annotation(x='-'.join([date_before,'1']), y=1.15, yref="paper",
                text="RMSE:<br>{:.2f}".format(mse(res_train.CANTIDAD,res_train.PREDICTED,squared=False)),
                font=dict(family="Courier New, monospace",size=16,color="black"),
                showarrow=False,
                arrowhead=1,
                ax=-40,
                ay=0,
                xanchor="center",)
    fig.update_layout(
        title = a,
        yaxis_title = "Número de ventas",
        font=dict(family="Courier New, monospace",size=18,color="RebeccaPurple")
        )         

    table_predictor = table_predictor.groupby(['REF','DATE','CATEGORIA','SUBCATEGORIA_POS',
                        'COLOR_POS','MATERIAL_POS','ACABADO','ORIGEN','AREA','ALTO','PUESTOS']).sum().reset_index()
    table_predictor['PREDICTED_ROUND'] = table_predictor['PREDICTED'].round()
    table_predictor =table_predictor[['REF','DATE','PREDICTED','PREDICTED_ROUND',
                        'CATEGORIA','SUBCATEGORIA_POS','COLOR_POS','MATERIAL_POS',
                        'ACABADO','ORIGEN','AREA','ALTO','PUESTOS']].sort_values(by=['DATE','PREDICTED_ROUND'], ascending=[True,False])
        
    exportTable = dash_table.DataTable(id='datatable2',data=table_predictor.to_dict('records'),
                                    columns=[{'id': x, 'name': x} for x in table_predictor.columns],
                                    sort_action='native',
                                    page_size=20,
                                    style_table={'height': '300px', 'overflowY': 'auto'},
                                    style_as_list_view=True,
                                    style_header={'backgroundColor': 'rgb(30, 30, 30)',
                                                'color':'white',
                                                'fontWeight': 'bold',
                                                'font_size':13,
                                                'textAlign': 'center'},
                                    style_cell={
                                        'backgroundColor': 'white',
                                        'color': 'black',
                                        'border': '1px solid grey',
                                        'font_size':11},
                                    style_cell_conditional=[{'textAlign': 'left'}],
                                    style_data={ 'border': '1px solid grey', },
                                    )               

    return fig, exportTable

## FileDownload_Predictor
@app.callback(Output("download_predictor", "data"),
            [Input("download_predictor", "n_clicks")],
            prevent_initial_call=True,)

def generate_csv(n_nlicks):
    return dcc.send_data_frame(DataManager().discontinued.to_csv, filename="pronostico.csv")
