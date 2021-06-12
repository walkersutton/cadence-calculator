from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import json
import os
import requests

CLIENT_ID = os.environ.get('CADENCE_CALCULATOR_CLIENT_ID')
CLIENT_SECRET = os.environ.get('CADENCE_CALCULATOR_CLIENT_SECRET')
AUTH_URL = 'https://www.strava.com/oauth/authorize?client_id=65000&redirect_uri=http://cadencecalculator.herokuapp.com/auth&response_type=code&scope=read_all'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////app/tokens.db'
db = SQLAlchemy(app)

class Access(db.Model):
    __tablename__ = 'access_token'
    access_token = db.Column(
        db.String(64),
        index=True)
    athlete_id = db.Column(
        db.Integer,
        primary_key=True)
    expires_at = db.Column(
        db.Integer,
        index=True) 
    scope = db.Column(
        db.Boolean)

class Refresh(db.Model):
    __tablename__ = 'refresh_token'
    athlete_id = db.Column(
        db.Integer,
        db.ForeignKey('access_token.athlete_id'),
        primary_key=True)
    refresh_token = db.Column(
        db.String(64),
        index=True)
    scope = db.Column(db.Boolean)

def token_exchange(code, scope):
    url = 'https://www.strava.com/oauth/token'
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code'
    }
    print(data)
    response = requests.post(url=url, data=data)
    if response.status_code == 200:
        obj = response.json()
        athlete_id = obj['athlete']['id']
        expires_at = obj['expires_at']
        refresh_token = obj['refresh_token']
        access_token = obj['access_token']
        token_type = obj['token_type']

        access_entry = Access(access_token=access_token, athlete_id=athlete_id, expires_at=expires_at, scope=scope)
        refresh_entry = Refresh(athlete_id=athlete_id, refresh_token=refresh_token, scope=scope) 
        db.session.add(access_entry)
        db.session.add(refresh_entry)
        db.session.commit()
    else:
        print('bad token exchange')
        print(response.status_code)
        print(response.json())

# @app.route('/getmsg/', methods=['GET'])
# def respond():
#     # Retrieve the name from url parameter
#     name = request.args.get("name", None)
# 
#     # For debugging
#     print(f"got name {name}")
# 
#     response = {}
# 
#     # Check if user sent a name at all
#     if not name:
#         response["ERROR"] = "no name found, please send a name."
#     # Check if the user entered a number not a name
#     elif str(name).isdigit():
#         response["ERROR"] = "name can't be numeric."
#     # Now the user entered a valid name
#     else:
#         response["MESSAGE"] = f"Welcome {name} to our awesome platform!!"
# 
#     # Return the response in json format
#     return jsonify(response)
# 
# @app.route('/post/', methods=['POST'])
# def post_something():
#     param = request.form.get('name')
#     print(param)
#     # You can add the test cases you made in the previous function, but in our case here you are just testing the POST functionality
#     if param:
#         return jsonify({
#             "Message": f"Welcome {name} to our awesome platform!!",
#             # Add this option to distinct the POST request
#             "METHOD" : "POST"
#         })
#     else:
#         return jsonify({
#             "ERROR": "no name found, please send a name."
#         })

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
    if error:
        status = 'error'
    else:
        if given_scope == required_scope:
            status  = 'success'
            token_exchange(code, True)
        else:
            status = 'insufficient authorization'
            token_exchange(code, False)
    
    return render_template('auth.html', status=status, auth_url=AUTH_URL)


if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
