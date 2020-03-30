#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import redis
import visiomode.config as cfg

ACTIVE = 'active'
STARTED = 'started'
STOPPED = 'stopped'
INACTIVE = 'inactive'
ERROR = 'error'


class RedisClient(redis.Redis):
    def __init__(self, *args, **kwargs):
        config = cfg.Config()
        super(RedisClient, self).__init__(host=config.redis_host, port=config.redis_port, charset="utf-8",
                                          decode_responses=True, *args, **kwargs)

    def get_status(self):
        return self.get('status')

    def set_status(self, status):
        self.mset({'status': status})

    def subscribe_status(self, callback=None, threaded=True, thread_sleep=0.01):
        pubsub = self.pubsub()
        status_key = "__key*__:status"

        if callback:
            pubsub.psubscribe(**{status_key: callback})
        else:
            pubsub.psubscribe(status_key)

        if threaded:
            return pubsub.run_in_thread(sleep_time=thread_sleep, daemon=True)

        return pubsub
