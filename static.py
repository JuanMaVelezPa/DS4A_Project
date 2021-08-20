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
from datetime import datetime as dt

# Sidebar
controls = dbc.FormGroup(
    [
        html.P('Por favor seleccionar los filtros para visualizar en las graficas', style=TEXT_STYLE),
        html.Hr(),
        dbc.Button(
            id='submit_button',
            n_clicks=0,
            children='Borrar filtros',
            color='secondary',
            block=True
        ),
        html.Hr(),
        html.P('Categoria', style=TEXT_STYLE),
        dcc.Dropdown(id='dropdown',
            options=[
                    {'label': 'ALCOBAS', 'value': 'ALCOBAS'}, 
                    {'label': 'COMEDORES', 'value': 'COMEDORES'}, 
                    {'label': 'ESTUDIO', 'value': 'ESTUDIO'}, 
                    {'label': 'SALAS Y SOFAS', 'value': 'SALAS Y SOFAS'}, 
            ],
            value=['SALAS Y SOFAS'],
            placeholder='Please select...',
            multi=True,
        ),
        html.Br(),
        html.P('Calendar', style=TEXT_STYLE),
        dcc.DatePickerRange(
            id='my-date-picker-range',  # ID to be used for callback
            calendar_orientation='horizontal',  # vertical or horizontal
            day_size=39,  # size of calendar image. Default is 39
            end_date_placeholder_text="Return",  # text that appears when no end date chosen
            with_portal=True,  # if True calendar will open in a full screen overlay portal
            first_day_of_week=1,  # Display of calendar when open (0 = Sunday)
            reopen_calendar_on_clear=True,
            is_RTL=False,  # True or False for direction of calendar
            clearable=True,  # whether or not the user can clear the dropdown
            number_of_months_shown=1,  # number of months shown when calendar is open
            min_date_allowed=dt(2019, 1, 1),  # minimum date allowed on the DatePickerRange component
            max_date_allowed=dt(2022, 12, 31),  # maximum date allowed on the DatePickerRange component
            initial_visible_month=dt(2019, 1, 1),  # the month initially presented when the user opens the calendar
            start_date=dt(2019, 1, 1).date(),
            end_date=dt(2022, 12, 31).date(),
            display_format='DD, MMM YY',  # how selected dates are displayed in the DatePickerRange component.
            month_format='MMMM, YYYY',  # how calendar headers are displayed when the calendar is opened.
            minimum_nights=2,  # minimum number of days between start and end date
            persistence=True,
            persisted_props=['start_date'],
            persistence_type='session',  # session, local, or memory. Default is 'local'
            updatemode='singledate',  # singledate or bothdates. Determines when callback is triggered
        ),
        html.Br(),
        html.P('Check Box', style=TEXT_STYLE),
        dbc.Card([dbc.Checklist(
            id='check_list',
            options=[
                    {'label': 'Value 1','value': 'value1'},
                    {'label': 'Value 2','value': 'value2'},
                    {'label': 'Value 3','value': 'value3'},
            ],
            value=['value1', 'value2'],
            inline=True
        )]),
        html.Br(),
        html.P('Radio Items', style=TEXT_STYLE),
        dbc.Card([dbc.RadioItems(
            id='radio_items',
            options=[
                    {'label': 'Value 1','value': 'value1'},
                    {'label': 'Value 2','value': 'value2'},
                    {'label': 'Value 3','value': 'value3'},
            ],
            value='value1',
            style={'margin': 'auto'}
        )]),
    ]
)

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
        html.H6('David FeliH6e Rubio Mendez', style=TEXT_STYLE_2),
        html.H6('Johann Sebastian Roa Amorocho', style=TEXT_STYLE_2),
        html.H6('Andres Manrique', style=TEXT_STYLE_2),
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