"""Module that defines the available task and stimulation protocols in a stimulus agnostic manner."""

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.
import re
import collections
import time
import threading
import queue
import flask
import pygame as pg
import visiomode.stimuli as stim

HIT = "hit"
MISS = "miss"
PRECUED = "precued"
ON_TARGET = "on_target"
ON_DISTRACTOR = "on_distractor"
ON_BLANK = "on_blank"

TouchResponse = collections.namedtuple(
    "TouchResponse", ["action", "x", "y", "dist_x", "dist_y", "duration"]
)


class BaseProtocol(object):
    form_path = "protocols/protocol.html"

    def __init__(self, screen, duration: float, *args, **kwargs):
        self.screen = screen
        self.is_running = False

        self._timer_thread = threading.Thread(
            target=self._timer, args=[duration], daemon=True
        )

    def start(self):
        """Start the protocol"""
        self.is_running = True
        self._timer_thread.start()

    def stop(self):
        self.is_running = False

    def _timer(self, duration: float):
        start_time = time.time()
        while time.time() - start_time < duration:
            # If the session has been stopped, stop timer
            if not self.is_running:
                return
        self.stop()

    @classmethod
    def get_common_name(cls):
        """"Return the human-readable, space-separated name for the class."""
        return re.sub(r"((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))", r" \1", cls.__name__)

    @classmethod
    def get_children(cls):
        """Return all inheriting children as a list."""
        return cls.__subclasses__()

    @classmethod
    def get_identifier(cls):
        return cls.__name__.lower()

    @classmethod
    def get_form(cls):
        return flask.render_template(
            cls.form_path, stimuli=stim.BaseStimulus.get_children()
        )


class Task(BaseProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.iti = 3  # TODO embed in request
        self.stim_duration = 2  # TODO embed in request

        self.events = []

        self._response_q = queue.Queue()

        self._session_thread = threading.Thread(
            target=self._session_runner, daemon=True
        )

    def start(self):
        super().start()
        self._session_thread.start()

    def show_stim(self):
        pass

    def hide_stim(self):
        pass

    def _session_runner(self):
        while self.is_running:
            self.hide_stim()
            iti_start = time.time()
            while time.time() - iti_start < self.iti:
                if not self._response_q.empty():
                    print("precued")
                    response = self._response_q.get()
                    print(response)
                    break
            else:
                # To prevent stimulus showing after the session has ended, check if the session is still running.
                if not self.is_running:
                    return
                self.show_stim()
                stim_start = time.time()
                while time.time() - stim_start < self.stim_duration:
                    if not self._response_q.empty():
                        response = self._response_q.get()
                        print("hit")
                        print(response)
                        break


class Presentation(BaseProtocol):
    pass


class SingleTarget(Task):
    form_path = "protocols/single_target.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.background = pg.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((0, 0, 0))
        self.screen.blit(self.background, (0, 0))
        self.target = pg.sprite.RenderClear(stim.Grating())

        self._last_touchdown = time.time()
        self._last_pos = (0, 0)

    def stop(self):
        print("stop")
        super().stop()
        self.target.clear(self.screen, self.background)

    def show_stim(self):
        self.target.draw(self.screen)

    def hide_stim(self):
        self.target.clear(self.screen, self.background)

    def handle_events(self, events):
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN:
                self._last_touchdown = time.time()
                self._last_pos = event.pos
            if event.type == pg.MOUSEBUTTONUP:
                for sprite in self.target.sprites():
                    if sprite.rect.collidepoint(event.pos):
                        self._response_q.put(
                            TouchResponse(
                                ON_TARGET,
                                event.pos[0],
                                event.pos[1],
                                event.pos[0] - self._last_pos[0],
                                event.pos[1] - self._last_pos[1],
                                time.time() - self._last_touchdown,
                            )
                        )
                        break
                else:
                    self._response_q.put(
                        TouchResponse(
                            ON_BLANK,
                            event.pos[0],
                            event.pos[1],
                            event.pos[0] - self._last_pos[0],
                            event.pos[1] - self._last_pos[1],
                            time.time() - self._last_touchdown,
                        )
                    )


def get_protocol(protocol_id):
    protocols = Task.get_children() + Presentation.get_children()
    for Protocol in protocols:
        if Protocol.get_identifier() == protocol_id:
            return Protocol


class InvalidProtocol(Exception):
    pass
