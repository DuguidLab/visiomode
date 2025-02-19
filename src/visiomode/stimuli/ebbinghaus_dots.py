#  This file is part of visiomode.
#  Copyright (c) 2025 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import random
from math import cos, pi, sin

import pygame as pg

from visiomode import stimuli


class EbbinghausDot(stimuli.Stimulus):
    form_path = "stimuli/ebbinghaus_dot.html"

    def __init__(
        self,
        background,
        context_enabled=True,
        n_context=6,
        center_sizes=(10, 20, 30),
        ratios=(0.25, 0.5, 1, 2),
        center_colour=(127, 127, 127),
        context_colour=(127, 127, 127),
        **kwargs,
    ):
        super().__init__(background, **kwargs)

        self.center_sizes = center_sizes
        self.ratios = ratios
        self.context_enabled = context_enabled
        self.n_context = n_context
        self.center_colour = center_colour
        self.context_colour = context_colour

        self.image = pg.Surface((self.width, self.height))
        self.rect = self.image.get_rect()

    def generate_new_trial(self):
        center_size = random.sample(self.center_sizes, 1)[0]
        context_ratio = random.sample(self.ratios, 1)[0]

        # draw centre circle
        self.centre_circle = pg.draw.circle(
            self.image,
            self.center_colour,
            (self.rect.centerx, self.rect.centery),
            center_size,
        )

        # draw surrounding circles
        distance_from_center = (center_size * 2) + (center_size * context_ratio)
        for circle_idx in range(self.n_context):
            angle = (2 * pi * circle_idx) / self.n_context
            x1 = self.centre_circle.centerx + int(distance_from_center * cos(angle))
            y1 = self.centre_circle.centery + int(distance_from_center * sin(angle))
            pg.draw.circle(self.image, self.context_colour, (x1, y1), center_size * context_ratio)

        super().generate_new_trial()

    def hide(self):
        self.image = pg.Surface((self.width, self.height))
        self.rect = self.image.get_rect()
        super().hide()
