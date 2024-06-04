"""Visiomode main class and application loop."""

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import os
import logging
import time
import datetime
import threading
import queue
import pkg_resources
import pygame as pg
import visiomode.config as conf
import visiomode.models as models
import visiomode.webpanel as webpanel
import visiomode.protocols as protocols

# Register mouse events as touch events - useful for debugging.
os.environ["SDL_MOUSE_TOUCH_EVENTS"] = "1"


class Visiomode:
    """Visiomode application main class.

    This class handles the main application loop, and initialises the mouse GUI
    and user webpanel. It also handles requests from the webpanel, and passes
    them on to the appropriate protocol runner.
    """

    def __init__(self):
        """Initialise application.

        This initialises the application, and starts the webpanel and GUI
        threads. It also loads the configuration file, and displays the
        loading animation on the GUI screen while the webpanel is loading.
        """
        self.clock = pg.time.Clock()
        self.config = conf.Config()

        self.action_q = queue.Queue()  # Queue for action messages
        self.log_q = queue.Queue()  # Queue for log messages

        self.session = None

        # Initialise webpanel, run in background
        webpanel.runserver(action_q=self.action_q, log_q=self.log_q, threaded=True)

        request_thread = threading.Thread(target=self.request_listener, daemon=True)
        request_thread.start()

        # Initialise GUI
        pg.init()

        # Set app icon
        # Dimensions should be 512x512, 300 ppi for retina
        icon = pg.image.load(
            pkg_resources.resource_filename("visiomode.res", "icon.png")
        )
        pg.display.set_icon(icon)

        # Initialise screen
        self.screen = pg.display.set_mode(
            (self.config.width, self.config.height),
            pg.FULLSCREEN if self.config.fullscreen else 0,
        )
        pg.display.set_caption("Visiomode")

        self.loading_screen()

        self.run_main()

    def loading_screen(self):
        """Rotating logo to entertain user and mouse while the webpanel is loading."""
        # Fill background
        self.background = pg.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((0, 0, 0))

        # Display some text
        self.font = pg.font.Font(None, 36)
        text = self.font.render("Loading...", 1, (255, 255, 255))
        textpos = text.get_rect()
        textpos.centerx = self.background.get_rect().centerx
        textpos.centery = self.background.get_rect().centery + 60

        self.background.blit(text, textpos)

        # Loading screen - wait until webpanel comes online
        loading_img = pg.image.load(
            pkg_resources.resource_filename("visiomode.res", "loading.png")
        )
        loading_img = pg.transform.smoothscale(loading_img, (100, 100))
        loading_img_pos = loading_img.get_rect()
        loading_img_pos.centerx = self.background.get_rect().centerx
        loading_img_pos.centery = self.background.get_rect().centery - 40

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

    def run_main(self):
        """Main application loop.

        This is the main application loop. It checks for events, and updates the
        protocol runner if one is active. If the protocol is no longer running,
        or the session duration has elapsed, the session is saved and the
        protocol is stopped. If the application receives a quit event, the
        session is saved and the application exits.
        """
        while True:
            if self.session:
                self.session.protocol.update()
                self.session.trials = self.session.protocol.trials
            if self.session and (
                not self.session.protocol.is_running
                or time.time() - self.session.protocol.start_time
                > self.session.duration * 60
            ):
                logging.info("Session finished.")
                self.session.protocol.stop()
                self.session.complete = True
                self.session.trials = self.session.protocol.trials
                self.session.save(self.config.data_dir)

                self.session = None
                pg.event.clear()  # Clear unused events so queue doesn't fill up

            if pg.event.get(eventtype=pg.QUIT):
                if self.session:
                    self.session.trials = self.session.protocol.trials
                    self.session.save(self.config.data_dir)
                return

            pg.display.flip()

    def request_listener(self):
        """Parser for requests from the webpanel.

        This tries to parse the request and pass it on to the appropriate
        protocol runner. It also handles requests for the current status of the
        application.

        Requests are read from the class action queue, which is written to by
        the webpanel thread. The response is written to the class log queue,
        which is read by the webpanel thread.
        """
        while True:
            request = self.action_q.get()
            if "type" not in request.keys():
                logging.error("Invalid request - {}".format(request))
                continue
            if request["type"] == "start":
                # Update config
                conf.Config().input_device_address = (
                    request["data"].get("response_address")
                    or conf.Config().input_device_address
                )
                conf.Config().reward_device_address = (
                    request["data"].get("reward_address")
                    or conf.Config().reward_device_address
                )
                conf.Config().save()

                protocol = protocols.get_protocol(request["data"].pop("protocol"))
                self.session = models.Session(
                    animal_id=request["data"].pop("animal_id"),
                    experiment=request["data"].pop("experiment"),
                    duration=float(request["data"].pop("duration")),
                    timestamp=datetime.datetime.now().isoformat(),
                    protocol=protocol(screen=self.screen, **request["data"]),
                    spec=request["data"],
                )
                self.session.protocol.start()
            elif request["type"] == "status":
                self.log_q.put(
                    {
                        "status": "active" if self.session else "inactive",
                        "data": self.session.to_json() if self.session else [],
                    }
                )
            elif request["type"] == "stop":
                self.session.protocol.stop()


def rotate(image, rect, angle):
    """Rotate an image while keeping its center.

    Used for the loading screen.

    Args:
        image (pygame.Surface): Image to rotate.
        rect (pygame.Rect): Rectangle to rotate.
        angle (float): Angle to rotate by.

    Returns:
        pygame.Surface: Rotated image.
        pygame.Rect: New rectangle for the rotated image.
    """
    # Rotate the original image without modifying it.
    new_image = pg.transform.rotozoom(image, angle, 1)
    # Get a new rect with the center of the old rect.
    rect = new_image.get_rect(center=rect.center)
    return new_image, rect
