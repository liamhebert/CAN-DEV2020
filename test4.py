import dash

app = dash.Dash(__name__)
server = app.server
app.config.suppress_callback_exceptions = True

import os
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go


df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/2014_ebola.csv')
df = df.dropna(axis=0)

if 'DYNO' in os.environ:
    app_name = os.environ['DASH_APP_NAME']
else:
    app_name = 'dash-pieplot'

layout = html.Div([
    html.Div([html.H1("Ebola Cases Reported in Africa - 2014")], style={"textAlign": "center"}),
    dcc.Graph(id="my-graph"),
    html.Div([dcc.Slider(id='month-selected', min=3, max=12, value=8,
                         marks={3: "March", 4: "April", 5: "May", 6: "June", 7: "July", 8: "August", 9: "September",
                                10: "October", 11: "November", 12: "December"})],
             style={'textAlign': "center", "margin": "30px", "padding": "10px", "width": "65%", "margin-left": "auto",
                    "margin-right": "auto"}),
], className="container")


@app.callback(
    dash.dependencies.Output("my-graph", "figure"),
    [dash.dependencies.Input("month-selected", "value")]
)
def update_graph(selected):
    return {
        "data": [go.Pie(labels=df["Country"].unique().tolist(), values=df[df["Month"] == selected]["Value"].tolist(),
                        marker={'colors': ['#EF963B', '#C93277', '#349600', '#EF533B', '#57D4F1']}, textinfo='label')],
        "layout": go.Layout(title=f"Cases Reported Monthly", margin={"l": 300, "r": 300, },
                            legend={"x": 1, "y": 0.7})}


import os
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

if 'DYNO' in os.environ:
    app_name = os.environ['DASH_APP_NAME']
else:
    app_name = 'dash-pieplot/'

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])



if __name__ == '__main__':
    app.run_server(debug=True)

    funding_allocation = df[["DepartmentNumber-Numéro-de-Ministère", "AGRG_PYMT_AMT"]]

    for index, row in funding_allocation.iterrows():
        key = row['DepartmentNumber-Numéro-de-Ministère']
        funding_allocation.at[index, 'DepartmentNumber-Numéro-de-Ministère'] = str(department_dict[key])[2:-2]
    funding_allocation.groupby(["DepartmentNumber-Numéro-de-Ministère"]).sum()

    for index, row in funding_allocation.iterrows():
        payment = row["AGRG_PYMT_AMT"]
        if payment / funding_allocation["AGRG_PYMT_AMT"].sum() < 0.0005:
            funding_allocation.at[index, 'DepartmentNumber-Numéro-de-Ministère'] = 'Other'

