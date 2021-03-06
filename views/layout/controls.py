import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc

from datetime import date as dt
from managers.dataManager import *

df = DataManager().sales_prod

category_unique = df['CATEGORIA'].unique()
subcategory_unique = df['SUBCATEGORIA_POS'].unique()
tienda_unique = df['TIENDA'].unique()
ref_unique = df[['REF','DESCRIPCION']].copy()
ref_unique.drop_duplicates(inplace=True)
ref_unique['NAME'] = ref_unique.DESCRIPCION + '  (' + ref_unique.REF + ')'

dateMin = DataManager().sales_prod["FECHA"].min()
dateMax = DataManager().sales_prod["FECHA"].max()

# ---------------------------------------------------------------------- #
# ----------------------------- INDICATORS ----------------------------- #
# ---------------------------------------------------------------------- #

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

# ---------------------------------------------------------------------- #
# ------------------------------ FEATURES ------------------------------ #
# ---------------------------------------------------------------------- #

features_controls = html.Div(
    [
        html.P('Por favor seleccionar filtro y característica a analizar'),
        html.Hr(),
        html.P('Filtro'),
        dcc.Dropdown(id='filter',
            options=[
                    {'label': i, 'value': j} for i,j in zip(['Categoría','Sub-categoría'], DataManager().sales_prod[['CATEGORIA','SUBCATEGORIA_POS']].columns.sort_values())
            ],
            value = [],
            placeholder='Please select...',
            multi=False,
        ),
        html.Br(),
        html.P('Característica'),
        dcc.Dropdown(id='feature',
            options=[
                    {'label': i, 'value': i} for i in DataManager().sales_prod[['COLOR_POS','MATERIAL_POS','ACABADO','VIGENCIA','ESTILO','PUESTOS']].columns.sort_values()
            ],
            value = [],
            placeholder='Please select...',
            multi=False,
        ),
        html.Br(),
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

# ---------------------------------------------------------------------- #
# ---------------------------- CLASIFICATOR ---------------------------- #
# ---------------------------------------------------------------------- #
category_clasf = dbc.FormGroup(
    children=[
        html.P('Categoria'),
        dcc.Dropdown(id='dropdown_category_clasf',
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

subcat_clasf = dbc.FormGroup(
    children=[
        html.P('SubCategoria'),
        dcc.Dropdown(id='dropdown_subcategory_clasf',
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

calendar_clasf = dbc.FormGroup(
    children=[
        html.P('Calendar'),
        dcc.DatePickerRange(
            id='calendar_clasf',
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

demand_controls = html.Div(
    [
        html.P('Por favor seleccionar los filtros para visualizar en las graficas'),
        html.Hr(),
        category_clasf,
        subcat_clasf,
        calendar_clasf,
        html.Hr()
    ],
    id="demand_controls"
)

# ---------------------------------------------------------------------- #
# ----------------------------- PREDICTOR ------------------------------ #
# ---------------------------------------------------------------------- #

category_pred = dbc.FormGroup(
    children=[
        html.P('Categoria'),
        dcc.Dropdown(id='dropdown_category_pred',
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

subcat_pred = dbc.FormGroup(
    children=[
        html.P('SubCategoria'),
        dcc.Dropdown(id='dropdown_subcategory_pred',
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

ref_pred = dbc.FormGroup(
    children=[
        html.P('Referencia'),
        dcc.Dropdown(
            id = 'dropdown_ref',
            options = [
                {'label': i, 'value': j} for i,j in zip(ref_unique.NAME, ref_unique.REF)
            ],
            value = [],
            placeholder = 'Please select...',
            multi = True,
            optionHeight = 55,
        ),
        html.Br()
    ]
)

predict_controls = html.Div([
    html.P('Por favor seleccionar los filtros para visualizar en las graficas'),
    html.Hr(),
    category_pred,
    subcat_pred,
    ref_pred,
    html.Hr()
])