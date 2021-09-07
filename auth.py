from datetime import datetime
import json
import logging
import requests
import subprocess
import time

from supabase_py import create_client, Client
import config

# should we create a class with a Supabase Client as a property?

"""
returns: Strava OAuth URL
"""
def auth_url():
	try:
		auth_endpoint = 'https://www.strava.com/oauth/authorize'
		redirect_uri = config.SERVER_DOMAIN + '/auth'
		scope = 'activity:read_all'
		return f'{auth_endpoint}?client_id={config.STRAVA_CLIENT_ID}&redirect_uri={redirect_uri}&response_type=code&scope={scope}'
	except Exception as e:
		logging.error('error creating redirect url:')
		logging.error(e)

"""
Creates a connection to Supabase
returns: supabase Client object
"""
def create_db_conn():
	try:
		logging.info('connecting to db...')
		url = config.SUPABASE_URL
		key = config.SUPABASE_KEY
		supabase: Client = create_client(url, key)	
		logging.info('connected to db!')
		return supabase
	except Exception as e:
		logging.error('error creating connection to database:')
		logging.error(e)

# def get_query_values(cursor):
# # TODO deprecate?

#     try:
#         vals = []
#         for val in cursor:
#             vals.append(val)
#         if len(vals) > 0:
#             return vals[0]
#         else:
#             return vals
#     except Exception as e:
#         logging.error('error getting query value:')
#         logging.error(e)

"""
Executes and returns value of query in a tuple
If query doesn't match any rows, returns empty list
"""
# def execute_query(conn, query):
# # TODO deprecate?
#     try:
# 		# TODO
# 		# supabase
#         # cursor = conn.cursor()
#         # cursor.execute(query)
#         return get_query_values(cursor)
#     except Exception as e:
#         logging.error('error executing query:')
#         logging.error(query)
#         logging.error(e)

def commit_query(conn, query):
# TODO deprecate?
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit() 
    except Exception as e:
        logging.error('error comitting query:')
        logging.error(query)
        logging.error(e)

""" Inserts a new record into Supabase access_token table """
def insert_access_token(supabase, athlete_id, access_token, expires_at):
	try:
		insert_query = {
			'athlete_id': athlete_id,
			'access_token_code': access_token,
			'expires_at': expires_at
		}
		supabase.table('access_token').insert(insert_query).execute()
	except Exception as e:
		logging.error('error inserting access token:')
		logging.error(insert_query)
		logging.error(e)

""" Inserts a new record into Supabase refresh_token table """
def insert_refresh_token(supabase, athlete_id, refresh_token):
	try:
		insert_query = f"INSERT INTO refresh_token VALUES ({athlete_id}, '{refresh_token}');"
		insert_query = {
			'athlete_id': athlete_id,
			'refresh_token_code': refresh_token
		}
		supabase.table('refresh_token').insert(insert_query).execute()
	except Exception as e:
		logging.error('error inserting refresh token:')
		logging.error(insert_query)
		logging.error(e)

""" Inserts a new record into Supabase access_token table """
def update_access_token(supabase, athlete_id, access_token, expires_at):
# TODO: update once functionality changes
	try:
		# TODO: this is shit
		# Explanation: Since Supabase doesn't support UPDATEs yet, update_access_token(...) will just insert, and we will perform some extra logic to clean expired access tokens and retreive the latest access token when we query
		# update_query = f"UPDATE access_token SET access_token='{access_token}', expires_at={expires_at} WHERE athlete_id={athlete_id};"
		# update_query = {}
		insert_access_token(supabase, athlete_id, access_token, expires_at)
	except Exception as e:
		logging.error('error updating access_token:')
		# logging.error(update_query)
		logging.error(e)

""" Inserts a new record into Supabase refresh_token table """
def update_refresh_token(supabase, athlete_id, refresh_token):
	# TODO: update once functionality changes
	try:
		# TODO: this is shit
		# Explanation: same as above
		# update_query = f"UPDATE refresh_token SET refresh_token='{refresh_token}' WHERE athlete_id={athlete_id};"
		insert_refresh_token(supabase, athlete_id, refresh_token)
	except Exception as e:
		logging.error('error updating refresh_token:')
		# logging.error(update_query)
		logging.error(e)

"""
code:	a string provided by Strava used to authenticate this user

Attempts to request refresh and access tokens. If all goes well, these tokens are added to the database.
"""
def token_exchange(code):
    try:
        url = 'https://www.strava.com/oauth/token'
        data = {
            'client_id': config.STRAVA_CLIENT_ID,
            'client_secret': config.STRAVA_CLIENT_SECRET,
            'code': code,
            'grant_type': 'authorization_code'
        }
        response = requests.post(url=url, data=data)
        if response.ok:
            obj = response.json()
            athlete_id = obj['athlete']['id']
            expires_at = obj['expires_at']
            refresh_token = obj['refresh_token']
            access_token = obj['access_token']
            token_type = obj['token_type']
            try:
                supabase = create_db_conn()
                insert_access_token(supabase, athlete_id, access_token, expires_at)
                insert_refresh_token(supabase, athlete_id, refresh_token)
                logging.info('user authenticated successfully!')
            except Exception as e:
                logging.error('error establishing initial connecting with database:')
                logging.error(e)
        else:
            logging.error('token exchange failed:')
            logging.error(response.status_code)
            logging.error(response.json())
    except Exception as e:
        logging.error('error exchanging token:')
        logging.error(e)

"""
	Requests a new access token
	(access tokens are short lived with a 6 hour life)
	TODO 
	returns: a String representing the new access token
"""
def request_new_access_token(supabase, athlete_id):
	try:
		# TODO: once functionality is added for completing more advanced queries, rewrite this
		# refresh_token_query = f'SELECT refresh_token FROM refresh_token WHERE athlete_id={athlete_id};'
		data = supabase.table('refresh_token').select('*').execute()['data']
		refresh_token = None
		for record in data:
			if int(record['athlete_id']) == athlete_id:
				refresh_token = record['refresh_token_code']
				break
		data = {
            'client_id': config.STRAVA_CLIENT_ID,
            'client_secret': config.STRAVA_CLIENT_SECRET,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
		url = f'{config.API_ENDPOINT}/oauth/token'
		response = requests.post(data=data, url=url)
		if response.ok:
			obj = response.json()
			access_token = obj['access_token']
			expires_at = obj['expires_at']
			refresh_token = obj['refresh_token']
			try:
				supabase = create_db_conn()
				update_access_token(supabase, athlete_id, access_token, expires_at)
				update_refresh_token(supabase, athlete_id, refresh_token)
				logging.info('successfully refreshed access token')
				return access_token
			except Exception as e:
				logging.error('error updating tokens:')
				logging.error(e)
		else:
			logging.error('token refresh failed:')
			logging.error(response.status_code)
			logging.error(response.json())
	except Exception as e:
		logging.error('error requesting refresh token:')
		logging.error(e)

"""
Finds the youngest access token for this user
returns: the access token (String), and the expiration time(Integer)
"""
def get_latest_access_token(supabase, athlete_id):
# TODO - this method will no longer be needed once UPDATEs are functional
	# expires_at_access_token_query = f'SELECT expires_at, access_token FROM access_token WHERE athlete_id={athlete_id};'
	data = supabase.table('access_token').select('*').execute()['data']
	expires_at = 0
	access_token = ''	
	for record in data:
		if record['athlete_id'] == athlete_id and record['expires_at'] > expires_at:
			expires_at, access_token = record['expires_at'], record['access_token_code']
	return expires_at, access_token

"""
returns:	the existing short-lived access token if it isn't dead.
			Otherwise gets a new access token and updates db appropriately
"""
def get_access_token(athlete_id):
# TODO: 'updates db appropriately' is a bit misleading above; see above update_access_token(...)
    try:
        supabase = create_db_conn()
        expires_at, access_token = get_latest_access_token(supabase, athlete_id)
        if expires_at < round(time.time()):
            access_token = request_new_access_token(supabase, athlete_id)
        return access_token
    except Exception as e:
        logging.error('error getting access token:')
        logging.error(e)
