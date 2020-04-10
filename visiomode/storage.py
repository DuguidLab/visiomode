"""Session active storage and message broker module."""

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import redis
import visiomode.config as cfg

ACTIVE = "active"
REQUESTED = "requested"
STOPPED = "stopped"
INACTIVE = "inactive"
ERROR = "error"
STATUS_CODES = (ACTIVE, REQUESTED, STOPPED, INACTIVE, ERROR)
STATUS_KEY = "status"
SESSION_REQUEST_KEY = "session_request"
REQUIRED_SESSION_KEYS = (
    "animal_id",
    "experiment",
    "protocol",
    "duration",
)


class RedisClient(redis.Redis):
    """Client handler for Redis storage.

    Acts as a convenience layer over raw Redis calls and sanitises user input.
    """

    def __init__(self, *args, **kwargs):
        """Initialises connection to Redis server."""
        _config = cfg.Config()
        super(RedisClient, self).__init__(
            host=_config.redis_host,
            port=_config.redis_port,
            charset="utf-8",
            decode_responses=True,
            *args,
            **kwargs
        )

        # Make sure notifications are enabled so pubsub works.
        self.config_set("notify-keyspace-events", "AKE")

    def get_status(self):
        """Gets current session status.

         This corresponds to the value of the STATUS_KEY hash on the Redis server.

        Returns:
            A string representing the current value of the STATUS_KEY.
        """
        return self.get(STATUS_KEY)

    def set_status(self, status):
        """Sets the current status.

        Will create a key-value pair (STATUS_KEY: status) on the Redis server if it doesn't exist.

        Args:
            status: A string of the status code to be set. The string must be a valid STATUS_CODE.

        Raises:
            InvalidStatusCodeError: If an illegal status code string is supplied.
        """
        if status not in STATUS_CODES:
            raise InvalidStatusCodeError(
                "Valid status codes are: {}".format(STATUS_CODES)
            )
        self.mset({STATUS_KEY: status})

    def subscribe_status(self, callback=None, threaded=True, thread_sleep=0.01):
        """Sets up a subscription to session status updates.

        The subscriber can either run as a daemon with a callback function on every update, or alternatively the
        user can check for updates manually.

        Args:
            callback: If the subscriber is threaded, this specifies the function to be called every time a
                status update is published. Required if `threaded=True`, otherwise it's ignored.
            threaded: Boolean that specifies whether the subscriber should run in a separate thread as a deamon.
                If True, a `callback` function must be supplied to the call.
            thread_sleep: Float that specifies how often the daemon should check for an update. Required if
                `threaded=True`, otherwise it's ignored.

        Returns:
            Redis subscriber (pubsub) object.

        Raises:
            PubSubError: Raised if threaded=True but no callback is specified.

       Examples:
            To run as a background daemon, call as follows.

            >>> rds = RedisClient()
            >>> status_sub_threaded = rds.subscribe_status(threaded=True, callback=lambda: return "I am a callback")

            Alternatively, a subscriber can check for updates manually
            >>> rds.subscribe_status()
            >>> status_sub_manual = rds.subscribe_status(threaded=False)
            >>> status_sub_manual.get_message()  # This will indicate that there has been an update
            >>> rds.get_status()  # To get the new updated status as a string
        """
        pubsub = self.pubsub()
        status_key = "__key*__:" + STATUS_KEY

        if threaded:
            pubsub.psubscribe(**{status_key: callback})
            return pubsub.run_in_thread(sleep_time=thread_sleep, daemon=True)

        pubsub.psubscribe(status_key)

        return pubsub

    def request_session(self, request: dict):
        """Submits a request for a new experimental session to Redis.

        The request manifests as a setting of the session_request key to a hash of session parameters, followed by
        a status update. The status is changed to REQUESTED, with the expectation that listening clients will pick
        up the change and fill the request.

        Args:
            request: A dictionary of session parameters. Required keys are specified in REQUIRED_SESSION_KEYS.

        Raises:
            SessionRequestError: Raised if one of the required keys hasn't been supplied.
        """
        for key in REQUIRED_SESSION_KEYS:
            if key not in request.keys():
                raise SessionRequestError("Missing required key - {}".format(key))
        self.hmset(SESSION_REQUEST_KEY, request)
        self.set_status(REQUESTED)

    def get_session_request(self):
        """Fetches a pending session request.

         This corresponds to the value of the SESSION_REQUEST_KEY hash on the Redis server.

        Returns:
            A dictionary holding the requested session parameters."""
        return self.hgetall(SESSION_REQUEST_KEY)

    def request_session_stop(self):
        """Ask for the current active session to stop.

        This is implemented as a status update, which a listening active client should pick up to stop the session.
        """
        self.set_status(STOPPED)


class RedisClientError(Exception):
    """Custom generic exception class for anything that goes wrong with the RedisClient class."""

    pass


class SessionRequestError(RedisClientError):
    """Describes errors that occur while a session request is uploaded to Redis."""

    pass


class InvalidStatusCodeError(RedisClientError):
    """An invalid status code has been supplied by the user."""

    pass
