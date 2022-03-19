import logging
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support.expected_conditions import alert_is_present
from selenium.common.exceptions import NoSuchElementException

from flaskr import config


def verify_strava_creds(athlete_id: int, email: str, password: str) -> webdriver.Chrome:
    ''' Determines if the provided email and password are valid credentials for the provided athlete

    Args:
        athlete_id:
            the user's athlete_id
        email:
            the user's email
        password:
            the user's password

    Returns: a webdriver object with the provided user successfully authenticated. Otherwise None
    '''
    try:
        service = Service(config.CHROMEDRIVER_PATH)
        options = webdriver.ChromeOptions()
        options.binary_location = config.GOOGLE_CHROME_BIN
        options.add_argument('--headless')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        driver = webdriver.Chrome(service=service, options=options)
        driver.get('https://www.strava.com/login')
        driver.find_element(By.ID, value='email').send_keys(email)
        driver.find_element(By.ID, value='password').send_keys(password)
        driver.find_element(By.ID, 'login-button').click()
        # do some check to verify logged in and verify that the logged in user has the same athlete_id associated with email on file
        if athlete_id:
            print('oh shit mate')
    except NoSuchElementException as e:
        logging.error('Element not found:')
        logging.error(e)
        driver.quit()
        return None
    except Exception as e:
        logging.error('verify_strava_creds: Generic Selenium exception:')
        logging.error(e)
        driver.quit()
        return None

    # selenium work here
    # attempt to login
    # grab class at top
    # also verify athlete_id matches?
    # could theoretically be valid login for the wrong athelte
    # verify user is logged in - can check for the existence of a class in body/root tag
    # driver.find_element(By.XPATH, value='//button[@class="btn-accept-cookie-banner"]').click() - pretty sure this is unnecessary


def delete_activity(athlete_id: int, email: str, password: str, activity_id: int) -> bool:
    ''' Deletes the given activity_id

    Args:
        athlete_id:
            the id of the athlete
        email:
            the user's email address
        password:
            the user's password
        activity_id:
            the id of the activity
    Returns:
        Whether or not this activity was deleted successfully
    '''
    driver = verify_strava_creds(athlete_id, email, password)
    if not driver:
        pass
        logging.error(
            f'Attempted to delete an activity {activity_id} for athlete {athlete_id}, but could not verify Strava credentials')
        return False
    try:
        driver.get(f'https://www.strava.com/activities/{activity_id}')
        driver.find_element(
            By.XPATH, value='//div[@title="Actions"]').click()
        driver.find_element(
            By.XPATH, value='//a[@data-method="delete"][text()[contains(.,"Delete")]]').click()
        wait(driver, 3).until(alert_is_present())
        Alert(driver).accept()
        time.sleep(3)
        driver.quit()
        logging.info('successfully deleted the activity')
        return True
        # TODO
        # make a call to the strava api and see if the activity is still available
        # or maybe we actually just use the /subscribe post endpoint giving us a delete event - less api hits
    except NoSuchElementException as e:
        logging.error('Element not found:')
        logging.error(e)
        driver.quit()
        return False
    except Exception as e:
        logging.error('Generic Selenium exception:')
        logging.error(e)
        driver.quit()
        return False
