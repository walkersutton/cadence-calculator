import subscriptions
import sys
import unittest

sys.path.append('..')


class TestSubscriptions(unittest.TestCase):

    @unittest.skip('I do not want to hit the API rate limit')
    # deletes subscription if there was an existing subscription
    def test_subscriptions_flow(self):
        initial_subscriptions = subscriptions.get_existing_subscriptions()
        subscription_id = subscriptions.get_subscription_id()
        self.assertIsNotNone(subscription_id)
        current_subscriptions = subscriptions.get_existing_subscriptions()
        self.assertEqual(len(current_subscriptions), 1)
        self.assertEqual(subscriptions.delete_subscription(
            subscription_id), 'successfully deleted')
        self.assertEqual(len(subscriptions.get_existing_subscriptions()), 0)


if __name__ == '__main__':
    unittest.main()
