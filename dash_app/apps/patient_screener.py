import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from app import app, server
from flask_login import current_user
from methods.User import User
import sqlite3
import pandas as pd

edit_patients_modal = []

empty_table = pd.DataFrame(columns=[''])
layout = html.Div([
    html.H5("Patients Screener"),
    html.Div(
        "Only the latest 30 patients registered are shown by default. Max allowable records to be returned per query is 500.",
        style={'margin-bottom': '1rem'}),
    html.Div(
        dbc.Row([
            dbc.Row([
                dbc.Col(
                    [dbc.Row([html.Div([dbc.Label('Patient ID', style={'float': 'left', 'margin-right': '1rem'}),

                                        ])
                              ]),
                     dbc.Row(dbc.Spinner(dcc.Dropdown(placeholder='Patient ID', multi=True,
                                                      id='update-patients-patient-id',
                                                      style={'zIndex': '1'}
                                                      ), fullscreen=False, color='#0D6EFD')),
                     ]),
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Row([html.Div([dbc.Label('Registered Date', style={'float': 'left', 'margin-right': '1rem'}),
                                       ])
                             ]),
                    dbc.Row([dbc.Spinner(dcc.DatePickerRange(id='update-patients-registered-date',
                                                             clearable=True,
                                                             style={'zIndex': '1'}), fullscreen=False,
                                         color='#0D6EFD')])
                ]),
            ], style={"margin-top": '1rem'}),
            dbc.Col([dbc.Button("Query Results", id="update-patients-screener",
                                className="ms-auto", n_clicks=0,
                                style={"margin": '1rem', 'float': 'right'}
                                ),
                     dbc.Button("Edit Patients", id="edit-patients-open",
                                className="ms-auto", n_clicks=0,
                                style={"margin": '1rem', 'float': 'right'}
                                ),
                     edit_patients_modal
                     ]),
        ])
    ),
    html.Hr(),
    dbc.Spinner([
        dash_table.DataTable(
            style_table={'overflowX': 'auto', 'height': 300, 'zIndex': '0'},
            style_cell={'font-family': 'Arial', 'minWidth': 95, 'width': 95, 'maxWidth': 95},
            id='patients-data-table',
            virtualization=True,
            fixed_rows={'headers': True},
            filter_action='native',
            sort_action='native',
            row_selectable='single', #requires empty data for intialization
            data = empty_table.to_dict('records'),
            columns = [{"name": i, "id": i} for i in empty_table.columns],
        )
    ], fullscreen=False, color='#0D6EFD')

], id='patients-layout')

@app.callback(Output("update-patients-patient-id", 'options'),
              Input('patients-layout', 'children'),
              )
def render_options(page_load):
    conn = sqlite3.connect('assets/hospital_database.db')
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT DISTINCT(patient_id) FROM patients;")
    all_patients = [x for x in list(sorted(cursor.fetchall()))]
    all_patients = [{'label': x[0], 'value': x[0]} for x in all_patients]
    return all_patients


@app.callback(Output("update-patients-registered-date", 'max_date_allowed'),
              Output("update-patients-registered-date", 'min_date_allowed'),
              Input('patients-layout', 'children'),
              )
def render_options(page_load):
    conn = sqlite3.connect('assets/hospital_database.db')
    cursor = conn.cursor()

    cursor.execute(
        f"""SELECT MAX("first_appt") FROM patients;""")
    max_register_time = cursor.fetchone()[0]

    cursor.execute(
        f"""SELECT MIN("first_appt") FROM patients;""")
    min_register_time = cursor.fetchone()[0]

    return max_register_time, min_register_time


@app.callback(Output('patients-data-table', 'data'),
              Output('patients-data-table', 'columns'),
              Input("update-patients-screener", 'n_clicks'),
              State("update-patients-patient-id", 'value'),
              State("update-patients-registered-date", 'start_date'),
              State("update-patients-registered-date", 'end_date'),
              )
def render_table(n1, patient_id, registered_date_start,registered_date_end):
    conn = sqlite3.connect('assets/hospital_database.db')
    if n1:
        basic_sql = f'SELECT * FROM patients WHERE TRUE'

        condition2 = patient_id not in [None, []]
        condition5 = registered_date_start is not None
        condition6 = registered_date_end is not None

        if condition2:
            patient_id_edited = tuple(patient_id) if len(patient_id) > 1 else str(tuple(patient_id)).replace(',', '')
            basic_sql += f' AND patient_id IN {patient_id_edited}'

        if condition5:
            registered_date_start = pd.to_datetime(registered_date_start).tz_localize('UTC').tz_convert(
                'Asia/Singapore')
            basic_sql += f' AND "first_appt" >= "{registered_date_start}"'

        if condition6:
            registered_date_end = pd.to_datetime(registered_date_end).tz_localize('UTC').tz_convert(
                'Asia/Singapore')
            basic_sql += f' AND "first_appt" <= "{registered_date_end}"'

        basic_sql += ' LIMIT 500;'
    else:
        basic_sql = f'SELECT * FROM patients ORDER BY first_appt DESC LIMIT 30;'

    print(basic_sql)
    c = conn.cursor()

    query = c.execute(basic_sql)
    cols = [column[0] for column in query.description]
    patients = pd.DataFrame(c.fetchall())

    try:
        patients.columns = cols
    except:
        data = None

    if len(patients.index) > 0:
        data = patients.to_dict('records')
        columns = [{"name": i, "id": i} for i in patients.columns]

    else:
        data = empty_table.to_dict('records')
        columns =  [{"name": i, "id": i} for i in empty_table.columns]

    return data, columns

