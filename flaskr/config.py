import os
# maybe add another .env file and move environemnt variables there

STRAVA_CLIENT_ID = os.environ.get('CADENCE_CALCULATOR_CLIENT_ID')
STRAVA_CLIENT_SECRET = os.environ.get('CADENCE_CALCULATOR_CLIENT_SECRET')
VERIFY_TOKEN = os.environ.get('CADENCE_CALCULATOR_VERIFY_TOKEN')
API_ENDPOINT = 'https://www.strava.com/api/v3'

SERVER_DOMAIN = 'https://cadecalc.app'
# SERVER_DOMAIN = 'https://cadencecalculator.herokuapp.com'
# SERVER_DOMAIN = 'http://localhost:5000'

SUPABASE_URL = os.environ.get('CC_SUPABASE_URL')
SUPABASE_KEY = os.environ.get('CC_SUPABASE_KEY')

TEST_ATHLETE_ID = os.environ.get('CC_TEST_ATHLETE_ID')
TEST_ATHLETE_EMAIL = os.environ.get('CC_TEST_ATHLETE_EMAIL')
TEST_ATHLETE_PASSWORD = os.environ.get('CC_TEST_ATHLETE_PASSWORD')

PERSONAL_ATHLETE_ID = os.environ.get('STRAVA_ATHLETE_ID')
PERSONAL_STRAVA_EMAIL = os.environ.get('STRAVA_EMAIL')
PERSONAL_STRAVA_PASSWORD = os.environ.get('STRAVA_PASSWORD')

GOOGLE_CHROME_BIN = os.environ.get('GOOGLE_CHROME_BIN')
CHROMEDRIVER_PATH = os.environ.get('CHROMEDRIVER_PATH')
