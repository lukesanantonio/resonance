import flask
from werkzeug.datastructures import ImmutableDict

import flask_login

import argparse

import ssl
import sqlite3
import bcrypt

import oauth2client.client
import oauth2client.crypt

import requests

app = flask.Flask(__name__)
app.secret_key = 'HDKaskjayuwq5163h1bdsbhfihds'

app.jinja_options = ImmutableDict({'extensions':
    ['jinja2.ext.autoescape', 'jinja2.ext.with_',
     'spaceless.SpacelessExtension']})

# Try to initialize SSL
context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)

# Try to use ssl if we are given a certificate.
use_ssl = False
try:
    context.load_cert_chain('resonance.crt', 'resonance.key')
except FileNotFoundError:
    load_ssl = False

context.options |= ssl.OP_NO_SSLv2
context.options |= ssl.OP_NO_SSLv3

# Get credentials to the server.
parser = argparse.ArgumentParser(description='Initialize a DB.')
parser.add_argument('db')

args = parser.parse_args()

conn = sqlite3.connect(args.db, check_same_thread=False)

# Initialize Redis
#redis = redis.StrictRedis(host='50.30.35.9', port=3365,
#                          password='57f30b0a8da8fbf9f25ae046be3c2135')

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

class User(flask_login.UserMixin):
    def __init__(self, first, last, email, id):
        self.first_name = first
        self.last_name = last
        self.email = email
        self.id = id

@login_manager.user_loader
def user_loader(id):
    id = int(id)

    cur = conn.cursor()
    cur.execute('select first_name,last_name,email from users '
                'where id = ?', (id,))
    user_data = cur.fetchone()
    cur.close()

    ret = User(user_data[0], user_data[1], user_data[2], id)
    return ret

# == Spotify Credentials
SPOTIFY_CLIENT_ID = '642055f7320044edafd1d6290b5a4b57'
SPOTIFY_CLIENT_SECRET = '77d07dc919034af598c6b228475a9ec3'
SPOTIFY_REDIRECT_URL = 'http://localhost:5000/spotify_auth_callback'
SPOTIFY_USE_SCOPE = ('playlist-read-private '
                     'streaming '
                     'user-follow-modify '
                     'user-top-read ')

@app.route('/')
def index():
    return flask.render_template('user_sign_up.html')

def hash_passwd(passwd):
    bites = bytes(passwd, 'utf-8')
    return bcrypt.hashpw(bites, bcrypt.gensalt())

def check_passwd(passwd, hashed):
    bites = bytes(passwd, 'utf-8')
    return bcrypt.hashpw(bites, hashed) == hashed

# Registers a new user and returns that new user's id.
def register_user(first_name, last_name, email, password=None,
                  cursor=None):
    if cursor == None:
        cursor = conn.cursor()

    cursor.execute('insert into users (first_name, last_name, email,'
                   ' password) values (?, ?, ?, ?)',
                   (first_name, last_name, email, password))

    cursor.execute('select last_insert_rowid() from users')
    conn.commit()

    user_id = cursor.fetchone()[0]
    cursor.close()

    return User(first_name, last_name, email, user_id)

@app.route('/spotify_auth', methods=['GET'])
def spotify_auth():
    auth_url = ('https://accounts.spotify.com/authorize?client_id={}'
                '&response_type=code'
                '&redirect_uri={}'
                '&scope={}').format(SPOTIFY_CLIENT_ID, SPOTIFY_REDIRECT_URL,
                                    SPOTIFY_USE_SCOPE)

    return flask.redirect(auth_url)

@app.route('/spotify_auth_callback', methods=['GET'])
def spotify_auth_callback():
    code = flask.request.args.get('code', None)
    if code == None:
        return

    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': SPOTIFY_REDIRECT_URL,
        'client_id': SPOTIFY_CLIENT_ID,
        'client_secret': SPOTIFY_CLIENT_SECRET
    }
    res = requests.post('https://accounts.spotify.com/api/token',
                        data=token_data)
    res.raise_for_status()

    # Find the top fifty tracks now
    headers = {
        'Authorization': 'Bearer ' + res.json()['access_token']
    }
    tracks_res = requests.get('https://api.spotify.com/v1/me/top/artists?'
                              'limit=50&time_range=medium_term',
                              headers=headers)

    tracks = tracks_res.json().get('items', [])
    track_names = [track['name'] for track in tracks]

    return str(track_names)

@app.route('/user', methods=['POST'])
def new_user():
    request = flask.request

    hashed = hash_passwd(request.form['password'])

    # Insert the user into the database
    user = register_user(request.form['first_name'],
                         request.form['last_name'],
                         request.form['email'], hashed)

    flask_login.login_user(user);

    # Redirect our new user to their new page.
    return flask.redirect('/user/' + str(user.id), code=303)

@app.route('/user/<int:u_id>')
def user_info(u_id):
    cur = conn.cursor()
    cur.execute('select * from users where id = ?', (u_id,))
    user = cur.fetchone()

    if user == None:
        return 'Bad user'

    cur.close()

    user = {
        'first_name': user[1],
        'last_name': user[2],
        'email': user[3]
    }

    return flask.render_template('user_info.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return flask.render_template('login.html')
    else:
        email = flask.request.form['email']

        # Find user id and hashed password
        cur = conn.cursor()
        cur.execute('select * from users where email = ?',
                    (email,))
        # We get back something like (1,'BCRYPTPASS')
        user_data = cur.fetchone()
        cur.close()

        user = User(user_data[1], user_data[2], user_data[3], user_data[0])

        is_authenticated = check_passwd(flask.request.form['password'],
                                        user_data[4])

        if not is_authenticated:
            return 'Fail'
        else:
            flask_login.login_user(user)
            return 'Success Login'

@app.route('/me')
@flask_login.login_required
def me():
    return flask.render_template('me.html')

@app.route('/logout')
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return 'Logged out'

@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized'

if __name__ == '__main__':
    if use_ssl:
        app.run(ssl_context=context, debug=True)
    else:
        app.run(debug=True)
