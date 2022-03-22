import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from app import app, server
from flask_login import logout_user, current_user, UserMixin, LoginManager, login_user
from apps import login, no_such_page, home
import sqlite3

server = server # required for deployment

navbar = html.Div([
    dbc.Row([
        dbc.Col(dbc.Button('XYZ Hospital', className='navbar-btns', href='/home', style={'float': 'left'}), ),
        dbc.Col([
            dbc.Button('Log In', className='navbar-btns', id='login-btn', style={'float': 'right'}, href='/login'),
            dbc.Button('Log Out', className='navbar-btns', id="logout-user", style={'display': 'none'}, href='/logout'),
            dbc.DropdownMenu([dbc.DropdownMenuItem('Patient Screener', href='/patients'),
                              dbc.DropdownMenuItem('Appointment Screener', href='/appointments'),
                              dbc.DropdownMenuItem('ML Model', href='/machine-learning'),
                              ], className='navbar-btns', label='More', style={'display': 'none'},id='navbar-dropdown-menu'),
        ]),
    ], justify="between",
    ),
], className='navbar-custom')

footer = html.Div([
    dbc.Alert('Footer')
], style={"margin-top": "3rem"})

app.layout = html.Div([
    dcc.Location(id="url"),
    navbar,
    html.Div(id='page-output', style={'margin': '1rem'}),
    html.Div(id='login-page-status', style={'margin': 'auto','margin-top':'1rem'}),
    footer,
])

@app.callback(Output('page-output', 'children'),
              Input('url', 'pathname'),
              Input('login-page-status', 'children'),
              )
def render_content(url, login_trigger):
    if url in ['/', '/home','/login']:
        try:
            if current_user.is_authenticated:
                return home.layout
            else:
                return login.layout
        except:
            return login.layout

    elif url in ['/success']:
        if current_user.is_authenticated:
            return home.layout
        else:
            return login.layout
    elif url in ['/logout']:
        if current_user.is_authenticated:
            logout_user()
            return login.layout
        else:
            return login.layout
    else:
        return no_such_page.layout

@app.callback(
    Output('login-btn', 'style'),
    Output('login-btn', 'disabled'),
    Output('navbar-dropdown-menu', 'style'),
    Output('logout-user', 'children'),
    Output('logout-user', 'style'),
    Output('logout-user', 'disabled'),
    Input('page-output', 'children')
)
def login_user_modl(n1):
    if current_user.is_authenticated:
        new_btn_label = html.Div("Log out " + current_user.username)
        return {'display': 'none'}, True,{'float': 'right'}, new_btn_label, {'float': 'right'}, False
    else:
        return {'float': 'right'}, False,{'display': 'none'}, None, {'display': 'none'}, True


# ---------------------------------------------------------------------------------------------------------------------
# Flask-login
# References:
# https://dev.to/naderelshehabi/securing-plotly-dash-using-flask-login-4ia2
# https://github.com/RafaelMiquelino/dash-flask-login
# https://flask-login.readthedocs.io/en/latest/
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
# ---------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=False)
