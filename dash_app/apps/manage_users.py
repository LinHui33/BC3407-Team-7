import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from app import app, server
from flask_login import LoginManager, current_user
from methods.User import User
import sqlite3

layout = html.Div([

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
