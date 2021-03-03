"""Visiomode Application main class and core utilities"""

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import time
import queue
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

        action_q = queue.Queue()  # Queue for action messages
        log_q = queue.Queue()  # Queue for log messages

        # Initialise webpanel, run in background
        webpanel.runserver(threaded=True)

        # Initialise GUI
        pg.init()

        # Set app icon
        # Dimensions should be 512x512, 300 ppi for retina
        icon = pg.image.load("visiomode/res/icon.png")
        pg.display.set_icon(icon)

        # Initialise screen
        self.screen = pg.display.set_mode(
            (400, 800)
        )  # TODO refactor resolution settings to config
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

        # Main program loop and session handler
        # TODO session timing should go here?
        while True:
            request = dict()
            try:
                request = action_q.get(block=False)
            except queue.Empty:
                pass
            if request:
                if "type" not in request.keys():
                    print("Invalid request - {}".format(request))
                    continue
                if request["type"] == "start":
                    self.session = models.Session(
                        animal_id=request["data"].pop("animal_id"),
                        experiment=request["data"].pop("experiment"),
                        protocol=request["data"].pop("protocol"),
                        duration=float(request["data"].pop("duration")),
                    )
                    Protocol = protocols.get_protocol(self.session.protocol)
                    self.protocol = Protocol(screen=self.screen, **request["data"])
                    self.protocol.start()

            events = pg.event.get()
            if self.session:
                self.protocol.update(events)
                self.session.trials = self.protocol.trials

            if (
                self.session
                and time.time() - self.protocol.start_time < self.session.duration * 60
            ):
                print("finished!")
                self.protocol.stop()
                self.session.complete = True
                self.session.trials = self.protocol.trials
                self.session.save(self.config.data_dir)

                self.protocol = None
                self.session = None

            for event in events:
                if event.type == pg.QUIT:
                    if self.session:
                        self.session.trials = self.protocol.trials
                        self.session.save(self.config.data_dir)
                    return


def rotate(image, rect, angle):
    """Rotate an image while keeping its center."""
    # Rotate the original image without modifying it.
    new_image = pg.transform.rotozoom(image, angle, 1)
    # Get a new rect with the center of the old rect.
    rect = new_image.get_rect(center=rect.center)
    return new_image, rect
