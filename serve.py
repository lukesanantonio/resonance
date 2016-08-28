import flask
from werkzeug.datastructures import ImmutableDict

import sys

import flask_login

import argparse

import ssl
import sqlite3
import bcrypt

import oauth2client.client
import oauth2client.crypt

import requests

import user_match

app = flask.Flask(__name__)
app.secret_key = 'HDKaskjayuwq5163h1bdsbhfihds'

app.jinja_options = ImmutableDict({'extensions':
    ['jinja2.ext.autoescape', 'jinja2.ext.with_',
     'spaceless.SpacelessExtension']})

# Try to initialize SSL

# Get credentials to the server.

conn = sqlite3.connect('resonance_db.sqlite3', check_same_thread=False)

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

    if user_data == None:
        return None

    ret = User(user_data[0], user_data[1], user_data[2], id)
    return ret

# == Spotify Credentials
SPOTIFY_CLIENT_ID = '642055f7320044edafd1d6290b5a4b57'
SPOTIFY_CLIENT_SECRET = '77d07dc919034af598c6b228475a9ec3'
SPOTIFY_REDIRECT_URL = 'http://www.redcrane.net/spotify_auth_callback'
SPOTIFY_USE_SCOPE = ('user-top-read ')

@app.route('/')
def index():
    return flask.render_template('user_sign_up.html')

def hash_passwd(passwd):
    bites = passwd.encode('utf-8')
    return bcrypt.hashpw(bites, bcrypt.gensalt())

def check_passwd(passwd, hashed):
    bites = passwd.encode('utf-8')
    return bcrypt.hashpw(bites, hashed.encode('utf-8')) == hashed

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
@flask_login.login_required
def spotify_auth():
    auth_url = ('https://accounts.spotify.com/authorize?client_id={}'
                '&response_type=code'
                '&redirect_uri={}'
                '&scope={}'
                '&state={}').format(SPOTIFY_CLIENT_ID, SPOTIFY_REDIRECT_URL,
                                    SPOTIFY_USE_SCOPE,
                                    flask_login.current_user.id)

    return flask.redirect(auth_url)

@app.route('/spotify_auth_callback', methods=['GET'])
def spotify_auth_callback():
    code = flask.request.args.get('code', None)
    if code == None:
        return 'Bad spotify for some reason'

    user = user_loader(flask.request.args.get('state', 0))

    if user == None:
        return 'Bad user id returned'
    flask_login.login_user(user)

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

    artists = tracks_res.json().get('items', [])
    artist_ids = [artist['id'] for artist in artists]

    top_artists = ''
    for id in artist_ids:
        top_artists = top_artists + ' ' + id

    top_artists = top_artists.strip()

    cur = conn.cursor()
    cur.execute('update users set top_artists = ? where id = ?',
                (top_artists, flask_login.current_user.id))
    conn.commit()
    cur.close()

    return str([artist['name'] for artist in artists])

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

user_matches = {}

@app.route('/me')
@flask_login.login_required
def me():
    sys.stderr.write(str(user_matches) + '\n')
    # Check match with others, then cache it
    cur_id = flask_login.current_user.id

    # See if it's already in the cache
    if cur_id in user_matches:
        matches = user_matches[cur_id]
        return flask.render_template('me.html', matches=matches)

    # Find the top artists of all users
    cur = conn.cursor()
    cur.execute('select id,top_artists from users')

    all_users_artists = cur.fetchall()
    cur.close()

    user_artists = {id: artists_str.split()
                    for id, artists_str in all_users_artists
                    if artists_str != None}

    our_matches, do_cache = user_match.match(user_artists, cur_id)

    # Cache if necessary
    if do_cache:
        user_matches[cur_id] = our_matches

    # Take the list of user ids and convert that to a list of names
    cur = conn.cursor()
    cur.execute('select id,first_name,last_name from users')
    user_names_tup = cur.fetchall()
    user_names = {id: first + ' ' + last for id, first, last in user_names_tup}
    artists_to_find = []
    match_names = []
    for match in our_matches:
        match.name = user_names[match.id]
        # For every matched artist
        for artist in match.artists:
            if artist not in artists_to_find:
                artists_to_find.append(artist)

    artist_names = {}
    for artist in artists_to_find:
        artist_obj_res = requests.get('https://api.spotify.com/v1/artists/'
                                      '{}'.format(artist))
        artist_names[artist] = artist_obj_res.json()['name']

        # Now update the artist for each match
        for match in our_matches:
            for i, artist in enumerate(match.artists):
                match.artists[i] = artist_names[artist]

    return flask.render_template('me.html', matches=our_matches)

@app.route('/logout')
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return 'Logged out'

@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized'

if __name__ == '__main__':
    app.run(debug=True)
