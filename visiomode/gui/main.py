"""GUI Application entry point"""

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import pyglet
import redis
import visiomode.config as cfg

import faulthandler  # report segmentation faults as tracebacks
faulthandler.enable()

config = cfg.Config()
rds = redis.Redis(host=config.redis_host, port=config.redis_port)


def main():
    window = pyglet.window.Window(resizable=True)
    main_batch = pyglet.graphics.Batch()

    session_sub = rds.pubsub()
    session_sub.psubscribe("__key*__:status")

    label = pyglet.text.Label('Hello, world',
                              font_name='Times New Roman',
                              font_size=36,
                              x=window.width // 2, y=window.height // 2,
                              anchor_x='center', anchor_y='center', batch=main_batch)

    @window.event
    def on_mouse_press(x, y, button, modifiers):
        if button == pyglet.window.mouse.LEFT:
            print('The left mouse button was pressed.')

    @window.event
    def on_draw():
        window.clear()
        main_batch.draw()

    def update_status(dt):
        if not session_sub.get_message():
            return
        status = rds.get('status').decode("utf8")
        if status == 'test':
            label.text = 'something'
        if status == 'started':
            label.text = 'started!'

    pyglet.clock.schedule_interval(update_status, 1 / 60)
    pyglet.app.run()


if __name__ == '__main__':
    main()
