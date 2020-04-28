"""Module that defines the available task and stimulation protocols in a stimulus agnostic manner."""

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.
import time
import threading
import queue
import pygame as pg
import stimuli as stim

HIT = "hit"
MISS = "miss"
PRECUED = "precued"


def get_protocol(protocol_id, screen, request):
    return SingleTarget(screen, request)


class Protocol(object):
    REQUIRED_ATTRS = (
        "animal_id",
        "experiment",
        "protocol",
        "duration",
    )

    def __init__(self, screen, request):
        for key in self.REQUIRED_ATTRS:
            if key not in request.keys():
                raise InvalidProtocol("Missing required key - {}".format(key))
        self.screen = screen
        self.is_running = False

        self._timer_thread = threading.Thread(
            target=self._timer, args=[float(request["duration"])], daemon=True
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


class Task(Protocol):
    # REQUIRED_ATTRS = Protocol.REQUIRED_ATTRS + ("iti",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.iti = 3  # TODO embed in request
        self.stim_duration = 2  # TODO embed in request

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
                    self._response_q.get()
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


class Presentation(Protocol):
    pass


class SingleTarget(Task):
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
            if event.type == pg.MOUSEBUTTONUP:
                for sprite in self.target.sprites():
                    if sprite.rect.collidepoint(event.pos):
                        self._response_q.put(("hit", event))
                        break
                else:
                    self._response_q.put(("precued", event))


class InvalidProtocol(Exception):
    pass
