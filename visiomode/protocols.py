"""Module that defines the available task and stimulation protocols in a stimulus agnostic manner."""

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.
import collections
import time
import datetime
import random
import threading
import queue
import pygame as pg
import visiomode.config as conf
import visiomode.stimuli as stim
import visiomode.devices as devices
import visiomode.models as models
import visiomode.mixins as mixins


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
        self,
        screen,
        duration,
        iti,
        stim_duration,
        reward_address,
        reward_profile,
        **kwargs
    ):
        super().__init__(screen)

        self.iti = float(iti) / 1000  # ms to s
        self.stim_duration = float(stim_duration) / 1000  # ms to s

        self.corrections_enabled = False
        self.correction_trial = False

        self.target = None

        self.reward_device = devices.WaterReward(reward_address)

        self._response_q = queue.Queue()

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
                self._response_q.put(
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
        """Trial block supporting signal detection theory styled trials."""
        trial_start_iso = datetime.datetime.now().isoformat()
        self.hide_stim()
        block_start = time.time()
        touchdown_response = None
        touchup_response = None
        trial_outcome = NO_RESPONSE

        while self.is_running and (
            (time.time() - block_start < self.iti) or touchdown_response
        ):
            if not self._response_q.empty():
                response = self._response_q.get()
                # If touchdown, log trial as precued
                if response.event_type == TOUCHDOWN:
                    trial_outcome = PRECUED
                    touchdown_response = response
                # On touchup, register the trial and reset the ITI by breaking out of loop
                if response.event_type == TOUCHUP:
                    touchup_response = response
                    break
        else:
            # To prevent stimulus showing after the session has ended, check if the session is still running.
            if not self.is_running:
                return
            self.show_stim()
            stim_start = time.time()
            while self.is_running and (
                (time.time() - stim_start < self.stim_duration) or touchdown_response
            ):
                if not self._response_q.empty():
                    response = self._response_q.get()
                    if response.event_type == TOUCHDOWN:
                        if response.on_target:
                            trial_outcome = CORRECT
                        else:
                            trial_outcome = INCORRECT
                        touchdown_response = response
                    if response.event_type == TOUCHUP:
                        touchup_response = response
                        break
            else:
                # if the target was not visible, i.e. the stimulus was a distractor, and there was no touch event during
                # the response window then the trial outcome is a correct rejection
                if self.is_running and self.target.hidden:
                    trial_outcome = CORRECT

        # Log trial
        trial = models.Trial(
            outcome=trial_outcome,
            iti=self.iti,
            response_time=-1,
            duration=-1,
            pos_x=-1,
            pos_y=-1,
            dist_x=-1,
            dist_y=-1,
            timestamp=trial_start_iso,
            correction=self.correction_trial,
        )
        # Touchup events from the previous session can sometimes leak through (e.g. if touchup is after
        # session has ended). Prevent this crashing everything by checking for both touchup and touchdown
        # objects exist before creating a trial.
        if touchup_response and touchdown_response:
            trial.response_time = touchdown_response.timestamp - block_start - self.iti
            trial.duration = touchup_response.timestamp - touchdown_response.timestamp
            trial.pos_x = touchdown_response.x
            trial.pos_y = touchdown_response.y
            trial.dist_x = touchup_response.x - touchdown_response.x
            trial.dist_y = touchup_response.y - touchdown_response.y
            trial.timestamp = datetime.datetime.fromtimestamp(
                touchdown_response.timestamp
            ).isoformat()

        print(trial.__dict__)
        self.trials.append(trial)

        # Hide stimulus at end of trial before calling handlers, so any reward dispensation associated
        # delays don't keep the stimulus hanging about on the screen.
        if self.is_running:
            self.hide_stim()

        # Call trial outcome handlers
        if trial.outcome == PRECUED:
            self.on_precued()
        elif trial.outcome == CORRECT:
            self.on_correct()
        elif trial.outcome == INCORRECT:
            self.on_incorrect()
        elif trial.outcome == NO_RESPONSE:
            self.on_no_response()

        # Correction trials
        if self.corrections_enabled and (
            trial.outcome == NO_RESPONSE or trial.outcome == INCORRECT
        ):
            self.correction_trial = True
        if (
            self.corrections_enabled
            and self.correction_trial
            and (trial.outcome == CORRECT)
        ):
            self.correction_trial = False

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


class SingleTarget(Task):
    form_path = "protocols/single_target.html"

    def __init__(self, target, **kwargs):
        super(SingleTarget, self).__init__(**kwargs)

        self.background = pg.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((0, 0, 0))
        self.screen.blit(self.background, (0, 0))

        target = stim.get_stimulus(target)
        self.target = target(background=self.background, **kwargs)

    def update_stim(self):
        self.target.update()

    def show_stim(self):
        self.target.show()

    def hide_stim(self):
        self.target.hide()


class TwoAlternativeForcedChoice(Task):
    form_path = "protocols/tafc.html"

    def __init__(
        self, target, distractor, sep_size=50, corrections_enabled="false", **kwargs
    ):
        super(TwoAlternativeForcedChoice, self).__init__(**kwargs)

        self.background = pg.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((0, 0, 0))
        self.screen.blit(self.background, (0, 0))

        self.corrections_enabled = True if corrections_enabled == "true" else False

        self.separator_size = int(sep_size)  # pixels
        self.separator = pg.Rect(
            ((0, 0), (self.separator_size, self.screen.get_height()))
        )
        self.separator.centerx = self.screen.get_rect().centerx

        target = stim.get_stimulus(target)
        target_params = {
            key.replace("t_", ""): kwargs[key]
            for key in kwargs.keys()
            if key.startswith("t_")
        }
        self.target = target(background=self.background, **target_params)

        distractor = stim.get_stimulus(distractor)
        distractor_params = {
            key.replace("d_", ""): kwargs[key]
            for key in kwargs.keys()
            if key.startswith("d_")
        }
        self.distractor = distractor(background=self.background, **distractor_params)

    def show_stim(self):
        if not self.correction_trial:
            target_x, distr_x = self.shuffle_centerx()
            self.target.set_centerx(target_x)
            self.distractor.set_centerx(distr_x)

        self.target.show()
        self.distractor.show()

    def hide_stim(self):
        self.target.hide()
        self.distractor.hide()

    def update(self, events):
        # ignore events on the background sprite if target and distractor are visible
        for event in events:
            if event.type == TOUCHDOWN or event.type == TOUCHUP:
                if not self.target.hidden:  # if target is visible, so is the distractor
                    x = event.x * self.config.width
                    y = event.y * self.config.height
                    if self.separator.collidepoint(x, y):
                        return
        super(TwoAlternativeForcedChoice, self).update(events)

    def update_stim(self):
        self.distractor.update()
        self.target.update()

    def shuffle_centerx(self):
        centers = [
            0 - (self.separator_size / 2),
            self.screen.get_width() + (self.separator_size / 2),
        ]
        return random.sample(centers, 2)


class GoNoGo(Task):
    form_path = "protocols/tifc.html"

    def __init__(self, target, distractor, corrections_enabled="false", **kwargs):
        super(GoNoGo, self).__init__(**kwargs)

        self.background = pg.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((0, 0, 0))
        self.screen.blit(self.background, (0, 0))

        self.corrections_enabled = True if corrections_enabled == "true" else False

        target = stim.get_stimulus(target)
        target_params = {
            key.replace("t_", ""): kwargs[key]
            for key in kwargs.keys()
            if key.startswith("t_")
        }
        self.target = target(background=self.background, **target_params)

        distractor = stim.get_stimulus(distractor)
        distractor_params = {
            key.replace("d_", ""): kwargs[key]
            for key in kwargs.keys()
            if key.startswith("d_")
        }
        self.distractor = distractor(background=self.background, **distractor_params)

        self.current_stimulus = self.get_random_stimulus()

    def show_stim(self):
        if not self.correction_trial:
            self.current_stimulus = self.get_random_stimulus()
        self.current_stimulus.show()

    def hide_stim(self):
        self.current_stimulus.hide()

    def update_stim(self):
        self.current_stimulus.update()

    def get_random_stimulus(self):
        return random.choice([self.target, self.distractor])

    @classmethod
    def get_common_name(cls):
        return "Go / NoGo"


class InvalidProtocol(Exception):
    pass
