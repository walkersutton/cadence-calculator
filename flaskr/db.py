import logging
import time

from cryptography import Fernet
from supabase_py import create_client, Client

from flaskr import auth, config


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


def update_record(supabase: Client, table_name: str, query: dict, key: str, id: int) -> None:
    ''' Updates a record into a table

    Args:
        supabase:
            connection to Supabase
        table_name:
            the name of the Supabase table
        query:
            the object to be updated
        key:
            the column name of the key
        id:
            the value of the record's key to be update
    '''
    try:
        supabase.table(table_name).update(query).eq(key, id).execute()
    except Exception as e:
        logging.error(f'error updating records in {table_name}')
        logging.error(f'query: {query}')
        logging.error(f'key: {key}')
        logging.error(f'id: {id}')
        logging.error(e)


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
            access_token = auth.request_new_access_token(supabase, athlete_id)
        if access_token:
            return access_token
    except Exception as e:
        logging.error('error getting access_token:')
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


def update_access_token(supabase: Client, athlete_id: int, access_token: str, expires_at: int) -> None:
    ''' Updates an access_token record

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
        update_query = {
            'athlete_id': athlete_id,  # not sure i need this param
            'access_token_code': access_token,
            'expires_at': expires_at
        }
        update_record(supabase, 'access_token',
                      update_query, 'athlete_id', athlete_id)
        insert_access_token(supabase, athlete_id, access_token, expires_at)
    except Exception as e:
        logging.error('error updating access_token:')
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
    try:
        insert_query = {
            'athlete_id': athlete_id,
            'refresh_token_code': refresh_token,
            'created_at': round(time.time())
        }
        insert_record(supabase, 'refresh_token', insert_query)
    except Exception as e:
        logging.error(f'error inserting refresh token: {refresh_token}')
        logging.error(f'athlete_id: {athlete_id}')
        logging.error(e)


def update_refresh_token(supabase: Client, athlete_id: int, refresh_token: str) -> None:
    ''' Update a refresh_token record

    Args:
        supabase:
            connection to Supabase
        athlete_id:
            the id of the athlete
        refresh_token:
            the refresh_token
    '''
    try:
        update_query = {
            'athlete_id': athlete_id,  # might not need
            'refresh_token_code': refresh_token,
            'created_at': round(time.time())
        }
        update_record(supabase, 'refresh_token',
                      update_query, 'athlete_id', athlete_id)
    except Exception as e:
        logging.error(f'error updating refresh token: {refresh_token}')
        logging.error(f'athlete_id: {athlete_id}')
        logging.error(e)


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
        encrypted_email_bytes, encrypted_password_bytes = tup['email'].encode(
            'utf-8'), tup['password'].encode('utf-8')

        key = bytes(config.CIPHER_KEY, 'utf-8')
        fernet = Fernet(key)
        email = fernet.decrypt(encrypted_email_bytes)
        password = fernet.decrypt(encrypted_password_bytes)
        return (email, password)
    except Exception as e:
        logging.error('error getting strava credentials')
        logging.error(e)
    return None


def insert_strava_credential(supabase: Client, athlete_id: int, email: str, password: str) -> None:
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
    key = bytes(config.CIPHER_KEY, 'utf-8')
    fernet = Fernet(key)
    encrypted_email = fernet.encrypt(bytes(email, 'utf-8')).decode('utf-8')
    encrypted_password = fernet.encrypt(
        bytes(password, 'utf-8')).decode('utf-8')
    insert_query = {
        'athlete_id': athlete_id,
        'email': encrypted_email,
        'password': encrypted_password
    }
    insert_record(supabase, 'strava_credential', insert_query)


def update_strava_credential(supabase: Client, athlete_id: int, email: str, password: str) -> None:
    '''
    TODO
    update strava credentials if current credentails are no longer valid
    probably send email to user and provide link to html form where they update credentials
    '''
    pass
