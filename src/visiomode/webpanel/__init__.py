"""Webapp factory"""

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import os
import logging

import redis
import flask
import werkzeug.serving
import gevent.pywsgi as wsg
import visiomode.config as cfg
import visiomode.webpanel.db as db


def create_app():
    """Flask app factory

    Returns:
        Flask app object
    """
    config = cfg.Config()
    rds = redis.Redis(host=config.redis_host, port=config.redis_port)

    app = flask.Flask(__name__)
    app.config.from_mapping({
        'SECRET_KEY': config.flask_key,
        'DEBUG': config.debug,
        'DATABASE': os.path.join(app.instance_path, 'visiomode.sqlite'),
    })

    # ensure that instance dir exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        logging.warning("Could not create instance directory at {}".format(app.instance_path))

    # Initialise the database if it doesn't exist
    if not os.path.exists(app.config['DATABASE']):
        with app.app_context():
            db.init_db()
    app.teardown_appcontext(db.close_db)

    @app.route('/')
    def index():
        return flask.render_template('index.html')

    @app.route('/session')
    def session():
        return flask.render_template('session.html')

    @app.route('/history')
    def history():
        return flask.render_template('history.html')

    @app.route('/settings')
    def settings():
        return flask.render_template('settings.html')

    @app.route('/help')
    def docs():
        return flask.render_template('help.html')

    @app.route('/about')
    def about():
        return flask.render_template('about.html')

    return app


@werkzeug.serving.run_with_reloader
def runserver():
    http_server = wsg.WSGIServer(('', 5000), create_app())
    http_server.serve_forever()


if __name__ == '__main__':
    runserver()
