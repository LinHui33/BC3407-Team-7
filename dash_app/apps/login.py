import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from app import app, server
from werkzeug.security import check_password_hash
from flask_login import UserMixin, LoginManager, login_user
import sqlite3

layout = html.Div([
    dbc.Card([
        html.Div([
            html.Center(html.H5('XYZ Hospital Data Portal'), style={"margin":'1rem'})
        ]),
        dbc.CardBody([
            dbc.Row([
                dbc.Label("Username:", width=3),
                dbc.Col(dbc.Input(id='login-username-page')),
            ]),
            dbc.Row([
                dbc.Label("Password:", width=3),
                dbc.Col(dbc.Input(type='password', id='login-password-page')),
            ]),
        ]),
        dbc.CardFooter([
            dbc.Row([
                dbc.Button(
                    "Log In", id="login-submit-page", className="ms-auto", n_clicks=0, href='/'
                ),
            ], justify='end'),
        ]),
    ],style={"max-width":"1000px",'margin':'auto','margin-top':'3rem'}),
])

@app.callback(
    Output('login-page-status', "children"),
    Input("login-submit-page", "n_clicks"),
    State('login-username-page', "value"),
    State('login-password-page', "value"),
)
def login_user_callback(n1, username, password):
    if n1:
        try:
            user = load_user(username)
            if check_password_hash(user.password, password):
                login_user(user)
                return None
            else:
                return 'Wrong username or password. Please Try again.'
        except Exception as e:
            print(e)
            return 'Wrong username or password. Please Try again.'

    return dash.no_update


# ---------------------------------------------------------------------------------------------------------------------
# Flask-login
# ---------------------------------------------------------------------------------------------------------------------

# Setup the LoginManager for the server
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = '/login'

# Create User class with UserMixin
class User(UserMixin):
    def __init__(self, username, access_level, password):
        self.username = username
        self.access_level = access_level
        self.password = password
        self.authenticated = False

    def get_id(self):
        return (self.username)

# callback to reload the user object
@login_manager.user_loader
def load_user(username):
    try:
        conn = sqlite3.connect('assets/hospital_database.db')
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT * FROM login  WHERE (user_id = '{username}');")
        lu = cursor.fetchone()
        if lu is None:
            return None
        else:
            return User(lu[0], lu[1], lu[2])
    except Exception as e:
        print(e)
        return None
