"""Visual stimulus classes implemented """

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.
import os
import numpy as np
import pygame as pg
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


class Stimulus(
    pg.sprite.Group, mixins.BaseClassMixin, mixins.NamingMixin, mixins.WebFormMixin
):
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
        self.draw(self.screen)

    def hide(self):
        self.hidden = True
        self.clear(self.screen, self.background)

    def update(self):
        pass

    def collision(self, pos):
        for sprite in self.sprites():
            if sprite.rect.collidepoint(pos):
                return True
        return False

    def set_centerx(self, centerx):
        for sprite in self.sprites():
            sprite.rect.centerx = centerx


class Grating(Stimulus):
    form_path = "stimuli/grating.html"

    def __init__(self, background, period=20, contrast=1.0, **kwargs):
        super().__init__(background, **kwargs)
        self.period = int(period)

        grating = Grating.sinusoid(self.width, self.height, self.period, contrast)
        sprite = pg.sprite.Sprite()
        sprite.image = pg.surfarray.make_surface(grating)
        sprite.rect = sprite.image.get_rect()
        sprite.area = self.screen.get_rect()

        self.add(sprite)

    @classmethod
    def sinusoid(cls, width: int, height: int, period: int, contrast: float = 1.0):
        # generate 1-D sine wave of required period
        x = np.arange(width)
        y = np.sin(2 * np.pi * x / period)

        # offset sine wave by the max value to go out of negative range of sine
        y += max(y)

        # create 2-D array of sine-wave
        sinusoid = np.array([[y[j] for j in range(height)] for i in range(width)])
        return grayscale_array(sinusoid, contrast)


class MovingGrating(Stimulus):
    form_path = "stimuli/moving_grating.html"

    def __init__(self, background, period=20, freq=1.0, **kwargs):
        # Default direction is upwards, use negative frequency for downwards
        super().__init__(background, **kwargs)

        self.period = int(period)
        self.frequency = float(freq)
        self.px_per_cycle = (self.height / config.fps) * abs(self.frequency)
        self.px_travelled = 0
        # Determine sign of direction based on frequency (negative => downwards, positive => upwards)
        self.direction = (lambda x: (1, -1)[x < 0])(self.frequency)

        grating = Grating.sinusoid(self.width, self.height, self.period)

        # To emulate the movement, we use two sprites that are offset by the screen width on the y axis.
        # Then with every update, add or subtract y from both sprites. Reset to original position once
        # an image has moved its entire height.
        sprites = [pg.sprite.Sprite(), pg.sprite.Sprite()]
        for idx, sprite in enumerate(sprites):
            sprite.image = pg.surfarray.make_surface(grating)
            sprite.rect = sprite.image.get_rect()
            sprite.rect.y = sprite.rect.height * idx * self.direction  # offset
            sprite.area = self.screen.get_rect()

        self.add(sprites)

    def update(self):
        if self.hidden:
            return
        for sprite in self.sprites():
            sprite.rect.move_ip(0, self.direction * -self.px_per_cycle)
            self.px_travelled += self.px_per_cycle
        if self.px_travelled >= self.height:
            for idx, sprite in enumerate(self.sprites()):
                # reset offset position
                sprite.rect.y = sprite.rect.height * idx * self.direction
                self.px_travelled = 0
        self.draw(self.screen)


class SolidColour(Stimulus):
    form_path = "stimuli/solid_colour.html"

    def __init__(self, background, colour, **kwargs):
        super().__init__(background, **kwargs)
        rgb = pg.Color(colour)

        sprite = pg.sprite.Sprite()
        sprite.image = pg.Surface((self.width, self.height))
        sprite.image.fill(rgb)
        sprite.rect = sprite.image.get_rect()
        sprite.area = self.screen.get_rect()

        self.add(sprite)


class IsoluminantGray(SolidColour):
    """Based gratings pixel value mean"""

    form_path = None

    def __init__(self, background, **kwargs):
        super().__init__(background, colour=(127, 127, 127))
