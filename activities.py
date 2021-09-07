import config
from gpx import create_gpx
from cadence import generate_cadence_data
from auth import get_access_token
import json
import logging
import requests
import sys

sys.path.append('..')

# from main import generate_cadence

# TODO remove if don't need
# def athlete_exists(conn, athlete_id):
#     try:
#         athlete_query = f'SELECT * FROM access_token WHERE athlete_id={athlete_id};'
#         athlete_access_token_entry = auth.execute_query(conn, athlete_query)
#         return len(athlete_access_token_entry) != 0
#     except Exception as e:
#         logging.error('error determining athlete existence:')
#         logging.error(athlete_query)
#         logging.error(e)


class Activity:
    def __init__(self, activity_id, athlete_id):
        """ Returns this activity object
        Args:
                activity_id: (int)
                        The id of the activity
                athlete_id: (int)
                        The id of the athlete

        Cretes an Activity
                TODO
                See Strava Developer resources for Activity Object
                https://developers.strava.com/docs/reference/#api-Activities
        """
        self.obj = {}
        self.chainring = -1
        self.cog = -1
        try:
            headers = {'Authorization': 'Bearer ' +
                       get_access_token(athlete_id)}
            params = {'include_all_efforts': 'false'}
            url = f'{config.API_ENDPOINT}/activities/{activity_id}'
            response = requests.get(headers=headers, params=params, url=url)
            if response.ok:
                self.obj = response.json()
            else:
                logging.error('error creating Activity:')
                logging.error(response.text)
        except Exception as e:
            logging.error('error accessing activity:')
            logging.error(e)

    def get_stream(self):
        """ Returns a Stream object of this activity

        Returns a dict
                Each key is specified in the 'params' 'keys' list - values are objects with relevant data (keys that are specified in 'params' that don't have existing data are not returned)
        """
        # might want to modify keys to include other things
        try:
            activity_id, athlete_id = self.obj['id'], self.obj['athlete']['id']
            headers = {'Authorization': 'Bearer ' +
                       get_access_token(athlete_id)}
            params = {
                'keys': 'time,latlng,distance,altitude,heartrate,cadence,watts,temp,moving', 'key_by_type': 'true'}
            # TODO
            # list of chr strings with any combination of "time", "latlng", "distance", "altitude", "velocity_smooth", "heartrate", "cadence", "watts", "temp", "moving", or "grade_smooth"
            # https://rdrr.io/github/fawda123/rStrava/man/get_streams.html
            url = f'{config.API_ENDPOINT}/activities/{activity_id}/streams'
            response = requests.get(headers=headers, params=params, url=url)
            if response.ok:
                return response.json()
            else:
                logging.error('error getting activity stream:')
                logging.error(response.text)
        except Exception as e:
            logging.error('error accessing activity stream:')
            logging.error(e)

    def generate_stream(self):
        """ Create a new stream with cadence data appended to the stream
                TODO
                Returns a stream with a cadence property
        """
        try:
            stream = self.get_stream()
            stream['cadence'] = {
                'data': generate_cadence_data(stream['distance']['data'], self.chainring, self.cog),
                'series_type': 'time',
                # do we need to verify that distance exists in this object?? probably should?
                'original_size': stream['distance']['original_size'],
                'resolution': stream['distance']['resolution']
            }
            return stream
        except Exception as e:
            logging.error('error generating stream:')
            logging.error(e)

    def valid_description(self):
        """ Sets the gear ratio if this description is properly formatted and determines whether or not the description is valid.
                TODO
        Returns a bool
                Returns True if the description is valid, otherwise returns False
                Format guidelines are posted on help page
                TODO add description format guidelins
                TODO TODO TODO
        """
        try:
            description = self.obj['description']
            description = description.split('\r\n')
            ratio = description[0].split('x')
            self.chainring = int(ratio[0])
            self.cog = int(ratio[1])
        except Exception as e:
            logging.error('error parsing gear ratio:')
            logging.error(e)
            return None

    # TODO - change method name
    # maybe something like 'view' or 'observe' - because we won't ALWAYS be modifyign the activity - it depends on the state
    def requires_cadence_data(self):
        """ Determines if this activity needs cadence data generated

        Returns a bool
        """
        try:
            return self.obj['type'] == 'Ride' and 'average_cadence' in self.obj and self.valid_description()
        except Exception as e:
            logging.error(
                'error determining if this activity requires cadence data generated:')
            logging.error(e)

    # url = f'{config.API_ENDPOINT}/routes/{activity_id}/export_gpx'
    # headers = {'Authorization': 'Bearer ' + get_access_token(owner_id)}
    # if response.ok:
    # response = requests.get(url=url, headers=headers)
    # TODO convert to Streams API
    # TODO
    # should have a GPX file in the response? I wonder how that will look.... - hopefully a url to the file itself
    # return response.json()
    # else:
    # TODO
    # logging.error(response.text)
    # sys.exit(1)
    # or a 4/500 with a fault descirbing the error
    # TODO investigate fault
    # this returns either a 200 with the gpx file
        # print(stream)

    def replace_activity(self):
        """ Uploads a new activity to Strava with identical data as this activity, but with the addition of cadence data
                TODO
                Returns TODO
        """
        try:
            stream = self.get_stream()

            # TODO might want tire width, and other props
            # probably want the start_date/start_date_local & timezone? -- use with stream
            # eventually, will want to check gear to see if this bike already has a recorded ratio?
            # stream = generate_cadence()

            headers = {'Authorization': 'Bearer ' +
                       get_access_token(self.obj['athelte']['id'])}
            params = {
                'activity_type': self.obj['type'],
                'name': self.obj['name'],
                # do we want to add a watermark? - similar to klimat?
                'description': self.obj['description'],
                'trainer': 1 if self.obj['trainer'] else 0,
                'commute': 1 if self.obj['commute'] else 0,
                # we might want to use FIT instead since we can preserve more data across replacing (lap & session data +), but lower priority
                'data_type': create_gpx(self.generate_stream())
                # 'external_id': '', # investigate TODO
                # 'file': # investigate - TODO - multipart/form-datat data type???
            }
            url = f'{config.API_ENDPOINT}/uploads'
            response = requests.post(headers=headers, params=params, url=url)
            # do we also want to be responsible for replacing images and other properties that were lost across deleting?
            if response.ok:
                self.obj = response.json()
            else:
                pass
        except Exception as e:
            logging.error('error replacing activity:')
            logging.error(e)
