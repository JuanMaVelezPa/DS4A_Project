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

# Sidebar
controls = dbc.FormGroup(
    [
        html.P('Dropdown', style={
            'textAlign': 'center'
        }),
        dcc.Dropdown(
            id='dropdown',
            options=[{
                'label': 'Value One',
                'value': 'value1'
            }, {
                'label': 'Value Two',
                'value': 'value2'
            },
                {
                    'label': 'Value Three',
                    'value': 'value3'
                }
            ],
            value=['value1'],  # default value
            multi=True
        ),
        html.Br(),
        html.P('Range Slider', style={
            'textAlign': 'center'
        }),
        dcc.RangeSlider(
            id='range_slider',
            min=0,
            max=20,
            step=0.5,
            value=[5, 15]
        ),
        html.P('Check Box', style={
            'textAlign': 'center'
        }),
        dbc.Card([dbc.Checklist(
            id='check_list',
            options=[{
                'label': 'Value One',
                'value': 'value1'
            },
                {
                    'label': 'Value Two',
                    'value': 'value2'
                },
                {
                    'label': 'Value Three',
                    'value': 'value3'
                }
            ],
            value=['value1', 'value2'],
            inline=True
        )]),
        html.Br(),
        html.P('Radio Items', style={
            'textAlign': 'center'
        }),
        dbc.Card([dbc.RadioItems(
            id='radio_items',
            options=[{
                'label': 'Value One',
                'value': 'value1'
            },
                {
                    'label': 'Value Two',
                    'value': 'value2'
                },
                {
                    'label': 'Value Three',
                    'value': 'value3'
                }
            ],
            value='value1',
            style={
                'margin': 'auto'
            }
        )]),
        html.Br(),
        dbc.Button(
            id='submit_button',
            n_clicks=0,
            children='Submit',
            color='primary',
            block=True
        ),
    ]
)

## Cards
content_first_row = dbc.Row([
    dbc.Nav([
        dbc.Col(
            dbc.Card(
                [
                    dbc.NavLink("Indicadores", href="/indicadores", active="exact", style=CARD_TEXT_STYLE)
                ]
            ),
            md=3
        ),
        dbc.Col(
            dbc.Card(
                [
                    dbc.NavLink("Prediccion Demanda", href="/demanda", active="exact", style=CARD_TEXT_STYLE)
                ]

            ),
            md=4
        ),
        dbc.Col(
            dbc.Card(
                [
                    dbc.NavLink("Cobertura Inventario", href="/inventario", active="exact", style=CARD_TEXT_STYLE)
                ]
            ),
            md=4
        ),
    ])
])

sidebar = html.Div(
    [
        html.H2('Parameters', style=TEXT_STYLE),
        html.Hr(),
        controls
    ],
    style=SIDEBAR_STYLE,
)

cards = html.Div(
    [
        content_first_row,
        html.Hr(),
    ],
    style=CONTENT_STYLE,
)