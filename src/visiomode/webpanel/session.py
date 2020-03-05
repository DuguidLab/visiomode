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
    """SocketIO namespace for the Session interface.

    Attributes:
        session_sub: Redis session channel.
        session_thread: Status update thread; listens for updates on the session channel.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Subscribe to Redis session status updates.
        self.session_sub = rds.pubsub()
        self.session_sub.psubscribe(**{"__key*__:status": self.update_status})
        self.session_thread = self.session_sub.run_in_thread(sleep_time=0.01)

    def on_connect(self):
        """Runs when a frontend client navigates to the session page.

        Corresponds to SocketIO `connect` event. Pushes current session status to frontend.
        """
        print('connected')
        self.update_status()

    def on_disconnect(self):
        """Runs when a frontend client disconnects from the session page.

        Corresponds to SocketIO `disconnect` event.
        """
        print("disconnected")

    def on_session_start(self, request: dict):
        """Runs when the a frontend client submits a request to start a new session.

        Args:
            request: A dictionary with session parameters. Required keys are 'animal_id', 'experiment', 'protocol' and
                'duration'.
        """
        print(request)
        rds.mset({'status': 'active'})  # TODO make this an interminent state, GUI sets active
        rds.mset(**request)

    def on_session_stop(self):
        """Runs when the a frontend client submits a request to stop the active session."""
        rds.mset({'status': 'stopped'})

    def on_message(self, data):
        """Generic message passing between frontend and backend, used for debugging."""
        print(data)

    def update_status(self, *args, **kwargs):
        """Pushes session status update to front-end."""
        self.emit('status', rds.get('status').decode("utf-8"))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Cleans up resources before instance is destroyed.

        Stop the Redis listener thread to allow the class to be garbage collected.
        """
        self.session_thread.stop()
