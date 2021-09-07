import sys
import unittest

sys.path.append('..')
import auth
import config

class TestAuthorization(unittest.TestCase):

    def test_auth_url(self):
        config.SERVER_DOMAIN = 'server_domain'
        config.STRAVA_CLIENT_ID = 'strava_client_id'
        url = auth.auth_url()
        self.assertEqual(url, 'https://www.strava.com/oauth/authorize?client_id=strava_client_id&redirect_uri=server_domain/auth&response_type=code&scope=activity:read_all')

    # tests create_db_conn(), execute_query(), and get_query_values() 
    def test_execute_query(self):
        conn = auth.create_db_conn()
        query = 'SELECT * FROM access_token WHERE athlete_id=-1'
        response = auth.execute_query(conn, query)
        self.assertEqual(response, [])
    
if __name__ == '__main__':
    unittest.main()
