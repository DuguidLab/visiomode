"""GUI Application entry point"""

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import pygame
import pygame.locals
import visiomode.storage as storage
import visiomode.models as models
import visiomode.gui.stimuli as stim

import faulthandler  # report segmentation faults as tracebacks

faulthandler.enable()


def main():
    # Initialise screen
    pygame.init()
    screen = pygame.display.set_mode((600, 400))
    pygame.display.set_caption("Basic Pygame program")

    # Fill background
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((250, 250, 250))

    # Display some text
    font = pygame.font.Font(None, 36)
    text = font.render("Hello There", 1, (10, 10, 10))
    textpos = text.get_rect()
    textpos.centerx = background.get_rect().centerx
    background.blit(text, textpos)

    # Blit everything to the screen
    screen.blit(background, (0, 0))
    pygame.display.flip()

    # Event loop
    while 1:
        for event in pygame.event.get():
            if event.type == pygame.locals.QUIT:
                return

        screen.blit(background, (0, 0))
        pygame.display.flip()

    # window = pyglet.window.Window(resizable=True)
    # main_batch = pyglet.graphics.Batch()
    #
    # status_sub = rds.subscribe_status(threaded=False)
    # session = None
    #
    # label = pyglet.text.Label(
    #     "Hello, world",
    #     font_name="Times New Roman",
    #     font_size=36,
    #     x=window.width // 2,
    #     y=window.height // 2,
    #     anchor_x="center",
    #     anchor_y="center",
    #     batch=main_batch,
    # )
    #
    # @window.event
    # def on_mouse_press(x, y, button, modifiers):
    #     if button == pyglet.window.mouse.LEFT:
    #         print("The left mouse button was pressed.")
    #
    # @window.event
    # def on_draw():
    #     window.clear()
    #     main_batch.draw()
    #
    # def update_status(dt):
    #     if not status_sub.get_message():
    #         return
    #     status = rds.get_status()
    #     print("updating...")
    #     if status == storage.DEBUG:
    #         label.text = "DEBUG"
    #     if status == storage.REQUESTED:
    #         label.text = "started!"
    #         # get request
    #         request = rds.get_session_request()
    #         print(request)
    #         task = pyglet.window.Window(resizable=True)
    #         rds.set_status(storage.ACTIVE)
    #
    # pyglet.clock.schedule_interval(update_status, 1 / 60)
    # pyglet.app.run()


if __name__ == "__main__":
    main()
