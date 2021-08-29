from numpy.lib.type_check import asfarray
import pandas as pd
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go

import dash  # (version 1.12.0) pip install dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from styles import *
from dataManager import *
from mainDash import *
from datetime import date as dt

from layout.menus import ind_menu

indicators_general = [
    dbc.Col([
        html.Div(
            [
                html.H3("Indicadores", className='title'),
                dcc.Graph(id='graph_general_1', figure={}),
            ],
            className='graph-chunk'
        ),
        
        html.Div(
            [
                html.H3(id='prueba', className='title', children=['Ventas totales por año']),
                dcc.Graph(id='graph_general_2', figure={})
            ],
            className='graph-chunk'
        ),

        html.Div(
            [
                html.H3(id='prueba', className='title', children=['Venta media por años']),
                dcc.Graph(id='graph_general_3', figure={})
            ],
            className='graph-chunk'
        ),

        html.Div(
            [
                html.H3(id='prueba', className='title', children=['Colores más vendidos']),
                dcc.Graph(id='graph_general_4', figure={})
            ],
            className='graph-chunk'
        )

    ],
    ),
]

indicators_features = [
    dbc.Col([
        html.H3("Caracteristicas",className='title'),
        html.Div(
            [
                dbc.Col([
                    dcc.Graph(id='graph_features_1', figure={})
                ]),

                dbc.Col([
                    dcc.Graph(id='graph_features_2', figure={})
                ])

                


            ],
            className='graph-chunk'
        )
    ]),
]

ind_content = html.Div(className='content-data',id='indicators-container',children=indicators_general)

indicators_container = [
    ind_menu,
    ind_content
]

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

features_controls = dbc.FormGroup(
    [
        html.P('Por favor seleccionar las características a analizar'),
        html.Hr(),
        dcc.Dropdown(id='dropdown_field1',
            options=[
                    {'label': i, 'value': i} for i in DataManager().sales_prod.columns.sort_values()
            ],
            value = [],
            placeholder='Please select...',
            multi=False,
        ),
        html.Br(),
        dcc.Dropdown(id='dropdown_field2',
            options=[
                    {'label': i, 'value': i} for i in DataManager().sales_prod.columns
            ],
            value = [],
            placeholder='Please select...',
            multi=False,
        ),
        html.P('Calendar'),
        dcc.DatePickerRange(
            id='calendar2',
            with_portal=True,
            first_day_of_week=1,
            reopen_calendar_on_clear=True,
            clearable=True,
            min_date_allowed=dt(dateMin.year, dateMin.month, dateMin.day),
            max_date_allowed=dt(2022, 12, 31),
            initial_visible_month=dt(dateMin.year, dateMin.month, dateMin.day),
            start_date=dt(2019, 1, 1),
            end_date=dt(dateMax.year, dateMax.month, dateMax.day),
            display_format='DD, MMM YY',
            month_format='MMMM, YYYY',
        ),
        html.Br()
    ]
)

## Indicatores
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

    if (start_date is None or start_date == ""):
        start_date = sales_prod['FECHA'].min()
    
    if (end_date is None or end_date == ""):
        end_date = sales_prod['FECHA'].max()
        
    mask = (sales_prod['FECHA'] >= start_date) & (sales_prod['FECHA'] <= end_date)
    sales_prod = sales_prod.loc[mask]
    fig = px.scatter(sales_prod,
        x="CANTIDAD",
        y="TOTAL",
        color="SUBCATEGORIA",
        hover_data=['REF', 'DESC_LARGA','CATEGORIA'],
        title="\t Sales Subategories | Money vs Units",
    )
    return fig

# Analisis de ventas totales
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
    
    
    sales1 = sales_prod.groupby(['ANIO','MES'])['TOTAL'].sum().to_frame().reset_index()
    fig = px.line(sales1, x="MES", y="TOTAL", color='ANIO', labels = {1:"JAN",
    2:"FEB",3:"MAR",4:"APR",5:"MAY",6:"JUN",7:"JUL",8:"AUG",9:"SEP",10:"OCT",11:"NOV",12:"DEC"})
    
    return fig

# Analisis de ventas por año
@app.callback(
    Output('graph_general_3', 'figure'),
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
    
    
    sales1 = sales_prod.groupby(['ANIO','MES'])['TOTAL'].mean().to_frame().reset_index()
    sales1['ANIO'] = sales1['ANIO'].astype("category")
    fig = px.bar(sales1, x="MES", y="TOTAL", color='ANIO',barmode='group')
    

    
    return fig


## Colores más vendidos
@app.callback(
    Output('graph_general_4', 'figure'),
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
        marker_color=colors, # marker color can be a single color value or an iterable
    )])
    
    return fig

@app.callback(
    Output('graph_features_1', 'figure'),
    [Input('dropdown_field1', 'value'),
    Input('dropdown_field2', 'value'),
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
                hoverongaps = False),layout=go.Layout( title=f"{value1} VS {value2} Total Sales"))
    else:
        data = DataManager().sales_prod
        x_values = data["SUBCATEGORIA_POS"].unique()
        y_values = data["CATEGORIA"].unique()
        z_values = pd.crosstab(data["CATEGORIA"], data["SUBCATEGORIA_POS"]).values.tolist()
        fig1 =  go.Figure(data=go.Heatmap(
                z=z_values,
                x=x_values,
                y=y_values,
                hoverongaps = False),layout=go.Layout( title="CATEGORIA VS SUBCATEGORIA_POS Total Sales"))
    return fig1

@app.callback(
    Output('graph_features_2', 'figure'),
    [Input('dropdown_field1', 'value'),
    Input('dropdown_field2', 'value'),
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
                hoverongaps = False),layout=go.Layout( titletitle=f"{value1} VS {value2} Total Sales Money"))
    else:
        data = DataManager().sales_prod
        x_values = data["SUBCATEGORIA_POS"].unique()
        y_values = data["CATEGORIA"].unique()
        z_values2 = data.groupby(['CATEGORIA', 'SUBCATEGORIA_POS']).TOTAL.sum().unstack(fill_value=0).values.tolist()
        fig2 = go.Figure(data=go.Heatmap(
                z=z_values2,
                x=x_values,
                y=y_values,
                hoverongaps = False),layout=go.Layout( title="CATEGORIA VS SUBCATEGORIA_POS Total Sales Money"))

    return fig2
