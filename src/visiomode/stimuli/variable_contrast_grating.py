#  This file is part of visiomode.
#  Copyright (c) 2022 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import random
import pygame as pg

import visiomode.stimuli as stimuli
import visiomode.stimuli.grating as grating


class VariableContrastGrating(grating.Grating):
    form_path = ""

    def __init__(self, background, contrasts=(0, 0.06, 0.12, 0.25, 0.5, 1.0), **kwargs):
        super().__init__(background, **kwargs)

        self.contrasts = contrasts
        self.sinusoid_array = grating.Grating._sinusoid(
            self.width, self.height, self.period
        )

        self.generate_new_trial()

    def generate_new_trial(self):
        self.trial_contrast = random.choice(self.contrasts)

        _grating = stimuli.grayscale_array(self.sinusoid_array, self.trial_contrast)
        self.image = pg.surfarray.make_surface(_grating)
        self.rect = self.image.get_rect()
        self.area = self.screen.get_rect()

    def get_details(self):
        return {
            "id": self.get_identifier(),
            "common_name": self.get_common_name(),
            "trial_contrast": self.trial_contrast,
        }
