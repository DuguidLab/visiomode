"""Module that defines the available task and stimulation protocols in a stimulus agnostic manner."""

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.
import re
import collections
import time
import datetime
import random
import threading
import queue
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


def get_protocol(protocol_id):
    protocols = Task.get_children() + Presentation.get_children()
    for Protocol in protocols:
        if Protocol.get_identifier() == protocol_id:
            return Protocol


class BaseProtocol(object):
    form_path = "protocols/protocol.html"

    def __init__(self, screen, duration: float):
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

    def update(self):
        pass

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
        return cls.form_path


class Task(BaseProtocol):
    def __init__(self, screen, duration, iti, stim_duration, **kwargs):
        super().__init__(screen, duration)

        self.iti = float(iti) / 1000  # ms to s
        self.stim_duration = float(stim_duration) / 1000  # ms to s

        self.trials = []

        self.corrections = False
        self._correction_trial = False

        self.target = None

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

    def handle_events(self, events):
        for event in events:
            if event.type in TOUCHDOWN or event.type in TOUCHUP:
                on_target = self.target.collision(event.pos)
                self._response_q.put(
                    TouchEvent(
                        event_type=event.type,
                        on_target=on_target,
                        x=event.pos[0],
                        y=event.pos[1],
                        timestamp=time.time(),
                    )
                )
        self.target.update()  # update stimulus drawing here since this is called on every iteration in the main loop

    def _session_runner(self):
        while self.is_running:
            self.hide_stim()
            iti_start = time.time()
            touchdown_response = None
            touchup_response = None
            trial_outcome = str()
            stim_time = iti_start  # default to start of ITI until stimulus shows up
            while (time.time() - iti_start < self.iti) or touchdown_response:
                if not self._response_q.empty():
                    response = self._response_q.get()
                    # If touchdown, log trial as precued
                    if response.event_type in TOUCHDOWN:
                        trial_outcome = PRECUED
                        touchdown_response = response
                    # On touchup, register the trial and reset the ITI by breaking out of loop
                    if response.event_type in TOUCHUP:
                        touchup_response = response
                        break
            else:
                # To prevent stimulus showing after the session has ended, check if the session is still running.
                if not self.is_running:
                    return
                self.show_stim()
                stim_start = time.time()
                while (
                    time.time() - stim_start < self.stim_duration
                ) or touchdown_response:
                    if not self._response_q.empty():
                        response = self._response_q.get()
                        if response.event_type in TOUCHDOWN:
                            trial_outcome = HIT if response.on_target else MISS
                            touchdown_response = response
                        if response.event_type in TOUCHUP:
                            touchup_response = response
                            break
            # Touchup events from the previous session can sometimes leak through (e.g. if touchup is after
            # session has ended). Prevent this crashing everything by checking for both touchup and touchdown
            # objects exist before creating a trial.
            if touchup_response and touchdown_response:
                trial = models.Trial(
                    outcome=trial_outcome,
                    iti=self.iti,
                    reaction_time=touchdown_response.timestamp - stim_time,
                    duration=touchup_response.timestamp - touchdown_response.timestamp,
                    pos_x=touchdown_response.x,
                    pos_y=touchdown_response.y,
                    dist_x=touchup_response.x - touchdown_response.x,
                    dist_y=touchup_response.y - touchdown_response.y,
                    timestamp=datetime.datetime.fromtimestamp(
                        touchdown_response.timestamp
                    ).isoformat(),
                    correction=self._correction_trial,
                )
                print(trial.__dict__)
                self.trials.append(trial)

                # Correction trials
                if self.corrections and trial.outcome == MISS:
                    self._correction_trial = True
                if self.corrections and self._correction_trial and trial.outcome == HIT:
                    self._correction_trial = False


class Presentation(BaseProtocol):
    pass


class SingleTarget(Task):
    form_path = "protocols/single_target.html"

    def __init__(self, target, **kwargs):
        super().__init__(**kwargs)

        self.background = pg.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((0, 0, 0))
        self.screen.blit(self.background, (0, 0))

        Target = stim.get_stimulus(target)
        self.target = Target(background=self.background, **kwargs)

    def stop(self):
        print("stop")
        super().stop()
        self.hide_stim()

    def show_stim(self):
        self.target.show()

    def hide_stim(self):
        self.target.hide()


class TwoAlternativeForcedChoice(Task):
    form_path = "protocols/tafc.html"

    def __init__(self, target, distractor, sep_size=50, corrections="false", **kwargs):
        super().__init__(**kwargs)

        self.background = pg.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((0, 0, 0))
        self.screen.blit(self.background, (0, 0))

        self.corrections = True if corrections == "true" else False

        self.separator_size = int(sep_size)  # pixels

        Target = stim.get_stimulus(target)
        target_params = {
            key.replace("t_", ""): kwargs[key]
            for key in kwargs.keys()
            if key.startswith("t_")
        }
        self.target = Target(background=self.background, **target_params)

        Distractor = stim.get_stimulus(distractor)
        distractor_params = {
            key.replace("d_", ""): kwargs[key]
            for key in kwargs.keys()
            if key.startswith("d_")
        }
        self.distractor = Distractor(background=self.background, **distractor_params)

    def stop(self):
        print("stop")
        super().stop()
        self.hide_stim()

    def show_stim(self):
        if not self._correction_trial:
            target_x, distr_x = self.shuffle_centerx()
            self.target.set_centerx(target_x)
            self.distractor.set_centerx(distr_x)

        self.target.show()
        self.distractor.show()

    def hide_stim(self):
        self.target.hide()
        self.distractor.hide()

    def handle_events(self, events):
        super().handle_events(events)
        self.distractor.update()

    def shuffle_centerx(self):
        centers = [
            0 - (self.separator_size / 2),
            self.screen.get_width() + (self.separator_size / 2),
        ]
        return random.sample(centers, 2)


class TwoIntervalForcedChoice(Task):
    pass


class InvalidProtocol(Exception):
    pass
