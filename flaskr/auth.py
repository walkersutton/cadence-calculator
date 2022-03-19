import logging
import time

from flask import Blueprint
from flask import render_template
from flask import request
import requests

from flaskr import config, db, forms, webdriver
from supabase import Client


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


def token_exchange(supabase: Client, code: str, scope: str) -> int:
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
                db.insert_access_token(supabase, athlete_id,
                                       access_token, expires_at)
                db.insert_refresh_token(supabase, athlete_id, refresh_token)
                db.insert_scope_record(supabase, athlete_id, scope)
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
    access_token = None
    try:
        # TODO: once functionality is added for completing more advanced queries, rewrite this
        # refresh_token_query = f'SELECT refresh_token FROM refresh_token WHERE athlete_id={athlete_id};'
        data = supabase.table('refresh_token').select('*').execute()['data']
        stored_refresh_token = db.get_refresh_token(supabase, athlete_id)
        data = {
            'client_id': config.STRAVA_CLIENT_ID,
            'client_secret': config.STRAVA_CLIENT_SECRET,
            'grant_type': 'refresh_token',
            'refresh_token': stored_refresh_token
        }
        url = f'{config.API_ENDPOINT}/oauth/token'
        response = requests.post(data=data, url=url)
        if response.ok:
            obj = response.json()
            access_token = obj['access_token']
            expires_at = obj['expires_at']
            refresh_token = obj['refresh_token']
            try:
                db.update_access_token(supabase, athlete_id,
                                       access_token, expires_at)
                if refresh_token != stored_refresh_token:
                    db.update_refresh_token(
                        supabase, athlete_id, refresh_token)
                    logging.info('successfully refreshed refresh token')
                logging.info('successfully refreshed access token')
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
    return access_token


def verify_strava_creds(athlete_id: int, email: str, password: str) -> Client:
    # TODO - bit of an awkward return - maybe add a flag to return active client / boolean?
    ''' Determines if the provided email and password are valid Strava credentials

    '''
    return webdriver.verify_strava_creds(athlete_id, email, password)


@bp.route('/auth', methods=['GET', 'POST'])
def auth():
    '''
    Strava auth redirect
    '''
    status = None
    form = forms.StravaCredsForm()
    form.athlete_id.data = 1
    if form.validate_on_submit():  # GOOD POST
        athlete_id, email, password = form.athlete_id.data, form.email.data, form.password.data
        driver = verify_strava_creds(athlete_id, email, password)
        if driver:
            driver.quit()
            status = 'good creds'
            supabase = db.create_db_conn()
            db.insert_strava_credential(
                supabase, athlete_id, email, password)
        else:
            status = 'bad creds'
    else:  # GET OR BAD POST
        code = request.args.get('code')
        error = request.args.get('error')
        scope = request.args.get('scope')
        if error:
            status = 'strava error'
        elif scope:  # return from strava
            if scope == SCOPE:
                supabase = db.create_db_conn()
                form.athlete_id.data = token_exchange(supabase, code, scope)
                status = 'good scope'
            else:
                status = 'bad scope'
        else:  # failed post
            # TODO verify that athlete_id is passed to template on retry
            status = 'bad form'

    # TODO dynamic title
    if not status:
        status = 'unknown'
    return render_template('auth.html', title='Authorization', status=status, auth_url=auth_url(), form=form)
