from dash_html_components.P import P
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
        dbc.Row([
                html.H3("Indicadores generales", className='title'),
                ind_menu,
            ],
            className='flexy-row'
        ),
        html.Hr(),
        
        dbc.Row([
            dbc.Col([
                    dcc.Graph(id='historic_sales_money', figure={})
                ],
                className='graph-chunk'
            ),

            dbc.Col([
                    dcc.Graph(id='historic_sales_mean', figure={})
                ],
                className='graph-chunk halved'
            ),
        ]),

        html.Div([
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
                ind_menu
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

# Callbask to draw sales($) according to controls
@app.callback(
    Output('historic_sales_money', 'figure'),
    [Input('dropdown_category', 'value'),
     Input('dropdown_subcategory', 'value'),
     Input('dropdown_tienda', 'value'),
     Input('calendar', 'start_date'),
     Input('calendar', 'end_date')])

def update_historic_sales_money_graph(category, subcat, store, start_date, end_date):
    if(store == []):
        temp = DataManager().sales_prod
    else:
        temp = DataManager().sales_prod.query("TIENDA==@store")
    
    if (category == [] and subcat == []):
        sales_prod = temp
    elif (category != [] and subcat == []):
        sales_prod = temp.query("CATEGORIA==@category")
    elif (category == [] and subcat != []):
        sales_prod = temp.query("SUBCATEGORIA==@subcat")
    else:
        sales_prod = temp.query("CATEGORIA==@category")
        sales_prod = temp.query("SUBCATEGORIA==@subcat")
    
    mask = (sales_prod['FECHA'] >= start_date) & (sales_prod['FECHA'] <= end_date)
    sales_prod = sales_prod.loc[mask]
    res = sales_prod.groupby(['ANIO','MES'])['TOTAL'].sum().to_frame().reset_index()
    
    fig = px.line(res, x="MES", y="TOTAL", color='ANIO', 
        labels = {'TOTAL':'Total','MES':'Mes','ANIO':'',1:"Ene",2:"Feb",3:"Mar",4:"Abr",5:"May",6:"Jun",7:"Jul",8:"Ago",9:"Sep",10:"Oct",11:"Nov",12:"Dic"},
        height = 250,
        width = 550,
        color_discrete_sequence=px.colors.qualitative.Prism
    )
    fig.update_layout(
        font_size = 12,
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

# Analisis de ventas por año
@app.callback(
    Output('historic_sales_mean', 'figure'),
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
    fig = px.bar(sales1, x="MES", y="TOTAL", color='ANIO',barmode='group',
        height = 250,
        width = 400
    )
    fig.update_layout(
        font_size=12,
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

## Indicatores
@app.callback(
    Output('sales_map', 'figure'),
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

""" ## Colores más vendidos
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
    
    return fig """


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
