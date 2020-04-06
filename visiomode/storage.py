#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import redis
import visiomode.config as cfg

ACTIVE = "active"
STARTED = "started"
STOPPED = "stopped"
INACTIVE = "inactive"
ERROR = "error"
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
        return self.get("status")

    def set_status(self, status):
        self.mset({"status": status})

    def subscribe_status(self, callback=None, threaded=True, thread_sleep=0.01):
        pubsub = self.pubsub()
        status_key = "__key*__:status"

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
        self.hmset("session_request", request)

    def get_session_request(self):
        return self.hgetall("session_request")


class RedisClientError(Exception):
    pass


class SessionRequestError(RedisClientError):
    pass
