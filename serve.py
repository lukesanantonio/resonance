import flask
from werkzeug.datastructures import ImmutableDict

import argparse

import ssl
import pg8000
import bcrypt

import oauth2client.client
import oauth2client.crypt

app = flask.Flask(__name__)

app.jinja_options = ImmutableDict({'extensions':
    ['jinja2.ext.autoescape', 'jinja2.ext.with_',
     'spaceless.SpacelessExtension']})

# Try to initialize SSL
context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)

# Try to use ssl if we are given a certificate.
use_ssl = True
try:
    context.load_cert_chain('resonance.crt', 'resonance.key')
except FileNotFoundError:
    load_ssl = False

context.options |= ssl.OP_NO_SSLv2
context.options |= ssl.OP_NO_SSLv3

# Get credentials to the server.
parser = argparse.ArgumentParser(description='Initialize a DB.')
parser.add_argument('host')
parser.add_argument('user')
parser.add_argument('password')
parser.add_argument('db')

args = parser.parse_args()

conn = pg8000.connect(database=args.db, user=args.user, password=args.password,
                      host=args.host)
conn.autocommit = True

@app.route('/')
def index():
    return flask.render_template('user_sign_up.html')

@app.route('/login')
def login():
    return flask.render_template('login.html')

google_oauth_client_id = ('1006156623232-pk0jjnlkqib9chpa87vesh4j9v1jeafc'
                          '.apps.googleusercontent.com')

@app.route('/googletoken_login', methods=['POST'])
def googletoken_login():
    client = oauth2client.client
    crypt = oauth2client.crypt;

    token = flask.request.form['id_token']
    try:
        id_info = oauth2client.client.verify_id_token(token,
                                                      google_oauth_client_id)
        if id_info['aud'] is not google_oauth_client_id:
            raise crypt.AppIdentityError('Unrecognized client.')

        issuers = ['accounts.google.com', 'https://accounts.google.com']
        if id_info['iss'] not in issuers:
            raise crypt.AppIdentityError('Wrong Issuer.')

        if id_info['hd'] != APPS_DOMAIN_NAME:
            raise crypt.AppIdentityError('Wrong hosted domain.')
    except crypt.AppIdentityError:
        # Invalid token
        pass

    # We have a valid email.
    # Let's see if the user already signed up
    cur = conn.cursor()
    cur.execute('select * from users where email=%s', (id_info['email'],))
    user = cur.fetchone()

    return str(user[1])

@app.route('/user', methods=['POST'])
def new_user():
    request = flask.request

    # Hash our password
    bites = bytes(request.form['password'], 'utf-8')
    hashed = bcrypt.hashpw(bites, bcrypt.gensalt())

    # Insert the user into the database
    cur = conn.cursor()
    cur.execute('insert into users (first_name, last_name, email, password)'
                ' values (%s, %s, %s, %s) returning id',
                (request.form['first_name'], request.form['last_name'],
                 request.form['email'], hashed))
    conn.commit()
    user_id = cur.fetchone()[0]
    cur.close()

    # Redirect our new user to their new page.
    return flask.redirect('/user/' + str(user_id), code=303)

@app.route('/user/<int:u_id>')
def user_info(u_id):
    cur = conn.cursor()
    cur.execute('select * from users where id = %s', (u_id,))
    user = cur.fetchone()
    cur.close()
    # TODO: Make a user info page.
    return str(user[1])

if __name__ == '__main__':
    if use_ssl:
        app.run(ssl_context=context, debug=True)
    else:
        app.run(debug=True)
