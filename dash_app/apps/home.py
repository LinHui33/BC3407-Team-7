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
from methods.machine_learning import predict_no_show

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 20)
pd.set_option('display.width', 300)
pd.set_option('max_colwidth', 20)

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
                            dbc.Label('Select Patient ID', width=5),
                            dbc.Col(dcc.Dropdown(id='create-appointment-patient-selection', ), width=5),
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
                                     dbc.Label('New Patient ID', width=5),
                                     dbc.Col(dbc.Input(id='create-patient-patient-id', disabled=True), width=5),
                                 ], className="mb-3"),
                                 dbc.Row([
                                     dbc.Label('Age', width=5),
                                     dbc.Col(dbc.Input(type='number', id='create-patient-age', min=0, max=250, value=30,
                                                       step=1),
                                             width=5),
                                 ], className="mb-3"),
                                 dbc.Row([
                                     dbc.Label('Select Gender', width=5),
                                     dbc.Col(dcc.Dropdown(options=[{'label': y, 'value': x} for x, y in
                                                                   zip([0, 1], ['Male', 'Female'])
                                                                   ],
                                                          value=1,
                                                          clearable=False,
                                                          id='create-patient-gender', ), width=5),
                                 ], className="mb-3"),
                             ] + [dbc.Row([
                        dbc.Label(x, width=5),
                        dbc.Col(dcc.Dropdown(options=[{'label': y, 'value': x} for x, y in
                                                      zip([0, 1], ['No', 'Yes'])
                                                      ],
                                             value=0,
                                             clearable=False,
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
    dbc.Row([html.Div(['To view all appointments, please go to the ',
                       html.A("Appointments Screener", href='/appointments', target='_blank'), '.'])]),
    dbc.Row([
        dbc.Spinner(html.Div(style={'margin': "1rem"}, id='insight-home')
                    , fullscreen=False, color='#0D6EFD'),
    ]),
    dbc.Spinner([
        create_appointment, create_patient,
        html.Div([
            dbc.Button('Create Appointment', id='create-appointment-open',
                       style={'margin': '0.5rem'}),
            dbc.Button('Create Patient', id='create-patient-open',
                       style={'margin': '0.5rem'}),
        ], style={"text-align": 'right'}),
        dcc.Graph(id='home-gantt-schedule'),
    ], id='home-loading', fullscreen=False, color='#0D6EFD'),

    dbc.Row([
        dbc.Col(html.H5('Click on the schedule above to filter appointments'), ),
        dbc.Col(dbc.Button('Reset Filtering', id='reset-home-appointment-information',
                           style={'margin': '0.5rem', "float": "right"}), ),
    ]),
    dbc.Spinner(html.Div(id='home-appointment-information'), fullscreen=False, color='#0D6EFD'),
    dbc.Row([
        dbc.Col(html.H5('Appointments for the next two weeks:'), ),  # TODO
        dcc.Graph(id='home-two-weeks-insights', ),
    ], style={"margin-top": '2rem'})
], id='home-page')


def get_appointments_patients_today(date_now, conn):
    date = f"'{date_now.replace(tzinfo=timezone.utc).date().strftime('%Y-%m-%d %H:%M:%S%z')}'"
    appointments = pd.read_sql(
        f"SELECT * FROM appointments left join patients using (patient_id) where Date(Appointment) = date({date});",
        conn,
    )
    return appointments


@app.callback(Output('home-two-weeks-insights', 'figure'),
              Input('home-loading', 'children'),
              )
def render_chart(dummy):
    conn = sqlite3.connect('assets/hospital_database.db')
    today = f"'{datetime.now(sgt).replace(tzinfo=timezone.utc).date().strftime('%Y-%m-%d %H:%M:%S%z')}'"
    two_weeks = f"'{(datetime.now(sgt).replace(tzinfo=timezone.utc) + timedelta(weeks=2)).date().strftime('%Y-%m-%d %H:%M:%S%z')}'"
    df = pd.read_sql(
        f"SELECT * FROM appointments left join patients using (patient_id) where "
        f"DATE(Appointment) >= DATE({today}) AND DATE(Appointment) < DATE({two_weeks});",
        conn,
    )

    today = datetime.now(sgt).replace(tzinfo=timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    two_weeks = today + timedelta(weeks=2)

    df['Appointments'] = pd.to_datetime(df["Appointment"])
    today_df = df[(df['Appointments'] >= today) & (df['Appointments'] < tomorrow)]
    two_weeks = df[(df['Appointments'] >= today) & (df['Appointments'] < two_weeks)]

    two_weeks = predict_no_show(two_weeks)
    two_weeks['Predicted'] = two_weeks['Predicted'].apply(lambda x: 1 if x == 'Yes' else 0).astype(int)

    two_weeks = two_weeks.groupby(['Appointment']).agg({"appointment_id": 'count', 'Predicted': 'sum'}).reset_index()
    two_weeks.rename({'appointment_id': 'Count',
                      'Predicted': 'Predicted to Show'}, axis=1, inplace=True)

    two_weeks['Full Capacity'] = int(1067 / 20)

    fig = go.Figure(go.Indicator(
        mode="number+delta",
        value=len(today_df.index),
        number={'suffix': " Appointments today", 'font': {'size': 30}},
        delta={"reference": 1067, 'increasing': {'color': 'red'}, 'decreasing': {'color': 'green'}},
        domain={'y': [0, 1], 'x': [0.25, 0.75]}))

    fig.add_trace(go.Scatter(
        y=two_weeks['Count'], x=two_weeks['Appointment'],
        line=dict(color='blue'),
        name='Appointments Scheduled'))

    fig.add_trace(go.Scatter(
        y=two_weeks['Predicted to Show'], x=two_weeks['Appointment'],
        line=dict(color='green'),
        name='Predicted to Show'))

    fig.add_trace(go.Scatter(
        y=two_weeks['Full Capacity'], x=two_weeks['Appointment'],
        mode='lines',
        line=dict(dash='dash', color='red'),
        name='Full Capacity', ))

    fig.update_layout(paper_bgcolor='#FFFFFF',
                      plot_bgcolor='#FFFFFF',
                      hovermode='x unified',
                      font={'color': "black", 'family': "Helvetica"},
                      )
    fig.update_xaxes(
        rangebreaks=[
            dict(bounds=[18, 8], pattern="hour"),  # hide hours outside of 8am-6pm
            dict(bounds=["sat", "mon"]),  # hide weekends
        ]
    )

    return fig


@app.callback(Output('appointment-date-selection', 'min_date_allowed'),
              Output('appointment-date-selection', 'initial_visible_month'),
              Output('appointment-date-selection', 'date'),
              Output('home-gantt-schedule', 'figure'),
              Output('insight-home', 'children'),
              Input('home-loading', 'children'),
              )
def render_home(dummy):
    date_now = datetime.now(sgt).replace(tzinfo=timezone.utc)
    conn = sqlite3.connect('assets/hospital_database.db')

    appointments_today = get_appointments_patients_today(date_now, conn)

    min_date_allowed = datetime(date_now.year, date_now.month, date_now.day)
    initial_visible_month = date_now
    date = date_now

    appointments_today['Start'] = appointments_today['Appointment']
    appointments_today['End'] = pd.to_datetime(appointments_today['Start']) + timedelta(minutes=30)

    num_appts = len(appointments_today.index)

    if num_appts > 0:
        appointments_today = predict_no_show(appointments_today)

        appointments_today_plot = appointments_today.groupby(['Start', 'End', 'Predicted'])[
            'patient_id'].count().reset_index()
        appointments_today_plot.rename({'patient_id': 'Number of Appointments',
                                        'Predicted': 'Predicted to Show',
                                        }, axis=1, inplace=True)
        appointments_today_plot = appointments_today_plot[appointments_today_plot['Number of Appointments'] > 0]

        fig = px.timeline(appointments_today_plot,
                          x_start='Start',
                          x_end='End',
                          y='Number of Appointments',
                          color="Predicted to Show",
                          color_discrete_map={'Yes': '#35c41f', 'No': '#c4221f'},
                          hover_data=["Start", "End", 'Predicted to Show'],
                          )
        try:  # mac
            fig.update_layout(yaxis={'visible': True, 'showticklabels': True},
                              paper_bgcolor='#FFFFFF',
                              plot_bgcolor='#FFFFFF',
                              title=f'Appointments for {date_now.strftime("%A %-d %b %Y")}',
                              hovermode='x unified',
                              )
        except:  # windows
            fig.update_layout(yaxis={'visible': True, 'showticklabels': True},
                              paper_bgcolor='#FFFFFF',
                              plot_bgcolor='#FFFFFF',
                              title=f'Appointments for {date_now.strftime("%A %#d %b %Y")}',
                              hovermode='x unified',
                              )
        fig.add_vrect(x0=date_now, x1=date_now,
                      annotation_text="  " + date_now.strftime("%H:%M"), annotation_position="outside top right",
                      fillcolor="green", opacity=1, line_width=1)

        exp_filled_capacity = round(len(appointments_today[appointments_today['Predicted'] == 'Yes'].index) / 759 * 100,
                                    2)
        free_capacity = 759 - len(appointments_today[appointments_today['Predicted'] == 'Yes'].index)
        exp_no_show = len(appointments_today[appointments_today['Predicted'] == 'No'].index)
        exp_no_show_rate = round(exp_no_show / num_appts * 100, 2)

        fig_insight = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            number={'suffix': "% Capacity", 'font': {'size': 50}},
            value=exp_filled_capacity,
            domain={'x': [0, 1], 'y': [0, 1]},
            delta={'reference': 100, 'relative': True, 'increasing': {'color': 'red'},
                   'decreasing': {'color': 'green'}},
            gauge={
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "darkblue"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 60], 'color': 'green'},
                    {'range': [60, 85], 'color': 'yellow'},
                    {'range': [85, 100], 'color': 'red'}],
            }))

        fig_insight.update_layout(
            font={'color': "black", 'family': "Helvetica"},
            title={
                "text": "<span style='font-size:2.0em;color:black'>"
                        "Hospital Utilization Rate"
                        "</span>"
                        "<br>"
                        "<span style='font-size:1.0em;color:black'>"
                        f"Total Appointments Today: {num_appts}"
                        f"</span>"
                        "<br>"
                        "<span style='font-size:1.0em;color:black'>"
                        f"Additional Capacity Available: {free_capacity} slots"
                        f"</span>"
                        "<br>"
                        "<span style='font-size:1.0em;color:black'>"
                        f"Predicted No Show(s): {exp_no_show} appointments ({exp_no_show_rate}%)"
                        f"</span>"
            },
            xaxis={'showgrid': False, 'range': [-1, 1]},
            yaxis={'showgrid': False, 'range': [0, 1]}
        )
        insight_msg = [dcc.Graph(figure=fig_insight, style={'margin': '1rem'})]

    else:
        fig = go.Figure()
        try:  # linux
            fig.update_layout(yaxis={'visible': False, 'showticklabels': False},
                              paper_bgcolor='#FFFFFF',
                              plot_bgcolor='#FFFFFF',
                              title=f'No Appointments for {date_now.strftime("%A %-d %b %Y")}'
                              )
        except:  # windows
            fig.update_layout(yaxis={'visible': False, 'showticklabels': False},
                              paper_bgcolor='#FFFFFF',
                              plot_bgcolor='#FFFFFF',
                              title=f'No Appointments for {date_now.strftime("%A %#d %b %Y")}'
                              )
        fig.add_annotation(x=2.5, y=2.5, text="Select 'Create Appointment' to start booking appointments.",
                           showarrow=False)
        fig.update_yaxes(fixedrange=True)
        fig.update_xaxes(fixedrange=True)
        insight_msg = [html.P(
            f"There are no appointments for today."),
        ]

    return min_date_allowed, initial_visible_month, date, fig, insight_msg


@app.callback(Output('home-appointment-information', 'children'),
              Input('home-gantt-schedule', 'clickData'),
              Input('reset-home-appointment-information', 'n_clicks')
              )
def render_table(clickData, n1):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    date_now = datetime.now(sgt).replace(tzinfo=timezone.utc)
    conn = sqlite3.connect('assets/hospital_database.db')
    appointments_today = get_appointments_patients_today(date_now, conn)

    if len(appointments_today.index) > 0:
        appointments_today = predict_no_show(appointments_today)

        if (clickData is not None) and ('reset-home-appointment-information' not in changed_id):
            clicked_id = clickData['points'][0]['x']
            appointments_today['Appointment'] = pd.to_datetime(appointments_today['Appointment'])
            appointments_today = appointments_today[appointments_today['Appointment'] == clicked_id]
        try:
            req_columns = ['appointment_id', 'patient_id', 'Appointment', 'Sms_Reminder', 'Age', 'Gender',
                           'Scholarship', 'Predicted', 'Show_Up']
        except:
            req_columns = ['appointment_id', 'patient_id', 'Appointment', 'Sms_Reminder', 'Age', 'Gender',
                           'Scholarship', 'Show_Up']

        appointments_today = appointments_today[req_columns]

        appointments_today = appointments_today.rename({
            'appointment_id': 'Appointment ID',
            'patient_id': 'Patient ID',
            'Appointment': 'Appt Date & Time',
            'Show_Up': 'Show Up',
            'Sms_Reminder': 'SMS Reminder Sent?',
        }, axis=1)

        background_highlight = [
            {
                'if': {
                    'column_id': f'Predicted',
                    'filter_query': '{Predicted} = "No"',
                },
                'backgroundColor': '#c4221f',
            },
            {
                'if': {
                    'column_id': f'Predicted',
                    'filter_query': '{Predicted} = "Yes"',
                },
                'backgroundColor': '#35c41f',
            },
        ]

        table = dash_table.DataTable(
            data=appointments_today.to_dict('records'),
            columns=[{"name": i, "id": i} for i in appointments_today.columns],
            style_table={'overflowX': 'auto', 'height': '500px'},
            style_cell={'font-family': 'Arial', 'minWidth': 150, 'width': 150, 'maxWidth': 150, 'textAlign': 'center'},
            style_data_conditional=background_highlight,
            sort_action='native',
        )
    else:
        empty_df = pd.DataFrame(['Add in some appointments for today!'], columns=[''])
        table = dash_table.DataTable(
            data=empty_df.to_dict('records'),
            columns=[{"name": i, "id": i} for i in empty_df.columns],
            style_table={'overflowX': 'auto', 'height': '500px'},
            style_cell={'font-family': 'Arial', 'minWidth': 150, 'width': 150, 'maxWidth': 150, 'textAlign': 'center'},
            sort_action='native',
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
    State('create-appointment-patient-selection', 'value'),
    State("appointment-date-selection", "date"),
    State("create-appointment-timeslot-selection", "value"),
)
def toggle_modal(n1, patient_id, appt_date, timeslot_selected):
    if None in [patient_id, appt_date, timeslot_selected]:
        return dash.no_update
    else:
        date_now = datetime.now(sgt).replace(tzinfo=timezone.utc)
        conn = sqlite3.connect('assets/hospital_database.db')
        c = conn.cursor()
        hour_selected = int(timeslot_selected.split(":")[0])
        minute_selected = int(timeslot_selected.split(":")[1])

        appointment_id = int(pd.read_sql('SELECT MAX(appointment_id) FROM appointments;', conn, ).iat[0, 0]) + 1
        patient_id = int(patient_id)
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

        cols = (
            "appointment_id", "patient_id", "Register_Time", "Appointment", "Day", "Sms_Reminder", "Waiting_Time",
            "Show_Up",
            "Appointment_Month", "Appointment_Week_Number")
        data_tuple = (
            appointment_id, patient_id, registered_date, appointment_date, day, sms_reminder, waiting_time, show_up,
            appointment_month, appointment_week_number)

        sql = f'INSERT INTO appointments {cols} VALUES (?,?,?,?,?,?,?,?,?,?)'
        c.execute(sql, data_tuple)
        conn.commit()

        first_appointment = pd.read_sql(f'SELECT first_appt FROM patients WHERE patient_id = {patient_id}'
                                        f';', conn).iat[0, 0]
        if first_appointment == '':
            data = (appointment_date, patient_id)
            sql_to_edit = f"UPDATE patients SET first_appt = ? WHERE patient_id = ? ;"
            c.execute(sql_to_edit, data)
            conn.commit()
        return layout


@app.callback(
    Output('create-patient-status', 'children'),
    Output('create-patient-patient-id', 'value'),
    Output('create-appointment-patient-selection', 'options'),
    Input('create-patient-submit', "n_clicks"),
    State('create-patient-age', 'value'),
    State('create-patient-gender', 'value'),
    [State(f'create-patient-{x}', 'value') for x in
     ['Diabetes', 'Drinks', 'HyperTension', 'Handicap', 'Smoker', 'Scholarship', 'Tuberculosis']]
)
def add_patient(n1, age, gender, diabetes, drinks, hypertension, handicap, smoker, scholarship, tuberculosis):
    conn = sqlite3.connect('assets/hospital_database.db')
    c = conn.cursor()
    patients = pd.read_sql('SELECT * FROM patients;', conn)
    patient_options = [{'label': x, 'value': x} for x in patients['patient_id'].unique()]
    patient_id = int(max(patients['patient_id'].unique()) + 1)
    data_tuple = (
        patient_id, '', age, gender, diabetes, drinks, hypertension, handicap, smoker, scholarship, tuberculosis)
    if n1:
        try:
            if None not in data_tuple:
                # date_now = datetime.now(sgt).replace(tzinfo=timezone.utc)
                sql = f'INSERT INTO patients VALUES (?,?,?,?,?,?,?,?,?,?,?)'
                c.execute(sql, data_tuple)
                conn.commit()
                return dbc.Alert(
                    f"New patient {patient_id} successfully added to database."), patient_id + 1, patient_options + [
                           {'label': x, 'value': x} for x in [patient_id]]
            else:
                return dbc.Alert(f"Error. Please try again.", color='warning'), dash.no_update, dash.no_update
        except Exception as e:
            print(e)
            return dbc.Alert(f"Error. Please try again.", color='warning'), dash.no_update, dash.no_update
    else:
        return dash.no_update, patient_id, patient_options
