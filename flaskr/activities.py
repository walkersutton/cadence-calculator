import logging
import time

import requests

from flaskr import config
from flaskr.auth import get_strava_credential
from flaskr.gpx import create_gpx
from flaskr.cadence import generate_cadence_data
from flaskr.webdriver import delete_activity


class Activity:
    ''' Represents a Strava activity object
    https://developers.strava.com/docs/reference/#api-models-DetailedActivity

    Properties:
        obj: dict
            the JSON object used by Strava to represent this Activity
        chainring: int
            the size of the chainring used during this Activity
        cog: int
            the size of the cog used during this Activity
    '''
    # TODO - do we actually need athlete ID? should we store access token instead?

    def __init__(self, activity_id: int, athlete_id: int, access_token: int, supabase) -> None:
        ''' Initializes an Activity object

        Args:
            activity_id:
                The id of this activity
            athlete_id:
                The id of this athlete
            access_token:
                The current access_token for this athlete
            supabase:
                a supabase Client object
        '''

        def set_gear_ratio(self: Activity) -> None:
            # TODO make sure this method works in this configuration
            ''' Sets the gear ratio 
            Activity description note: 
            * Each line in the description is delimited by "\r\n" 

            '''
            try:
                description = self.obj['description']
                if not description:
                    logging.info(
                        'Cannot set gear ratio - description is empty')
                    return
                lines = description.split('\r\n')
                for line in lines:
                    parts = line.split('x')
                    if len(parts) >= 2:
                        for ii in range(len(parts) - 1):
                            left, right = parts[ii][-2:], parts[ii + 1][:2]
                            if left.isnumeric() and right.isnumeric():
                                self.chainring = int(left)
                                self.cog = int(right)
                                break
            except Exception as e:
                logging.error('error parsing gear ratio:')
                logging.error(e)

        logging.info(
            f'Creating Activity {activity_id} object for athlete {athlete_id}')
        self.obj = {}
        self.chainring = None
        self.cog = None
        self.access_token = access_token
        self.supabase = supabase
        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            params = {'include_all_efforts': 'false'}
            url = f'{config.API_ENDPOINT}/activities/{activity_id}'
            response = requests.get(headers=headers, params=params, url=url)
            if response.ok:
                self.obj = response.json()
            else:
                logging.error('error creating Activity:')
                if 'message' in response.text:
                    logging.error(response.text['message'])
                else:
                    logging.error(response.text)
                raise Exception('This is an invalid activity')
            set_gear_ratio(self)
            # TODO - gear ratio might not be set -
            # need to handle this
        except Exception as e:
            logging.error('error accessing activity:')
            logging.error(e)

    def get_streams(self) -> dict:
        ''' Gets a stream object of this activity

        Returns:
            An object whose keys are a subset of params['keys'].
            Values are objects with relevant data (keys that are specified
            in params['keys'] that don't have existing data are not returned)
        '''
        try:
            activity_id = self.obj['id']
            headers = {'Authorization': f'Bearer {self.access_token}'}
            # TODO might want to modify params to include other things
            params = {
                'keys': 'time,latlng,distance,altitude,heartrate,cadence,watts,temp,moving',
                'key_by_type': 'true'
            }
            # TODO
            # list of chr strings with any combination of "time", "latlng", "distance",
            # "altitude", "velocity_smooth", "heartrate", "cadence", "watts", "temp",
            # "moving", or "grade_smooth"
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
        return None

    def generate_stream(self) -> dict:
        ''' Create a stream with cadence data appended to the original stream

            Returns:
                A stream object of this Activity with the addition of a cadence stream
        '''
        try:
            streams = self.get_streams()
            if streams:
                logging.info('Pulled streams from Strava')
                if 'distance' in streams:
                    streams['cadence'] = {
                        'data': generate_cadence_data(streams['distance']['data'], self.chainring, self.cog),
                        'series_type': 'time',
                        'original_size': streams['distance']['original_size'],
                        'resolution': streams['distance']['resolution']
                    }
                    return streams
                else:
                    logging.error('existing stream lacks distance data')
                    return None
            else:
                logging.error('generate_stream: error getting stream')
                return None
        except Exception as e:
            logging.error('error generating stream:')
            logging.error(e)
        return None

    # TODO - change method name
    # maybe something like 'view' or 'observe' - because we won't ALWAYS be modifyign the
    # activity - it depends on the state

    def requires_cadence_data(self) -> bool:
        ''' Determines if this activity needs cadence data generated

        Returns:
            Whether or not this Activity requires cadence data to be generated

        When should an activity require cadence data?
        * when an activity doesn't already have cadence data
        * either if:
            * a gear ratio is provided in the description
            * the bike has previously been seen to be fixed

        '''
        requires = False
        try:
            # TODO what is the significance 'average_cadence' in self.obj?
            # TODO
            # if this activity has at least 1 kudos, maybe check for a special flag in description to verify the user is aware their kudos will be deleted
            # do better checking here - probably needs to have average_speed, don't want to override cadence, etc...
            requires = (
                self.obj['type'] == 'Ride' and 'average_cadence' not in self.obj and self.cog and self.chainring)
            if requires:
                logging.info("Activity requires cadence data")
            else:
                logging.info("Activity doesn't require cadence data 2222")
                logging.info(self.obj['type'] == 'Ride')
                logging.info('average_cadence' not in self.obj)
                logging.info(self.cog)
                logging.info(self.chainring)

        except Exception as e:
            logging.error(
                'error determining if this activity requires generated cadence data:')
            logging.error(e)
            logging.error(self.obj)
            logging.error(self)
        return requires

    # url = f'{config.API_ENDPOINT}/routes/{activity_id}/export_gpx'
    # headers = {'Authorization': 'Bearer ' + get_access_token(owner_id)}
    # if response.ok:
    # response = requests.get(url=url, headers=headers)
    # TODO convert to Streams API
    # TODO
    # should have a GPX file in the response? I wonder how that will look.... -
    # hopefully a url to the file itself
    # return response.json()
    # else:
    # TODO
    # logging.error(response.text)
    # sys.exit(1)
    # or a 4/500 with a fault descirbing the error
    # TODO investigate fault
    # this returns either a 200 with the gpx file
        # print(stream)

    def delete_activity(self) -> bool:
        ''' Deletes the given activity_id

        Returns:
            Whether or not this activity was deleted successfully
            TODO - maybe instead of depending on return value here, we listen for a post DELETE? - seems better
        '''
        try:
            athlete_id = self.obj['athlete']['id']
            activity_id = self.obj['id']
            logging.info('beginning to delete activity')
            email, password = get_strava_credential(self.supabase, athlete_id)
            if not(email and password):
                logging.error('email or password was not set')
                return False
        except Exception as e:
            logging.error('error getting strava credentials')
            logging.error(e)

        return delete_activity(email, password, activity_id)

    def upload_activity(self, data_type: str, external_id: str, file_path: str) -> int:
        ''' Uploads an Activity

        Args:
            athlete_id:
                the id of the athlete
            name: 
                the title of the activity
            desc:
                the description of the activity
            trainer:
                TODO
            commute:
                TODO
            data_type:
                the file type of the activity data [gpx, tar.gz, TODO ]
            external_id:
                a string used to identify an uploaded Activity
            file_path:
                the path to the activity data file (relative to the root of this repository)
        Returns:
            The upload_id of the activity
        '''

        name = f'{self.obj["name"]}'
        description = f'{self.obj["description"]} - cadence by cadecalc.app'
        trainer = self.obj['trainer']
        commute = self.obj['commute']
        try:
            headers = {'Authorization': f'Bearer {self.access_token}'}
            params = {
                'name': name,
                'description': description,
                'trainer': trainer,
                'commute': commute,
                'data_type': data_type,
                'external_id': external_id
            }
            files = {
                'file': open(file_path, 'rb')
            }
            url = f'{config.API_ENDPOINT}/uploads'

            # TODO review these comments:
            #     'activity_type': self.obj['type'],
            #     'trainer': 1 if self.obj['trainer'] else 0,
            #     'commute': 1 if self.obj['commute'] else 0,
            #     # we might want to use FIT instead since we can preserve more data across replacing
            #     #  (lap & session data +), but lower priority
            # # do we also want to be responsible for replacing images and other properties that
            # #  were lost across deleting?
            logging.info('about to post the new activity')
            response = requests.post(
                files=files, headers=headers, params=params, url=url)
            logging.info('posted the new activity')
            if response.ok:
                logging.info('success posting the new activity')
                return response.json()['id']
            else:
                logging.error('error posting the new activity')
                logging.error(response.json())
        except Exception as e:
            logging.error('error uploading activity:')
            logging.error(e)
        return None

    def uploaded_activity_id(self, upload_id: int) -> int:
        ''' Gets the activity_id of a recently uploaded activity

        Args:
            athlete_id:
                the id of the athlete
            upload_id:
                the id of the upload
        Returns:
            The activity_id of the activity
        '''
        try:
            logging.info('waiting for new activity id to be created')
            headers = {'Authorization': f'Bearer {self.access_token}'}
            url = f'{config.API_ENDPOINT}/uploads/{upload_id}'
            response = requests.get(headers=headers, url=url)
            counter = 0
            while response.json()['status'] == 'Your activity is still being processed.':
                logging.info('activity still being processed')
                counter += 1
                time.sleep(5)
                logging.info('trying response again in 5 seconds')
                logging.info(response)
                logging.info(response.json())
                response = requests.get(headers=headers, url=url)
                if counter == 4 and not response.ok:
                    logging.error('why is the upload taking so fucking long')
                    logging.error('giving up')
                    return None
            logging.info('Activity finished processing')
            if response.json()['status'] == 'There was an error processing your activity.':
                raise Exception('duplicate activity???')
            logging.info(response)
            logging.info(response.json())
            return response.json()['activity_id']
            # HERE
            # not returning None because I think it's possible the response tells us the activity is still uploading
            # - in that case, we don't want to assume the upload didn't work if it was still in progress
            # TODO add some better handling for the response here
        except Exception as e:
            logging.error('error getting uploaded activity id:')
            logging.error(e)
        logging.info(
            'returning none in uploaded_activty id for some odd reason')
        # this is usually because the old activity hasn't been deleted yet
        return None

    def replace_activity(self) -> int:
        ''' Uploads a new activity to Strava with with the addition of cadence data.
            This function is only called when cadence data doesn't already exist

        Returns:
            The activity_id of the newly replaced activity
        '''
        try:
            # TODO might want tire width, and other props
            # probably want the start_date/start_date_local & timezone? -- use with stream
            # eventually, will want to check gear to see if this bike already has a recorded ratio?
            filename = 'cadence_test'
            filetype = 'gpx'
            external_id = 'ex_id_1'
            filepath = f'{filename}.{filetype}'
            stream = self.generate_stream()
            if not stream:
                # TODO find a more descriptive exception
                raise Exception('stream could not be built')
            file_created = create_gpx(stream, self.obj, filename, filetype)
            if file_created:
                if self.delete_activity():
                    upload_id = self.upload_activity(
                        filetype, external_id, filepath)
                    logging.info('uploaded id')
                    logging.info(upload_id)
                    logging.info('uploaded id')
                    if upload_id:
                        id = self.uploaded_activity_id(upload_id)
                        logging.info('the id is here')
                        logging.info(id)
                        logging.info('the id is here')
                        if id:
                            logging.info('successfully replaced activity')
                            return id
                        else:
                            logging.error('error getting uploaded activity id')
                            return None
                    else:
                        logging.error(
                            'replace_activity: error uploading activity')
                        return None
                else:
                    logging.error(
                        'replace_activity: error deleting old activity')
                    return None
            else:
                logging.error('replace_activity: error creating gpx file')
                return None
        except Exception as e:
            logging.error('error replacing activity:')
            logging.error(e)
        logging.info('returning none here1')
        return None
