"""GUI Application entry point"""

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import pyglet as pgt


def main():
    # Dummy hello world pyglet window
    window = pgt.window.Window()
    label = pgt.text.Label('Hello, world',
                           font_name='Times New Roman',
                           font_size=36,
                           x=window.width // 2, y=window.height // 2,
                           anchor_x='center', anchor_y='center')

    @window.event
    def on_draw():
        window.clear()
        label.draw()

    pgt.app.run()


if __name__ == '__main__':
    main()
