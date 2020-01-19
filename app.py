import os
import pickle
import pathlib
import numpy as np
import datetime as dt
import dash
import dash_core_components as dcc
import dash_html_components as html

from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
from scipy.stats import rayleigh
from db.api import get_wind_data, get_wind_data_by_id

import pandas as pd
import test

df = pd.read_csv('transfer_payment.csv', usecols=['FSCL_YR', 'MINC', 'DepartmentNumber-Numéro-de-Ministère',
        'RCPNT_CLS_EN_DESC', 'RCPNT_NML_EN_DESC', 'CTY_EN_NM',
       'PROVTER_EN', 'CNTRY_EN_NM', 'TOT_CY_XPND_AMT', 'AGRG_PYMT_AMT'])


for i, row in df.iterrows():
      df.at[i, 'FSCL_YR'] = 2018

department_dict = pickle.load( open( "department.p", "rb" ) )
ministry_dict = pickle.load( open( "mine.p", "rb" ) )

GRAPH_INTERVAL = os.environ.get("GRAPH_INTERVAL", 5000)

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

server = app.server

app_color = {"graph_bg": "#082255", "graph_line": "#007ACE"}

app.layout = html.Div(
    [dcc.Dropdown(
        id='my-dropdown',
        options=[
            {'label': 'Coke', 'value': 'COKE'},
            {'label': 'Tesla', 'value': 'TSLA'},
            {'label': 'Apple', 'value': 'AAPL'}
        ],
        value='COKE'
    ),
        # header
        html.Div(
            [
                html.Div(
                    [
                        html.H4("CANDEV DATA CHALLENGE", className="app__header__title"),
                        html.P(
                            "This app summarizes and displays information related to deparment spending and programs funds allocation",
                            className="app__header__title--grey",
                        ),
                    ],
                    className="app__header__desc",
                ),
                html.Div(
                    [
                        html.Img(
                            src=app.get_asset_url("candev-eng-new.png"),
                            className="app__menu__img",
                        )
                    ],
                    className="app__header__logo",
                ),
            ],
            className="app__header",
        ),
        html.Div(
            [
                # wind speed
                html.Div(
                    [
                        html.Div(
                            [html.H6("WIND SPEED (MPH)", className="graph__title")]
                        ),
                        dcc.Graph(
                            id="wind-speed",
                            figure=dict(
                                layout=dict(
                                    plot_bgcolor=app_color["graph_bg"],
                                    paper_bgcolor=app_color["graph_bg"],
                                )
                            ),
                        ),
                        dcc.Interval(
                            id="wind-speed-update",
                            interval=int(GRAPH_INTERVAL),
                            n_intervals=0,
                        ),
                    ],
                    className="two-thirds column wind__speed__container",
                ),
                html.Div(
                    [
                        # histogram
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.H6(
                                            "ANNUAL SPENDING", className="graph__title"
                                        )
                                    ]
                                ),
                                dcc.Graph(
                                    id="annual-spending",
                                    figure=dict(
                                        layout=dict(
                                            plot_bgcolor=app_color["graph_bg"],
                                            paper_bgcolor=app_color["graph_bg"],
                                        )
                                    ),
                                ),
                            ],
                            className="graph__container first",
                        ),
                        # wind direction
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.H6(
                                            "WIND DIRECTION", className="graph__title"
                                        )
                                    ]
                                ),
                                dcc.Graph(
                                    id="wind-direction",
                                    figure=dict(
                                        layout=dict(
                                            plot_bgcolor=app_color["graph_bg"],
                                            paper_bgcolor=app_color["graph_bg"],
                                        )
                                    ),
                                ),
                            ],
                            className="graph__container second",
                        ),
                    ],
                    className="one-third column histogram__direction",
                ),
            ],
            className="app__content",
        ),
    ],
    className="app__container",
)


def get_current_time():
    """ Helper function to get the current time in seconds. """

    now = dt.datetime.now()
    total_time = (now.hour * 3600) + (now.minute * 60) + (now.second)
    return total_time


@app.callback(
    Output("wind-speed", "figure"), [Input("wind-speed-update", "n_intervals")]
)
def gen_wind_speed(interval):
    """
    Generate the wind speed graph.
    :params interval: update the graph based on an interval
    """

    total_time = get_current_time()
    df = get_wind_data(total_time - 200, total_time)

    trace = dict(
        type="scatter",
        y=df["Speed"],
        line={"color": "#42C4F7"},
        hoverinfo="skip",
        error_y={
            "type": "data",
            "array": df["SpeedError"],
            "thickness": 1.5,
            "width": 2,
            "color": "#B4E8FC",
        },
        mode="lines",
    )

    layout = dict(
        plot_bgcolor=app_color["graph_bg"],
        paper_bgcolor=app_color["graph_bg"],
        font={"color": "#fff"},
        height=700,
        xaxis={
            "range": [0, 200],
            "showline": True,
            "zeroline": False,
            "fixedrange": True,
            "tickvals": [0, 50, 100, 150, 200],
            "ticktext": ["200", "150", "100", "50", "0"],
            "title": "Time Elapsed (sec)",
        },
        yaxis={
            "range": [
                min(0, min(df["Speed"])),
                max(45, max(df["Speed"]) + max(df["SpeedError"])),
            ],
            "showgrid": True,
            "showline": True,
            "fixedrange": True,
            "zeroline": False,
            "gridcolor": app_color["graph_line"],
            "nticks": max(6, round(df["Speed"].iloc[-1] / 10)),
        },
    )

    return dict(data=[trace], layout=layout)


@app.callback(
    Output("wind-direction", "figure"), [Input("wind-speed-update", "n_intervals")]
)
def gen_wind_direction(interval):
    """
    Generate the wind direction graph.
    :params interval: update the graph based on an interval
    """

    total_time = get_current_time()
    df = get_wind_data_by_id(total_time)
    val = df["Speed"].iloc[-1]
    direction = [0, (df["Direction"][0] - 20), (df["Direction"][0] + 20), 0]

    traces_scatterpolar = [
        {"r": [0, val, val, 0], "fillcolor": "#084E8A"},
        {"r": [0, val * 0.65, val * 0.65, 0], "fillcolor": "#B4E1FA"},
        {"r": [0, val * 0.3, val * 0.3, 0], "fillcolor": "#EBF5FA"},
    ]

    data = [
        dict(
            type="scatterpolar",
            r=traces["r"],
            theta=direction,
            mode="lines",
            fill="toself",
            fillcolor=traces["fillcolor"],
            line={"color": "rgba(32, 32, 32, .6)", "width": 1},
        )
        for traces in traces_scatterpolar
    ]

    layout = dict(
        height=350,
        plot_bgcolor=app_color["graph_bg"],
        paper_bgcolor=app_color["graph_bg"],
        font={"color": "#fff"},
        autosize=False,
        polar={
            "bgcolor": app_color["graph_line"],
            "radialaxis": {"range": [0, 45], "angle": 45, "dtick": 10},
            "angularaxis": {"showline": False, "tickcolor": "white"},
        },
        showlegend=False,
    )

    return dict(data=data, layout=layout)


@app.callback(
    #'test','children'
    Output("annual-spending", "figure"), [Input("wind-speed-update", "n_intervals")]
)
#actual graph
def gen_wind_histogram(selected_check):
    """
    Genererate wind histogram graph.
    :params interval: upadte the graph based on an interval
    """
    #will update to list later for year and total amount
    total = 0
    for department in range (len(df['DepartmentNumber-Numéro-de-Ministère'])):
        if (df['DepartmentNumber-Numéro-de-Ministère'][department] == '001'):
            total += df['AGRG_PYMT_AMT'][department]

    data = [
        dict(
            x=df['FSCL_YR'],
            y=total,
        )
    ]
    layout = dict(
        height=350,
        plot_bgcolor=app_color["graph_bg"],
        paper_bgcolor=app_color["graph_bg"],
        font={"color": "#fff"},
        autosize=False,
        xaxis={'type': 'log', 'title': 'Year'},
        yaxis={'title': 'Payment'},
        margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
    )

    return dict(data=data, layout=layout)


if __name__ == "__main__":
    app.run_server(debug=True)
