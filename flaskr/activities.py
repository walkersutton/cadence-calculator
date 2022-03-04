import logging

import requests
from selenium import webdriver
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.firefox.options import Options

from flaskr import config
from flaskr.gpx import create_gpx
from flaskr.cadence import generate_cadence_data
from flaskr.auth import get_access_token


def delete_activity(athlete_id: int, activity_id: int) -> bool:
    ''' Deletes the given activity_id

    Args:
        athlete_id:
            the id of the athlete
        activity_id:
            the id of the activity
    Returns:
        Whether or not this activity was deleted successfully
    '''
    try:
        if athlete_id == config.TEST_ATHLETE_ID:
            email = config.TEST_ATHLETE_EMAIL
            password = config.TEST_ATHLETE_PASSWORD
        elif athlete_id == config.PERSONAL_ATHLETE_ID:
            email = config.PERSONAL_STRAVA_EMAIL
            password = config.PERSONAL_STRAVA_PASSWORD
        else:
            exit('delete_activity: athlete_id is invalid')
        opts = Options()
        opts.headless = True
        driver = webdriver.Firefox(options=opts)
        driver.get('https://www.strava.com/login')
        driver.find_element_by_id('email').send_keys(email)
        driver.find_element_by_id('password').send_keys(password)
        driver.find_element_by_id('login-button').click()
        driver.get(f'https://www.strava.com/activities/{activity_id}')
        driver.find_element_by_xpath('//div[@class="selection"]').click()
        driver.find_element_by_xpath(
            '//a[@data-method="delete"][text()[contains(.,"Delete")]]').click()
        Alert(driver).accept()
        driver.quit()
        return True
        # TODO
        # make a call to the strava api and see if the activity is still available
    except Exception as e:
        logging.error('generic Selenium exception:')
        logging.error(e)
        driver.quit()
        return False


def upload_activity(athlete_id: int, name: str, desc: str, trainer: str, commute: str, data_type: str, external_id: str, file_path: str) -> int:
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
    try:
        headers = {'Authorization': 'Bearer ' +
                   get_access_token(athlete_id)}
        params = {
            'name': name,
            'description': desc,
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
        #     # do we want to add a watermark? - similar to klimat?
        #     'trainer': 1 if self.obj['trainer'] else 0,
        #     'commute': 1 if self.obj['commute'] else 0,
        #     # we might want to use FIT instead since we can preserve more data across replacing
        #     #  (lap & session data +), but lower priority
        # # do we also want to be responsible for replacing images and other properties that
        # #  were lost across deleting?

        response = requests.post(
            files=files, headers=headers, params=params, url=url)
        if response.ok:
            return response.json()['id']
    except Exception as e:
        logging.error('error uploading activity:')
        logging.error(e)
    return None


def uploaded_activity_id(athlete_id: int, upload_id: int) -> int:
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
        headers = {'Authorization': 'Bearer ' +
                   get_access_token(athlete_id)}
        url = f'{config.API_ENDPOINT}/uploads/{upload_id}'
        response = requests.get(headers=headers, url=url)
        if response.ok:
            return response.json()['activity_id']
        else:
            # not returning None because I think it's possible the response tells us the activity is still uploading - in that case, we don't want to assume the upload didn't work if it was still in progress
            # TODO add some better handling for the response here
            return response.json()
    except Exception as e:
        logging.error('error getting uploaded activity id:')
        logging.error(e)
    return None


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

    def __init__(self, activity_id: int, athlete_id: int) -> None:
        ''' Initializes an Activity object

        Args:
            activity_id:
                The id of the activity
            athlete_id:
                The id of the athlete
        '''

        def set_gear_ratio(self: Activity) -> None:
            # TODO make sure this method works in this configuration
            ''' Sets the gear ratio '''
            try:
                description = self.obj['description']
                description = description.split('\r\n')
                ratio = description[0].split('x')
                self.chainring = int(ratio[0])
                self.cog = int(ratio[1])
            except Exception as e:
                logging.error('error parsing gear ratio:')
                logging.error(e)

        self.obj = {}
        self.chainring = None
        self.cog = None
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
            set_gear_ratio(self)
        except Exception as e:
            logging.error('error accessing activity:')
            logging.error(
                'is activity_id the first parameter and athlete_id the second parameter???')
            logging.error(e)

    def get_stream(self) -> dict:
        ''' Gets a stream object of this activity

        Returns:
            An object whose keys are a subset of params['keys'].
            Values are objects with relevant data (keys that are specified
            in params['keys'] that don't have existing data are not returned)
        '''
        try:
            activity_id, athlete_id = self.obj['id'], self.obj['athlete']['id']
            headers = {'Authorization': 'Bearer ' +
                       get_access_token(athlete_id)}
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
            stream = self.get_stream()
            if stream:
                if 'distance' in stream:
                    stream['cadence'] = {
                        'data': generate_cadence_data(stream['distance']['data'], self.chainring, self.cog),
                        'series_type': 'time',
                        'original_size': stream['distance']['original_size'],
                        'resolution': stream['distance']['resolution']
                    }
                    return stream
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
        '''
        try:
            # TODO what is the significance 'average_cadence' in self.obj?
            return (self.obj['type'] == 'Ride' and 'average_cadence' in self.obj and self.cog and self.chainring)
        except Exception as e:
            logging.error(
                'error determining if this activity requires generated cadence data:')
            logging.error(e)
        return False

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
            filepath = f'{filename}.{filetype}'

            if create_gpx(self.generate_stream(), self.obj, filename, filetype):
                if delete_activity(self.obj['athlete']['id'], self.obj['id']):
                    upload_id = upload_activity(self.obj['athlete']['id'], f'{self.obj["name"]} with cadence', self.obj[
                                                'description'], self.obj['trainer'], self.obj['commute'], filetype, 'ex_id_1', filepath)
                    if upload_id:
                        return uploaded_activity_id(self.obj["athlete"]["id"], upload_id)
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
        return None
