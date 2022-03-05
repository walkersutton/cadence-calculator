import json
import logging

from flask import Blueprint
from flask import make_response
from flask import request
import requests

from flaskr.activities import Activity
from flaskr import config

bp = Blueprint('subscriptions', __name__)

# TODO add support for handling 429s
# https://developers.strava.com/docs/rate-limits/

# TODO is this an unused method? only appears to be called in tests; hmm....


def get_existing_subscriptions() -> dict:
    ''' Gets the subscriptions for this Strava client

    Returns:
        A list of subscription objects (this list should never have more than 1 item)
        Example:
        [
            {
                "id": 12345,
                "resource_state": 1,
                "application_id": 12345,
                "callback_url": "https://url.org/callback",
                "created_at": "1970-01-01T20:20:20Z",
                "updated_at": "2000-01-01T20:20:20Z"
            }
        ]
    '''
    try:
        url = f'{config.API_ENDPOINT}/push_subscriptions'
        data = {
            'client_id': config.STRAVA_CLIENT_ID,
            'client_secret': config.STRAVA_CLIENT_SECRET
        }
        response = requests.get(url=url, data=data)
        if response.ok:
            return response.json()
        else:
            logging.error(response.json())
            return get_existing_subscriptions[0]['id']
    except Exception as e:
        logging.error('error getting existing subscriptions:')
        logging.error(e)
    return None


def get_subscription_id() -> int:
    ''' Gets the id of an available subscription (existing or new id) '''
    try:
        callback_url = config.SERVER_DOMAIN + '/subscribe'
        url = f'{config.API_ENDPOINT}/push_subscriptions'
        data = {
            'client_id': config.STRAVA_CLIENT_ID,
            'client_secret': config.STRAVA_CLIENT_SECRET,
            'callback_url': callback_url,
            'verify_token': config.VERIFY_TOKEN
        }
        logging.info(data)
        response = requests.post(data=data, url=url)
        # TODO rather than sending a post everytime to Strava, why don't we store subscription information? is this nonsensical?
        # or should we call get existing subscriptions first?????
        logging.warning(response.json())
        if response.ok:
            return response.json()['id']
        else:
            subs = get_existing_subscriptions()
            logging.warning('existing subscriptions:')
            logging.warning(subs)
            if len(subs) > 0:
                return subs[0]['id']
            else:
                logging.error('cannot get subscription')
                return 'errorrrrrrrr_id'
    except Exception as e:
        logging.error('error getting subscription id:')
        logging.error(e)
    return 'errorrrrrrrr_id'


def delete_subscription(subscription_id: int) -> bool:
    ''' Deletes the subscription with the given subscription_id

    Args:
        subscription_id:
            The id of the subscription to be deleted
    Returns:
        Whether or not the subscription was deleted
    '''
    try:
        url = f'{config.API_ENDPOINT}/push_subscriptions/{subscription_id}'
        data = {
            'client_id': config.STRAVA_CLIENT_ID,
            'client_secret': config.STRAVA_CLIENT_SECRET
        }
        response = requests.delete(data=data, url=url)
        if response.ok:
            return True
        else:
            logging.error('error deleting subscription')
            logging.error(response.text)
            return False
    except Exception as e:
        logging.error('error performing subscription delete:')
        logging.error(e)
    return False


def handle_event(event: dict) -> str:
    ''' Handles users' activity & profile updates and acts accordingly

    Args:
        event:
            TODO

    Returns:
        returns the body of the response to be sent back...... TODO 
    '''
    response = {}
    try:
        object_type = event['object_type']
        object_id = event['object_id']
        aspect_type = event['aspect_type']
        owner_id = event['owner_id']
        # TODO: determine if we need a new token for user - not sure if this is relevant
        if object_type == 'activity' and aspect_type in ('create', 'update'):
            activity = Activity(object_id, owner_id)
            if activity:
                logging.info('simply testing this ish')
            # if activity.requires_cadence_data():
            #     # KUDOS WILL BE DELETED
            #     # IMAGES WILL BE DELETED
            #     logging.debug('handle_event triggered')
            #     logging.debug(f'owner_id: {owner_id}')
            #     logging.debug(f'object_type: {object_type}')
            #     logging.debug(activity.obj)
            #     if activity.replace_activity():
            #         response = {
            #             'status': 200,
            #             # could append upload id here, but not sure how accureate that'll be
            #             'body': 'activity successfully replaced'
            #         }
            #     else:
            #         response = {
            #             'status': 500,
            #             'body': 'error replacing activity'
            #         }
            #         # TODO change this ^ - look into what th eexpected response should be
            #         # maybe we want to store GPX so that we don't lose data - store with activity_id and athletE_id I guess?
            else:
                return 'activity already has cadence data'

    except Exception as e:
        logging.error('failed handling event:')
        logging.error(e)
        # TODO investigate this status - not sure if it's bogus or not
        response = {
            'status': 418,
            'body': 'error'
        }
    return json.dumps(response)


@bp.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    status_code = -1
    if request.method == 'GET':
        # subscription validation request
        try:
            # verify_token = request.args.get('hub.verify_token')
            logging.info(request.args)
            challenge = request.args.get('hub.challenge')
            body = json.dumps({'hub.challenge': challenge})
            status_code = 200
        except Exception as e:
            logging.error('error validating callback address')
            logging.error(e)
            body = "error handling GET request"
            status_code = 404
    elif request.method == 'POST':
        try:
            event = request.get_json()
            body = handle_event(event)
            status_code = 200
        except Exception as e:
            logging.error('error listening on webhooks endpoint')
            logging.error(e)
            body = "error handling POST request"
            status_code = 404

    response = make_response(body)
    response.status_code = status_code
    response.mimetype = 'application/json'
    return response
