import logging
import time

from cryptography.fernet import Fernet
from supabase import create_client, Client

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


def update_record(supabase: Client, table_name: str, query: dict, key: str, val: str) -> None:
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
        val:
            the value of the record's key to be update
    '''
    try:
        supabase.table(table_name).update(query).eq(key, val).execute()
    except Exception as e:
        logging.error(f'error updating records in {table_name}')
        logging.error(f'query: {query}')
        logging.error(f'key: {key}')
        logging.error(f'val: {val}')
        logging.error(e)


def select_record(supabase: Client, table_name: str, columns: list, athlete_id: int) -> dict:
    ''' Selects a record from a table

    Args:
        supabase:
            connection to Supabase
        table_name:
            the name of the Supabase table
        columns:
            the columns to be selected
        athlete_id:
            the athlete_id of the athlete
        val:
            the value of the record's key to be update
    '''
    try:
        record = supabase.table(table_name).select(', '.join(columns)).eq(
            'athlete_id', str(athlete_id)).execute().data
        if record:
            return record[0]
        else:
            logging.error(f"select_record didn't select any records")
            logging.error(f'table_name: {table_name}')
            logging.error(f'columns: {", ".join(columns)}')
            logging.error(f'athlete_id: {athlete_id}')
    except Exception as e:
        logging.error(f'error selecting records from {table_name}')
        logging.error(f'columns: {", ".join(columns)}')
        logging.error(f'athlete_id: {athlete_id}')
        logging.error(e)
    return None


def update_record(supabase: Client, table_name: str, query: dict, key: str, val: str) -> None:
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
        val:
            the value of the record's key to be update
    '''
    try:
        supabase.table(table_name).update(query).eq(key, val).execute()
    except Exception as e:
        logging.error(f'error updating records in {table_name}')
        logging.error(f'query: {query}')
        logging.error(f'key: {key}')
        logging.error(f'val: {val}')
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
    logging.info(f'Getting access token for athlete: {athlete_id}')
    access_token = None
    try:
        data = select_record(supabase, 'access_token', [
                             'access_token_code', 'expires_at'], athlete_id)
        access_token, expires_at = data['access_token'], data['expires_at']
        if expires_at < round(time.time()):
            access_token = auth.request_new_access_token(supabase, athlete_id)
    except Exception as e:
        logging.error('error getting access_token:')
        logging.error(f'athlete_id: {athlete_id}')
        logging.error(f'data: {data}')
        logging.error(e)
    return access_token


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
                      update_query, 'athlete_id', str(athlete_id))
        insert_access_token(supabase, athlete_id, access_token, expires_at)
    except Exception as e:
        logging.error('error updating access_token:')
        logging.error(e)


def get_refresh_token(supabase: Client, athlete_id: int) -> str:
    ''' Gets the refresh_token for this athlete

    Args:
        supabase:
            connection to Supabase
        athlete_id:
            the id of the athlete

    Returns: The refresh token
    '''
    refresh_token_code = None
    try:
        data = select_record(supabase, 'refresh_token', [
                             'refresh_token_code'], athlete_id)['']
        refresh_token_code = data['refresh_token_code']
    except Exception as e:
        logging.error(f'error getting refresh token for athlete {athlete_id}')
        logging.error(f'data: {data}')
        logging.error(e)
    return refresh_token_code
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
                      update_query, 'athlete_id', str(athlete_id))
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
    scope = None
    try:
        data = select_record(supabase, 'scope_record', ['scope'], athlete_id)
        scope = data['scope']
    except Exception as e:
        logging.error('error getting athlete scope')
        logging.error(f'data: {data}')
        logging.error(f'athlete_id: {athlete_id}')
        logging.error(e)
    return scope


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
        data = select_record(supabase, 'strava_credential', [
                             'email', 'password'], athlete_id)
        encrypted_email_bytes, encrypted_password_bytes = data['email'].encode(
            'utf-8'), data['password'].encode('utf-8')

        key = bytes(config.CIPHER_KEY, 'utf-8')
        fernet = Fernet(key)
        email = fernet.decrypt(encrypted_email_bytes)
        password = fernet.decrypt(encrypted_password_bytes)
        return (email, password)
    except Exception as e:
        logging.error('error getting strava credentials')
        logging.error(f'data: {data}')
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
    key = bytes(config.CIPHER_KEY, 'utf-8')
    fernet = Fernet(key)
    encrypted_email = fernet.encrypt(bytes(email, 'utf-8')).decode('utf-8')
    encrypted_password = fernet.encrypt(
        bytes(password, 'utf-8')).decode('utf-8')
    update_query = {
        'athlete_id': athlete_id,
        'email': encrypted_email,
        'password': encrypted_password
    }
    update_record(supabase, 'strava_credential',
                  update_query, 'athlete_id', athlete_id)


def set_strava_credential(supabase: Client, athlete_id: int, email: str, password: str) -> None:
    '''
    TODO
    '''
    if get_strava_credential(supabase, athlete_id):
        update_strava_credential(supabase, athlete_id, email, password)
    else:
        insert_strava_credential(supabase, athlete_id, email, password)
