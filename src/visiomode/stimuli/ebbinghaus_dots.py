#  This file is part of visiomode.
#  Copyright (c) 2025 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import random
from math import cos, pi, sin

import pygame as pg

from visiomode import stimuli


class EbbinghausDot(stimuli.Stimulus):
    form_path = ""

    def __init__(self, background, **kwargs):
        super().__init__(background, **kwargs)

        self.image = pg.Surface((self.width, self.height))
        self.rect = self.image.get_rect()

    def generate_new_trial(self):
        CENTER_SIZES = (10, 20, 30)
        RATIOS = (0.25, 0.5, 1, 2, 2.5)

        center_size = random.sample(CENTER_SIZES, 1)[0]
        context_ratio = random.sample(RATIOS, 1)[0]

        # draw centre circle
        self.centre_circle = pg.draw.circle(
            self.image,
            (127, 127, 127),
            (self.rect.centerx, self.rect.centery),
            center_size,
        )

        # draw surrounding circles
        n_surround = 6
        distance_from_center = (center_size * 2) + (center_size * context_ratio)
        for circle_idx in range(n_surround):
            angle = (2 * pi * circle_idx) / n_surround
            x1 = self.centre_circle.centerx + int(distance_from_center * cos(angle))
            y1 = self.centre_circle.centery + int(distance_from_center * sin(angle))
            pg.draw.circle(self.image, (127, 127, 127), (x1, y1), center_size * context_ratio)

        super().generate_new_trial()

    def hide(self):
        self.image = pg.Surface((self.width, self.height))
        self.rect = self.image.get_rect()
        super().hide()
