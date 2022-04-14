from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from app import app, server
import sqlite3
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import plotly.express as px

tabs_styles = {
    'height': '44px',
    'margin': '1rem'
}
tab_style = {
    'borderBottom': '1px solid #0D6EFD',
    'padding': '6px',
}

tab_selected_style = {
    'borderTop': '1px solid #0D6EFD',
    'borderBottom': '1px solid #0D6EFD',
    'backgroundColor': '#0D6EFD',
    'color': 'white',
    'padding': '6px'
}

layout = html.Div([
    html.H5("Dashboard"),
    dcc.Loading(children=[html.Div(id='dashboard-loading-dummy',
                                   style={'height': '3rem', 'width': '3rem', 'float': 'right', 'margin': '1rem'}),
                          dcc.Tabs(id="tabs-styled-with-inline", value='dashboard-tab-2', children=[
                              dcc.Tab(label='No. of Appointments', value='dashboard-tab-2', style=tab_style,
                                      selected_style=tab_selected_style,
                                      children=html.Div([html.H5('Filter by:'),
                                                         dbc.Row([
                                                             dbc.Col([

                                                                 dbc.Row([dbc.Spinner([dbc.Label('View by: '),
                                                                                       dcc.Dropdown(
                                                                                           id='chosen-time-frame-tab-2',
                                                                                           options=[
                                                                                               {'label': i, 'value': i}
                                                                                               for i in
                                                                                               ['Year', 'Quarter',
                                                                                                'Month',
                                                                                                'Day']],
                                                                                           value='Month',
                                                                                       )],
                                                                                      fullscreen=False,
                                                                                      color='#0D6EFD')])
                                                             ]),
                                                         ], style={"margin": '1rem'}),
                                                         ])
                                      ),
                              dcc.Tab(label='Show Up Rates', value='dashboard-tab-1', style=tab_style,
                                      selected_style=tab_selected_style,
                                      children=html.Div([html.H5('Filter by:'),
                                                         dbc.Row([
                                                             dbc.Col([
                                                                 dbc.Row([html.Div(
                                                                     [dbc.Label('Appointment Date',
                                                                                style={'float': 'left',
                                                                                       'margin-right': '1rem'}),

                                                                      ])
                                                                 ]),
                                                                 dbc.Row([dbc.Spinner([dcc.DatePickerRange(
                                                                     id='dashboard-tab-1-appt-date',
                                                                     start_date='2014-01-02 00:00:00+00:00',
                                                                     end_date='2015-12-30 00:00:00+00:00',
                                                                     clearable=False,
                                                                     style={'zIndex': '1', 'float': 'left'}),
                                                                                       dbc.Button('Apply filter',
                                                                                                  id='apply-dashboard-tab-1-appt-date',
                                                                                                  className='mb-3',
                                                                                                  style={
                                                                                                      'margin-left': '1rem',
                                                                                                      'float': 'left'})
                                                                                       ],
                                                                                      fullscreen=False,
                                                                                      color='#0D6EFD'),
                                                                          ])
                                                             ]),
                                                         ], style={"margin": '1rem'}, justify='start'),
                                                         ])
                                      ),
                              dcc.Tab(label='Patients', value='dashboard-tab-3', style=tab_style,
                                      selected_style=tab_selected_style,
                                      children=html.Div([html.H5('Filter by:'),
                                                         dbc.Row([
                                                             dbc.Col([

                                                                 dbc.Row([dbc.Spinner([dbc.Label('View by: '),
                                                                                       dcc.Dropdown(
                                                                                           id='chosen-time-frame-tab-3',
                                                                                           options=[
                                                                                               {'label': i, 'value': i}
                                                                                               for i in
                                                                                               ['Year', 'Quarter',
                                                                                                'Month',
                                                                                                'Day']],
                                                                                           value='Month',
                                                                                           )],
                                                                                      fullscreen=False,
                                                                                      color='#0D6EFD')])
                                                             ]),
                                                         ], style={"margin": '1rem'}),
                                                         ])
                                      ),
                              dcc.Tab(label='Historical Hospital Capacity', value='dashboard-tab-4', style=tab_style,
                                      selected_style=tab_selected_style,
                                      children=html.Div([])
                                      ),

                          ], style=tabs_styles), ]),
    html.Div(id='tabs-content-output', style={"margin": "1rem"})
])


@app.callback(Output('tabs-content-output', 'children'),
              Output('dashboard-loading-dummy', 'children'),
              Input('tabs-styled-with-inline', 'value'),
              Input('apply-dashboard-tab-1-appt-date', 'n_clicks'),
              Input('chosen-time-frame-tab-2', 'value'),
              Input('chosen-time-frame-tab-3', 'value'),
              State('dashboard-tab-1-appt-date', 'start_date'),
              State('dashboard-tab-1-appt-date', 'end_date'),
              )
def render_content(tab, n1, n2, n3, start_date_1, end_date_1):
    if tab == 'dashboard-tab-1':
        conn = sqlite3.connect('assets/hospital_database.db')
        df = pd.read_sql('SELECT * FROM appointments;', conn)
        df.rename({"Appointment_Month": "Appointment Month",
                   "Appointment_Week_Number": "Appointment Week Number",
                   "Register_Time": "Register Time",
                   "Waiting_Time": "Waiting Time",
                   "Show_Up": "Show Up",
                   }, axis=1, inplace=True)

        df2 = pd.read_sql_query(
            'SELECT Appointment, appointments."show_up", patients.diabetes, appointments.patient_id, patients.drinks, patients.hypertension, patients.handicap, patients.smoker, patients.tuberculosis, patients.Scholarship, patients.gender, appointments.sms_reminder FROM appointments INNER JOIN patients ON appointments.patient_id=patients.patient_id;',
            conn)

        def create_graph1(df=df):
            df['Appointment'] = pd.to_datetime(df['Appointment'])

            if start_date_1 not in ['', None]:
                if end_date_1 in ['', None]:
                    df = df[(df['Appointment'] >= start_date_1)]
                else:
                    df = df[(df['Appointment'] >= start_date_1) & (df['Appointment'] <= end_date_1)]

            elif end_date_1 not in ['', None]:
                df = df[(df['Appointment'] <= end_date_1)]

            # convert from categorical to int
            df['Show Up'] = df['Show Up'].astype('int')
            sr_month = df.groupby('Appointment Month')['Show Up'].mean().round(2)
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(x=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                           y=sr_month,
                           mode='lines+markers'))
            fig.update_layout(
                title="Average Show up rates by Appointment Month",
                xaxis_title="Month",
                yaxis_title="Show up rate",
                font_family="Helvetica",
                title_font_family="Helvetica",
                showlegend=False,  # change True/False accordingly
                plot_bgcolor="white",
                hovermode='x unified',  # see https://plotly.com/python/hover-text-and-formatting/
            )
            fig.update_xaxes(visible=True, fixedrange=False)
            fig.update_yaxes(visible=True, fixedrange=False)
            return fig

        def create_graph2(df=df2):
            conn = sqlite3.connect('assets/hospital_database.db')
            df = pd.read_sql_query(
                'SELECT Appointment, appointments."show_up", patients.age, appointments.patient_id FROM appointments INNER JOIN patients ON appointments.patient_id=patients.patient_id',
                conn)
            df.rename({"Appointment_Month": "Appointment Month",
                       "Appointment_Week_Number": "Appointment Week Number",
                       "Register_Time": "Register Time",
                       "Waiting_Time": "Waiting Time",
                       "Show_Up": "Show Up",
                       }, axis=1, inplace=True)
            # convert from categorical to int
            df['Show Up'] = df['Show Up'].astype('int')

            if start_date_1 not in ['', None]:
                if end_date_1 in ['', None]:
                    df = df[(df['Appointment'] >= start_date_1)]
                else:
                    df = df[(df['Appointment'] >= start_date_1) & (df['Appointment'] <= end_date_1)]
            elif end_date_1 not in ['', None]:
                df = df[(df['Appointment'] <= end_date_1)]

            sr_age = df.groupby('Age')['Show Up'].mean()
            x = np.array(df['Age'])
            x = np.unique(x).tolist()
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=x, y=sr_age,
                                     mode='lines'))
            fig.update_layout(
                title="Average Show up rates by Age",
                xaxis_title="Age",
                yaxis_title="Show up rate",
                font_family="Helvetica",
                title_font_family="Helvetica",
                showlegend=False,  # change True/False accordingly
                plot_bgcolor="white",
                hovermode='x unified',  # see https://plotly.com/python/hover-text-and-formatting/
            )

            fig.update_xaxes(visible=True, fixedrange=False)  # change True/False accordingly
            fig.update_yaxes(visible=True, fixedrange=False)  # change True/False accordingly
            return fig

        def create_graph3(df=df2):

            df.rename({"Appointment_Month": "Appointment Month",
                       "Appointment_Week_Number": "Appointment Week Number",
                       "Register_Time": "Register Time",
                       "Waiting_Time": "Waiting Time",
                       "Show_Up": "Show Up",
                       }, axis=1, inplace=True)
            # convert from categorical to int
            df['Show Up'] = df['Show Up'].astype('int')
            if start_date_1 not in ['', None]:
                if end_date_1 in ['', None]:
                    df = df[(df['Appointment'] >= start_date_1)]
                else:
                    df = df[(df['Appointment'] >= start_date_1) & (df['Appointment'] <= end_date_1)]

            elif end_date_1 not in ['', None]:
                df = df[(df['Appointment'] <= end_date_1)]

            diabetes = df.groupby('Diabetes')['Show Up'].mean()
            x1 = np.array(df['Diabetes'])
            x1 = np.unique(x1).tolist()
            x1 = ['Yes' if x == '1' else 'No' for x in x1]

            drinks = df.groupby('Drinks')['Show Up'].mean()
            x2 = np.array(df['Drinks'])
            x2 = np.unique(x2).tolist()
            x2 = ['Yes' if x == '1' else 'No' for x in x2]

            hypert = df.groupby('HyperTension')['Show Up'].mean()
            x3 = np.array(df['HyperTension'])
            x3 = np.unique(x3).tolist()
            x3 = ['Yes' if x == '1' else 'No' for x in x3]

            handicap = df.groupby('Handicap')['Show Up'].mean()
            x4 = np.array(df['Handicap'])
            x4 = np.unique(x4).tolist()
            x4 = ['Yes' if x == '1' else 'No' for x in x4]

            smoker = df.groupby('Smoker')['Show Up'].mean()
            x5 = np.array(df['Smoker'])
            x5 = np.unique(x5).tolist()
            x5 = ['Yes' if x == '1' else 'No' for x in x5]

            schol = df.groupby('Scholarship')['Show Up'].mean()
            x6 = np.array(df['Scholarship'])
            x6 = np.unique(x6).tolist()
            x6 = ['Yes' if x == '1' else 'No' for x in x6]

            tb = df.groupby('Tuberculosis')['Show Up'].mean()
            x7 = np.array(df['Tuberculosis'])
            x7 = np.unique(x7).tolist()
            x7 = ['Yes' if x == '1' else 'No' for x in x7]

            gender = df.groupby('Gender')['Show Up'].mean()
            x8 = np.array(df['Gender'])
            x8 = np.unique(x8).tolist()
            x8 = ['Male' if x == '1' else 'Female' for x in x8]

            sms = df.groupby('Sms_Reminder')['Show Up'].mean()
            x9 = np.array(df['Sms_Reminder'])
            x9 = np.unique(x9).tolist()
            x9 = ['None' if x == 0 else x for x in x9]

            fig = make_subplots(
                rows=3, cols=3,
                subplot_titles=(
                    "Diabetes", "Drinks", "HyperTension", "Handicap", "Smoker", "Scholarship", "Tuberculosis", "Gender",
                    "Sms reminder"))

            fig.add_trace(go.Bar(x=x1, y=diabetes, name="Diabetes", text=round(diabetes, 4)),
                          row=1, col=1)

            fig.add_trace(go.Bar(x=x2, y=drinks, name="Drinks", text=round(drinks, 4)),
                          row=1, col=2)

            fig.add_trace(go.Bar(x=x3, y=hypert, name="HyperTension", text=round(hypert, 4)),
                          row=1, col=3)

            fig.add_trace(go.Bar(x=x4, y=handicap, name="Handicap", text=round(handicap, 4)),
                          row=2, col=1)

            fig.add_trace(go.Bar(x=x5, y=smoker, name="Smoker", text=round(smoker, 4)),
                          row=2, col=2)

            fig.add_trace(go.Bar(x=x6, y=schol, name="Scholarship", text=round(schol, 4)),
                          row=2, col=3)

            fig.add_trace(go.Bar(x=x7, y=tb, name="Tuberculosis", text=round(tb, 4)),
                          row=3, col=1)

            fig.add_trace(go.Bar(x=x8, y=gender, name="Gender", text=round(gender, 4)),
                          row=3, col=2)

            fig.add_trace(go.Bar(x=x9, y=sms, name="Sms_Reminder", text=round(sms, 4)),
                          row=3, col=3)

            fig.update_layout(title_text="Average Show up rates by Characteristics",
                              font_family="Helvetica",
                              title_font_family="Helvetica",
                              showlegend=True,  # change True/False accordingly
                              plot_bgcolor="white",
                              height=800,
                              hovermode='closest',  # see https://plotly.com/python/hover-text-and-formatting/
                              )

            fig.update_xaxes(type='category', visible=True, fixedrange=True)
            fig.update_yaxes(visible=True, fixedrange=True, range=[0, 1])
            return fig

        def create_graph4(df=df):
            # convert from categorical to int
            df['Show Up'] = df['Show Up'].astype('int')
            if start_date_1 not in ['', None]:
                if end_date_1 in ['', None]:
                    df = df[(df['Appointment'] >= start_date_1)]
                else:
                    df = df[(df['Appointment'] >= start_date_1) & (df['Appointment'] <= end_date_1)]
            elif end_date_1 not in ['', None]:
                df = df[(df['Appointment'] <= end_date_1)]

            sr_day = df.groupby('Day')['Show Up'].mean()
            fig = go.Figure()
            fig.add_trace(go.Bar(x=['Mon', 'Tue', 'Wed', 'Thurs', 'Fri', 'Sat', 'Sun'], y=sr_day, ))
            fig.update_layout(
                title="Average Show up rate by Day of Week",
                xaxis_title="Days of Week",
                yaxis_title="Show up rate",
                font_family="Helvetica",
                title_font_family="Helvetica",
                showlegend=False,  # change True/False accordingly
                plot_bgcolor="white",
                hovermode='closest',  # see https://plotly.com/python/hover-text-and-formatting/
            )

            fig.update_xaxes(visible=True, fixedrange=False)  # change True/False accordingly
            fig.update_yaxes(visible=True, fixedrange=False)  # change True/False accordingly
            return fig

        def create_graph5(df=df2):
            conn = sqlite3.connect('assets/hospital_database.db')
            df = pd.read_sql_query(
                'SELECT Appointment, appointments."show_up", appointments.day, patients.gender, appointments."Appointment_Month" '
                'FROM appointments INNER JOIN patients ON appointments.patient_id=patients.patient_id;',
                conn)
            df.rename({"Appointment_Month": "Appointment Month",
                       "Appointment_Week_Number": "Appointment Week Number",
                       "Register_Time": "Register Time",
                       "Waiting_Time": "Waiting Time",
                       "Show_Up": "Show Up",
                       }, axis=1, inplace=True)
            # convert from categorical to int
            df['Show Up'] = df['Show Up'].astype('int')
            df['Gender'] = df['Gender'].astype('int')

            if start_date_1 not in ['', None]:
                if end_date_1 in ['', None]:
                    df = df[(df['Appointment'] >= start_date_1)]
                else:
                    df = df[(df['Appointment'] >= start_date_1) & (df['Appointment'] <= end_date_1)]

            elif end_date_1 not in ['', None]:
                df = df[(df['Appointment'] <= end_date_1)]

            sr_day = df.groupby(['Day', 'Gender'], as_index=False)['Show Up'].mean()

            trace1 = go.Bar(x=['Mon', 'Tue', 'Wed', 'Thurs', 'Fri', 'Sat', 'Sun'],
                            y=(sr_day[sr_day["Gender"] == 0])['Show Up'], name="Male")
            trace2 = go.Bar(x=['Mon', 'Tue', 'Wed', 'Thurs', 'Fri', 'Sat', 'Sun'],
                            y=(sr_day[sr_day["Gender"] == 1])['Show Up'], name="Female")
            fig = go.Figure(data=[trace1, trace2],
                            layout=go.Layout(barmode='group'))

            fig.update_layout(
                title="Average Show up rate by Day of Week by Gender",
                xaxis_title="Days of Week",
                yaxis_title="Show up rate",
                legend_title="Gender",
                font_family="Helvetica",
                title_font_family="Helvetica",
                showlegend=True,  # change True/False accordingly
                plot_bgcolor="white",
                hovermode='closest',  # see https://plotly.com/python/hover-text-and-formatting/
            )

            fig.update_xaxes(visible=True, fixedrange=False)  # change True/False accordingly
            fig.update_yaxes(visible=True, fixedrange=False)  # change True/False accordingly
            return fig

        def create_graph6(df=df):
            conn = sqlite3.connect("assets/hospital_database.db")
            df = pd.read_sql('Select Appointment, "Waiting_Time", "Show_Up"from appointments', conn)
            df.rename({"Appointment_Month": "Appointment Month",
                       "Appointment_Week_Number": "Appointment Week Number",
                       "Register_Time": "Register Time",
                       "Waiting_Time": "Waiting Time",
                       "Show_Up": "Show Up",
                       }, axis=1, inplace=True)
            if start_date_1 not in ['', None]:
                if end_date_1 in ['', None]:
                    df = df[(df['Appointment'] >= start_date_1)]
                else:
                    df = df[(df['Appointment'] >= start_date_1) & (df['Appointment'] <= end_date_1)]
            elif end_date_1 not in ['', None]:
                df = df[(df['Appointment'] <= end_date_1)]

            df_group = df.groupby('Show Up').mean().reset_index()
            df_group['Show Up'] = df_group['Show Up'].apply(lambda x: 'Yes' if x == '1' else 'No')
            fig = px.bar(df_group, x="Show Up", y="Waiting Time")
            fig.update_layout(
                title="Difference in Average Waiting Times between Show-Ups and No-Shows",
                xaxis_title="Show Up",
                yaxis_title="Waiting Time",
                legend_title="Gender",
                font_family="Helvetica",
                title_font_family="Helvetica",
                showlegend=False,  # change True/False accordingly
                plot_bgcolor="white",
                hovermode='closest',  # see https://plotly.com/python/hover-text-and-formatting/
            )
            return fig

        content = html.Div([dcc.Graph(figure=create_graph1()),
                            dcc.Graph(figure=create_graph2()),
                            dcc.Graph(figure=create_graph3()),
                            dcc.Graph(figure=create_graph4()),
                            dcc.Graph(figure=create_graph5()),
                            dcc.Graph(figure=create_graph6()),
                            ])
    elif tab == 'dashboard-tab-2':
        def create_num_appts(chosen=n2):

            conn = sqlite3.connect("assets/hospital_database.db")
            df = pd.read_sql("""
            Select Appointment, appointment_id
            from appointments where
            "Show_Up" = '1';
            """, conn)

            if chosen == 'Year':
                time_group = '%Y'
            elif chosen == 'Month':
                time_group = '%y-%m'
            elif chosen == 'Day':
                time_group = '%y-%m-%d'
            if chosen == 'Quarter':
                df['Appointment'] = pd.to_datetime(df['Appointment']).dt.to_period("Q").astype(str)
            else:
                df['Appointment'] = pd.to_datetime(df['Appointment']).dt.strftime(time_group)
            df = df.groupby('Appointment')['appointment_id'].count().reset_index()
            df.rename({'Appointment': 'Appointment Date', 'appointment_id': 'Count of Appointments'}, axis=1,
                      inplace=True)
            fig = px.line(df, x='Appointment Date', y='Count of Appointments')
            fig.update_layout(
                title="Count of Appointments Serviced (Showed Up) over time",
                font_family="Helvetica",
                title_font_family="Helvetica",
                plot_bgcolor="white",
                hovermode='x unified',  # see https://plotly.com/python/hover-text-and-formatting/
            )
            return fig

        content = html.Div([dcc.Graph(figure=create_num_appts()),
                            ])
    elif tab == 'dashboard-tab-3':
        def create_num_new_patients(chosen=n3):
            conn = sqlite3.connect("assets/hospital_database.db")

            df = pd.read_sql("""
                       Select patient_id, first_appt 
                       from patients;
                       """, conn)
            df = df[(df['first_appt'] != '') & (df['first_appt'] != None) ]
            df['first_appt'] = df['first_appt'].apply(lambda x: str(x).split(" ")[0])

            if chosen == 'Year':
                time_group = '%Y'
            elif chosen == 'Month':
                time_group = '%y-%m'
            elif chosen == 'Day':
                time_group = '%y-%m-%d'
            if chosen == 'Quarter':
                df['first_appt'] = pd.to_datetime(df['first_appt'],errors='coerce').dt.to_period("Q").astype(str)
            else:
                df['first_appt'] = pd.to_datetime(df['first_appt'],errors='coerce').dt.strftime(time_group)

            df = df.groupby('first_appt')['patient_id'].count().reset_index()
            df.rename({'first_appt': 'Date', 'patient_id': 'Count of New Patients'}, axis=1,
                      inplace=True)
            fig = px.line(df, x='Date', y='Count of New Patients')
            fig.update_layout(
                title="Count of New Patients over time",
                font_family="Helvetica",
                title_font_family="Helvetica",
                plot_bgcolor="white",
                hovermode='x unified',  # see https://plotly.com/python/hover-text-and-formatting/
            )
            return fig
        def create_gender_dist():
            conn = sqlite3.connect("assets/hospital_database.db")

            df = pd.read_sql("""
                       Select *
                       from patients;
                       """, conn)
            df = df[df['first_appt'] != '']

            df['Gender'] = df['Gender'].apply(lambda x: 'Male' if x=='1' else 'Female')
            labels = df['Gender'].value_counts().index
            values = df['Gender'].value_counts().values

            fig = go.Figure()

            fig.add_trace(go.Pie(labels=labels, values=values))
            fig.update_traces(textposition='inside')
            fig.update_layout(
                title="Patient by Gender",
                font_family="Helvetica",
                title_font_family="Helvetica",
                plot_bgcolor="white",
                hovermode='x unified',
                uniformtext_minsize=15,
                uniformtext_mode='hide')

            return fig
        def create_age_dist():
            conn = sqlite3.connect("assets/hospital_database.db")

            df = pd.read_sql("""
                       Select *
                       from patients;
                       """, conn)
            df = df[df['first_appt'] != '']

            fig = go.Figure()

            fig.add_trace(go.Box(x=df.Age.values, name='Age'))
            fig.update_layout(
                title="Patient Age",
                font_family="Helvetica",
                title_font_family="Helvetica",
                plot_bgcolor="white")

            return fig


        content = html.Div([dcc.Graph(figure=create_num_new_patients()),
                            dcc.Graph(figure=create_gender_dist()),
                            dcc.Graph(figure=create_age_dist()),
                            ])
    elif tab == 'dashboard-tab-4':
        def create_capacity():
            conn = sqlite3.connect("assets/hospital_database.db")
            Max_cap_per_mth = 27455
            df = pd.read_sql("""
            Select "Appointment_Month",count(appointment_id) as num_of_appointments
            from appointments
            group by "Appointment_Month" 
            """, conn)
            df['Capacity'] = df['num_of_appointments'] / Max_cap_per_mth * 100
            df = df.astype({'Appointment_Month': 'int32'})
            df = df.sort_values(by=['Appointment_Month'])
            df.rename({'Appointment_Month': "Appointment Month"}, axis=1, inplace=True)
            df['Appointment Month'] = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov',
                                       'Dec']
            fig = px.bar(df, x="Appointment Month", y="Capacity", title='% of Total Capacity used by Month')
            fig.update_layout(
                font_family="Helvetica",
                title_font_family="Helvetica",
                plot_bgcolor="white",
                hovermode='x unified',  # see https://plotly.com/python/hover-text-and-formatting/
            )
            return fig

        content = html.Div([dcc.Graph(figure=create_capacity()),
                            ])
    return content, None
