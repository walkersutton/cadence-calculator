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


def verify_strava_creds(athlete_id: int, email: str, password: str) -> tuple:
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
        html = driver.find_element(By.XPATH, value='/html')
        classes = set(html.get_attribute('className').split(' '))
        if 'logged-in' in classes:
            for element in driver.find_elements(By.CLASS_NAME, 'nav-link'):
                href = element.get_attribute('href')
                if href and '/athletes/' in element.get_attribute('href'):
                    parsed_athlete_id = int(href.split('/')[-1])
                    if parsed_athlete_id == athlete_id:
                        logging.info(
                            f'successfully verified credentials for this athlete {athlete_id}')
                        return (True, driver)
                    else:
                        logging.error(
                            f'valid credentials, but for a different user {athlete_id}, {parsed_athlete_id}')
                        return (False, 'Wrong User')

                        # maybe there's a link to another athlete on the page? might want to do a better job about getting the link in the top right to this user's profile
        else:
            logging.error('incorrect strava credentials')
    except NoSuchElementException as e:
        logging.error('verify_strava_creds: Element not found:')
        logging.error(e)
    except Exception as e:
        logging.error('verify_strava_creds: Generic Selenium exception:')
        logging.error(e)
    finally:
        if driver:
            driver.quit()
        return (False, 'Bad Credentials')


def delete_activity(driver: webdriver.Chrome, athlete_id: int, email: str, password: str, activity_id: int) -> bool:
    ''' Deletes the given activity_id

    Args:
        driver:
            an active webdriver
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
        logging.error('delete_activity: Element not found:')
        logging.error(e)
        driver.quit()
        return False
    except Exception as e:
        logging.error('delete_activity: Generic Selenium exception:')
        logging.error(e)
        driver.quit()
        return False
