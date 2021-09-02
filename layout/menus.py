##
##
## developer: JuanMa y Andres
##
##

from typing import Container
import dash_bootstrap_components as dbc
import dash_html_components as html
from styles import *

from layout.controls import indicators_controls

top_menu = dbc.Navbar([
    html.H1('Furni', className='flex-field'),
    dbc.Nav([
            dbc.NavItem(dbc.NavLink('Indicadores generales', className='btn btn-primary round',href='/indicadores')),
            dbc.NavItem(dbc.NavLink('Características', className='btn btn-primary round',href="/indicadores/caracteristicas")),
            dbc.NavItem(dbc.NavLink('Clasificador demanda', className='btn btn-secondary round',href='/demanda')),
            dbc.NavItem(dbc.NavLink('Predicción futura', className='btn btn-third round',href='/demanda/prediccion')),
        ],
        className='top-menu'
    ),
],
className='menu flexy-row between')

sidebar_menu = html.Div([
        html.Div(
            indicators_controls,
            id='sidebar_container',
            className='wrap flexy-col'
        ),
        html.Div([
                html.H6('Developed by DS4A - Grupo 65'),
                html.Br(),
                html.H6('Juan Manuel Velez Parra'),
                html.H6('Nicholas Gooding Rios'),
                html.H6('David Felipe Rubio Mendez'),
                html.H6('Johann Sebastian Roa Amorocho'),
                html.H6('Andrés Manrique Ardila'),
                html.H6('---'),
                html.H6('Esteban Betancur | TA'),
                html.H6('Luis Rojas | TA'),
            ],
            className='team-info'
        )
    ],
    id='sidebar',
    className='sidebar bg-light'
)