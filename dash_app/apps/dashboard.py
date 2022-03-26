import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from app import app, server
from methods.User import User
import sqlite3

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
    dcc.Tabs(id="tabs-styled-with-inline", value='dashboard-tab-1', children=[
        dcc.Tab(label='Show Up Rates', value='dashboard-tab-1', style=tab_style, selected_style=tab_selected_style,
                children=html.Div([html.H5('Filter by:'),
                                   dbc.Row([
                                       dbc.Col([
                                           dbc.Row([html.Div(
                                               [dbc.Label('Appointment Date',
                                                          style={'float': 'left', 'margin-right': '1rem'}),

                                                ])
                                           ]),
                                           dbc.Row([dbc.Spinner(dcc.DatePickerRange(id='dashboard-tab-1-appt-date',
                                                                                    clearable=True,
                                                                                    style={'zIndex': '1'}),
                                                                fullscreen=False,
                                                                color='#0D6EFD')])
                                       ]),
                                   ], style={"margin": '1rem'}),
                                   ])
                ),
        dcc.Tab(label='No. of Appointments', value='dashboard-tab-2', style=tab_style, selected_style=tab_selected_style,
                children=html.Div([html.H5('Filter by:'),
                                   dbc.Row([
                                       dbc.Col([
                                           dbc.Row([html.Div(
                                               [dbc.Label('Appointment Date',
                                                          style={'float': 'left', 'margin-right': '1rem'}),

                                                ])
                                           ]),
                                           dbc.Row([dbc.Spinner(dcc.DatePickerRange(id='dashboard-tab-2-appt-date',
                                                                                    clearable=True,
                                                                                    style={'zIndex': '1'}),
                                                                fullscreen=False,
                                                                color='#0D6EFD')])
                                       ]),
                                   ], style={"margin": '1rem'}),
                                   ])

                ),
        dcc.Tab(label='No. of New Patients', value='dashboard-tab-3', style=tab_style, selected_style=tab_selected_style,
                children=html.Div([html.H5('Filter by:'),
                                   dbc.Row([
                                       dbc.Col([
                                           dbc.Row([html.Div(
                                               [dbc.Label('Registered Date',
                                                          style={'float': 'left', 'margin-right': '1rem'}),

                                                ])
                                           ]),
                                           dbc.Row([dbc.Spinner(dcc.DatePickerRange(id='dashboard-tab-3-registered-date',
                                                                                    clearable=True,
                                                                                    style={'zIndex': '1'}),
                                                                fullscreen=False,
                                                                color='#0D6EFD')])
                                       ]),
                                   ], style={"margin": '1rem'}),
                                   ])
                ),
        dcc.Tab(label='Historical Hospital Capacity', value='dashboard-tab-4', style=tab_style,
                selected_style=tab_selected_style,
                children=html.Div([html.H5('Filter by:'),
                                   dbc.Row([
                                       dbc.Col([
                                           dbc.Row([html.Div(
                                               [dbc.Label('Appointment Date',
                                                          style={'float': 'left', 'margin-right': '1rem'}),

                                                ])
                                           ]),
                                           dbc.Row([dbc.Spinner(dcc.DatePickerRange(id='dashboard-tab-4-appt-date',
                                                                                    clearable=True,
                                                                                    style={'zIndex': '1'}),
                                                                fullscreen=False,
                                                                color='#0D6EFD')])
                                       ]),
                                   ], style={"margin": '1rem'}),
                                   ])
                ),
        dcc.Tab(label='Patient Characteristics', value='dashboard-tab-5', style=tab_style,
                selected_style=tab_selected_style,
                children=html.Div([html.H5('Filter by:'),
                                   dbc.Row([
                                       dbc.Col([
                                           dbc.Row([html.Div(
                                               [dbc.Label('Registered Date',
                                                          style={'float': 'left', 'margin-right': '1rem'}),

                                                ])
                                           ]),
                                           dbc.Row([dbc.Spinner(dcc.DatePickerRange(id='dashboard-tab-5-registered-date',
                                                                                    clearable=True,
                                                                                    style={'zIndex': '1'}),
                                                                fullscreen=False,
                                                                color='#0D6EFD')])
                                       ]),
                                   ], style={"margin": '1rem'}),
                                   ])
                ),
    ], style=tabs_styles),
    html.Div(id='tabs-content-output', style={"margin": "1rem"})
])


@app.callback(Output('tabs-content-output', 'children'),
              Input('tabs-styled-with-inline', 'value'))
def render_content(tab): #TODO + Interact with Filters
    import plotly.express as px
    df = px.data.gapminder().query("continent=='Oceania'")  # replace with your own data source
    fig = px.line(
        df, x="year", y="lifeExp", color="country",
        title="Sample Graph. Hover over points to see the change")
    fig.update_layout(
        font_family="Helvetica",
        title_font_family="Helvetica",
        showlegend=False,  # change True/False accordingly
        plot_bgcolor="white",
        hovermode='x unified',  # see https://plotly.com/python/hover-text-and-formatting/
    )
    fig.update_xaxes(visible=True, fixedrange=False)  # change True/False accordingly
    fig.update_yaxes(visible=True, fixedrange=False)  # change True/False accordingly

    if tab == 'dashboard-tab-1':
        content = html.Div([html.Div('Combo Graph of Show up rates over time'),
                            dcc.Graph(figure=fig),
                            ])
    elif tab == 'dashboard-tab-2':
        content = html.Div([dcc.Graph(figure=fig),
                            ])
    elif tab == 'dashboard-tab-3':
        content = html.Div([dcc.Graph(figure=fig),
                            ])
    elif tab == 'dashboard-tab-4':
        content = html.Div([dcc.Graph(figure=fig),
                            ])
    elif tab == 'dashboard-tab-5':
        content = html.Div([dcc.Graph(figure=fig),
                            ])
    return content
