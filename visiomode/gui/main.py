"""GUI Application entry point"""

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import pygame
import pygame.locals
import visiomode.storage as storage

import faulthandler  # report segmentation faults as tracebacks

faulthandler.enable()

rds = storage.RedisClient()


def main():
    # Subscribe to Redis status updates
    status_sub = rds.subscribe_status(threaded=False)

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
        if status_sub.get_message():
            status = rds.get_status()
            print("updating...")
            if status == storage.DEBUG:
                text = font.render("Debug", 1, (10, 10, 10))
            if status == storage.REQUESTED:
                text = font.render("Started!", 1, (10, 10, 10))
                # get request
                request = rds.get_session_request()
                print(request)
                rds.set_status(storage.ACTIVE)
            background.fill((250, 250, 250))
            background.blit(text, textpos)
        for event in pygame.event.get():
            if event.type == pygame.locals.QUIT:
                return

        screen.blit(background, (0, 0))
        pygame.display.flip()


if __name__ == "__main__":
    main()
