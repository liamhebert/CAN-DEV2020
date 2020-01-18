import flask
import dash
import dash_html_components as html
import requests

server = flask.Flask(__name__)

# API Requests for news div
news_requests = requests.get(
    "https://newsapi.org/v2/top-headlines?sources=bbc-news&apiKey=da8e2e705b914f9f86ed2e9692e66012"
)


@server.route('/')
def index():
    return 'Hello Flask app'

app = dash.Dash(
    __name__,
    server=server,
    routes_pathname_prefix='/dash/'
)

app.layout = html.Div("My Dash app")

if __name__ == '__main__':
    app.run_server(debug=True)
