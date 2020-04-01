"""GUI Application entry point"""

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import pyglet
import visiomode.storage as storage

import faulthandler  # report segmentation faults as tracebacks

faulthandler.enable()

rds = storage.RedisClient()


def main():
    window = pyglet.window.Window(resizable=True)
    main_batch = pyglet.graphics.Batch()

    session_sub = rds.subscribe_status(threaded=False)

    label = pyglet.text.Label(
        "Hello, world",
        font_name="Times New Roman",
        font_size=36,
        x=window.width // 2,
        y=window.height // 2,
        anchor_x="center",
        anchor_y="center",
        batch=main_batch,
    )

    @window.event
    def on_mouse_press(x, y, button, modifiers):
        if button == pyglet.window.mouse.LEFT:
            print("The left mouse button was pressed.")

    @window.event
    def on_draw():
        window.clear()
        main_batch.draw()

    def update_status(dt):
        if not session_sub.get_message():
            return
        status = rds.get_status()
        if status == "test":
            label.text = "something"
        if status == "started":
            label.text = "started!"

    pyglet.clock.schedule_interval(update_status, 1 / 60)
    pyglet.app.run()


if __name__ == "__main__":
    main()
