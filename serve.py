import flask
from werkzeug.datastructures import ImmutableDict

import requests
import ssl

import oauth2client.client
import oauth2client.crypt

app = flask.Flask(__name__)

app.jinja_options = ImmutableDict({'extensions':
    ['jinja2.ext.autoescape', 'jinja2.ext.with_',
     'spaceless.SpacelessExtension']})

context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)

# Try to use ssl if we are given a certificate.
use_ssl = True
try:
    context.load_cert_chain('resonance.crt', 'resonance.key')
except FileNotFoundError:
    load_ssl = False

context.options |= ssl.OP_NO_SSLv2
context.options |= ssl.OP_NO_SSLv3

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
    return str(id_info)

@app.route('/user', methods=['POST'])
def new_user():
    r = requests.post('https://localhost:7677/user', data=flask.request.form,
                      verify='resonance.crt')
    return flask.redirect('/user/' + str(r.json()['user']), code=303)

@app.route('/user/<int:u_id>')
def user_info(u_id):
    r = requests.get('https://localhost:7677/user/' + str(u_id),
                     verify='resonance.crt')
    # TODO: Make a user info page.
    return str(r.json()['first_name'])

if __name__ == '__main__':
    if use_ssl:
        app.run(ssl_context=context, debug=True)
    else:
        app.run(debug=True)
