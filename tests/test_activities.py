import sys
import unittest

sys.path.append('..')
import activities
import auth

class TestActivities(unittest.TestCase):

    def test_athlete_exists(self):
        conn = auth.create_db_conn()
        self.assertFalse(activities.athlete_exists(conn, -1))
    
if __name__ == '__main__':
    unittest.main()
