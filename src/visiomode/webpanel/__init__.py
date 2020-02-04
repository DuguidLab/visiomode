"""Webapp factory"""

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import os
import logging

import redis
import flask
import flask_socketio as sock
import visiomode.config as cfg
import visiomode.webpanel.models as db
import visiomode.webpanel.session as sess


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
        'SQLALCHEMY_DATABASE_URI': "sqlite:////" + os.path.join(app.instance_path, 'visiomode.sqlite'),
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    })

    # ensure that instance dir exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError as exc:
        logging.warning("Could not create instance directory ({}) - {}".format(app.instance_path, str(exc)))

    db.init_app(app)
    # Initialise the database if it doesn't exist
    if not os.path.exists(app.config['SQLALCHEMY_DATABASE_URI']):
        with app.app_context():
            db.init_db()

    socketio = sock.SocketIO(app)
    socketio.on_namespace(sess.SessionNamespace('/session'))

    @app.route('/')
    def index():
        """Dashboard page."""
        return flask.render_template('index.html')

    @app.route('/session')
    def session():
        """Session page."""
        return flask.render_template('session.html')

    @app.route('/history')
    def history():
        """Session history page."""
        return flask.render_template('history.html')

    @app.route('/settings')
    def settings():
        """Settings page."""
        return flask.render_template('settings.html')

    @app.route('/help')
    def docs():
        """Help / documentation page."""
        return flask.render_template('help.html')

    @app.route('/about')
    def about():
        """About page."""
        return flask.render_template('about.html')

    @app.errorhandler(404)
    def page_not_found(e):
        """404 page not found redirect."""
        return flask.render_template('404.html')

    return app


def runserver():
    """Runs the flask app in an integrated server."""
    app = create_app()
    socketio = sock.SocketIO(app)
    socketio.run(app)


if __name__ == '__main__':
    runserver()
