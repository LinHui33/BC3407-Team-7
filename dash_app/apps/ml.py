import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from app import app, server
from flask_login import current_user
from methods.User import User
import sqlite3

layout = html.Div([
    html.H5("ML Performance"),
    dbc.Row([dbc.Col("Current Model used: CART, Trainset Accuracy: X%, Testset Accuracy X%"),
             dbc.Col(dbc.Button("Retrain Model", style={"float": "right", 'margin': "1rem"}, disabled=True))]),
    html.Div([html.Div('Graph of Show up rates over time VS. Predicted Show Up Rates'),
              dcc.Graph(),
              html.Div("CART Tree & Other model metrics"),
              dcc.Graph(),
              ]),
])