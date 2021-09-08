""" app.py """
import json
from flask import Flask, make_response, render_template, request
# import logging

from auth import auth_url, token_exchange
from subscriptions import get_subscription_id, delete_subscription, handle_event

app = Flask(__name__)


@app.route('/')
def index():
    """ index """
    return render_template('index.html', title='Home', auth_url=auth_url())


@app.route('/about')
def about():
    """ about """
    return render_template('about.html', title='About')


# pylint: disable=redefined-builtin
@app.route('/help')
def help():
    """ help """
    return render_template('help.html', title='Help')


@app.route('/auth')
def auth():
    """
    Strava auth redirect
    """
    # TODO change to include activity:write eventually
    required_scope = {'read', 'activity:read_all'}
    code = request.args.get('code')
    error = request.args.get('error')
    scope = request.args.get('scope')
    access_scope = set(scope.split(',')) if scope else {}
    status = ''

    if access_scope == required_scope:
        token_exchange(code)
        status = 'success'
    else:
        status = 'insufficient authorization'
    if error:
        status = 'error'

    # TODO: dynamic title here? - for template
    return render_template('auth.html', title='Authorization', status=status, auth_url=auth_url())


@app.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    """ subscribe """
    status_code = -1
    if request.method == 'GET':
        # subscription validation request
        try:
            # verify_token = request.args.get('hub.verify_token')
            challenge = request.args.get('hub.challenge')
            body = json.dumps({'hub.challenge': challenge})
            status_code = 200
        except Exception as e:
            app.logger.error('error validating callback address')
            app.logger.error(e)
            body = "error handling GET request"
            status_code = 404
    elif request.method == 'POST':
        try:
            event = request.get_json()
            body = handle_event(event)
            status_code = 200
        except Exception as e:
            app.logger.error('error listening on webhooks endpoint')
            app.logger.error(e)
            body = "error handling POST request"
            status_code = 404

    response = make_response(body)
    response.status_code = status_code
    response.mimetype = 'application/json'
    return response


if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    # auth.update_security_group()
    # app.logger.info('attempting to create subscription')
    # subscription_id = create_subscription()
    # app.logger.info('created subscription with id: ' + str(subscription_id))
    app.logger.info('starting app')
    app.run(threaded=True, port=5000)
    app.logger.info('app exited')
    # app.logger.info('attempting to delete subscription')
    # delete_subscription(subscription_id)
    # app.logger.debug('deleted subscription with id:', str(subscription_id))
