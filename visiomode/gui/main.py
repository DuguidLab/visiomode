"""GUI Application entry point"""

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import pygame as pg
import visiomode.storage as storage
import visiomode.gui.protocols as protocols

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
    background.fill((0, 0, 0))

    # Display some text
    font = pg.font.Font(None, 36)
    text = font.render("Ready", 1, (255, 255, 255))
    textpos = text.get_rect()
    textpos.centerx = background.get_rect().centerx
    textpos.centery = background.get_rect().centery
    background.blit(text, textpos)

    protocol = None

    # Blit everything to the screen
    screen.blit(background, (0, 0))
    pg.display.flip()

    # Event loop
    while True:
        if status_sub.get_message():
            status = rds.get_status()
            print("updating...")
            if status == storage.DEBUG:
                text = font.render("Debug", 1, (10, 10, 10))
                background.blit(text, textpos)
            if status == storage.REQUESTED:
                # text = font.render("Started!", 1, (10, 10, 10))
                request = rds.get_session_request()
                print(request)

                protocol = protocols.get_protocol(1, screen, request)

                protocol.start()

                rds.set_status(storage.ACTIVE)

            if status == storage.STOPPED:
                print("stopping...")

                if protocol and protocol.is_running:
                    protocol.stop()
        if protocol and not protocol.is_running:
            print("finished")

            background.blit(text, textpos)
            screen.blit(background, (0, 0))

            rds.set_status(storage.INACTIVE)

            protocol = None
        events = pg.event.get()
        if protocol and protocol.is_running:
            protocol.handle_events(events)
        for event in events:
            if event.type == pg.QUIT:
                return

        pg.display.flip()


if __name__ == "__main__":
    main()
