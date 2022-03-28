#  This file is part of visiomode.
#  Copyright (c) 2021 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import numpy as np
import pygame as pg

import visiomode.stimuli as stimuli


class Grating(stimuli.Stimulus):
    form_path = "stimuli/grating.html"

    def __init__(self, background, period=30, contrast=1.0, **kwargs):
        super().__init__(background, **kwargs)
        self.period = int(period)

        grating = Grating.sinusoid(self.width, self.height, self.period, contrast)
        self.image = pg.surfarray.make_surface(grating)
        self.rect = self.image.get_rect()
        self.area = self.screen.get_rect()

    @classmethod
    def sinusoid(cls, width: int, height: int, period: int, contrast: float = 1.0):
        sinusoid = Grating._sinusoid(width, height, period)
        return stimuli.grayscale_array(sinusoid, contrast)

    @classmethod
    def _sinusoid(cls, width: int, height: int, period: int):
        """Generate a sinusoid array in numpy.

        Args:
            width:
            height:
            period:

        Returns:

        """
        # generate 1-D sine wave of required period
        x = np.arange(height)
        y = np.sin(2 * np.pi * x / period)

        # offset sine wave by the max value to go out of negative range of sine
        y += max(y)

        # create 2-D array of sine-wave
        sinusoid = np.array([[y[j] for j in range(height)] for i in range(width)])

        return sinusoid
