from dash import dcc, html
import plotly.express as px
import pandas as pd

confusion_matrix = px.imshow([[11.08, 19.29],
                 [22.27, 47.36]],
                text_auto=True,
                title = "Confusion Matrix for CART Model",
                labels=dict(x="Predicted", y="Actual"),
                x=['No Show', 'Show Up'],
                y=['No Show', 'Show Up'])

measures =  pd.DataFrame({"Measures":["Accuracy","Precision","Recall","F1 Score"],"Values":[58.44,71.06,68.01,69.50]})
measures_fig = px.bar(measures,
             x='Measures',
             y='Values',
            title = "CART Model Performance")
measures_fig.update_layout(
                font_family="Helvetica",
                title_font_family="Helvetica",
                plot_bgcolor="white",
            )

layout = html.Div([
    html.H5("ML Performance"),
    html.Div([dcc.Graph(figure=confusion_matrix),
              dcc.Graph(figure = measures_fig),
              ]),
])