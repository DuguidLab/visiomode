"""GUI Application entry point"""

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import pygame as pg
import visiomode.storage as storage
import visiomode.gui.stimuli as stim

import faulthandler  # report segmentation faults as tracebacks

faulthandler.enable()

rds = storage.RedisClient()


def main():
    # Subscribe to Redis status updates
    status_sub = rds.subscribe_status(threaded=False)

    # Initialise screen
    pg.init()
    screen = pg.display.set_mode((600, 400))
    pg.display.set_caption("Basic Pygame program")

    # Fill background
    background = pg.Surface(screen.get_size())
    background = background.convert()
    background.fill((250, 250, 250))

    # Display some text
    font = pg.font.Font(None, 36)
    text = font.render("Hello There", 1, (10, 10, 10))
    textpos = text.get_rect()
    textpos.centerx = background.get_rect().centerx
    background.blit(text, textpos)

    target = None

    # Blit everything to the screen
    screen.blit(background, (0, 0))
    pg.display.flip()

    # Event loop
    while 1:
        if status_sub.get_message():
            status = rds.get_status()
            print("updating...")
            background.fill((250, 250, 250))
            if status == storage.DEBUG:
                text = font.render("Debug", 1, (10, 10, 10))
                background.blit(text, textpos)
            if status == storage.REQUESTED:
                # text = font.render("Started!", 1, (10, 10, 10))
                request = rds.get_session_request()
                print(request)

                target = pg.sprite.RenderClear(stim.Grating(0, 0))
                target.draw(screen)

                rds.set_status(storage.ACTIVE)
            if status == storage.STOPPED:
                print("stopping...")
                if target:
                    target.clear(screen, background)

                rds.set_status(storage.INACTIVE)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.MOUSEBUTTONUP:
                if target:
                    for sprite in target.sprites():
                        if sprite.rect.collidepoint(event.pos):
                            print("hit!")
                            target.clear(screen, background)

        # screen.blit(background, (0, 0))
        pg.display.flip()


if __name__ == "__main__":
    main()
