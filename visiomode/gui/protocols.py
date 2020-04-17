"""Module that defines the available task and stimulation protocols in a stimulus agnostic manner."""

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.
import time
import threading
import pygame as pg


def get_protocol(protocol_id, *args, **kwargs):
    return


class Protocol(object):
    def __init__(self, screen, duration):
        self.screen = screen
        self.is_running = False

        self._timer_thread = threading.Thread(
            target=self._timer, args=[duration], daemon=True
        )

    def start(self):
        """Start the protocol"""
        self.is_running = True
        self._timer_thread.run()

    def stop(self):
        self.is_running = False

    def _timer(self, duration):
        start_time = time.time()
        while time.time() - start_time < duration:
            # If the session has been stopped externally, stop timer
            if not self.is_running:
                return
        self.is_running = False


class Task(Protocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Presentation(Protocol):
    pass


class SingleTarget(Task):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
