#  This file is part of visiomode.
#  Copyright (c) 2021 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

"""Module that defines the available task and stimulation protocols in a stimulus agnostic manner."""
import collections
import time
import datetime
import threading
import logging
import queue
import pygame as pg

import visiomode.config as conf
import visiomode.devices as devices
import visiomode.models as models
import visiomode.mixins as mixins


CORRECT = "correct"
INCORRECT = "incorrect"
NO_RESPONSE = "no_response"
PRECUED = "precued"

HIT = "hit"
MISS = "miss"
FALSE_ALARM = "false_alarm"
CORRECT_REJECTION = "correct_rejection"

TOUCHDOWN = pg.FINGERDOWN
TOUCHUP = pg.FINGERUP

TouchEvent = collections.namedtuple(
    "TouchEvent", ["event_type", "on_target", "x", "y", "timestamp"]
)


def get_task(task_id):
    return Task.get_child(task_id)


class Task(mixins.BaseClassMixin, mixins.WebFormMixin, mixins.TaskEventsMixin):
    def __init__(
        self,
        screen,
        iti,
        stimulus_duration,
        response_device,
        response_address,
        reward_address,
        reward_profile,
        **kwargs,
    ):
        self.screen = screen
        self.is_running = False
        self.start_time = None

        self.trials = []

        self.clock = pg.time.Clock()
        self.config = conf.Config()
        self._timedelta = 0

        self.iti = float(iti) / 1000  # ms to s
        self.stimulus_duration = float(stimulus_duration) / 1000  # ms to s

        self.corrections_enabled = False
        self.correction_trial = False

        self.target = None
        self.distractor = None
        self.separator = None

        self.response_device = devices.get_input_device(
            response_device, response_address
        )

        self.reward_device = devices.get_output_profile(reward_profile, reward_address)

        self._response_q = queue.Queue()

        self._session_thread = threading.Thread(
            target=self._session_runner, daemon=True
        )

    def start(self):
        """Start the task"""
        self.is_running = True
        self.start_time = time.time()
        self._session_thread.start()

    def stop(self):
        self.hide_stimulus()
        self.is_running = False

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
        response_time = None
        sdt_type = "NA"

        self.on_trial_start()

        while self.is_running and (time.time() - block_start < self.iti):
            if not self._response_q.empty():
                response_event = self._response_q.get()
                # If touchdown, log trial as precued
                if response_event:
                    outcome = PRECUED
                    response = response_event
                    response_time = time.time() - block_start
                    break
        else:
            # To prevent stimulus showing after the session has ended, check if the session is still running.
            if not self.is_running:
                return
            self.show_stimulus()
            self.on_stimulus_start()
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
                            logging.debug("Separator response, ignoring...")
                            continue

                        if (
                            self.target.collision(
                                response_event.pos_x, response_event.pos_y
                            )
                            and not self.target.hidden
                        ):
                            outcome = CORRECT
                            sdt_type = HIT
                            response = response_event
                            response_time = time.time() - stimulus_start
                        else:
                            outcome = INCORRECT
                            sdt_type = FALSE_ALARM
                            response = response_event
                            response_time = time.time() - stimulus_start
                        break
            else:
                # if the target was not visible, i.e. the stimulus was a distractor, and there was no touch event during
                # the response window then the trial outcome is a correct rejection
                if self.is_running and self.target.hidden:
                    outcome = CORRECT
                    sdt_type = CORRECT_REJECTION
                else:
                    outcome = NO_RESPONSE
                    sdt_type = MISS

        # If no explicit outcome, return without doing anything else. This prevents previous session events from leaking
        # through.
        if not outcome:
            return

        stimulus = "None"
        if outcome != PRECUED:
            if (
                self.distractor
                and not self.target.hidden
                and not self.distractor.hidden
            ):
                stimulus = {
                    "target": self.target.get_details(),
                    "distractor": self.distractor.get_details(),
                }
            elif self.distractor and self.target.hidden:
                stimulus = self.distractor.get_details()
            else:
                stimulus = self.target.get_details()

        self.on_trial_end()

        if not response_time:
            response_time = time.time() - stimulus_start
        trial = self.parse_trial(
            trial_start_iso, outcome, response, response_time, sdt_type, stimulus
        )
        logging.debug("Trial info - {}".format(trial.__dict__))
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

    def parse_trial(
        self,
        trial_start,
        outcome,
        response=None,
        response_time=0,
        sdt_type="NA",
        stimulus=None,
    ):
        if not response:
            response = {"name": "none"}
        trial = models.Trial(
            outcome=outcome,
            iti=self.iti,
            response=response,
            response_time=response_time,
            timestamp=trial_start,
            correction=self.correction_trial,
            stimulus=stimulus,
            sdt_type=sdt_type,
        )
        return trial

    def on_task_start(self):
        self.response_device.on_task_start()
        self.reward_device.on_task_start()

    def on_trial_start(self):
        self.response_device.on_trial_start()
        self.reward_device.on_trial_start()

    def on_stimulus_start(self):
        self.response_device.on_stimulus_start()
        self.reward_device.on_stimulus_start()

    def on_trial_end(self):
        self.response_device.on_trial_end()
        self.reward_device.on_trial_end()

    def on_task_end(self):
        self.response_device.on_task_end()
        self.reward_device.on_task_end()

    def on_correct(self):
        self.response_device.on_correct()
        self.reward_device.on_correct()

    def on_incorrect(self):
        self.response_device.on_incorrect()
        self.reward_device.on_incorrect()

    def on_no_response(self):
        self.response_device.on_no_response()
        self.reward_device.on_no_response()

    def on_precued(self):
        self.response_device.on_precued()
        self.reward_device.on_precued()

    def _session_runner(self):
        self.on_task_start()
        while self.is_running:
            self.trial_block()
        self.on_task_end()


class InvalidTask(Exception):
    pass
