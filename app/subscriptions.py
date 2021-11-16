import json
import logging
import sys

import requests

from app.activities import Activity
import app.config as config

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
            logging.error(response.text)
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
        response = requests.post(data=data, url=url)
        # TODO rather than sending a post everytime to Strava, why don't we store subscription information? is this nonsensical?
        if response.ok:
            return response.json()['id']
        else:
            return get_existing_subscriptions()[0]['id']
    except Exception as e:
        logging.error('error getting subscription id:')
        logging.error(e)
    return None


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


def handle_event(event: str) -> str:
    ''' Handles users' activity & profile updates and acts accordingly

    Args:
        event:
            TODO

    Returns:
        returns the body of the response to be sent back...... TODO 
    '''
    response = {}
    try:
        event = json.loads(event)
        object_type = event['object_type']
        object_id = event['object_id']
        aspect_type = event['aspect_type']
        owner_id = event['owner_id']
        # TODO: determine if we need a new token for user - not sure if this is relevant
        if object_type == 'activity' and aspect_type in ('create', 'update'):
            activity = Activity(object_id, owner_id)
            if activity.requires_cadence_data():
                # KUDOS WILL BE DELETED
                # IMAGES WILL BE DELETED
                logging.debug('handle_event triggered')
                logging.debug(f'owner_id: {owner_id}')
                logging.debug(f'object_type: {object_type}')
                logging.debug(activity.obj)
                if not activity.replace_activity():
                    response = {
                        'status': 200,
                        'body': 'something happened, but little descipriotn . ya done goofed - TODO might neeed to change this body? but also jsut might not matter?'
                    }
                else:
                    logging.error('handle_event: error replacing activity')
                    return None
                    # TODO change this ^ - look into what th eexpected response should be 
                    # maybe we want to store GPX so that we don't lose data - store with activity_id and athletE_id I guess?
    except Exception as e:
        logging.error('failed handling event:')
        logging.error(e)
        # TODO investigate this status - not sure if it's bogus or not
        response = {
            'status': 418,
            'body': 'error'
        }
    return json.dumps(response)
