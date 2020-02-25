"""Real-time async session streaming module"""

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import redis
import flask_socketio as sock
import visiomode.config as cfg


config = cfg.Config()
rds = redis.Redis(host=config.redis_host, port=config.redis_port)


class SessionNamespace(sock.Namespace):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status_sub = rds.pubsub()
        self.status_sub.psubscribe(**{"__key*__:status": self.update_status})
        self.status_thread = self.status_sub.run_in_thread(sleep_time=0.01)

    def on_connect(self):
        print('connected')
        self.update_status()

    def on_disconnect(self):
        print("disconnected")

    def on_session_start(self, request):
        rds.mset({'status': 'active'})

    def on_session_stop(self):
        rds.mset({'status': 'inactive'})

    def on_message(self, data):
        print(data)

    def update_status(self, *args, **kwargs):
        """Handles session status update on Redis"""
        self.emit('status', rds.get('status').decode("utf-8") or 'inactive')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Cleans up resources before instance is destroyed.

        In this instance, stop the redis listener thread to allow the class to be garbage collected.
        """
        self.status_thread.stop()
