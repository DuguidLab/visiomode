#  This file is part of visiomode.
#  Copyright (c) 2021 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import random

import pygame as pg

import visiomode.stimuli as stimulus
import visiomode.protocols as protocols


class GoNoGo(protocols.Task):
    form_path = "protocols/gonogo.html"

    def __init__(self, target, distractor, corrections_enabled="false", **kwargs):
        super(GoNoGo, self).__init__(**kwargs)

        self.background = pg.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((0, 0, 0))
        self.screen.blit(self.background, (0, 0))

        self.corrections_enabled = True if corrections_enabled == "true" else False

        target = stimulus.get_stimulus(target)
        target_params = {
            key.replace("t_", ""): kwargs[key]
            for key in kwargs.keys()
            if key.startswith("t_")
        }
        self.target = target(background=self.background, **target_params)

        distractor = stimulus.get_stimulus(distractor)
        distractor_params = {
            key.replace("d_", ""): kwargs[key]
            for key in kwargs.keys()
            if key.startswith("d_")
        }
        self.distractor = distractor(background=self.background, **distractor_params)

        self.current_stimulus = self.get_random_stimulus()

    def show_stimulus(self):
        if not self.correction_trial:
            self.current_stimulus = self.get_random_stimulus()
        self.current_stimulus.show()

    def hide_stimulus(self):
        self.current_stimulus.hide()

    def update_stimulus(self):
        self.current_stimulus.update()

    def get_random_stimulus(self):
        return random.choice([self.target, self.distractor])

    @classmethod
    def get_common_name(cls):
        return "Go / NoGo"
