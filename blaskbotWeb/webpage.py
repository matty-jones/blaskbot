import flask
alerts = flask.Flask(__name__)


@alerts.route('/')
def render():
    return flask.render_template('./alert.html')

if __name__ == '__main__':
    alerts.run(debug=True, port=1234)
