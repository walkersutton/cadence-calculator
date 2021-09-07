import os

STRAVA_CLIENT_ID = os.environ.get('CADENCE_CALCULATOR_CLIENT_ID')
STRAVA_CLIENT_SECRET = os.environ.get('CADENCE_CALCULATOR_CLIENT_SECRET')
VERIFY_TOKEN = os.environ.get('CADENCE_CALCULATOR_VERIFY_TOKEN')
API_ENDPOINT = 'https://www.strava.com/api/v3'

# SERVER_DOMAIN = 'https://cadecalc.app'
# SERVER_DOMAIN = 'https://cadencecalculator.herokuapp.com'
SERVER_DOMAIN = 'http://localhost:5000'

SUPABASE_URL = os.environ.get('CC_SUPABASE_URL')
SUPABASE_KEY = os.environ.get('CC_SUPABASE_KEY')
