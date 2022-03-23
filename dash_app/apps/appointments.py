import dash
import pandas as pd
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from app import app, server
from flask_login import LoginManager, current_user
from methods.User import User
import sqlite3

# https://stackoverflow.com/questions/49456158/integer-in-python-pandas-becomes-blob-binary-in-sqlite
from datetime import datetime, timedelta, time, timezone
import numpy as np
import pytz

sqlite3.register_adapter(np.int64, lambda val: int(val))
sqlite3.register_adapter(np.int32, lambda val: int(val))
sgt = pytz.timezone('Asia/Singapore')

edit_appointment_modal = html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Edit Appointment")), # Todo, also manage zindex better
                dbc.ModalBody([
                    dbc.Form([
                        dbc.Row([
                            dbc.Label('Select Appointment ID', width=5),
                            dbc.Col(dcc.Dropdown(id='edit-appointment-appointment-selection', ), width=5),
                        ], className="mb-3"),
                        dbc.Row([
                            dbc.Label('Edit Appointment Date', width=5),
                            dbc.Col(dcc.DatePickerSingle(id='edit-appointment-date-selection'), width=5),
                        ], className="mb-3"),
                        dbc.Row([
                            dbc.Label('Edit Timeslot', width=5),
                            dbc.Col(dcc.Dropdown(options=[{'label': x, 'value': x} for x in
                                                          [time(t, m, 0, 0).strftime("%H:%M") for t in
                                                           range(time(8, 0, 0, 0).hour, time(18, 0, 0, 0).hour) for m in
                                                           [0, 30]]
                                                          ],
                                                 id='edit-appointment-timeslot-selection'), width=5),
                        ], className="mb-3"),

                    ])
                ]),
                dbc.ModalFooter([
                    dbc.Row([
                        dbc.Col([
                            dbc.Button(
                                "Close", id="edit-appointment-close", className="ms-auto", n_clicks=0,
                                style={"margin-right": '0.5rem'}, color='secondary',
                            ),
                            dbc.Button(
                                "Submit", id="edit-appointment-submit", className="ms-auto", n_clicks=0,
                                style={"margin-right": '0.5rem'}
                            ),
                        ])
                    ], justify='end')
                ]),
            ],
            id="edit-appointment-modal",
            style={'zIndex': '10000'},
            is_open=False,
        ),
    ]
)


@app.callback(
    Output(f"edit-appointment-modal", "is_open"),
    [Input(f"edit-appointment-open", "n_clicks"), Input(f"edit-appointment-close", "n_clicks")],
    [State(f"edit-appointment-modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


layout = html.Div([
    html.H5("Appointments Screener"),
    html.Div(
        dbc.Row([
            dbc.Row([
                dbc.Col([dbc.Row(dbc.Label('Appointment ID')),
                         dbc.Row(dcc.Dropdown(placeholder='Appointment ID', multi=True,
                                              id='update-appointments-appointment-id',
                                              style={'zIndex': '1000'}
                                              )),
                         ]),
                dbc.Col([dbc.Row(dbc.Label('Patient ID')),
                         dbc.Row(
                             dcc.Dropdown(placeholder='Patient ID', multi=True, id='update-appointments-patient-id',
                                          style={'zIndex': '1000'})),
                         ]),
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Row(dbc.Label('Registered Date')),
                    dbc.Row([dcc.DatePickerRange(id='update-appointments-registered-date',
                                                 clearable=True,
                                                 style={'zIndex': '900'})])
                ]),
                dbc.Col([
                    dbc.Row(dbc.Label('Appointment Date')),
                    dbc.Row([dcc.DatePickerRange(id='update-appointments-appointment-date',
                                                 clearable=True,
                                                 style={'zIndex': '900'})])
                ]),
            ], style={"margin-top": '1rem'}),
            dbc.Col([dbc.Button("Update Results", id="update-appointments-screener",
                                className="ms-auto", n_clicks=0,
                                style={"margin": '1rem', 'float': 'right'}
                                ),
                     dbc.Button("Edit Appointments", id="edit-appointment-open",
                                className="ms-auto", n_clicks=0,
                                style={"margin": '1rem', 'float': 'right'}
                                ),
                     edit_appointment_modal
                     ]),
        ])
    ),
    html.Hr(),
    dbc.Spinner([
        dash_table.DataTable(
            style_table={'overflowX': 'auto', 'height': 300},
            style_cell={'font-family': 'Arial', 'minWidth': 95, 'width': 95, 'maxWidth': 95},
            id='appointments-data-table',
            virtualization=True,
            fixed_rows={'headers': True},
            filter_action='native',
        )
    ], fullscreen=False, color='#0D6EFD')

], id='appointments-layout')


# Todo: Enable editing of Appointments


@app.callback(Output("update-appointments-appointment-id", 'options'),
              Output("update-appointments-patient-id", 'options'),
              Output("update-appointments-registered-date", 'max_date_allowed'),
              Output("update-appointments-registered-date", 'min_date_allowed'),
              Output("update-appointments-appointment-date", 'max_date_allowed'),
              Output("update-appointments-appointment-date", 'min_date_allowed'),
              Input('appointments-layout', 'children'),
              )
def render_options(page_load):
    conn = sqlite3.connect('assets/hospital_database.db')
    cursor = conn.cursor()

    cursor.execute(
        f"SELECT DISTINCT(patient_id) FROM appointments;")
    all_patients = [x for x in list(sorted(cursor.fetchall()))]
    all_patients = [{'label': x[0], 'value': x[0]} for x in all_patients]

    cursor.execute(
        f"SELECT DISTINCT(appointment_id) FROM appointments;")
    all_appointments = [x for x in list(sorted(cursor.fetchall()))]
    all_appointments = [{'label': x[0], 'value': x[0]} for x in all_appointments]

    cursor.execute(
        f"""SELECT MAX("Register Time") FROM appointments;""")
    max_register_time = cursor.fetchone()[0]

    cursor.execute(
        f"""SELECT MIN("Register Time") FROM appointments;""")
    min_register_time = cursor.fetchone()[0]

    cursor.execute(
        f"SELECT MAX(Appointment) FROM appointments;")
    max_appt_time = cursor.fetchone()[0]

    cursor.execute(
        f"SELECT MIN(Appointment) FROM appointments;")
    min_appt_time = cursor.fetchone()[0]

    return all_patients, all_appointments, max_register_time, min_register_time, max_appt_time, min_appt_time


@app.callback(Output('appointments-data-table', 'data'),
              Output('appointments-data-table', 'columns'),
              Input("update-appointments-screener", 'n_clicks'),
              State("update-appointments-appointment-id", 'value'),
              State("update-appointments-patient-id", 'value'),
              State("update-appointments-appointment-date", 'start_date'),
              State("update-appointments-appointment-date", 'end_date'),
              State("update-appointments-registered-date", 'start_date'),
              State("update-appointments-registered-date", 'end_date'),
              )
def render_table(n1, appointment_id, patient_id, appointment_date_start, appointment_date_end, registered_date_start,
                 registered_date_end):
    conn = sqlite3.connect('assets/hospital_database.db')

    if appointment_date_start is not None:
        appointment_date_start = pd.to_datetime(appointment_date_start).tz_localize('UTC').tz_convert(
            'Asia/Singapore')

    if appointment_date_end is not None:
        appointment_date_end = pd.to_datetime(appointment_date_end).tz_localize('UTC').tz_convert(
            'Asia/Singapore')

    if registered_date_start is not None:
        registered_date_start = pd.to_datetime(registered_date_start).tz_localize('UTC').tz_convert(
            'Asia/Singapore')

    if registered_date_end is not None:
        registered_date_end = pd.to_datetime(registered_date_end).tz_localize('UTC').tz_convert(
            'Asia/Singapore')

    appointments = pd.read_sql('SELECT * FROM appointments;', conn)

    appointments.loc[:, 'Register Time'] = pd.to_datetime(appointments['Register Time'])
    appointments.loc[:, 'Appointment'] = pd.to_datetime(appointments['Appointment'])

    # test = pd.to_datetime('2014-01-03 00:00:00+00:00').tz_convert('Asia/Singapore')
    # print( appointments.loc[appointments['Register Time']<=test,:])

    try:
        if appointment_id not in [None, []]:
            appointments = appointments.loc[appointments['appointment_id'].isin(appointment_id), :]
    except:
        pass
    try:
        if patient_id not in [None, []]:
            appointments = appointments.loc[appointments['patient_id'].isin(patient_id), :]
    except:
        pass
    try:
        appointments = appointments.loc[appointments['Appointment'] >= appointment_date_start, :]
    except:
        pass
    try:
        appointments = appointments.loc[appointments['Appointment'] <= appointment_date_end, :]
    except:
        pass

    try:
        appointments = appointments.loc[appointments['Register Time'] >= registered_date_start, :]
    except:
        pass

    try:
        appointments = appointments.loc[appointments['Register Time'] <= registered_date_end, :]
    except:
        pass

    if len(appointments.index) > 0:
        data = appointments.to_dict('records')
        columns = [{"name": i, "id": i} for i in appointments.columns]
    else:
        data = None
        columns = None
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
