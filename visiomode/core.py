"""Visiomode Application main class and core utilities"""

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import pygame as pg
import visiomode.config as conf
import visiomode.models as models
import visiomode.messaging as messaging
import visiomode.webpanel as webpanel
import visiomode.protocols as protocols


class Visiomode:
    def __init__(self):
        self.rds = messaging.RedisClient()
        self.clock = pg.time.Clock()
        self.config = conf.Config()

        # Subscribe to Redis status updates
        status_sub = self.rds.subscribe_status(
            threaded=True, callback=self._messaging_callback
        )
        # Initialise webpanel, run in background
        webpanel.runserver(threaded=True)

        # Initialise GUI
        pg.init()

        # Set app icon
        # Dimensions should be 512x512, 300 ppi for retina
        icon = pg.image.load("visiomode/res/icon.png")
        pg.display.set_icon(icon)

        # Initialise screen
        self.screen = pg.display.set_mode((400, 800), pg.FULLSCREEN)
        pg.display.set_caption("Visiomode")

        # Fill background
        self.background = pg.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((0, 0, 0))

        # Display some text
        self.font = pg.font.Font(None, 36)
        text = self.font.render("Loading...", 1, (255, 255, 255))
        textpos = text.get_rect()
        textpos.centerx = self.background.get_rect().centerx
        textpos.centery = (
            self.background.get_rect().centery + 60
        )  # TODO calculate offset at runtime

        self.background.blit(text, textpos)

        # Loading screen - wait until webpanel comes online
        loading_img = pg.image.load("visiomode/res/loading.png")
        loading_img = pg.transform.smoothscale(loading_img, (100, 100))
        loading_img_pos = loading_img.get_rect()
        loading_img_pos.centerx = self.background.get_rect().centerx
        loading_img_pos.centery = (
            self.background.get_rect().centery - 40
        )  # TODO calculate offset at runtime

        self.background.blit(loading_img, loading_img_pos)

        # Blit everything to the screen
        self.screen.blit(self.background, (0, 0))
        pg.display.flip()

        angle = 0
        while angle != 1080:
            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    return

            angle += 5

            image, rect = rotate(loading_img, loading_img_pos, angle)

            self.background.blit(image, rect)
            self.screen.blit(self.background, (0, 0))
            pg.display.flip()
            self.clock.tick(100)

        text.fill((0, 0, 0))
        self.background.blit(text, textpos)
        text = self.font.render("Ready", 1, (255, 255, 255))

        textpos = text.get_rect()
        textpos.centerx = self.background.get_rect().centerx
        textpos.centery = (
            self.background.get_rect().centery + 60
        )  # TODO calculate offset at runtime

        self.background.blit(text, textpos)
        self.screen.blit(self.background, (0, 0))

        pg.display.flip()

        self.protocol = None
        self.session = None

        # Event loop
        while True:
            if self.protocol and not self.protocol.is_running:
                print("finished")

                self.background.blit(text, textpos)
                self.screen.blit(self.background, (0, 0))

                self.rds.set_status(messaging.INACTIVE)

                self.session.complete = True
                self.session.trials = self.protocol.trials
                self.session.save(self.config.data_dir)

                self.protocol = None
                self.session = None
            events = pg.event.get()
            if self.protocol and self.protocol.is_running:
                self.protocol.update(events)
            for event in events:
                if event.type == pg.QUIT:
                    if self.session:
                        self.session.trials = self.protocol.trials
                        self.session.save(self.config.data_dir)
                    return

            pg.display.update()

            self.clock.tick(self.config.fps)

    def parse_request(self, request: dict):
        """Parse new session request parameters."""
        session = models.Session(
            animal_id=request.pop("animal_id"),
            experiment=request.pop("experiment"),
            protocol=request.pop("protocol"),
            duration=float(request.pop("duration")),
        )
        Protocol = protocols.get_protocol(session.protocol)
        protocol = Protocol(screen=self.screen, duration=session.duration, **request)
        return session, protocol

    def _messaging_callback(self, *args, **kwargs):
        status = self.rds.get_status()
        print("updating...")
        if status == messaging.REQUESTED:
            request = self.rds.get_session_request()
            print(request)
            self.session, self.protocol = self.parse_request(request)
            self.protocol.start()
            self.rds.set_status(messaging.ACTIVE)

        if status == messaging.STOPPED:
            print("stopping...")
            if self.protocol and self.protocol.is_running:
                self.protocol.stop()


def rotate(image, rect, angle):
    """Rotate an image while keeping its center."""
    # Rotate the original image without modifying it.
    new_image = pg.transform.rotozoom(image, angle, 1)
    # Get a new rect with the center of the old rect.
    rect = new_image.get_rect(center=rect.center)
    return new_image, rect
