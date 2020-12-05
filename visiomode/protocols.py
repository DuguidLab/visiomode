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

HIT = "hit"
MISS = "miss"
FALSE_ALARM = "false_alarm"
CORRECT_REJECTION = "correct_rejection"
PRECUED = "precued"

TOUCHDOWN = (pg.MOUSEBUTTONDOWN,)
TOUCHUP = (pg.MOUSEBUTTONUP,)

TouchEvent = collections.namedtuple(
    "TouchEvent", ["event_type", "on_target", "x", "y", "timestamp"]
)


def get_protocol(protocol_id):
    return Protocol.get_child(protocol_id)


class Protocol(mixins.BaseClassMixin, mixins.WebFormMixin):
    form_path = None

    def __init__(self, screen, duration: float):
        self.screen = screen
        self.is_running = False

        self._timer_thread = threading.Thread(
            target=self._timer, args=[duration], daemon=True
        )
        self.clock = pg.time.Clock()
        self.config = conf.Config()
        self._timedelta = 0

    def update(self, events):
        """Protocol event handling and graphics rendering"""

    def start(self):
        """Start the protocol"""
        self.is_running = True
        self._timer_thread.start()

    def stop(self):
        self.is_running = False

    def _timer(self, duration: float):
        start_time = time.time()
        while time.time() - start_time < duration * 60:
            # If the session has been stopped, stop timer
            if not self.is_running:
                return
        self.stop()


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
        super().__init__(screen, duration)

        self.iti = float(iti) / 1000  # ms to s
        self.stim_duration = float(stim_duration) / 1000  # ms to s

        self.trials = []

        self.corrections_enabled = False
        self._correction_trial = False

        self.target = None

        self.reward_device = devices.WaterReward(reward_address)

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

    def update(self, events):
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
        self.target.update(timedelta=self._timedelta)

    def trial_block(self):
        self.hide_stim()
        iti_start = time.time()
        touchdown_response = None
        touchup_response = None
        trial_outcome = MISS
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
            while (time.time() - stim_start < self.stim_duration) or touchdown_response:
                if not self._response_q.empty():
                    response = self._response_q.get()
                    if response.event_type in TOUCHDOWN:
                        if response.on_target:
                            trial_outcome = HIT
                            self.reward_device.output()
                        else:
                            trial_outcome = FALSE_ALARM
                        touchdown_response = response
                    if response.event_type in TOUCHUP:
                        touchup_response = response
                        break
            else:
                # if the target was not visible, i.e. the stimulus was a distractor, and there was no touch event during
                # the response window then the trial outcome is a correct rejection
                if self.target.hidden:
                    trial_outcome = CORRECT_REJECTION

        trial = models.Trial(
            outcome=trial_outcome,
            iti=self.iti,
            reaction_time=-1,
            duration=-1,
            pos_x=-1,
            pos_y=-1,
            dist_x=-1,
            dist_y=-1,
            timestamp=datetime.datetime.now().isoformat(),
            correction=self._correction_trial,
        )
        # Touchup events from the previous session can sometimes leak through (e.g. if touchup is after
        # session has ended). Prevent this crashing everything by checking for both touchup and touchdown
        # objects exist before creating a trial.
        if touchup_response and touchdown_response:
            trial.response_time = touchdown_response.timestamp - stim_time - self.iti
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

        # Correction trials
        if self.corrections_enabled and (
            trial.outcome == MISS or trial.outcome == FALSE_ALARM
        ):
            self._correction_trial = True
        if self.corrections_enabled and self._correction_trial and trial.outcome == HIT:
            self._correction_trial = False

    def _session_runner(self):
        while self.is_running:
            self.trial_block()


class Presentation(Protocol):
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
        self.separator = pg.Rect(
            ((0, 0), (self.separator_size, self.screen.get_height()))
        )
        self.separator.centerx = self.screen.get_rect().centerx

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

    def update(self, events):
        # ignore events on the background sprite if target and distractor are visible
        for event in events:
            if event.type in TOUCHDOWN or event.type in TOUCHUP:
                if not self.target.hidden:  # if target is visible, so is the distractor
                    if self.separator.collidepoint(*event.pos):
                        return
        super().update(events)
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
