import webhooks
import json
import sys
import unittest

sys.path.append('..')


class TestWebhooks(unittest.TestCase):

    def test_handle_event(self):
        pass
        test_event = {
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
        self.assertTrue(1 == 1)
        assert b'asdf' in b'lksjdflskjdasdf'
        pass
        json_event = json.dumps(test_event)

        response = {
            'status': 200,
            'body': 'ya done goofed'
        }
        json_response = json.dumps(response)

        self.assertEqual(webhooks.handle_event(json_event), json_response)


if __name__ == '__main__':
    unittest.main()
