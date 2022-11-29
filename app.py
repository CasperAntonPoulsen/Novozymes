# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from visualization import EarthquakeVisuals

us_visuals =  EarthquakeVisuals()
eu_visuals =  EarthquakeVisuals(region="europe")

visuals = dict(
    europe = {
        "scatterMap":eu_visuals.scatterMap(),
        "logPlot":eu_visuals.logPlot()
    },
    us = {
        "scatterMap":us_visuals.scatterMap(),
        "logPlot":us_visuals.logPlot()
    }
)

scatterMap = visuals['us']["scatterMap"]
logPlot = visuals['us']["logPlot"]


app = Dash(__name__)

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    
    html.H1(
        children='Earthquake activity from the past decade',
        style={
            'textAlign': 'left',
            'color': colors['text']
        }
    ),
    html.Div(children=[
        html.Div(children='A proof of concept for Novozymes by Casper Anton Poulsen', style={
        'textAlign': 'left','color': colors['text'],'padding': 10, 'flex': 1
        }),

        html.Div(children=dcc.Dropdown(
            id = "dropdown",
            options = [
                {"label":"US", "value":"us"},
                {"label":"Europe", "value":"europe"}
                ],
            value = "us"
        ), style = {'flex': 1,'padding': 10})
    ], style= {'display': 'flex', 'flex-direction': 'row'}),


    html.Div(children=[
        html.Div(children=[
        html.Label("ScatterMap"),
        dcc.Graph(
        id='scatter-map',
        figure=scatterMap),
        ], style={'padding': 10, 'flex': 1, 'color': colors['text']}),

        html.Div(children=[
            html.Label("LogPlot"),
            dcc.Graph(
            id="log-plot",
            figure=logPlot),
        ], style={'padding': 10, 'flex': 1, 'color': colors['text']})
    ], style={'display': 'flex', 'flex-direction': 'row'})
])


@app.callback(
    Output("scatter-map", component_property= 'figure'),
    Output("log-plot", component_property= 'figure'),
    Input("dropdown", component_property= 'value'))
def graph_update(dropdown_value):
    return visuals[dropdown_value]["scatterMap"], visuals[dropdown_value]["logPlot"]


if __name__ == '__main__':
    app.run_server(debug=True)