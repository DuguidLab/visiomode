"""Module that defines the available task and stimulation protocols in a stimulus agnostic manner."""

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.
import time
import threading
import pygame as pg
import visiomode.gui.stimuli as stim


def get_protocol(protocol_id, screen, request):
    return SingleTarget(screen, request)


class Protocol(object):
    def __init__(self, screen, request):
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
            # If the session has been stopped externally, stop timer
            if not self.is_running:
                return
        self.stop()


class Task(Protocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Presentation(Protocol):
    pass


class SingleTarget(Task):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.background = pg.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((0, 0, 0))
        self.target = pg.sprite.RenderClear(stim.Grating(0, 0))

    def start(self):
        self.target.draw(self.screen)
        super().start()

    def stop(self):
        print("stop")
        self.target.clear(self.screen, self.background)
        super().stop()
        print(self.is_running)

    def handle_events(self, events):
        for event in events:
            if event.type == pg.MOUSEBUTTONUP:
                for sprite in self.target.sprites():
                    if sprite.rect.collidepoint(event.pos):
                        print("hit!")
                        self.target.clear(self.screen, self.background)
