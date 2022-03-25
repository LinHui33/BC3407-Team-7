import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from app import app, server
from flask_login import logout_user, current_user, LoginManager, login_user
from methods.User import User
from apps import login, no_such_page, home, patient_screener, appointments, dashboard, manage_users, ml
import sqlite3

server = server  # required for deployment

navbar = html.Div([
    dbc.Row([
        dbc.Col(dbc.Button('XYZ Hospital', className='navbar-btns', href='/home', style={'float': 'left'}), ),
        dbc.Col([
            dbc.Button('Log In', className='navbar-btns', id='login-btn', style={'float': 'right'}, href='/login'),
            dbc.Button('Log Out', className='navbar-btns', id="logout-user", style={'display': 'none'}, href='/logout'),
            dbc.DropdownMenu([dbc.DropdownMenuItem('Dashboard', href='/dashboard', id='navbar-menu-dashboard'),
                              dbc.DropdownMenuItem('Patient Screener', href='/patients'),
                              dbc.DropdownMenuItem('Appointment Screener', href='/appointments'),
                              dbc.DropdownMenuItem('ML Model Performance', href='/ml', id='navbar-menu-ml',
                                                   style={"display": "none"}),
                              dbc.DropdownMenuItem('Manage Users', href='/manage-users', id='navbar-menu-manage-users',
                                                   style={"display": "none"}),
                              ], className='navbar-btns', label='More', style={'display': 'none'},
                             id='navbar-dropdown-menu'),
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
    html.Div(id='login-page-status', style={'margin': 'auto', 'margin-top': '1rem'}),
    footer,
])


@app.callback(Output('page-output', 'children'),
              Input('url', 'pathname'),
              Input('login-page-status', 'children'),
              )
def render_content(url, login_trigger):
    if url in ['/', '/home', '/login']:
        try:
            if current_user.is_authenticated:
                return home.layout
            else:
                return login.layout
        except:
            return login.layout
    elif url in ['/dashboard']:
        try:
            if current_user.is_authenticated:
                if (current_user.get_access_level() == 0):
                    return dashboard.layout
                else:
                    return no_such_page.layout
            else:
                return login.layout
        except:
            return login.layout
    elif url in ['/patients']:
        try:
            if current_user.is_authenticated:
                return patient_screener.layout
            else:
                return login.layout
        except:
            return login.layout
    elif url in ['/appointments']:
        try:
            if current_user.is_authenticated:
                return appointments.layout
            else:
                return login.layout
        except:
            return login.layout
    elif url in ['/manage-users']:
        try:
            if (current_user.is_authenticated):
                if (current_user.get_access_level() == 0):
                    return manage_users.layout
                else:
                    return no_such_page.layout
            else:
                return login.layout
        except:
            return login.layout
    elif url in ['/ml']:
        try:
            if (current_user.is_authenticated):
                if (current_user.get_access_level() == 0):
                    return ml.layout
                else:
                    return no_such_page.layout
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
    Output('navbar-menu-ml', 'style'),
    Output('navbar-menu-manage-users', 'style'),
    Output('navbar-menu-dashboard', 'style'),
    Input('page-output', 'children')
)
def render_navbar(n1):
    if current_user.is_authenticated:
        new_btn_label = html.Div("Log out " + current_user.username)
        if current_user.get_access_level() == 0:
            return {'display': 'none'}, True, {'float': 'right'}, new_btn_label, {'float': 'right'}, False, {
                "display": "block"}, {"display": "block"}, {'display': 'block'}
        else:
            return {'display': 'none'}, True, {'float': 'right'}, new_btn_label, {'float': 'right'}, False, {
                "display": "none"}, {"display": "none"}, {'display': 'none'}
    else:
        return {'float': 'right'}, False, {'display': 'none'}, None, {'display': 'none'}, True, {"display": "block"}, {
            "display": "block"}, {"display": "block"}


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


# ---------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=False)
