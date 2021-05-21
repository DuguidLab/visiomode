#  This file is part of visiomode.
#  Copyright (c) 2021 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import random

import pygame as pg

import stimuli as stim
import visiomode.protocols as protocols


class TwoAlternativeForcedChoice(protocols.Task):
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
            if event.type == protocols.TOUCHDOWN or event.type == protocols.TOUCHUP:
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
