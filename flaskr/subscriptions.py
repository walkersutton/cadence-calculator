""" subscriptions.py """
import json
import logging
import sys

import requests


from flaskr.activities import Activity
import config

# TODO add support for handling 429s
# https://developers.strava.com/docs/rate-limits/


def get_existing_subscriptions():
    """ Returns a list of subscriptions
    (this list should never have more than 1 item)
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
    """
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


def get_subscription_id():
    """ Returns the ID of an available subscription (new ID or existing ID)
    TODO
    """
    try:
        callback_url = config.SERVER_DOMAIN + '/subscribe'
        url = f'{config.API_ENDPOINT}/push_subscriptions'
        data = {
            'client_id': config.STRAVA_CLIENT_ID,
            'client_secret': config.STRAVA_CLIENT_SECRET,
            'callback_url': callback_url,
            'verify_token': config.VERIFY_TOKEN
        }
        response = requests.post(url=url, data=data)
        if response.ok:
            # subscription creation response
            subscription_id = response.json()['id']
            return subscription_id
        else:
            return get_existing_subscriptions()[0]['id']
    except Exception as e:
        logging.error('error getting subscription id:')
        logging.error(e)
    return None


def delete_subscription(subscription_id):
    """ Deletes the subscription with the given subscription_id

    Args:
                    subscription_id: TODO
    """
    try:
        url = f'{config.API_ENDPOINT}/push_subscriptions/' + \
            str(subscription_id)
        data = {
            'client_id': config.STRAVA_CLIENT_ID,
            'client_secret': config.STRAVA_CLIENT_SECRET
        }
        response = requests.delete(url=url, data=data)
        if response.ok:
            return 'successfully deleted'
        else:
            logging.error('error deleting subscription')
            logging.error(response.text)
            sys.exit(1)
    except Exception as e:
        logging.error('error deleting subscription:')
        logging.error(e)
    return None


def handle_event(event):
    """ Handles users' activity & profile updates and acts accordingly

    Returns json TODO
    """
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
                # we either want to prompt user that kudos and comments will be deleted, or do somethign else
                activity.replace_activity()
        response = {
            'status': 200,
            'body': 'something happened, but little descipriotn . ya done goofed - TODO might neeed to change this body? but also jsut might not matter?'
        }
    except Exception as e:
        logging.error('failed handling event:')
        logging.error(e)
        # TODO investigate this status - not sure if it's bogus or not
        response = {
            'status': 418,
            'body': 'error'
        }
    return json.dumps(response)
