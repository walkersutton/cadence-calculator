from datetime import date
from flask import Flask, jsonify, render_template, request
import json
import os
import psycopg2
import requests
import subprocess
import threading

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

# rename client_id -> strava_id??
CLIENT_ID = os.environ.get('CADENCE_CALCULATOR_CLIENT_ID')
CLIENT_SECRET = os.environ.get('CADENCE_CALCULATOR_CLIENT_SECRET')

# TODO maybe change user and db names on aws???
DBHOST = os.environ.get('CADENCE_CALCULATOR_DBHOST')
DBNAME = os.environ.get('CADENCE_CALCULATOR_DBNAME')
DBPASSWORD = os.environ.get('CADENCE_CALCULATOR_DB_PASSWORD')
DBUSER = os.environ.get('CADENCE_CALCULATOR_DBUSER')

app = Flask(__name__)

def configure_aws():
    default = '[default]\n'
    subprocess.run(["mkdir", "~.aws/"])
    filenames = ['config', 'credentials']
    content = {
        'config': [default, 'region = us-east-1\n', 'output = json'],
        'credentials': [default, f'aws_access_key_id = {AWS_ACCESS_KEY_ID}\n', f'aws_secret_access_key = {AWS_SECRET_ACCESS_KEY}']
    }
    for filename in filenames:
        f = open(f'~.aws/{filename}', 'w')
        for line in content[filename]:
            f.write(line)
        f.close()

def auth_url():
    auth_endpoint = 'https://www.strava.com/oauth/authorize'
    redirect_uri = 'https://cadencecalculator.herokuapp.com/auth'
    client_id = 65000
    return f'{auth_endpoint}?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope={scope}'
    
def update_security_group():
    group_id = 'sg-4fa8883b'
    ip = json.loads(requests.get('https://httpbin.org/ip').text)['origin']
    description = '"Heroku public ip on ' + str(date.today()) + '"'
    cmd = "aws"
    params = f"ec2 authorize-security-group-ingress --group-id {group_id} --ip-permissions IpProtocol=tcp,FromPort=0,ToPort=65535,IpRanges='[{{CidrIp={ip}/32,Description={description}}}]"
    subprocess.run([cmd, params])

def create_db_conn():
    try:
        update_security_group()
        print('connecting to db')
        conn = psycopg2.connect(
            user=DBUSER,
            password=DBPASSWORD,
            host=DBHOST,
            dbname=DBNAME)
        print('connected to db!')
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
    return render_template('index.html', auth_url=auth_url())

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

    return render_template('auth.html', status=status, auth_url=auth_url())

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    configure_aws()
    app.run(threaded=True, port=5000)
