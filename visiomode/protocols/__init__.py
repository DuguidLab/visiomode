#  This file is part of visiomode.
#  Copyright (c) 2021 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

"""Module that defines the available task and stimulation protocols in a stimulus agnostic manner."""
import collections
import time
import datetime
import threading
import queue
import pygame as pg

import visiomode.config as conf
import visiomode.devices as devices
import visiomode.models as models
import visiomode.mixins as mixins
import visiomode.plugins as plugins


CORRECT = "correct"
INCORRECT = "incorrect"
NO_RESPONSE = "no_response"
PRECUED = "precued"

TOUCHDOWN = pg.FINGERDOWN
TOUCHUP = pg.FINGERUP

TouchEvent = collections.namedtuple(
    "TouchEvent", ["event_type", "on_target", "x", "y", "timestamp"]
)


def get_protocol(protocol_id):
    return Protocol.get_child(protocol_id)


class Protocol(mixins.BaseClassMixin, mixins.WebFormMixin):
    form_path = None

    def __init__(self, screen):
        self.screen = screen
        self.is_running = False
        self.start_time = None

        self.trials = []

        self.clock = pg.time.Clock()
        self.config = conf.Config()
        self._timedelta = 0

    def update(self, events):
        """Protocol event handling and graphics rendering"""

    def start(self):
        """Start the protocol"""
        self.is_running = True
        self.start_time = time.time()

    def stop(self):
        self.is_running = False


class Task(Protocol):
    def __init__(
        self, screen, iti, stim_duration, reward_address, reward_profile, **kwargs
    ):
        super().__init__(screen)

        self.iti = float(iti) / 1000  # ms to s
        self.stim_duration = float(stim_duration) / 1000  # ms to s

        self.corrections_enabled = False
        self.correction_trial = False

        self.target = None

        self.reward_profile = devices.get_output_profile(reward_profile)
        self.reward_device = self.reward_profile(reward_address)

        self._touchevent_q = queue.Queue()

        self._session_thread = threading.Thread(
            target=self._session_runner, daemon=True
        )

    def start(self):
        super(Task, self).start()
        self._session_thread.start()

    def stop(self):
        self.hide_stim()
        super(Task, self).stop()

    def show_stim(self):
        raise NotImplementedError

    def hide_stim(self):
        raise NotImplementedError

    def update_stim(self):
        raise NotImplementedError

    def update(self, events):
        for event in events:
            if event.type == TOUCHDOWN or event.type == TOUCHUP:
                x = event.x * self.config.width
                y = event.y * self.config.height
                on_target = self.target.collision(x, y) and not self.target.hidden
                self._touchevent_q.put(
                    TouchEvent(
                        event_type=event.type,
                        on_target=on_target,
                        x=x,
                        y=y,
                        timestamp=time.time(),
                    )
                )
        self.update_stim()

    def trial_block(self):
        """Trial block"""
        trial_start_iso = datetime.datetime.now().isoformat()
        self.hide_stim()
        block_start = time.time()
        touchdown_event = None
        touchup_event = None
        outcome = None

        while self.is_running and (
            (time.time() - block_start < self.iti) or touchdown_event
        ):
            if not self._touchevent_q.empty():
                touchevent = self._touchevent_q.get()
                # If touchdown, log trial as precued
                if touchevent.event_type == TOUCHDOWN:
                    outcome = PRECUED
                    touchdown_event = touchevent
                # On touchup, register the trial and reset the ITI by breaking out of loop
                if touchevent.event_type == TOUCHUP:
                    touchup_event = touchevent
                    break
        else:
            # To prevent stimulus showing after the session has ended, check if the session is still running.
            if not self.is_running:
                return
            self.show_stim()
            stim_start = time.time()
            while self.is_running and (
                (time.time() - stim_start < self.stim_duration) or touchdown_event
            ):
                if not self._touchevent_q.empty():
                    touchevent = self._touchevent_q.get()
                    if touchevent.event_type == TOUCHDOWN:
                        if touchevent.on_target and not self.target.hidden:
                            outcome = CORRECT
                        else:
                            outcome = INCORRECT
                        touchdown_event = touchevent
                    if touchevent.event_type == TOUCHUP:
                        touchup_event = touchevent
                        break
            else:
                # if the target was not visible, i.e. the stimulus was a distractor, and there was no touch event during
                # the response window then the trial outcome is a correct rejection
                if self.is_running and self.target.hidden:
                    outcome = CORRECT
                else:
                    outcome = NO_RESPONSE

        if outcome:
            # Touchup events from the previous session can sometimes leak through (e.g. if touchup is after
            # session has ended). Prevent this crashing everything by checking for both touchup and touchdown
            # objects exist before creating a trial.
            response = None
            if touchup_event and touchdown_event:
                response = self.parse_response(
                    block_start, touchdown_event, touchup_event
                )
            trial = self.parse_trial(trial_start_iso, outcome, response)
            print(trial.__dict__)
            self.trials.append(trial)

            # Hide stimulus at end of trial before calling handlers, so any reward dispensation associated
            # delays don't keep the stimulus hanging about on the screen.
            if self.is_running:
                self.hide_stim()

            # Call trial outcome handlers
            if outcome == PRECUED:
                self.on_precued()
            elif outcome == CORRECT:
                self.on_correct()
            elif outcome == INCORRECT:
                self.on_incorrect()
            elif outcome == NO_RESPONSE:
                self.on_no_response()

            # Correction trials
            if self.corrections_enabled and (
                outcome == NO_RESPONSE or outcome == INCORRECT
            ):
                self.correction_trial = True
            if (
                self.corrections_enabled
                and self.correction_trial
                and (outcome == CORRECT)
            ):
                self.correction_trial = False

    def parse_trial(self, trial_start, outcome, response=None):
        trial = models.Trial(
            outcome=outcome,
            iti=self.iti,
            response_time=response["response_time"] if response else -1,
            duration=response["duration"] if response else -1,
            pos_x=response["pos_x"] if response else -1,
            pos_y=response["pos_y"] if response else -1,
            dist_x=response["dist_x"] if response else -1,
            dist_y=response["dist_y"] if response else -1,
            timestamp=trial_start,
            correction=self.correction_trial,
        )
        return trial

    def parse_response(self, block_start, touchdown, touchup):
        return {
            "response_time": touchdown.timestamp - block_start - self.iti,
            "duration": touchup.timestamp - touchdown.timestamp,
            "pos_x": touchdown.x,
            "pos_y": touchdown.y,
            "dist_x": touchup.x - touchdown.x,
            "dist_y": touchup.y - touchdown.y,
            "timestamp": datetime.datetime.fromtimestamp(
                touchdown.timestamp
            ).isoformat(),
        }

    def on_correct(self):
        self.reward_device.output()

    def on_incorrect(self):
        pass

    def on_no_response(self):
        pass

    def on_precued(self):
        pass

    def _session_runner(self):
        while self.is_running:
            self.trial_block()


class Presentation(Protocol):
    pass


class InvalidProtocol(Exception):
    pass


plugins.load_modules_dir(__path__[0])
