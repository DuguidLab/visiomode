"""GUI Application entry point"""

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import pygame as pg
import visiomode.storage as storage
import visiomode.webpanel as webpanel
import visiomode.protocols as protocols

import faulthandler  # report segmentation faults as tracebacks

faulthandler.enable()

rds = storage.RedisClient()

clock = pg.time.Clock()


def main():
    """Application entry point"""
    # Subscribe to Redis status updates
    status_sub = rds.subscribe_status(threaded=False)

    # Initialise webpanel, run in background
    webpanel.runserver(threaded=True)

    # Initialise GUI
    pg.init()

    # Set app icon
    # Dimensions should be 512x512, 300 ppi for retina
    icon = pg.image.load("visiomode/res/icon.png")
    pg.display.set_icon(icon)

    # Initialise screen
    screen = pg.display.set_mode((600, 400))
    pg.display.set_caption("Visiomode")

    # Fill background
    background = pg.Surface(screen.get_size())
    background = background.convert()
    background.fill((0, 0, 0))

    # Display some text
    font = pg.font.Font(None, 36)
    text = font.render("Loading...", 1, (255, 255, 255))
    textpos = text.get_rect()
    textpos.centerx = background.get_rect().centerx
    textpos.centery = (
        background.get_rect().centery + 60
    )  # TODO calculate offset at runtime
    background.blit(text, textpos)

    # Loading screen - wait until webpanel comes online
    loading_img = pg.image.load("visiomode/res/loading.png")
    loading_img = pg.transform.smoothscale(loading_img, (100, 100))
    loading_img_pos = loading_img.get_rect()
    loading_img_pos.centerx = background.get_rect().centerx
    loading_img_pos.centery = (
        background.get_rect().centery - 40
    )  # TODO calculate offset at runtime

    background.blit(loading_img, loading_img_pos)

    # Blit everything to the screen
    screen.blit(background, (0, 0))
    pg.display.flip()

    def rotate(image, rect, angle):
        """Rotate the image while keeping its center."""
        # Rotate the original image without modifying it.
        new_image = pg.transform.rotozoom(image, angle, 1)
        # Get a new rect with the center of the old rect.
        rect = new_image.get_rect(center=rect.center)
        return new_image, rect

    angle = 0
    while angle != 1080:
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                return

        angle += 5

        image, rect = rotate(loading_img, loading_img_pos, angle)

        background.blit(image, rect)
        screen.blit(background, (0, 0))
        pg.display.flip()
        clock.tick(100)

    text.fill((0, 0, 0))
    background.blit(text, textpos)
    text = font.render("Ready", 1, (255, 255, 255))

    textpos = text.get_rect()
    textpos.centerx = background.get_rect().centerx
    textpos.centery = (
        background.get_rect().centery + 60
    )  # TODO calculate offset at runtime
    background.blit(text, textpos)
    screen.blit(background, (0, 0))

    pg.display.flip()

    protocol = None

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
