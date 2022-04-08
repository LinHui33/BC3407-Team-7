import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from app import app, server
from flask_login import current_user
from methods.User import User
import sqlite3
import pandas as pd

edit_patients_modal = html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Edit Patient")),
                dbc.ModalBody([
                    dbc.Form([
                                 dbc.Row([
                                     dbc.Label('Selected Patient ID', width=5),
                                     dbc.Col(dbc.Input(id='edit-patients-patient-selection', disabled=True), width=5),
                                 ], className="mb-3"),
                             ] + [dbc.Row([dbc.Label(x, width=5),
                                           dbc.Col(dbc.Input(id=f'patient-{x}-selected', type='number', min=0, max=250,
                                                             step=1), width=5)])
                                  for x in ['Age']
                                  ] + [dbc.Row([dbc.Label(x, width=5),
                                                dbc.Col(dcc.Dropdown(clearable=False,
                                                                     id=f'patient-{x}-selected',
                                                                     options=[{'label': x, 'value': y} for x, y in
                                                                              zip(['Male', 'Female'], [1, 0])]),
                                                        width=5)])
                                       for x in ['Gender']
                                       ] + [dbc.Row([dbc.Label(x, width=5),
                                                     dbc.Col(dcc.Dropdown(clearable=False,
                                                                          id=f'patient-{x}-selected',
                                                                          options=[{'label': x, 'value': y} for x, y in
                                                                                   zip(['Yes', 'No'], [1, 0])]),
                                                             width=5)])
                                            for x in ['Diabetes',
                                                      'Drinks', 'HyperTension', 'Handicap',
                                                      'Smoker', 'Scholarship', 'Tuberculosis']
                                            ]
                             ),
                ]),
                html.Div(id='edit-patients-status', style={"display": "block"}),
                dbc.ModalFooter([
                    dbc.Row([
                        dbc.Col([
                            dbc.Button(
                                "Close", id="edit-patients-close", className="ms-auto", n_clicks=0,
                                style={"margin-right": '0.5rem'}, color='secondary',
                            ),
                            dbc.Button(
                                "Submit Changes", id="edit-patients-submit", className="ms-auto", n_clicks=0,
                                style={"margin-right": '0.5rem'}
                            ),
                        ])
                    ], justify='end'),
                ]),
            ],
            id="edit-patients-modal",
            # style={'zIndex': '1'},
            is_open=False,
        ),
    ]
)


@app.callback(Output('edit-patients-patient-selection', 'value'),
              [Output(f'patient-{x}-selected', 'value') for x in
               ['Age', 'Gender', 'Diabetes', 'Drinks', 'HyperTension', 'Handicap', 'Smoker', 'Scholarship',
                'Tuberculosis']],
              Input('edit-patients-open', 'n_clicks'),
              State('patients-data-table', 'selected_rows'),
              State('patients-data-table', 'data'),
              )
def render_selected_patient(n1, row, data):
    if n1:
        existing_data = pd.DataFrame(data).drop(['First Appointment'], axis=1)
        data = existing_data.iloc[row[0], :].values.tolist()
        if data[2] == 'Male':
            gender = '1'
        else:
            gender = '0'
        traits = ['1' if x == 'Yes' else '0' for x in data[3:]]
        results = data[0:2] + [gender] + traits
        return tuple(results)
    else:
        return dash.no_update


@app.callback(
    Output(f"edit-patients-modal", "is_open"),
    [Input(f"edit-patients-open", "n_clicks"), Input(f"edit-patients-close", "n_clicks")],
    [State(f"edit-patients-modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


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
                     dbc.Button("Edit Patient", id="edit-patients-open",
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
            style_cell={'font-family': 'Arial', 'minWidth': 150, 'width': 150, 'maxWidth': 150, 'textAlign': 'center'},
            id='patients-data-table',
            virtualization=True,
            fixed_rows={'headers': True},
            filter_action='native',
            sort_action='native',
            row_selectable='single',  # requires empty data for intialization
            data=empty_table.to_dict('records'),
            columns=[{"name": i, "id": i} for i in empty_table.columns],
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
              Output('edit-patients-status', 'children'),

              Input("update-patients-screener", 'n_clicks'),
              Input('edit-patients-submit', 'n_clicks'),

              State("update-patients-patient-id", 'value'),
              State("update-patients-registered-date", 'start_date'),
              State("update-patients-registered-date", 'end_date'),

              State('edit-patients-patient-selection', 'value'),
              [State(f'patient-{x}-selected', 'value') for x in
               ['Age', 'Gender', 'Diabetes', 'Drinks', 'HyperTension', 'Handicap', 'Smoker', 'Scholarship',
                'Tuberculosis']],
              )
def render_table(n1, n2, patient_id, registered_date_start, registered_date_end,
                 patient_id_edit, age_edit, gender_edit, diabetes_edit,
                 drinks_edit, hypert_edit, handicap_edit, smoker_edit, scholar_edit, tuber_edit,
                 ):
    conn = sqlite3.connect('assets/hospital_database.db')
    c = conn.cursor()

    if n2:
        try:
            sql_to_edit = f"""
    UPDATE patients
    SET 
    Age = {int(age_edit)},
    Gender = {gender_edit},
    Diabetes = {diabetes_edit},
    Drinks = {drinks_edit},
    HyperTension = {hypert_edit},
    Handicap = {handicap_edit},
    Smoker = {smoker_edit},
    Scholarship = {scholar_edit},
    Tuberculosis = {tuber_edit}
    WHERE
    patient_id = {patient_id_edit} 
    """
            c.execute(sql_to_edit)
            conn.commit()
            update_message = dbc.Alert('Updated successfully!', color='success')

        except:
            update_message = dbc.Alert('Error updating. Please try again!', color='warning')
    else:
        update_message = None

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

        basic_sql += ' ORDER BY patient_id DESC LIMIT 500;'
    else:
        basic_sql = f'SELECT * FROM patients ORDER BY patient_id DESC LIMIT 30;'

    print(basic_sql)

    query = c.execute(basic_sql)
    cols = [column[0] for column in query.description]
    patients = pd.DataFrame(c.fetchall())

    try:
        patients.columns = cols
    except:
        data = None

    if len(patients.index) > 0:

        patients = patients.rename(
            {'first_appt': 'First Appointment',
             'patient_id': 'Patient ID',
             }, axis=1)

        patients['First Appointment'] = pd.to_datetime(patients['First Appointment'],
                                                       format='%Y-%m-%d %H:%M:%S%z', errors='coerce').dt.strftime(
            '%Y-%m-%d %H:%M')

        patients['Gender'] = patients['Gender'].replace({"0": "Female", "1": "Male"})
        for each in ['Diabetes', 'Drinks', 'HyperTension', 'Handicap', 'Smoker', 'Scholarship', 'Tuberculosis']:
            patients[each] = patients[each].replace({"0": "No", "1": "Yes"})

        data = patients.to_dict('records')
        columns = [{"name": i, "id": i} for i in patients.columns]


    else:
        data = empty_table.to_dict('records')
        columns = [{"name": i, "id": i} for i in empty_table.columns]

    return data, columns, update_message
