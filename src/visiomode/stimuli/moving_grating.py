#  This file is part of visiomode.
#  Copyright (c) 2021 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import pygame as pg
from pygame import math as pgm

import visiomode.stimuli as stimuli
from visiomode.stimuli.grating import Grating


class MovingGrating(stimuli.Stimulus):
    form_path = "stimuli/moving_grating.html"

    def __init__(self, background, period=20, freq=1.0, contrast=1.0, **kwargs):
        # Default direction is upwards, use negative frequency for downwards
        super().__init__(background, **kwargs)

        self.period = int(period)
        self.frequency = float(freq)
        # Determine sign of direction based on frequency (negative => downwards, positive => upwards)
        self.direction = (lambda x: (-1, 1)[x < 0])(self.frequency)
        self.px_per_cycle = (
            self.direction * (self.period * abs(self.frequency)) / stimuli.config.fps
        )

        grating = Grating.sinusoid(
            self.width, self.height + (self.period * 2), self.period, contrast
        )
        self.image = pg.surfarray.make_surface(grating).convert(self.screen)
        self.rect = self.image.get_rect()
        self.area = self.screen.get_rect()

        self.orig_center = (self.rect.centerx, self.rect.centery)

        self.pos = pgm.Vector2(self.orig_center)
        self.velocity = pgm.Vector2(0, self.px_per_cycle)

    def update(self, timedelta=0):
        if self.hidden:
            return
        if self.rect.bottom <= self.height:
            self.pos = self.orig_center
        self.pos += self.velocity
        self.rect.centery = self.pos[1]
        # self.rect.move_ip(0, self.px_per_cycle)

        self.draw()
