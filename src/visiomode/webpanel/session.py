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
    """SocketIO namespace for the Session interface

    Attributes:
        session_sub: Redis session channel
        session_thread: Status update thread; listens for updates on the session channel
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Subscribe to Redis session status updates
        self.session_sub = rds.pubsub()
        self.session_sub.psubscribe(**{"__key*__:session": self.update_status})
        self.session_thread = self.session_sub.run_in_thread(sleep_time=0.01)

    def on_connect(self):
        print('connected')
        self.update_status()

    def on_disconnect(self):
        print("disconnected")

    def on_session_start(self, request):
        rds.mset({'session': 'active'})

    def on_session_stop(self):
        rds.mset({'session': 'inactive'})

    def on_message(self, data):
        print(data)

    def update_status(self, *args, **kwargs):
        """Pushes status update to front-end."""
        self.emit('session', rds.get('session').decode("utf-8") or 'inactive')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Cleans up resources before instance is destroyed.

        Stop the Redis listener thread to allow the class to be garbage collected.
        """
        self.session_thread.stop()
