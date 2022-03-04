import logging
import os

from flask import Flask
from flask import render_template
from flaskr.auth import auth_url
# apply the blueprints to the app
from flaskr import auth, subscriptions


def create_app(test_config=None) -> Flask:
    '''Create and configure an instance of the Flask application.'''
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY="dev",
        # store the database in the instance folder
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.update(test_config)

    # ensure the instance folder exists
    # try:
    #     os.makedirs(app.instance_path)
    # except OSError:
    #     pass

    @app.route('/')
    def index():
        return render_template('index.html', title='Home', auth_url=auth_url())

    @app.route('/about')
    def about():
        return render_template('about.html', title='About')

    @app.route('/help')
    def help():
        return render_template('help.html', title='Help')

    @app.route('/unfortunately')
    def unfortunately():
        return render_template('unfortunately.html', title='Unfortunately...')

    app.register_blueprint(auth.bp)
    app.register_blueprint(subscriptions.bp)

    # in another app, you might define a separate main index here with
    # app.route, while giving the blog blueprint a url_prefix, but for
    # the tutorial the blog will be the main index
    app.add_url_rule("/", endpoint="index")

    logging.info('starting app')
    return app
