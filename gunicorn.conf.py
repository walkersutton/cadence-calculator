import logging
from flaskr import subscriptions


def when_ready(server):
    logging.info('attempting to create subscription')
    subscription_id = subscriptions.get_subscription_id()
    logging.info('created subscription with id:' + str(subscription_id))
    pass


def on_exit(server):
    subscription_id = subscriptions.get_subscription_id()
    logging.info('getting current subscription id for deleting')
    if subscription_id == 'errorrrrrrrr_id':
        logging.error('errrorrr saying goodbye')
        return
    logging.info('attempting to delete subscription')
    subscriptions.delete_subscription(subscription_id)
    logging.debug('deleted subscription with id:' + str(subscription_id))
