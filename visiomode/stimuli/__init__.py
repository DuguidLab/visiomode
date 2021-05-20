#  This file is part of visiomode.
#  Copyright (c) 2021 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

"""Visual stimulus classes implemented """
import os
import numpy as np
import pygame as pg
import pygame.math as pgm
import visiomode.config as conf
import visiomode.mixins as mixins

config = conf.Config()


def get_stimulus(stimulus_id):
    return Stimulus.get_child(stimulus_id)


def load_image(name):
    """ Load image and return image object"""
    fullname = os.path.join("visiomode/gui/res", name)
    try:
        image = pg.image.load(fullname)
        if image.get_alpha is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
    except pg.error as message:
        print("Cannot load image:", fullname)
        raise SystemExit(message)
    return image, image.get_rect()


def normalise_array(array, contrast=1.0):
    """Cast array to a UINT8 image matrix."""
    image = (
        ((array - np.min(array)) / (np.max(array) - np.min(array)))
        * 255
        * float(contrast)
    )
    return image.astype(np.uint8)


def grayscale_array(array, contrast=1.0):
    """Convert a 2D array to 3D array of grayscale values."""
    return np.stack((normalise_array(array, contrast),) * 3, axis=-1)


class Stimulus(pg.sprite.Sprite, mixins.BaseClassMixin, mixins.WebFormMixin):
    form_path = "stimuli/stimulus.html"

    def __init__(self, background, **kwargs):
        super().__init__()
        self.screen = pg.display.get_surface()
        self.background = background

        self.height = self.screen.get_height()
        self.width = self.screen.get_width()

        self.hidden = False

    def show(self):
        self.hidden = False
        self.screen.blit(self.image, self.rect)

    def draw(self):
        self.screen.blit(self.image, self.rect)

    def hide(self):
        self.hidden = True
        # self.clear(self.screen, self.background)
        self.screen.blit(self.background, (0, 0))

    def update(self, timedelta=0):
        pass

    def collision(self, x, y):
        if self.rect.collidepoint(x, y):
            return True
        return False

    def set_centerx(self, centerx):
        self.rect.centerx = centerx


class Grating(Stimulus):
    form_path = "stimuli/grating.html"

    def __init__(self, background, period=20, contrast=1.0, **kwargs):
        super().__init__(background, **kwargs)
        self.period = int(period)

        grating = Grating.sinusoid(self.width, self.height, self.period, contrast)
        self.image = pg.surfarray.make_surface(grating)
        self.rect = self.image.get_rect()
        self.area = self.screen.get_rect()

    @classmethod
    def sinusoid(cls, width: int, height: int, period: int, contrast: float = 1.0):
        # generate 1-D sine wave of required period
        x = np.arange(height)
        y = np.sin(2 * np.pi * x / period)

        # offset sine wave by the max value to go out of negative range of sine
        y += max(y)

        # create 2-D array of sine-wave
        sinusoid = np.array([[y[j] for j in range(height)] for i in range(width)])
        return grayscale_array(sinusoid, contrast)


class MovingGrating(Stimulus):
    form_path = "stimuli/moving_grating.html"

    def __init__(self, background, period=20, freq=1.0, contrast=1.0, **kwargs):
        # Default direction is upwards, use negative frequency for downwards
        super().__init__(background, **kwargs)

        self.period = int(period)
        self.frequency = float(freq)
        # Determine sign of direction based on frequency (negative => downwards, positive => upwards)
        self.direction = (lambda x: (-1, 1)[x < 0])(self.frequency)
        self.px_per_cycle = (
            self.direction * (self.period * abs(self.frequency)) / config.fps
        )
        print(self.px_per_cycle)

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


class SolidColour(Stimulus):
    form_path = "stimuli/solid_colour.html"

    def __init__(self, background, colour, **kwargs):
        super().__init__(background, **kwargs)
        rgb = pg.Color(colour)

        self.image = pg.Surface((self.width, self.height))
        self.image.fill(rgb)
        self.rect = self.image.get_rect()
        self.area = self.screen.get_rect()


class IsoluminantGray(SolidColour):
    """Based gratings pixel value mean"""

    form_path = None

    def __init__(self, background, **kwargs):
        super().__init__(background, colour=(127, 127, 127))
