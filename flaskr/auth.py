import functools
import logging
import time

from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
import requests
from supabase_py import create_client, Client
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from flaskr import config
from flaskr.db import get_db

bp = Blueprint("auth", __name__, url_prefix="/auth")

def auth_url() -> str:
    ''' Generates the url used to authenticate new Strava users

    Returns:
        A Strava OAuth url
    '''
    try:
        auth_endpoint = 'https://www.strava.com/oauth/authorize'
        redirect_uri = config.SERVER_DOMAIN + '/auth'
        # TODO update scope
        scope = 'activity:read_all'
        return f'{auth_endpoint}?client_id={config.STRAVA_CLIENT_ID}&redirect_uri={redirect_uri}&response_type=code&scope={scope}'
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


def token_exchange(code: str) -> None:
    ''' Requests and stores refresh and access tokens from Strava

    Args:
        code:
            a string provided by Strava used to authenticate this user
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
                logging.info('user authenticated successfully!')
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


def get_access_token(athlete_id: int) -> str:
    ''' Gets an access_token for the athlete

    Args:
        athlete_id
            the id of the athlete

    Returns:
        The existing access_token if it isn't dead.
        Otherwise requests a new access_token and updates database
    '''
    # TODO: 'updates db appropriately' is a bit misleading above; see above update_access_token(...)

    try:
        supabase = create_db_conn()
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
@bp.route('/auth')
def auth():
    '''
    Strava auth redirect
    '''
    # TODO change to include activity:write eventually
    required_scope = {'read', 'activity:read_all'}
    code = request.args.get('code')
    error = request.args.get('error')
    scope = request.args.get('scope')
    access_scope = set(scope.split(',')) if scope else {}
    status = ''

    if access_scope == required_scope:
        # token_exchange(code)
        status = 'success'
    else:
        status = 'insufficient authorization'
    if error:
        status = 'error'

    # TODO: dynamic title here? - for template
    return render_template('auth.html', title='Authorization', status=status, auth_url=auth_url())

def login_required(view):
    """View decorator that redirects anonymous users to the login page."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    """If a user id is stored in the session, load the user object from
    the database into ``g.user``."""
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = (
            get_db().execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
        )


@bp.route("/register", methods=("GET", "POST"))
def register():
    """Register a new user.

    Validates that the username is not already taken. Hashes the
    password for security.
    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                # The username was already taken, which caused the
                # commit to fail. Show a validation error.
                error = f"User {username} is already registered."
            else:
                # Success, go to the login page.
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    """Log in a registered user by adding the user id to the session."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None
        user = db.execute(
            "SELECT * FROM user WHERE username = ?", (username,)
        ).fetchone()

        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user["password"], password):
            error = "Incorrect password."

        if error is None:
            # store the user id in a new session and return to the index
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("index"))

        flash(error)

    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    """Clear the current session, including the stored user id."""
    session.clear()
    return redirect(url_for("index"))
