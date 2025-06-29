#  This file is part of visiomode.
#  Copyright (c) 2022 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import random

import pygame as pg

from visiomode import stimuli
from visiomode.stimuli import grating, moving_grating


class VariableContrastMovingGrating(moving_grating.MovingGrating):
    form_path = ""

    def __init__(self, background, contrasts=(0, 0.06, 0.12, 0.25, 0.5, 1.0), **kwargs):
        super().__init__(background, **kwargs)

        self.contrasts = contrasts
        self.sinusoid_array = grating.Grating._sinusoid(self.width, self.height, self.period)

        self.generate_new_trial()

    def generate_new_trial(self):
        self.trial_contrast = random.choice(self.contrasts)  # noqa: S311

        _grating = stimuli.grayscale_array(self.sinusoid_array, self.trial_contrast)
        self.image = pg.surfarray.make_surface(_grating)
        self.rect = self.image.get_rect()
        self.area = self.screen.get_rect()

    def get_details(self):
        """Returns a dictionary of stimulus attributes."""
        return {
            "id": self.get_identifier(),
            "common_name": self.get_common_name(),
            "width": self.width,
            "height": self.height,
            "center_x": self.rect.centerx,
            "center_y": self.rect.centery,
            "trial_contrast": self.trial_contrast,
            "period": self.period,
            "frequency": self.frequency,
            "drift_direction": "upwards" if self.direction > 0 else "downwards",
            "velocity_px": self.px_per_cycle,
        }
