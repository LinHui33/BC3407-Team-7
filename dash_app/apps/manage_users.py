import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from app import app, server
from flask_login import current_user
from methods.User import User
import sqlite3

layout = html.Div([
    html.H5("Manage Users"),

])