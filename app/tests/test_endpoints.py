from app import app
from flask import request
import json
import logging
import sys
import unittest

sys.path.append('..')
logging.disable(logging.ERROR)


class TestEndpoints(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

        self.test_event = {
            'aspect_type': 'update',
            'event_time': 1516126040,
            'object_id': 1360128428,
            'object_type': 'activity',
            'owner_id': 134815,
            'subscription_id': 120475,
            'updates': {
                'title': 'Messy'
            }
        }

    # def test_auth(self):
    #     with app.test_request_context('/auth?state=&code=test_code8&scope=read,activity:read_all'):
    #         assert request.path == '/auth'
    #         assert request.args['state'] == ''

    def test_auth_get(self):
        full_scope_url = '/auth?state=&code=test_code&scope=read,activity:read_all'
        rv = self.app.get(full_scope_url)
        assert b'a success!!!' in rv.data

        missing_scope_url = '/auth?state=&code=test_code&scope=read'
        rv = self.app.get(missing_scope_url)
        assert b'need to provide more access, try again' in rv.data

        error_url = '/auth?state=&error=error&code=test_code&scope=read,activity:read_all'
        rv = self.app.get(error_url)
        assert b'there was an error' in rv.data

    def test_subscribe_get(self):
        url = '/subscribe?hub.verify_token=STRAVA&hub.challenge=test_challenge&hub.mode=subscribe'
        rv = self.app.get(url)
        assert b'{"hub.challenge": "test_challenge"}' == rv.data

    def test_subscribe_post(self):
        url = '/subscribe'
        data = json.dumps(self.test_event)
        rv = self.app.post(url, json=data)
        assert b'{"status": 200, "body": "ya done goofed"}' == rv.data

        # no body provided
        rv = self.app.post(url)
        assert b'{"status": 418, "body": "error"}' == rv.data


if __name__ == '__main__':
    unittest.main()
