import logging
import time

from flask import Blueprint
from flask import render_template
from flask import request
import requests

from cryptography.fernet import Fernet
from supabase_py import create_client, Client

from flaskr import config
from flaskr import forms


bp = Blueprint('auth', __name__)

SCOPE = 'read,activity:write,activity:read,activity:read_all'
# TODO update scope
# will eventualy need activity write
# if you don't provide 'read', 'read' will be appended in the response, so for simplicity, just doing a string comparison here rather than a set comparison - assuming order of permissions is consistent


def auth_url() -> str:
    ''' Generates the url used to authenticate new Strava users

    Returns:
        A Strava OAuth url
    '''
    try:
        auth_endpoint = 'https://www.strava.com/oauth/authorize'
        redirect_uri = config.SERVER_DOMAIN + '/auth'
        response_type = 'code'
        scope = SCOPE
        return f'{auth_endpoint}?client_id={config.STRAVA_CLIENT_ID}&redirect_uri={redirect_uri}&response_type={response_type}&scope={scope}'

    except Exception as e:
        logging.error('error creating redirect url:')
        logging.error(e)
        return None


def create_db_conn() -> Client:
    ''' Creates a connection to Supabase

    Returns:
        A Supabase Client
    '''
    try:
        logging.info('connecting to db...')
        supabase_url = config.SUPABASE_URL
        supabase_key = config.SUPABASE_KEY
        supabase: Client = create_client(supabase_url, supabase_key)
        logging.info('connected to db!')
        return supabase
    except Exception as e:
        logging.error('error creating connection to database:')
        logging.error(e)
    return None


def insert_record(supabase: Client, table_name: str, query: dict) -> None:
    ''' Inserts a record into a table

    Args:
        supabase:
            connection to Supabase
        table_name:
            the name of the Supabase table
        query:
            the object to be inserted
    '''
    try:
        supabase.table(table_name).insert(query).execute()
    except Exception as e:
        logging.error(f'error inserting records into {table_name}:')
        logging.error(query)
        logging.error(e)


def insert_access_token(supabase: Client, athlete_id: int, access_token: str, expires_at: int) -> None:
    ''' Stores a new access_token

    Args:
        supabase:
            connection to Supabase
        athlete_id:
            the id of the athlete
        access_token:
            the access_token
        expires_at:
            when this access_token expires (unix time)A
    '''
    insert_query = {
        'athlete_id': athlete_id,
        'access_token_code': access_token,
        'expires_at': expires_at
    }
    insert_record(supabase, 'access_token', insert_query)


def insert_refresh_token(supabase: Client, athlete_id: int, refresh_token: str) -> None:
    ''' Stores a new refresh_token

    Args:
        supabase:
            connection to Supabase
        athlete_id:
            the id of the athlete
        access_token:
            the access_token
        expires_at:
            when this access_token expires (unix time)A
    '''
    insert_query = {
        'athlete_id': athlete_id,
        'refresh_token_code': refresh_token,
        'created_at': round(time.time())
    }
    insert_record(supabase, 'refresh_token', insert_query)


def insert_scope_record(supabase: Client, athlete_id: int, scope: str) -> None:
    ''' Stores a new scope record

    Args:
        supabase:
            connection to Supabase
        athlete_id:
            the id of the athlete
        scope:
            the access level this athlete authorized
    '''
    insert_query = {
        'athlete_id': athlete_id,
        'scope': scope
    }
    insert_record(supabase, 'scope_record', insert_query)


def insert_strava_credential(supabase: Client, athlete_id: int, encrypted_email: bytes, encrypted_password: bytes) -> None:
    ''' Stores a new set of encrypted credentials

    Args:
        supabase:
            connection to Supabase
        athlete_id:
            the id of the athlete
        encrypted_email:
            this athlete's email, encrypted
        encrypted_password:
            this athlete's password, encrypted
    '''
    insert_query = {
        'athlete_id': athlete_id,
        'email': encrypted_email,
        'password': encrypted_password
    }
    # key = Fernet.generate_key()  # probably going to use a secret here to store the key
    # fernet = Fernet(key)
    # encrypted_email = fernet.encrypt(
    #     bytes(form.email.data, 'utf-8'))
    # encrypted_password = fernet.encrypt(
    #     bytes(form.password.data, 'utf-8'))
    insert_record(supabase, 'strava_credential', insert_query)


def update_access_token(supabase: Client, athlete_id: int, access_token: str, expires_at: int) -> None:
    ''' Inserts a  access_token record

    TODO: Modify once updates are supported by Supabase

    Explanation: Since Supabase doesn't support UPDATEs yet, update_access_token(...) will
        just insert, and we will perform some extra logic to clean expired access tokens and
        retreive the latest access token when we query

    Args:
        supabase:
            connection to Supabase
        athlete_id:
            the id of the athlete
        access_token:
            the access_token
        expires_at:
            when this access_token expires (unix time)A
    '''
    try:
        # update_query = f"UPDATE access_token SET access_token='{access_token}', expires_at={expires_at} WHERE athlete_id={athlete_id};"
        insert_access_token(supabase, athlete_id, access_token, expires_at)
    except Exception as e:
        logging.error('error updating access_token:')
        logging.error(e)


def update_refresh_token(supabase: Client, athlete_id: int, refresh_token: str) -> None:
    ''' Inserts a new refresh_token record

    TODO: Modify once updates are supported by Supabase

    Explanation: Same as above

    Args:
        supabase:
            connection to Supabase
        athlete_id:
            the id of the athlete
        refresh_token:
            the refresh_token
    '''
    try:
        # update_query = f"UPDATE refresh_token SET refresh_token='{refresh_token}' WHERE athlete_id={athlete_id};"
        insert_refresh_token(supabase, athlete_id, refresh_token)
    except Exception as e:
        logging.error('error updating refresh_token:')
        logging.error(e)


def update_strava_credential(supabase: Client, athlete_id: int, email: str, password: str) -> None:
    '''
    TODO
    update strava credentials if current credentails are no longer valid
    probably send email to user and provide link to html form where they update credentials
    '''
    pass


def token_exchange(code: str, scope: str) -> int:
    ''' Requests and stores refresh and access tokens from Strava

    Args:
        code:
            a string provided by Strava used to authenticate this user

    Returns:
        the athlete_id of the user exchanging tokens
    '''
    try:
        url = 'https://www.strava.com/oauth/token'
        data = {
            'client_id': config.STRAVA_CLIENT_ID,
            'client_secret': config.STRAVA_CLIENT_SECRET,
            'code': code,
            'grant_type': 'authorization_code'
        }
        response = requests.post(data=data, url=url)
        if response.ok:
            obj = response.json()
            athlete_id = obj['athlete']['id']
            expires_at = obj['expires_at']
            refresh_token = obj['refresh_token']
            access_token = obj['access_token']
            # token_type = obj['token_type']  # TODO
            try:
                supabase = create_db_conn()
                insert_access_token(supabase, athlete_id,
                                    access_token, expires_at)
                insert_refresh_token(supabase, athlete_id, refresh_token)
                insert_scope_record(supabase, athlete_id, scope)
                logging.info('user authenticated successfully!')
                return athlete_id
            except Exception as e:
                logging.error(
                    'error establishing initial connecting with database:')
                logging.error(e)
        else:
            logging.error('token exchange failed:')
            logging.error(response.status_code)
            logging.error(response.json())
    except Exception as e:
        logging.error('error exchanging token:')
        logging.error(e)


def get_latest_refresh_token(supabase: Client, athlete_id: int) -> str:
    ''' Gets the youngest refresh_token for this athlete

    Args:
        supabase:
            connection to Supabase
        athlete_id:
            the id of the athlete

    Returns: The refresh token
    '''
    # TODO - this method will no longer be needed once UPDATEs are functional
    data = supabase.table('refresh_token').select('*').execute()['data']
    created_at = 0
    refresh_token = None
    for record in data:
        if record['athlete_id'] == athlete_id and record['created_at'] > created_at:
            created_at, refresh_token = record['created_at'], record['refresh_token_code']
    return refresh_token
    # TODO add None handling


def request_new_access_token(supabase: Client, athlete_id: int) -> str:
    ''' Requests a new access_token from Strava (access_tokens are short lived with a 6 hour life)

    Args:
        supabase:
            connection to Supabase
        athlete_id:
            the id of the athlete
    Returns:
        the requested access_token
    '''
    try:
        # TODO: once functionality is added for completing more advanced queries, rewrite this
        # refresh_token_query = f'SELECT refresh_token FROM refresh_token WHERE athlete_id={athlete_id};'
        data = supabase.table('refresh_token').select('*').execute()['data']
        refresh_token = get_latest_refresh_token(supabase, athlete_id)
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
                update_access_token(supabase, athlete_id,
                                    access_token, expires_at)
                if refresh_token != get_latest_refresh_token(supabase, athlete_id):
                    update_refresh_token(supabase, athlete_id, refresh_token)
                    logging.info('successfully refreshed refresh token')
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
    return None


def get_latest_access_token(supabase: Client, athlete_id: int):
    # def get_latest_access_token(supabase: Client, athlete_id: int) -> tuple[int, str]:
    ''' Gets the youngest access token for this user

    Args:
        supabase:
            connection to Supabase
        athlete_id:
            the id of the athlete
    Returns:
        The access_token and expiration time
    '''
    # TODO - this method will no longer be needed once UPDATEs are functional
    # expires_at_access_token_query = f'SELECT expires_at, access_token FROM access_token WHERE athlete_id={athlete_id};'
    data = supabase.table('access_token').select('*').execute()['data']
    expires_at = 0
    access_token = None
    for record in data:
        if record['athlete_id'] == athlete_id and record['expires_at'] > expires_at:
            expires_at, access_token = record['expires_at'], record['access_token_code']
    return expires_at, access_token
    # TODO add None handling


def get_access_token(supabase: Client, athlete_id: int) -> str:
    ''' Gets an access_token for the athlete

    Args:
        supabase:
            connection to Supabase
        athlete_id
            the id of the athlete

    Returns:
        The existing access_token if it isn't dead.
        Otherwise requests a new access_token and updates database
    '''
    # TODO: 'updates db appropriately' is a bit misleading above; see above update_access_token(...)
    logging.info(f'Getting access token for athlete: {athlete_id}')
    try:
        expires_at, access_token = get_latest_access_token(
            supabase, athlete_id)
        if expires_at < round(time.time()):
            access_token = request_new_access_token(supabase, athlete_id)
        if access_token:
            return access_token
    except Exception as e:
        logging.error('error getting access_token:')
        logging.error(e)
    return None


def get_athlete_scope(supabase: Client, athlete_id: int) -> str:
    ''' Gets the access level authorized by this athlete

    Args:
        supabase:
            connection to Supabase
        athlete_id:
            the id of the athlete
    Returns:
        The scope string
    '''
    try:
        scope = supabase.table('scope_record').select('scope').eq(
            'athlete_id', str(athlete_id)).execute()['data'][0]['scope']
        return scope
    except Exception as e:
        logging.error('error getting athlete scope')
        logging.error(e)
    return None


def get_strava_credential(supabase: Client, athlete_id: int) -> tuple:
    ''' Gets the email and password for this athlete

    Args:
        supabase:
            connection to Supabase
        athlete_id:
            the id of the athlete
    Returns:
        This athlete's (email, password)
    '''
    try:
        tup = supabase.table('strava_credential').select('email, password').eq(
            'athlete_id', str(athlete_id)).execute()['data'][0]
        email, password = tup['email'], tup['password']
        # TODO decrypt
        return (email, password)
    except Exception as e:
        logging.error('error getting strava credentials')
        logging.error(e)
    return None


def verify_strava_creds(email: str, password: str) -> bool:
    ''' Determines if the provided email and password are valid Strava credentials

    '''
    # selenium work here
    # attempt to login
    # grab class at top
    return email and password


@bp.route('/auth', methods=['GET', 'POST'])
def auth():
    '''
    Strava auth redirect
    '''
    form = forms.StravaCredsForm()
    if request.method == 'POST':
        if form.validate():  # also form.validate_on_submit which checks post and validate - might want?
            email, password = form.email.data, form.password.data
            if verify_strava_creds(email, password):
                # insert_strava_credential(
                #     athlete_id, encrypted_email, encrypted_password)
                pass
            status = 'success'
        else:
            # TODO CLEAN
            return render_template('auth.html', title='Authorization', status='missing creds', form=form)

        return render_template('auth.html', title='Authorization', status=status)

    else:
        code = request.args.get('code')
        error = request.args.get('error')
        scope = request.args.get('scope')
        status = ''
        if scope == SCOPE:
            form.athlete_id.data = token_exchange(code, scope)
            status = 'good scope'
        else:
            status = 'bad scope'
        if error:
            status = 'error'
        # TODO: dynamic title here? - for template
        return render_template('auth.html', title='Authorization', status=status, auth_url=auth_url(), form=form)
