import dash
import pandas as pd
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from app import app, server
from flask_login import LoginManager, current_user
from methods.User import User
import sqlite3

from apps.home import get_appointments_patients_merged

# https://stackoverflow.com/questions/49456158/integer-in-python-pandas-becomes-blob-binary-in-sqlite
from datetime import datetime, timedelta, time, timezone
import numpy as np
import pytz
sqlite3.register_adapter(np.int64, lambda val: int(val))
sqlite3.register_adapter(np.int32, lambda val: int(val))
sgt = pytz.timezone('Asia/Singapore')

layout = html.Div([
    html.H5("Appointments Screener"),
    dbc.Spinner([
        html.Div(
        dbc.Row([
            dbc.Row([
                dbc.Col([dbc.Row(dbc.Label('Appointment ID')),
                         dbc.Row(dcc.Dropdown(placeholder='Appointment ID', multi=True)),
                         ]),
                dbc.Col([dbc.Row(dbc.Label('Patient ID')),
                         dbc.Row(dcc.Dropdown(placeholder='Patient ID', multi=True)),
                         ]),
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Row(dbc.Label('Registered Date')),
                    dbc.Row([dcc.DatePickerRange()])
                ]),
                dbc.Col([
                    dbc.Row(dbc.Label('Appointment Date')),
                    dbc.Row([dcc.DatePickerRange()])
                ]),
            ], style={"margin-top": '1rem'}),
            dbc.Col(dbc.Button("Update Results", id="update-appointments-screener",
                               className="ms-auto", n_clicks=0,
                               style={"margin": '1rem', 'float': 'right'}
                               ))
        ])
    ),
    html.Hr(),
        dash_table.DataTable(
            style_table={'overflowX': 'auto','height': 300},
            style_cell={'font-family': 'Arial','minWidth': 95, 'width': 95, 'maxWidth': 95},
            id='appointments-data-table',
            virtualization=True,
            fixed_rows={'headers': True},
        )
    ], fullscreen=False, color='#0D6EFD')

])

# Todo: Callbacks to update filter options
# Todo: Callbacks to Link filters to datatable
# Todo: Enable editing of Future Appointments

@app.callback(Output('appointments-data-table','data'),
              Output('appointments-data-table','columns'),
              Input("update-appointments-screener",'n_clicks')
              )
def render_table(n1):
    conn = sqlite3.connect('assets/hospital_database.db')

    date_now = datetime.now(sgt).replace(tzinfo=timezone.utc)
    selected_date = pd.to_datetime('2014-01-08 00:00:00+00:00')

    appointments = get_appointments_patients_merged(selected_date, conn)
    data=appointments.to_dict('records')
    columns = [{"name": i, "id": i} for i in appointments.columns]
    return data, columns




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
