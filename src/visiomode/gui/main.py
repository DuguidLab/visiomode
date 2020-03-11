"""GUI Application entry point"""

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import redis
import pyglet
import visiomode.config as cfg


config = cfg.Config()
rds = redis.Redis(host=config.redis_host, port=config.redis_port)


class RedisEventHandler(pyglet.event.EventDispatcher):
    def __init__(self):
        super(RedisEventHandler, self).__init__()
        self.session_sub = rds.pubsub()
        self.session_sub.psubscribe(**{"__key*__:status": self.get_status})
        self.session_thread = self.session_sub.run_in_thread(sleep_time=0.01, daemon=True)

    def get_status(self, *args, **kwargs):
        status = rds.get('status').decode("utf8")
        print("Status is {}".format(status))
        self.dispatch_event('on_status_update')


RedisEventHandler.register_event_type('on_status_update')


def main():
    # Dummy hello world pyglet window
    window = pyglet.window.Window()
    redis_handler = RedisEventHandler()
    label = pyglet.text.Label('Hello, world',
                              font_name='Times New Roman',
                              font_size=36,
                              x=window.width // 2, y=window.height // 2,
                              anchor_x='center', anchor_y='center')

    @window.event
    def on_draw():
        window.clear()
        label.draw()

    pyglet.app.run()


if __name__ == '__main__':
    main()
