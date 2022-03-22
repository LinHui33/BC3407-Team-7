import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta, time, timezone
from app import app
import sqlite3
import numpy as np
import pytz

# https://stackoverflow.com/questions/49456158/integer-in-python-pandas-becomes-blob-binary-in-sqlite
sqlite3.register_adapter(np.int64, lambda val: int(val))
sqlite3.register_adapter(np.int32, lambda val: int(val))
sgt = pytz.timezone('Asia/Singapore')

create_appointment = html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("New Appointment")),
                dbc.ModalBody([
                    dbc.Form([
                        dbc.Row([
                            dbc.Label('Select User ID', width=5),
                            dbc.Col(dcc.Dropdown(id='create-appointment-user-selection', ), width=5),
                        ], className="mb-3"),
                        dbc.Row([
                            dbc.Label('Appointment Date', width=5),
                            dbc.Col(dcc.DatePickerSingle(id='appointment-date-selection'), width=5),
                        ], className="mb-3"),
                        dbc.Row([
                            dbc.Label('Select Timeslot', width=5),
                            dbc.Col(dcc.Dropdown(options=[{'label': x, 'value': x} for x in
                                                          [time(t, m, 0, 0).strftime("%H:%M") for t in
                                                           range(time(8, 0, 0, 0).hour, time(18, 0, 0, 0).hour) for m in
                                                           [0, 30]]
                                                          ],
                                                 id='create-appointment-timeslot-selection'), width=5),
                        ], className="mb-3"),

                    ])
                ]),
                dbc.ModalFooter([
                    dbc.Row([
                        dbc.Col([
                            dbc.Button(
                                "Close", id="create-appointment-close", className="ms-auto", n_clicks=0,
                                style={"margin-right": '0.5rem'}, color='secondary',
                            ),
                            dbc.Button(
                                "Submit", id="create-appointment-submit", className="ms-auto", n_clicks=0,
                                style={"margin-right": '0.5rem'}
                            ),
                        ])
                    ], justify='end')

                ]),
            ],
            id="create-appointment-modal",
            is_open=False,
        ),
    ]
)
create_patient = html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("New Patient")),
                dbc.ModalBody([
                    dbc.Form([
                                 dbc.Row([
                                     dbc.Label('New User ID', width=5),
                                     dbc.Col(dbc.Input(id='create-patient-user-id', disabled=True), width=5),
                                 ], className="mb-3"),
                                 dbc.Row([
                                     dbc.Label('Age', width=5),
                                     dbc.Col(dbc.Input(type='number', id='create-patient-age', min=0, max=150),
                                             width=5),
                                 ], className="mb-3"),
                                 dbc.Row([
                                     dbc.Label('Select Gender', width=5),
                                     dbc.Col(dcc.Dropdown(options=[{'label': y, 'value': x} for x, y in
                                                                   zip([0, 1], ['Male', 'Female'])
                                                                   ],
                                                          id='create-patient-gender', ), width=5),
                                 ], className="mb-3"),
                             ] + [dbc.Row([
                        dbc.Label(x, width=5),
                        dbc.Col(dcc.Dropdown(options=[{'label': y, 'value': x} for x, y in
                                                      zip([0, 1], ['No', 'Yes'])
                                                      ],
                                             id=f'create-patient-{x}', ), width=5),
                    ], className="mb-3") for x in
                                 ['Diabetes', 'Drinks', 'HyperTension', 'Handicap', 'Smoker', 'Scholarship',
                                  'Tuberculosis']
                             ])
                ]),
                html.Div(id='create-patient-status'),
                dbc.ModalFooter([
                    dbc.Row([
                        dbc.Col([
                            dbc.Button(
                                "Close", id="create-patient-close", className="ms-auto", n_clicks=0,
                                style={"margin-right": '0.5rem'}, color='secondary',
                            ),
                            dbc.Button(
                                "Submit", id="create-patient-submit", className="ms-auto", n_clicks=0,
                                style={"margin-right": '0.5rem'}
                            ),
                        ])
                    ], justify='end')

                ]),

            ],
            id="create-patient-modal",
            is_open=False,
        ),
    ]
)

layout = html.Div([
    html.H3(["Welcome to the data portal"], id='home-header'),
    dbc.Spinner([
        html.Div(' ', id='home-header-status', className='mb-3'),
        create_appointment, create_patient,
        html.Div([
            dbc.Button('Create Appointment', id='create-appointment-open',
                       style={'margin': '0.5rem'}),
            dbc.Button('Create Patient', id='create-patient-open',
                       style={'margin': '0.5rem'}),
        ], style={"text-align": 'right'}),
        dcc.Graph(id='home-gantt-schedule'),
    ], id='home-loading', fullscreen=False, color='#0D6EFD'),
    # dcc.Loading([
    dbc.Row([
        dbc.Col(html.H5('Click on the schedule above to filter appointments'), ),
        dbc.Col(dbc.Button('Reset Filtering', id='reset-home-appointment-information',
                           style={'margin': '0.5rem', "float": "right"}), ),
        # ]),
    ]),
    dbc.Spinner(html.Div(id='home-appointment-information'), fullscreen=False, color='#0D6EFD'),

    # dcc.Interval(n_intervals=1000,id='refresh-home')
], id='home-page')


def get_appointments_users_merged(date_now, conn):
    if date_now == 'all':
        appointments = pd.read_sql('SELECT * FROM appointments left join users using (user_id);',
                                   conn,
                                   )
        return appointments
    else:
        date = f"'{date_now.replace(tzinfo=timezone.utc).date().strftime('%Y-%m-%d %H:%M:%S%z')}'"

        appointments = pd.read_sql(
            f"SELECT * FROM appointments left join users using (user_id) where Date(Appointment) = date({date});",
            conn,
        )
        # appointments['Appointment'] = pd.to_datetime(appointments['Appointment'])
        # appointments_today = appointments[appointments['Appointment'].dt.date == date_now]
        return appointments


@app.callback(Output('home-header-status', 'children'),
              Output('appointment-date-selection', 'min_date_allowed'),
              Output('appointment-date-selection', 'initial_visible_month'),
              Output('appointment-date-selection', 'date'),
              Output('home-gantt-schedule', 'figure'),
              Input('home-loading', 'children'),
              )
def render_home(dummy):
    date_now = datetime.now(sgt).replace(tzinfo=timezone.utc)
    conn = sqlite3.connect('assets/hospital_database.db')
    appointments_today = get_appointments_users_merged(date_now, conn)

    appt_count_today = len(appointments_today)
    message = f"There {'is' if appt_count_today == 1 else 'are'} {appt_count_today if appt_count_today > 0 else 'no'} appointment{'' if appt_count_today == 1 else 's'} for today. "
    message = html.Div([message, 'To view all appointments, please go to the ',
                        html.A("Appointments Screener", href='/appointments', target='_blank'), '.'])

    min_date_allowed = datetime(date_now.year, date_now.month, date_now.day)
    initial_visible_month = date_now
    date = date_now

    appointments_today['Start'] = appointments_today['Appointment']
    appointments_today['End'] = pd.to_datetime(appointments_today['Start']) + timedelta(minutes=30)

    # TODO: Add in predictions to appointments_today

    if appt_count_today > 0:
        fig = px.timeline(appointments_today,
                          x_start='Start',
                          x_end='End',
                          y='appointment_id',
                          color="Show Up",
                          # hover_name="",
                          hover_data=['user_id', "appointment_id", "Start", "End", 'Show Up'],
                          )
        fig.update_layout(yaxis={'visible': False, 'showticklabels': False},
                          paper_bgcolor='#FFFFFF',
                          plot_bgcolor='#FFFFFF',
                          title=f'Appointments for {date_now.strftime("%A %-d %b %Y")}'
                          )
        fig.add_vrect(x0=date_now, x1=date_now,
                      annotation_text="  " + date_now.strftime("%H:%M"), annotation_position="outside top right",
                      fillcolor="green", opacity=1, line_width=1)
    else:
        fig = go.Figure()
        fig.update_layout(yaxis={'visible': False, 'showticklabels': False},
                          paper_bgcolor='#FFFFFF',
                          plot_bgcolor='#FFFFFF',
                          title=f'No Appointments for {date_now.strftime("%A %-d %b %Y")}'
                          )
        fig.add_annotation(x=2.5, y=2.5, text="Select 'Create Appointment' to start booking appointments.",
                           showarrow=False)
        fig.update_yaxes(fixedrange=True)
        fig.update_xaxes(fixedrange=True)

    return message, min_date_allowed, initial_visible_month, date, fig


@app.callback(Output('home-appointment-information', 'children'),
              Input('home-gantt-schedule', 'clickData'),
              Input('reset-home-appointment-information', 'n_clicks')
              )
def render_table(clickData, n1):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    date_now = datetime.now(sgt).replace(tzinfo=timezone.utc)
    conn = sqlite3.connect('assets/hospital_database.db')
    appointments_today = get_appointments_users_merged(date_now, conn)

    if (clickData is not None) and ('reset-home-appointment-information' not in changed_id):
        clicked_id = clickData['points'][0]['y']
        appointments_today = appointments_today[appointments_today['appointment_id'] == clicked_id]

    table = dash_table.DataTable(
        data=appointments_today.to_dict('records'),
        columns=[{"name": i, "id": i} for i in appointments_today.columns],
        style_table={'overflowX': 'auto'},
        style_cell={'font-family': 'Arial'},
    )
    return table


for modal in ['appointment', 'patient']:
    @app.callback(
        Output(f"create-{modal}-modal", "is_open"),
        [Input(f'create-{modal}-open', "n_clicks"), Input(f"create-{modal}-close", "n_clicks")],
        [State(f"create-{modal}-modal", "is_open")],
    )
    def toggle_modal(n1, n2, is_open):
        if n1 or n2:
            return not is_open
        return is_open


@app.callback(
    Output('home-page', 'children'),
    Input('create-appointment-submit', "n_clicks"),
    State('create-appointment-user-selection', 'value'),
    State("appointment-date-selection", "date"),
    State("create-appointment-timeslot-selection", "value"),
)
def toggle_modal(n1, user_id, appt_date, timeslot_selected):
    if None in [user_id, appt_date, timeslot_selected]:
        return dash.no_update
    else:
        date_now = datetime.now(sgt).replace(tzinfo=timezone.utc)
        conn = sqlite3.connect('assets/hospital_database.db')
        c = conn.cursor()
        hour_selected = int(timeslot_selected.split(":")[0])
        minute_selected = int(timeslot_selected.split(":")[1])

        appointment_id = int(pd.read_sql('SELECT MAX(appointment_id) FROM appointments;', conn, ).iat[0, 0]) + 1
        user_id = int(user_id)
        registered_date = date_now.isoformat().replace("T", " ")
        appointment_date = pd.to_datetime(appt_date)
        appointment_date = pd.to_datetime(
            datetime(appointment_date.year, appointment_date.month, appointment_date.day) + timedelta(
                hours=hour_selected, minutes=minute_selected)).replace(tzinfo=timezone.utc)
        day = str(appointment_date.day)
        sms_reminder = str(0)
        waiting_time = (appointment_date - date_now).days
        show_up = str(0)
        appointment_month = str(appointment_date.month)
        appointment_week_number = str(appointment_date.week)
        appointment_date = datetime(appointment_date.year, appointment_date.month, appointment_date.day) + timedelta(
            hours=hour_selected, minutes=minute_selected)
        appointment_date = appointment_date.replace(tzinfo=timezone.utc).isoformat().replace("T", " ")

        # TODO: Add in predictions? Any use for admin to know if user will show up or not before submitting?

        cols = (
            "appointment_id", "user_id", "Register Time", "Appointment", "Day", "Sms_Reminder", "Waiting Time",
            "Show Up",
            "Appointment Month", "Appointment Week Number")
        data_tuple = (
            appointment_id, user_id, registered_date, appointment_date, day, sms_reminder, waiting_time, show_up,
            appointment_month, appointment_week_number)

        sql = f'INSERT INTO appointments {cols} VALUES (?,?,?,?,?,?,?,?,?,?)'
        c.execute(sql, data_tuple)
        conn.commit()

        return home_layout


@app.callback(
    Output('create-patient-status', 'children'),
    Output('create-patient-user-id', 'value'),
    Output('create-appointment-user-selection', 'options'),
    Input('create-patient-submit', "n_clicks"),
    State('create-patient-age', 'value'),
    State('create-patient-gender', 'value'),
    [State(f'create-patient-{x}', 'value') for x in
     ['Diabetes', 'Drinks', 'HyperTension', 'Handicap', 'Smoker', 'Scholarship', 'Tuberculosis']]
)
def add_user(n1, age, gender, diabetes, drinks, hypertension, handicap, smoker, scholarship, tuberculosis):
    conn = sqlite3.connect('assets/hospital_database.db')
    c = conn.cursor()
    users = pd.read_sql('SELECT * FROM users;', conn)
    user_options = [{'label': x, 'value': x} for x in users['user_id'].unique()]
    user_id = int(max(users['user_id'].unique()) + 1)
    data_tuple = (user_id, age, gender, diabetes, drinks, hypertension, handicap, smoker, scholarship, tuberculosis)
    if n1:
        try:
            if None not in data_tuple:
                # date_now = datetime.now(sgt).replace(tzinfo=timezone.utc)
                sql = f'INSERT INTO users VALUES (?,?,?,?,?,?,?,?,?,?)'
                c.execute(sql, data_tuple)
                conn.commit()
                return dbc.Alert(
                    f"New patient {user_id} successfully added to database."), user_id + 1, user_options + [
                           {'label': x, 'value': x} for x in [user_id]]
            else:
                return dbc.Alert(f"Error. Please try again.", color='warning'), dash.no_update, dash.no_update
        except:
            return dbc.Alert(f"Error. Please try again.", color='warning'), dash.no_update, dash.no_update
    else:
        return dash.no_update, user_id, user_options
