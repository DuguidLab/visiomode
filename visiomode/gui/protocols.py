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
    def __init__(self, screen):
        self.screen = screen
        self.running = True

        self._timer_thread = threading.Thread(target=self._timer)
        self._timer_thread.run()

    def _timer(self, duration):
        start_time = time.time()
        while time.time() - start_time < duration:
            continue
        self.running = False


class Task(Protocol):
    def __init__(self, screen):
        super().__init__(screen)


class Presentation(Protocol):
    pass


class SingleTarget(Task):
    def __init__(self, screen):
        super().__init__(screen)
