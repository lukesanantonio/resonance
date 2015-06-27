import flask
from werkzeug.datastructures import ImmutableDict

app = flask.Flask(__name__)

app.jinja_options = ImmutableDict({'extensions':
    ['jinja2.ext.autoescape', 'jinja2.ext.with_',
     'spaceless.SpacelessExtension']})

@app.route('/')
def index():
    return flask.render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
