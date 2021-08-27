##
##
## sidebar
## developer: JuanMa y Andres
##
##

import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
from styles import *
from datetime import date as dt
from dataManager import *

# Sidebar
df = DataManager().sales_prod

category_unique = df['CATEGORIA'].unique()
subcategory_unique = df['SUBCATEGORIA'].unique()
tienda_unique = df['TIENDA'].unique()

dateMin = DataManager().sales_prod["FECHA"].min()
dateMax = DataManager().sales_prod["FECHA"].max()

controls = html.Div(id = "sidebar_control", children=[
dbc.FormGroup(
    [
        html.P('Por favor seleccionar los filtros para visualizar en las graficas', style=TEXT_STYLE),
        html.Hr(),
        html.P('Punto de venta', style=TEXT_STYLE),
        dcc.Dropdown(id='dropdown_tienda',
            options=[
                    {'label': i, 'value': i} for i in tienda_unique
            ],
            value = [],
            placeholder='Please select...',
            multi=True,
        ),
        html.Br(),
        html.P('Categoria', style=TEXT_STYLE),
        dcc.Dropdown(id='dropdown_category',
            options=[
                    {'label': i, 'value': i} for i in category_unique
            ],
            value = [],
            placeholder='Please select...',
            multi=True,
        ),
        html.Br(),
        html.P('SubCategoria', style=TEXT_STYLE),
        dcc.Dropdown(id='dropdown_subcategory',
            options=[
                    {'label': i, 'value': i} for i in subcategory_unique
            ],
            value=[],
            placeholder='Please select...',
            multi=True,
        ),
        html.Br(),
        html.P('Calendar', style=TEXT_STYLE),
        dcc.DatePickerRange(
            id='calendar',
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
)])


## Cards
content_first_row = dbc.Row([
    dbc.Nav([
        dbc.Button("Indicadores", href="/indicadores", outline=True, color="primary", className="mr-1"),
        dbc.Button("Prediccion Demanda", href="/demanda", outline=True, color="primary", className="mr-1"),
        dbc.Button("Cobertura Inventario", href="/inventario", outline=True, color="primary", className="mr-1"),
    ]),
])

sidebar = html.Div(
    [
        html.H2('Furni', style=TEXT_STYLE),
        html.Hr(),
        controls,
        html.Hr(),
        html.H6('Developed by DS4A - Grupo 65', style=TEXT_STYLE),
        html.Br(),
        html.H6('Juan Manuel Velez Parra', style=TEXT_STYLE_2),
        html.H6('Nicholas Gooding Rios', style=TEXT_STYLE_2),
        html.H6('David Felipe Rubio Mendez', style=TEXT_STYLE_2),
        html.H6('Johann Sebastian Roa Amorocho', style=TEXT_STYLE_2),
        html.H6('Andrés Manrique Ardila', style=TEXT_STYLE_2),
        html.H6('---', style=TEXT_STYLE_2),
        html.H6('Esteban Betancur | TA', style=TEXT_STYLE_2),
        html.H6('Luis Rojas | TA', style=TEXT_STYLE_2),
    ],
    style=SIDEBAR_STYLE,
)

cards = html.Div(
    [
        content_first_row,
        html.Hr(),
    ],
    style=BUTTON_STYLE,
)