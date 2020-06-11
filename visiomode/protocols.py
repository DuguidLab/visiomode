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
import visiomode.models as models

HIT = "hit"
MISS = "miss"
PRECUED = "precued"

TOUCHDOWN = (pg.MOUSEBUTTONDOWN, pg.FINGERDOWN)
TOUCHUP = (pg.MOUSEBUTTONUP, pg.FINGERUP)

TouchEvent = collections.namedtuple(
    "TouchEvent", ["event_type", "on_target", "x", "y", "timestamp"]
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
                    response = self._response_q.get()
                    # If touchdown, log trial as precued
                    if response.event_type in TOUCHDOWN:
                        print("precued")
                        print(response)
                    # On touchup, register the trial and reset the ITI by breaking out of loop
                    if response.event_type in TOUCHUP:
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
                        if response.event_type in TOUCHDOWN:
                            print("hit")
                            print(response)
                        if response.event_type in TOUCHUP:
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
            if event.type in TOUCHDOWN or event.type in TOUCHUP:
                on_target = False
                for sprite in self.target.sprites():
                    if sprite.rect.collidepoint(event.pos):
                        on_target = True
                        break
                self._response_q.put(
                    TouchEvent(
                        event_type=event.type,
                        on_target=on_target,
                        x=event.pos[0],
                        y=event.pos[1],
                        timestamp=time.time(),
                    )
                )


def get_protocol(protocol_id):
    protocols = Task.get_children() + Presentation.get_children()
    for Protocol in protocols:
        if Protocol.get_identifier() == protocol_id:
            return Protocol


class InvalidProtocol(Exception):
    pass
