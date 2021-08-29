import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
from dash_html_components.Div import Div

from datetime import date as dt
from dataManager import *

df = DataManager().sales_prod

category_unique = df['CATEGORIA'].unique()
subcategory_unique = df['SUBCATEGORIA'].unique()
tienda_unique = df['TIENDA'].unique()
ref_unique = df['REF'].unique()

dateMin = DataManager().sales_prod["FECHA"].min()
dateMax = DataManager().sales_prod["FECHA"].max()


store = dbc.FormGroup(
    children=[
        html.P('Punto de venta'),
        dcc.Dropdown(id='dropdown_tienda',
            options=[
                    {'label': i, 'value': i} for i in tienda_unique
            ],
            value = [],
            placeholder='Please select...',
            multi=True,
        ),
        html.Br()
    ]
)

category = dbc.FormGroup(
    children=[
        html.P('Categoria'),
        dcc.Dropdown(id='dropdown_category',
            options=[
                    {'label': i, 'value': i} for i in category_unique
            ],
            value = [],
            placeholder='Please select...',
            multi=True,
        ),
        html.Br()
    ]
)

subcat = dbc.FormGroup(
    children=[
        html.P('SubCategoria'),
        dcc.Dropdown(id='dropdown_subcategory',
            options=[
                    {'label': i, 'value': i} for i in subcategory_unique
            ],
            value=[],
            placeholder='Please select...',
            multi=True,
        ),
        html.Br()
    ]
)

ref = dbc.FormGroup(
    children=[
        html.P('Referencia'),
        dcc.Dropdown(id='dropdown_ref',
            options=[
                    {'label': i, 'value': i} for i in ref_unique
            ],
            value=[],
            placeholder='Please select...',
        ),
        html.Br()
    ]
)

calendar = dbc.FormGroup(
    children=[
        html.P('Calendar'),
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
)

indicators_controls = html.Div(
    [
        html.P('Por favor seleccionar los filtros para visualizar en las graficas'),
        html.Hr(),
        store,
        category,
        subcat,
        calendar,
        html.Hr()
    ],
    id="indicators_controls"
)

demand_controls = html.Div(
    [
        html.P('Por favor seleccionar los filtros para visualizar en las graficas'),
        html.Hr(),
        category,
        subcat,
        calendar,
        html.Hr()
    ],
    id="demand_controls"
)

predict_controls = html.Div([
    html.P('Por favor seleccionar los filtros para visualizar en las graficas'),
    html.Hr(),
    ref,
    html.Hr()
])

inventory_controls = []