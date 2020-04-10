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
    def __init__(self, *args, **kwargs):
        config = cfg.Config()
        super(RedisClient, self).__init__(
            host=config.redis_host,
            port=config.redis_port,
            charset="utf-8",
            decode_responses=True,
            *args,
            **kwargs
        )
        self.config_set("notify-keyspace-events", "AKE")

    def get_status(self):
        return self.get(STATUS_KEY)

    def set_status(self, status):
        if status not in STATUS_CODES:
            raise InvalidStatusCodeError(
                "Valid status codes are: {}".format(STATUS_CODES)
            )
        self.mset({STATUS_KEY: status})

    def subscribe_status(self, callback=None, threaded=True, thread_sleep=0.01):
        pubsub = self.pubsub()
        status_key = "__key*__:" + STATUS_KEY

        if threaded:
            pubsub.psubscribe(**{status_key: callback})
            return pubsub.run_in_thread(sleep_time=thread_sleep, daemon=True)

        pubsub.psubscribe(status_key)

        return pubsub

    def request_session(self, request: dict):
        """Submits a request for a new experimental session to Redis

        Args:
            request:
        """
        for key in REQUIRED_SESSION_KEYS:
            if key not in request.keys():
                raise SessionRequestError("Missing required key - {}".format(key))
        self.hmset(SESSION_REQUEST_KEY, request)
        self.set_status(REQUESTED)

    def get_session_request(self):
        return self.hgetall(SESSION_REQUEST_KEY)

    def request_session_stop(self):
        self.set_status(STOPPED)


class RedisClientError(Exception):
    pass


class SessionRequestError(RedisClientError):
    pass


class InvalidStatusCodeError(RedisClientError):
    pass
