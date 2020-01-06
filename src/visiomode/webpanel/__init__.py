"""Webapp factory"""

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import os

import redis as rds
import flask as fsk
import gevent.pywsgi as wsg
import visiomode.config as cfg


def create_app():
    """Flask app factory

    Returns:
        Flask app object
    """
    config = cfg.Config()
    redis = rds.Redis(host=config.redis_host, port=config.redis_port)

    app = fsk.Flask(__name__)
    app.config.from_mapping({
        'SECRET_KEY': config.flask_key,
        'DEBUG': config.debug,
    })

    @app.route('/')
    def hello_world():
        return 'Hello, World!'

    return app


if __name__ == '__main__':
    http_server = wsg.WSGIServer(('', 5000), create_app())
    http_server.serve_forever()
