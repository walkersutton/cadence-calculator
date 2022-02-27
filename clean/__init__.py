from flask import Flask, make_response, render_template, request

from app.auth import auth_url, token_exchange
from app.subscriptions import get_subscription_id, handle_event, delete_subscription
# get_subscription_id, delete_subscription


def create_app() -> Flask:
    app = Flask(__name__)
    # Threaded option to enable multiple instances for multiple user access support
    # auth.update_security_group()
    # app.logger.info('attempting to create subscription')
    # subscription_id = get_subscription_id()
    # app.logger.info('created subscription with id:' + str(subscription_id))
    # app.logger.info('starting app')
    app.run(threaded=True)
    # app.logger.info('app exited')
    # app.logger.info('attempting to delete subscription')
    # delete_subscription(subscription_id)
    # app.logger.debug('deleted subscription with id:' + str(subscription_id))


if __name__ == '__main__':
	app.run(host='0.0.0.0')
