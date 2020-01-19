import dash
import dash_table
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_core_components as dcc
import pandas as pd


#  df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/solar.csv')
#  d = {'col1': [1, 2], 'col2': [3, 4]}


def build_table(data):
    return dash_table.DataTable(
        id='table',
        data=data.to_dict('records'),
        columns=[{"name": i, "id": i} for i in df.columns],
        style_cell={'textAlign': 'left'},
        row_selectable="multi",
        selected_rows=[],
        active_cell={'row': 0, 'column': 0, 'row_id': 0, 'column_id': 'col1'},
        style_data_conditional=[
            {
                'if': {
                    'column_id': 'Generation (GWh)',
                    'filter_query': '{Generation (GWh)} > 500'
                },
                'color': 'red',
            },
        ]
    )

d = {'col1': [1, 2], 'col2': [3, 4]}
print(d)
df = pd.DataFrame(data=d)

app = dash.Dash(__name__)

federal_page = html.Div([
    build_table(df),
    html.Div(id='test'),
    html.Div(id='test2'),
])

app.layout = federal_page


@app.callback(
    Output(component_id='test', component_property='children'),
    [Input(component_id='table', component_property='selected_rows')]
)
def update_output_div(input_value):
    return input_value


@app.callback(
    Output(component_id='test2', component_property='children'),
    [Input(component_id='table', component_property='active_cell')]
)
def find_active_cell(active_cell):
    print(active_cell)
    return active_cell['row']




if __name__ == '__main__':
    app.run_server(debug=True)
