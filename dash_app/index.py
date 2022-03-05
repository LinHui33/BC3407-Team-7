from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from app import app
from apps import no_such_page, home

navbar = html.Div([
    dbc.Row([
        dbc.Col(dbc.Button('XYZ Hospital', className='navbar-btns', href='/home', style={'float': 'left'}), ),
        dbc.Col([
            dbc.Button('Login', className='navbar-btns', href='/login', style={'float': 'right'}),
            dbc.DropdownMenu([dbc.DropdownMenuItem('Patient Screener', href='/patients'),
                              dbc.DropdownMenuItem('Appointment Screener', href='/appointments'),
                              dbc.DropdownMenuItem('ML Model', href='/machine-learning'),
                              ], className='navbar-btns', label='More', style={'float': 'right'}),
        ]),
    ], justify="between",
    ),
], className='navbar-custom')

footer = html.Div([
    dbc.Alert('Footer')
],style={"margin-top":"3rem"})

app.layout = html.Div([
    dcc.Location(id="url"),
    navbar,
    html.Div(id='page-output',style={'margin':'1rem'}),
    footer,
], style={"margin": '1rem'})


@app.callback(Output('page-output', 'children'),
              Input('url', 'pathname')
              )
def render_content(url):
    if url in ['/', '/home']:
        return home.layout
    else:
        return no_such_page.layout


if __name__ == '__main__':
    app.run_server(debug=False)
