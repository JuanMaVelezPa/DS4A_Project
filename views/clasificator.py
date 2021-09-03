import json
import plotly.express as px  # (version 4.7.0)

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import ALL, Input, Output, State

from mainDash import *
from managers.dataManager import DataManager
import dash_table

options = [
    html.H6('Selecciona un tipo de comportamiento para ver el detalle de la clasificacion:\n'),
    html.Hr(),
    dbc.Col([
            dbc.Button(
                'Intermittent', id={'type': 'modal_button', 'index': 1}, 
                color='dark', outline=True, block=True, n_clicks=0
            ),
            dbc.Button(
                'Lumpy', id={'type': 'modal_button', 'index': 2}, 
                color='dark', outline=True, block=True, n_clicks=0
            ),
            dbc.Button(
                'Smooth', id={'type': 'modal_button', 'index': 3}, 
                color='dark', outline=True, block=True, n_clicks=0
            ),
            dbc.Button(
                'Erratic', id={'type': 'modal_button', 'index': 4}, 
                color='dark', outline=True, block=True, n_clicks=0
            )
        ],
        className = 'buttons-panel flexy-col start'
    ),
    html.Hr(),
    dbc.Col([
            html.H6('Productos sugeridos a descontinuar:'),
            dbc.Button('Productos', id={'type': 'modal_button', 'index': 5}, color='dark', outline=True, block=True)
        ],
        className = 'discontinued-panel'
    )
]

modal_info = html.Div([ 
    html.H5('Para determinar la previsibilidad de un producto, aplicamos dos coeficientes:'),
    html.P('- The Average Demand Interval (ADI): Mide la regularidad de la demanda en el tiempo calculando el intervalo promedio entre dos demandas.'),
    html.P('- the square of the Coefficient of Variation (CV2): Es la medida de la variacion en cantidades'),
    html.Hr(),
    html.H5('- Demanda tipo "Smooth": (ADI> = 1,32 y CV2 <0,49)'),
    html.P('El historial de la demanda muestra muy poca variacion en la cantidad de demanda, pero una gran variacion en el intervalo entre dos demandas. Aunque los metodos de pronostico especificos abordan las demandas intermitentes, el margen de error de pronostico es considerablemente mayor.'),
    html.Br(),
    html.H5('- Demanda tipo "Intermittent": (ADI <1,32 y CV2 <0,49)'),
    html.P('La demanda es muy regular en tiempo y cantidad. Por lo tanto, es facil de pronosticar y no tendra problemas para alcanzar un nivel de error de pronostico bajo.'),
    html.Br(),
    html.H5('- Demanda tipo "Erratic": (ADI> = 1,32 y CV2> = 0,49)'),
    html.P('La demanda se caracteriza por una gran variacion en cantidad y en el tiempo. En realidad, es imposible producir un pronostico confiable, independientemente de las herramientas de pronostico que utilice. Este tipo particular de patron de demanda es imprevisible.'),
    html.Br(),
    html.H5('- Demanda tipo "Lumpy": (ADI <1,32 y CV2 <0,49)'),
    html.P('La demanda es muy regular en tiempo y cantidad. Por lo tanto, es facil de pronosticar y no tendra problemas para alcanzar un nivel de error de pronostico bajo.'),
])

modal_inte = html.Div([
        dbc.Row([
            html.H6('Filtro por referencia:'),
            dbc.Col(
                dcc.Dropdown(id='dropdown_inter',
                    options=[],
                    value=[],
                    placeholder='Please select...',
                    multi=True
                )
            )
        ],className='flexy-row start col-8'),
        dbc.Row([
                dcc.Graph(id='intermittent_graph', figure={},style={"marginLeft": "0"})
            ],
            className = 'graph-chunk modal-graph'
        )
    ],
    className = 'flexy-col start'
)

modal_lump = html.Div([
        dbc.Row([
            html.H6('Filtro por referencia:'),
            dbc.Col(
                dcc.Dropdown(id='dropdown_lump',
                    options=[],
                    value=[],
                    placeholder='Please select...',
                    multi=True
                )
            )
        ],className='flexy-row start col-8'),
        dbc.Row([
                dcc.Graph(id='lumpy_graph', figure={},style={"marginLeft": "0"})
            ],
            className = 'graph-chunk modal-graph'
        )
    ],
    className = 'flexy-col start'
)

modal_smoo = html.Div([
        dbc.Row([
            html.H6('Filtro por referencia:'),
            dbc.Col(
                dcc.Dropdown(id='dropdown_smoo',
                    options=[],
                    value=[],
                    placeholder='Please select...',
                    multi=True
                )
            )
        ],className='flexy-row start col-8'),
        dbc.Row([
                dcc.Graph(id='smooth_graph', figure={},style={"marginLeft": "0"})
            ],
            className = 'graph-chunk modal-graph'
        )
    ],
    className = 'flexy-col start'
)

modal_erra = html.Div([
        dbc.Row([
            html.H6('Filtro por referencia:'),
            dbc.Col(
                dcc.Dropdown(id='dropdown_erra',
                    options=[],
                    value=[],
                    placeholder='Please select...',
                    multi=True
                )
            )
        ],className='flexy-row start col-8'),
        dbc.Row([
                dcc.Graph(id='erratic_graph', figure={},style={"marginLeft": "0"})
            ],
            className = 'graph-chunk modal-graph'
        )
    ],
    className = 'flexy-col start'
)

modal_down = html.Div([
    html.Div(id='table-container'),
    dbc.Button("Descargar csv",id="download_discontinued",outline=True, color="dark",n_clicks=0,),
    dcc.Download(id='download')
])

classificator = [
    dbc.Col([
            dbc.Row([
                html.H3("Clasificador de Demanda"),
                html.A(
                    html.I("I"),
                    id = {'type': 'modal_button', 'index': 0},
                    n_clicks = 0,
                    className = 'btn btn-outline-dark info-btn flexy-row'
                ),
            ]),

            dbc.Row([
                    dbc.Col([
                            dcc.Graph(id='general_graph', figure={})
                        ],
                        width = 8
                    ),
                    dbc.Col(options)
                ],
                className = 'graph-chunk'
            )
        ],
        className='classificators-content content-data'
    ),

    dbc.Modal([
            dbc.ModalHeader([], id='modal-header'),
            dbc.ModalBody([], id='modal-body'),
            dbc.ModalFooter(
                dbc.Button(
                    "Close", id="modal-close", color='dark', outline=True, n_clicks=0
                )
            ),
        ],
        id = "modal-clasf",
        size = 'lg',
        is_open = False,
        centered = True,
        scrollable = True,
        contentClassName = 'round'
    ),
]

## ---------------------------------------------------------------------- ##
## ------------------------------ METHODS ------------------------------- ##
## ---------------------------------------------------------------------- ##

## ------------------------- GET FILTERED DATA -------------------------- ##
def get_filtered(category,subcategory,start_date,end_date):

    data, discontinued, demand_classificator, classifier = DataManager().demand_data(start_date,end_date,True)
    smooth = demand_classificator.query("CLASSIFIER == 'Smooth'")
    intermittent = demand_classificator.query("CLASSIFIER == 'Intermittent'")
    lumpy = demand_classificator.query("CLASSIFIER == 'Lumpy'")
    erratic = demand_classificator.query("CLASSIFIER == 'Erratic'")
    
    if len(category)>0:
        data = data.query('CATEGORIA == @category')
        discontinued = discontinued.query('CATEGORIA == @category')
        smooth = smooth.query('CATEGORIA == @category')
        intermittent = intermittent.query('CATEGORIA == @category')
        erratic = erratic.query('CATEGORIA == @category')
        lumpy = lumpy.query('CATEGORIA == @category')
    
    if len(subcategory)>0:
        data = data.query('SUBCATEGORIA_POS == @subcategory')
        discontinued = discontinued.query('SUBCATEGORIA_POS == @subcategory')
        smooth = smooth.query('SUBCATEGORIA_POS == @subcategory')
        intermittent = intermittent.query('SUBCATEGORIA_POS == @subcategory')
        erratic = erratic.query('SUBCATEGORIA_POS == @subcategory')
        lumpy = lumpy.query('SUBCATEGORIA_POS == @subcategory')

    return data, discontinued, smooth, intermittent, erratic, lumpy

## ---------------------------------------------------------------------- ##
## ------------------------ GENERAL CALLBACKS --------------------------- ##
## ---------------------------------------------------------------------- ##

## -------------------------- FILTER CALLBACK --------------------------- ##
@app.callback(
    Output('general_graph', 'figure'),
    [
        Input('dropdown_category_clasf', 'value'),
        Input('dropdown_subcategory_clasf', 'value'),
        Input('calendar_clasf', 'start_date'),
        Input('calendar_clasf', 'end_date')
    ]
)
def update_graph(category,subcategory,start_date,end_date):
    data = get_filtered(category,subcategory,start_date,end_date)[0]
    
    fig = px.scatter(
        data,
        x="CV2", y="ADI", color="SUBCATEGORIA_POS",
        hover_data=['CATEGORIA','SUBCATEGORIA_POS','PROD_REF', 'DESCRIPCION',],
    )

    fig.add_hline(y=1.32, line_dash="dot", line_width=2,  line_color="black")
    fig.add_vline(x=0.49, line_dash="dot", line_width=2,  line_color="black")
    fig.add_annotation(text="INTERMITTENT", x=0.1, y=round(data['ADI'].max()+2), showarrow=False)
    fig.add_annotation(text="LUMPY", x=2, y=round(data['ADI'].max()+2), showarrow=False)
    fig.add_annotation(text="SMOOTH", x=0.1, y=0.5, showarrow=False)
    fig.add_annotation(text="ERRATIC", x=2, y=0.5, showarrow=False)

    fig.update_layout(
        font_size = 10,
        margin=dict(t=20, l=10, r=10, b=10, pad=0),
        paper_bgcolor = '#c8c8c8'
    )

    return fig

## -------------------------- MODALS CALLBACK -------------------------- ##
@app.callback(
    Output("modal-clasf", "is_open"),
    Output('modal-body', 'children'),
    Output('modal-header', 'children'),
    [
        Input({'type': 'modal_button', 'index': ALL}, "n_clicks"), 
        Input("modal-close", "n_clicks")
    ],
    State("modal-clasf", "is_open"),
    prevent_initial_call = True,
)
def toggle_modal(n1, n2, is_open):
    body = []
    header = []

    invoker = [p['prop_id'] for p in dash.callback_context.triggered][0]
    try:
        invoker_type = json.loads(invoker.split('.')[0])['type']
        invoker_index = json.loads(invoker.split('.')[0])['index']
    except ValueError:
        invoker_type = 'close_button'
        invoker_index = -1

    if invoker_index == 0:
        body = modal_info
        header = '¿Cómo se clasifica la demanda?'
    if invoker_index == 1:
        body = modal_inte
        header = 'Demanda Intermitente'
    if invoker_index == 2:
        body = modal_lump
        header = 'Demanda Lumpy'
    if invoker_index == 3:
        body = modal_smoo
        header = 'Demanda Smooth'
    if invoker_index == 4:
        body = modal_erra
        header = 'Demanda Erratica'
    if invoker_index == 5:
        body = modal_down
        header = 'Productos sugeridos - Descontinuar'

    if invoker_type == 'modal_button' or n2:
        return not is_open, body, header
    return is_open, body, header

## ----------------------- INTERMITTENT CALLBACK ----------------------- ##
@app.callback(
    Output('dropdown_inter', 'value'),
    Output('dropdown_inter', 'options'),
    
    Input({'type': 'modal_button', 'index': 1}, "n_clicks"),
    
    State('dropdown_category_clasf', 'value'),
    State('dropdown_subcategory_clasf', 'value'),
    State('calendar_clasf', 'start_date'),
    State('calendar_clasf', 'end_date')
)
def set_classificators_satate(modal, cat_state, subcat_state, sd_state, ed_state):
    intermittent = get_filtered(cat_state, subcat_state, sd_state, ed_state)[3]
    options = [{'label':opt, 'value':opt} for opt in intermittent.sort_values('DEMAND_BUCKETS',ascending=False)['PROD_REF'].unique()]
    return [], options

## --------------------------- LUMPY CALLBACK -------------------------- ##
@app.callback(
    Output('dropdown_lump', 'value'),
    Output('dropdown_lump', 'options'),
    
    Input({'type': 'modal_button', 'index': 2}, "n_clicks"),
    
    State('dropdown_category_clasf', 'value'),
    State('dropdown_subcategory_clasf', 'value'),
    State('calendar_clasf', 'start_date'),
    State('calendar_clasf', 'end_date')
)
def set_classificators_satate(modal, cat_state, subcat_state, sd_state, ed_state):
    lumpy = get_filtered(cat_state, subcat_state, sd_state, ed_state)[5]
    options = [{'label':opt, 'value':opt} for opt in lumpy.sort_values('DEMAND_BUCKETS',ascending=False)['PROD_REF'].unique()]
    return [], options

## -------------------------- SMOOTH CALLBACK -------------------------- ##
@app.callback(
    Output('dropdown_smoo', 'value'),
    Output('dropdown_smoo', 'options'),
    
    Input({'type': 'modal_button', 'index': 3}, "n_clicks"),
    
    State('dropdown_category_clasf', 'value'),
    State('dropdown_subcategory_clasf', 'value'),
    State('calendar_clasf', 'start_date'),
    State('calendar_clasf', 'end_date')
)
def set_classificators_satate(modal, cat_state, subcat_state, sd_state, ed_state):
    smooth = get_filtered(cat_state, subcat_state, sd_state, ed_state)[2]
    options = [{'label':opt, 'value':opt} for opt in smooth.sort_values('DEMAND_BUCKETS',ascending=False)['PROD_REF'].unique()]
    return [], options

## -------------------------- ERRATIC CALLBACK ------------------------- ##
@app.callback(
    Output('dropdown_erra', 'value'),
    Output('dropdown_erra', 'options'),
    
    Input({'type': 'modal_button', 'index': 4}, "n_clicks"),
    
    State('dropdown_category_clasf', 'value'),
    State('dropdown_subcategory_clasf', 'value'),
    State('calendar_clasf', 'start_date'),
    State('calendar_clasf', 'end_date')
)
def set_classificators_satate(modal, cat_state, subcat_state, sd_state, ed_state):
    erratic = get_filtered(cat_state, subcat_state, sd_state, ed_state)[4]
    options = [{'label':opt, 'value':opt} for opt in erratic.sort_values('DEMAND_BUCKETS', ascending=False)['PROD_REF'].unique()]
    return [], options


## ----------------------- DISCONTINUED CALLBACK ----------------------- ##
@app.callback(
    Output('table-container', 'children'),
    
    Input({'type': 'modal_button', 'index': 5}, "n_clicks"),
    
    State('dropdown_category_clasf', 'value'),
    State('dropdown_subcategory_clasf', 'value'),
    State('calendar_clasf', 'start_date'),
    State('calendar_clasf', 'end_date')
)
def set_classificators_satate(modal, cat_state, subcat_state, sd_state, ed_state):
    discontinued = get_filtered(cat_state, subcat_state, sd_state, ed_state)[1]

    table = dash_table.DataTable(
        id='datatable1',
        data=discontinued.to_dict('records'),
        columns=[{'id': x, 'name': x} for x in discontinued.columns],
        sort_action='native',
        page_size=20,
        style_table={'height': '300px', 'overflowY': 'auto'},
        style_as_list_view=True,
        style_header={'backgroundColor': 'rgb(30, 30, 30)',
            'color':'white',
            'fontWeight': 'bold',
            'font_size':13,
            'textAlign': 'center'
        },
        style_cell={
            'backgroundColor': 'white',
            'color': 'black',
            'border': '1px solid grey',
            'font_size':11
        },
        style_cell_conditional=[{'textAlign': 'left'}],
        style_data={'border': '1px solid grey'},
    )
    
    return table

## ----------------------- OTHER CALLBACKS ----------------------- ##
@app.callback(
    Output('intermittent_graph', 'figure'),
    [Input('dropdown_inter', 'value'),
    Input('dropdown_inter', 'options')],
    prevent_initial_call = True
)
def update_drown(value,options):
    intermittent = DataManager().demand_classifier.query("CLASSIFIER=='Intermittent'").sort_values('DEMAND_BUCKETS', ascending=False)
    if(options is not None and len(options) > 0):
        refs = [d['label'] for d in options]
        intermittent = intermittent.query('PROD_REF in @refs')

    if (len(value)>0):
        intermittent = intermittent[intermittent['PROD_REF'].isin(value)]

    fig = px.bar(intermittent, y='YY_MM',x='CANTIDAD',
       hover_data = ['PROD_REF','CATEGORIA','SUBCATEGORIA_POS','DESCRIPCION'], 
       labels = {'YY_MM':'FECHA'}
    ).update_layout(
        font_size = 10,
        margin=dict(t=20, l=10, r=10, b=10, pad=0),
        paper_bgcolor = '#c8c8c8'
    )

    return fig

## Lumpy
@app.callback(
    Output('lumpy_graph', 'figure'),
    [Input('dropdown_lump', 'value'),
    Input('dropdown_lump', 'options')],
    prevent_initial_call = True
)
def update_drown(value,options):
    lumpy = DataManager().demand_classifier.query("CLASSIFIER=='Lumpy'").sort_values('DEMAND_BUCKETS', ascending=False)
    if(options is not None and len(options) > 0):
        refs = [d['label'] for d in options]
        lumpy = lumpy.query('PROD_REF in @refs')

    if (len(value)>0):
        lumpy = lumpy[lumpy['PROD_REF'].isin(value)]

    fig = px.bar(lumpy, y='YY_MM',x='CANTIDAD',
       hover_data = ['PROD_REF','CATEGORIA','SUBCATEGORIA_POS','DESCRIPCION'], 
       labels = {'YY_MM':'FECHA'}
    ).update_layout(
        font_size = 10,
        margin=dict(t=20, l=10, r=10, b=10, pad=0),
        paper_bgcolor = '#c8c8c8'
    )

    return fig

## Smooth
@app.callback(
    Output('smooth_graph', 'figure'),
    [Input('dropdown_smoo', 'value'),
    Input('dropdown_smoo', 'options')],
    prevent_initial_call = True
)
def update_drown(value,options):
    smooth = DataManager().demand_classifier.query("CLASSIFIER=='Smooth'").sort_values('DEMAND_BUCKETS', ascending=False)
    if(options is not None and len(options) > 0):
        refs = [d['label'] for d in options]
        smooth = smooth.query('PROD_REF in @refs')

    if (len(value)>0):
        smooth = smooth[smooth['PROD_REF'].isin(value)]

    fig = px.bar(smooth, y='YY_MM',x='CANTIDAD',
       hover_data = ['PROD_REF','CATEGORIA','SUBCATEGORIA_POS','DESCRIPCION'], 
       labels = {'YY_MM':'FECHA'}
    ).update_layout(
        font_size = 10,
        margin=dict(t=20, l=10, r=10, b=10, pad=0),
        paper_bgcolor = '#c8c8c8'
    )

    return fig

## Erratic
@app.callback(
    Output('erratic_graph', 'figure'),
    [Input('dropdown_erra', 'value'),
    Input('dropdown_erra', 'options')],
    prevent_initial_call = True
)
def update_drown(value,options):
    erratic = DataManager().demand_classifier.query("CLASSIFIER=='Erratic'").sort_values('DEMAND_BUCKETS', ascending=False)
    if(options is not None and len(options) > 0):
        refs = [d['label'] for d in options]
        erratic = erratic.query('PROD_REF in @refs')

    if (len(value)>0):
        erratic = erratic[erratic['PROD_REF'].isin(value)]

    fig = px.bar(erratic, y='YY_MM', x='CANTIDAD',
       hover_data = ['PROD_REF','CATEGORIA','SUBCATEGORIA_POS','DESCRIPCION'], 
       labels = {'YY_MM':'FECHA'}
    ).update_layout(
        font_size = 10,
        margin=dict(t=20, l=10, r=10, b=10, pad=0),
        paper_bgcolor = '#c8c8c8'
    )

    return fig

## FileDownload
@app.callback(
    Output("download", "data"),
    [Input("download_discontinued", "n_clicks")],
    prevent_initial_call=True
)
def generate_csv(n_nlicks):
    return dcc.send_data_frame(DataManager().discontinued.to_csv, filename="discontinued.csv")
