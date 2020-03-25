#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import pyglet
import redis
import visiomode.config as cfg


config = cfg.Config()
rds = redis.Redis(host=config.redis_host, port=config.redis_port)


class RedisEventDispatch(pyglet.event.EventDispatcher):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.session_sub = rds.pubsub()
        self.session_sub.psubscribe(**{"__key*__:status": self.handle_update})
        self.session_thread = self.session_sub.run_in_thread(sleep_time=0.01, daemon=True)

    def handle_update(self, *args, **kwargs):
        status = rds.get('status').decode("utf8")
        print(status)
        if status == "started":
            print("starting")
        elif status == "stopped":
            print("stopping")
        self.dispatch_event("on_update")


RedisEventDispatch.register_event_type("on_update")
