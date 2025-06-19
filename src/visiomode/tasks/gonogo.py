#  This file is part of visiomode.
#  Copyright (c) 2021 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import random

import pygame as pg

import visiomode.stimuli as stimulus
from visiomode import tasks


class GoNoGo(tasks.Task):
    form_path = "tasks/gonogo.html"

    def __init__(self, target, distractor, corrections_enabled="false", **kwargs):
        super().__init__(**kwargs)

        self.background = pg.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((0, 0, 0))
        self.screen.blit(self.background, (0, 0))

        self.corrections_enabled = True if corrections_enabled == "true" else False

        self._trial_count = 0

        target = stimulus.get_stimulus(target)
        target_params = {key.replace("t_", ""): kwargs[key] for key in kwargs.keys() if key.startswith("t_")}
        self.target = target(background=self.background, **target_params)

        distractor = stimulus.get_stimulus(distractor)
        distractor_params = {key.replace("d_", ""): kwargs[key] for key in kwargs.keys() if key.startswith("d_")}
        self.distractor = distractor(background=self.background, **distractor_params)

        self.current_stimulus = self.target

    def show_stimulus(self):
        if self._trial_count == 0:
            self.current_stimulus = self.target
        if not self.correction_trial:
            self.current_stimulus = self.get_random_stimulus()
            self.current_stimulus.generate_new_trial()
        self.current_stimulus.show()
        self._trial_count += 1

    def hide_stimulus(self):
        self.current_stimulus.hide()

    def update_stimulus(self):
        self.current_stimulus.update()

    def get_random_stimulus(self):
        return random.choice([self.target, self.distractor])  # noqa: S311

    def get_spec(self):
        """Return task specification as a dictionary."""
        return {
            "iti": self.iti,
            "stimulus_duration": self.stimulus_duration,
            "response_profile": self.response_profile,
            "response_address": self.response_address,
            "corrections_enabled": self.corrections_enabled,
            "target_stimulus": self.target.get_identifier(),
            "distractor_stimulus": self.distractor.get_identifier(),
        }

    @classmethod
    def get_common_name(cls):
        return "Go / NoGo"
