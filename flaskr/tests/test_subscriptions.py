import unittest

from flaskr.subscriptions import get_existing_subscriptions, get_subscription_id, delete_subscription

class TestSubscriptions(unittest.TestCase):

    @unittest.skip('I do not want to hit the API rate limit')
    # deletes subscription if there was an existing subscription
    def test_subscriptions_flow(self):
        # initial_subscriptions = get_existing_subscriptions()
        subscription_id = get_subscription_id()
        self.assertIsNotNone(subscription_id)
        current_subscriptions = get_existing_subscriptions()
        self.assertEqual(len(current_subscriptions), 1)
        self.assertTrue(delete_subscription(
            subscription_id))
        self.assertEqual(len(get_existing_subscriptions()), 0)


if __name__ == '__main__':
    unittest.main()
