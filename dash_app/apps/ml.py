import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from app import app, server
from flask_login import LoginManager, current_user
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

# ---------------------------------------------------------------------------------------------------------------------
# Flask-login
# ---------------------------------------------------------------------------------------------------------------------
# Setup the LoginManager for the server
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = '/login'


# callback to reload the user object
@login_manager.user_loader
def load_user(username):
    try:
        conn = sqlite3.connect('assets/hospital_database.db')
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT * FROM users  WHERE (user_id = '{username}');")
        lu = cursor.fetchone()
        if lu is None:
            return None
        else:
            return User(lu[0], lu[1], lu[2])
    except Exception as e:
        print(e)
        return None
