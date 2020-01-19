import copy

import dash
import dash_table
import dash_html_components as html
from alpha_vantage.timeseries import TimeSeries
from dash.dependencies import Input, Output
import dash_core_components as dcc
import pickle
import pandas as pd

app_color = {"graph_bg": "#082255", "graph_line": "#007ACE"}

df_department = {}
df_department_agg = {}
for i in range(7):
    df_department[2013 + i] = pd.read_csv('excel_sheets/transfer_payment_{}.csv'.format(13+i), usecols=['FSCL_YR', 'MINC', 'DepartmentNumber-Numéro-de-Ministère',
        'RCPNT_CLS_EN_DESC', 'RCPNT_NML_EN_DESC', 'TOT_CY_XPND_AMT', 'AGRG_PYMT_AMT'])

    department_dict = pickle.load(open("department.p", "rb"))
    ministry_dict = pickle.load(open("mine.p", "rb"))
    funding_allocation = df_department[2013 + i][["DepartmentNumber-Numéro-de-Ministère", "AGRG_PYMT_AMT"]]
    for index, row in funding_allocation.iterrows():
        key = row['DepartmentNumber-Numéro-de-Ministère']
        if key in department_dict.keys():
            funding_allocation.at[index, 'DepartmentNumber-Numéro-de-Ministère'] = str(department_dict[key])[2:-2]
        else:
            funding_allocation.drop(index, axis=0)
    department_spending = copy.deepcopy(funding_allocation)
    department_spending = department_spending.groupby(["DepartmentNumber-Numéro-de-Ministère"], as_index=False).sum()

    df_department_agg[2013 + i] = department_spending



class Page:
    def __init__(self, name, url):
        self.name = name
        self.url = url


def build_table(data, height, width, name):
    print("NEW")
    print(data)
    print(data.columns)
    data_dict = data.to_dict('records')
    print(data_dict)
    return html.Div(
        [
            dash_table.DataTable(
                id='table_' + name,
                data=data_dict,
                columns=[{"name": i, "id": i} for i in data.columns],
                row_selectable="multi",
                style_data_conditional=[
                    {
                        'if': {
                            'column_id': 'AGRG_PYMT_AMT',
                            'filter_query': '{AGRG_PYMT_AMT} > 0'
                        },
                        'color': 'green',
                    },
                    {
                        'if': {
                            'column_id': 'AGRG_PYMT_AMT',
                            'filter_query': '{AGRG_PYMT_AMT} < 0'
                        },
                        'color': 'red',
                    },
                ],
                selected_rows=[51],
                style_as_list_view=True,
                style_cell={
                    'textAlign': 'left',
                    'backgroundColor': '#082255',
                    'color': 'white',
                },
                style_table={
                    'overflowX': 'ellipse',
                    'backgroundColor': '#082255',
                    'border-radius': '0.55rem',
                    'box-shadow': '0 3px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)'
                }),

        ], className="wind__speed__container one column")


def build_year_slider():
    return dcc.Slider(
        min=0,
        max=16,
        marks={i: '{}'.format(i + 2003) for i in range(17)},
        value=16,
        updatemode='drag'
    )


def build_nav_stack(stack):
    children = []
    for site in stack:
        children.append(html.Li(html.A(site.name, href=site.url), className='crumb'))
    return html.Div(children=[
        html.Nav(children=html.Ol(children), className='crumbs')
    ])


def build_header(title, subparagraph):
    # header
    title = title.replace("_", " ")
    return html.Div(
        [
            html.Div(
                [
                    html.H4(title, className="app__header__title"),
                    html.P(
                        subparagraph,
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
    )

def build_graph(title, id):
    html.Div(
        [
            html.Div(
                [
                    html.H6(
                        title, className="graph__title"
                    )
                ]
            ),
            dcc.Graph(
                id=id,
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


d = {'Department': ['Department of Defence', 'Department of Agriculture'], 'Funding': [3, 4]}
print(d)
df = pd.DataFrame(data=d)

app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}])
app.config.suppress_callback_exceptions = True
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='content'),
], className="app__container")

federal_page = html.Div(
    children=[
        # dcc.Location(id='url', href="/federal"),
        build_nav_stack([Page('Federal Overview', '\\')]),
        build_header("Federal Overview", "Government funding per department"),
        html.Div([
            build_year_slider()
        ], className='slider__container'),
        html.Div([
            build_table(df_department_agg[2019], 300, 300, "fed"),
            build_graph('ANNUAL SPENDING', 'annual-spending'),
            html.Div(id='test'),
            html.Div(id='test2'),
        ], className="app__content"),
        build_graph('ANNUAL SPENDING', 'annual-spending'),
    ]
)

nav_stack = [Page('Federal Overview', '\\')]


def create_department_page(name, data):
    # Data should contain all programs and their spending
    while len(nav_stack) > 1:
        nav_stack.pop()
    nav_stack.append(Page(name.replace("_", " "), '/department/' + name))
    html_div = html.Div(
        children=[
            build_nav_stack(nav_stack),
            build_header(name.replace("_", " ") + " Overview", "Funding given to each program by the " + name),
            build_year_slider(),
            build_table(df, height=400, width=None, name="dept")
        ]
    )

    return html_div


def create_program_page(name, data):
    while len(nav_stack) > 2:
        nav_stack.pop()
    nav_stack.append(Page(name, '/program/' + name))
    # data should contain the businesses associated with that program
    html_div = html.Div(
        children=[

        ]
    )

    return html_div


def create_business_page(name, data):
    while len(nav_stack) > 3:
        nav_stack.pop()
    nav_stack.append(Page(name, '/program/' + name))
    # data should contain value of all programs funded to that business
    html_div = html.Div(
        children=[

        ]
    )

    return html_div

@app.callback(
    Output(component_id='annual-spending', component_property='figure'),
    [Input(component_id='table_fed', component_property='selected_rows'), Input(component_id='url', component_property='pathname')],
)
def build_spending_graph(active_rows, url):
    lines = {}

    years_list = [2013, 2014, 2015, 2016, 2017, 2018, 2019]
    for agency in df_department_agg[2019]['DepartmentNumber-Numéro-de-Ministère'].iloc[active_rows]:
        lines[agency] = {'2013': 0, '2014': 0, '2015': 0, '2016': 0, '2017': 0, '2018': 0, '2019': 0}
        for year in years_list:
            lines[agency][str(year)] = df_department_agg[year].loc[[agency]]['AGRG_PYMT_AMT']
    print("HERE")
    print(lines)
    data = [
        dict(
            x=years_list,
            y=list(lines.values())
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


@app.callback(
    Output(component_id='test', component_property='children'),
    [Input(component_id='table', component_property='selected_rows')],
)
def update_output_div(input_value):
    return input_value


@app.callback(
    Output(component_id='url', component_property='pathname'),
    [Input(component_id='table_fed', component_property='active_cell')]
)
def find_active_cell_fed(active_cell):
    if active_cell['column'] == 1:
        return '/department/Department_of_Defence'


@app.callback(
    Output(component_id='content', component_property='children'),
    [Input(component_id='url', component_property='pathname')]
)
def load_page(url):
    if url == '/':
        return federal_page
    format_url = url.split('/')
    if format_url[1] == 'federal':
        return federal_page
    elif format_url[1] == 'department':
        return create_department_page(format_url[2], df)
    elif format_url[1] == 'program':
        return create_program_page(format_url[2], df)
    elif format_url[1] == 'business':
        return create_business_page(format_url[2], df)
    else:
        return '404'


if __name__ == '__main__':
    # ts = TimeSeries(key='TRNGRDL7KZKFC5SD', output_format='pandas')
    # data, meta_data = ts.get_monthly(symbol='MSFT')
    # print(data)
    app.run_server(debug=True)
