from flask import Flask, jsonify, render_template, request
import json
import os
import psycopg2
import requests
import threading

CLIENT_ID = os.environ.get('CADENCE_CALCULATOR_CLIENT_ID')
CLIENT_SECRET = os.environ.get('CADENCE_CALCULATOR_CLIENT_SECRET')

# TODO - bring these into env vars
# maybe change user and db names on aws???
DBUSER ***REMOVED***
DBPASSWORD = '***REMOVED***'
DBNAME ***REMOVED***
DBHOST = '***REMOVED***'

# TODO - break auth_url into sub pieces, maybe make a simple fn auth_url()
# redirect_uri = 'http://localhost:5000/auth'
redirect_uri = 'https://cadencecalculator.herokuapp.com/auth'
AUTH_URL = 'https://www.strava.com/oauth/authorize?client_id=65000&redirect_uri=' + redirect_uri + '&response_type=code&scope=read_all'

app = Flask(__name__)

def create_db_conn():
    try:
        conn = psycopg2.connect(
            user=DBUSER,
            password=DBPASSWORD,
            host=DBHOST,
            dbname=DBNAME)
        return conn
    except Exception as e:
        print('error creating connection to database:')
        print(e)

def insert_access_token(conn, athlete_id, scope, access_token, expires_at):
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO access_tokens VALUES (%s, %s, %s, %s);", (athlete_id, scope, access_token, expires_at))
        conn.commit()
    except Exception as e:
        print('error populating access token:')
        print(e)

def insert_refresh_token(conn, athlete_id, code, scope):
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO refresh_tokens VALUES (%s, %s, %s);", (athlete_id, code, scope))
        conn.commit()
    except Exception as e:
        print('error populating refresh token:')
        print(e)

def token_exchange(code, scope):
    url = 'https://www.strava.com/oauth/token'
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code'
    }
    # if DEBUG: TODO if want to put debugs
    # print('token_exchange_data:')
    # print(data)
    response = requests.post(url=url, data=data)

    if response.status_code == 200:
        obj = response.json()
        athlete_id = obj['athlete']['id']
        expires_at = obj['expires_at']
        refresh_token = obj['refresh_token']
        access_token = obj['access_token']
        token_type = obj['token_type']
        try:
            conn = create_db_conn()
            insert_access_token(conn, athlete_id, scope, access_token, expires_at)
            insert_refresh_token(conn, athlete_id, code, scope)
        except Exception as e:
            print('error establishing initial connecting with database:')
            print(e)
    else:
        print('token exchange failed:')
        print(response.status_code)
        print(response.json())


# A welcome message to test our server
@app.route('/')
def index():
    return render_template('index.html', auth_url=AUTH_URL)

# strava Oauth redirect 
@app.route('/auth')
def auth():
    # TODO change to include activity:write eventually
    required_scope = {'read', 'read_all'}
    code = request.args.get('code')
    error = request.args.get('error')
    scope = request.args.get('scope')
    given_scope = set(scope.split(',')) if scope else {}
    status = ''
   
    if error:
        status = 'error'
    else:
        threading.Thread(target=token_exchange, args=(code, given_scope == required_scope)).start()
        status = 'success' if given_scope == required_scope else 'insufficient authorization'

    return render_template('auth.html', status=status, auth_url=AUTH_URL)


if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
