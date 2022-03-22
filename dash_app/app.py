import dash
import dash_bootstrap_components as dbc
import secrets

app = dash.Dash(__name__,
                title='XYZ Hospital Data Portal',
                update_title='',
                suppress_callback_exceptions=True,
                external_stylesheets=[dbc.themes.BOOTSTRAP,
                                      "https://use.fontawesome.com/releases/v5.7.2/css/all.css"],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}],
                )

server = app.server
# server.config.update(SECRET_KEY=secrets.token_hex(24))
server.config.update(SECRET_KEY='my secret key')