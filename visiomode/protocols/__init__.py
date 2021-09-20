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

    def update(self):
        """Protocol event handling and graphics rendering"""

    def start(self):
        """Start the protocol"""
        self.is_running = True
        self.start_time = time.time()

    def stop(self):
        self.is_running = False


class Task(Protocol):
    def __init__(
        self,
        screen,
        iti,
        stimulus_duration,
        response_device,
        reward_address,
        reward_profile,
        **kwargs
    ):
        super().__init__(screen)

        self.iti = float(iti) / 1000  # ms to s
        self.stimulus_duration = float(stimulus_duration) / 1000  # ms to s

        self.corrections_enabled = False
        self.correction_trial = False

        self.target = None
        self.distractor = None
        self.separator = None

        self.response_device = devices.get_input_profile(response_device)

        # TODO - autodetect address (issue 140)
        self.reward_profile = devices.get_output_profile(reward_profile)
        self.reward_device = self.reward_profile(reward_address)

        self._response_q = queue.Queue()

        self._session_thread = threading.Thread(
            target=self._session_runner, daemon=True
        )

    def start(self):
        super(Task, self).start()
        self._session_thread.start()

    def stop(self):
        self.hide_stimulus()
        super(Task, self).stop()

    def show_stimulus(self):
        raise NotImplementedError

    def hide_stimulus(self):
        raise NotImplementedError

    def update_stimulus(self):
        raise NotImplementedError

    def update(self):
        # check input device for response
        response_event = self.response_device.get_response()
        if response_event:
            self._response_q.put(response_event)
        self.update_stimulus()

    def trial_block(self):
        """Trial block"""
        trial_start_iso = datetime.datetime.now().isoformat()
        self.hide_stimulus()
        block_start = time.time()
        outcome = None
        response = None
        response_time = -1

        while self.is_running and (time.time() - block_start < self.iti):
            if not self._response_q.empty():
                response_event = self._response_q.get()
                # If touchdown, log trial as precued
                if response_event:
                    outcome = PRECUED
                    response = response_event
                    response_time = time.time()
                    break
        else:
            # To prevent stimulus showing after the session has ended, check if the session is still running.
            if not self.is_running:
                return
            self.show_stimulus()
            stimulus_start = time.time()
            while self.is_running and (
                time.time() - stimulus_start < self.stimulus_duration
            ):
                if not self._response_q.empty():
                    response_event = self._response_q.get()
                    if response_event:
                        # If the response is on the separator (and one exists), ignore it.
                        if self.separator and self.separator.collidepoint(
                            response_event.pos_x, response_event.pos_y
                        ):
                            print("blipblop")
                            continue

                        if (
                            self.target.collision(
                                response_event.pos_x, response_event.pos_y
                            )
                            and not self.target.hidden
                        ):
                            outcome = CORRECT
                            response = response_event
                            response_time = time.time()
                        else:
                            outcome = INCORRECT
                            response = response_event
                            response_time = time.time()
                        break
            else:
                # if the target was not visible, i.e. the stimulus was a distractor, and there was no touch event during
                # the response window then the trial outcome is a correct rejection
                if self.is_running and self.target.hidden:
                    outcome = CORRECT
                else:
                    outcome = NO_RESPONSE

        # If no explicit outcome, return without doing anything else. This prevents previous session events from leaking
        # through.
        if not outcome:
            return

        trial = self.parse_trial(trial_start_iso, outcome, response, response_time)
        print(trial.__dict__)
        self.trials.append(trial)

        # Hide stimulus at end of trial before calling handlers, so any reward dispensation associated
        # delays don't keep the stimulus hanging about on the screen.
        if self.is_running:
            self.hide_stimulus()

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
        if self.corrections_enabled and self.correction_trial and (outcome == CORRECT):
            self.correction_trial = False

    def parse_trial(self, trial_start, outcome, response=None, response_time=-1):
        trial = models.Trial(
            outcome=outcome,
            iti=self.iti,
            response=response,
            response_time=response_time,
            timestamp=trial_start,
            correction=self.correction_trial,
        )
        return trial

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
