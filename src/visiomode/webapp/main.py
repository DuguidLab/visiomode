#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import redis as rds
import flask as fsk
import gevent.pywsgi as wsg
import visiomode.config as cfg


def main():
    config = cfg.Config()
    redis = rds.Redis(host=config.redis_host, port=config.redis_port)

    # Dummy flask placeholder app
    app = fsk.Flask(__name__)

    @app.route('/')
    def hello_world():
        return 'Hello, World!'

    http_server = wsg.WSGIServer(('', 5000), app)
    http_server.serve_forever()


if __name__ == '__main__':
    main()
