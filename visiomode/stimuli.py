"""Visual stimulus classes implemented """

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.
import os
import re
import flask
import numpy as np
import pygame as pg


def get_stimulus(stimulus_id):
    stimuli = BaseStimulus.get_children()
    for Stimulus in stimuli:
        if Stimulus.get_identifier() == stimulus_id:
            return Stimulus


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


def normalise_array(array: np.ndarray) -> np.ndarray:
    """Cast array to a UINT8 image matrix."""
    image = ((array - np.min(array)) / (np.max(array) - np.min(array))) * 255
    return image.astype(np.uint8)


def grayscale_array(array: np.ndarray) -> np.ndarray:
    """Convert a 2D array to 3D array of grayscale values."""
    return np.stack((normalise_array(array),) * 3, axis=-1)


class BaseStimulus(pg.sprite.Group):
    form_path = "stimuli/stimulus.html"

    def __init__(self, background, **kwargs):
        super().__init__()
        self.screen = pg.display.get_surface()
        self.background = background

    def show(self):
        self.draw(self.screen)

    def hide(self):
        self.clear(self.screen, self.background)

    def update(self):
        pass

    def collision(self, pos):
        for sprite in self.sprites():
            if sprite.rect.collidepoint(pos):
                return True
        return False

    @classmethod
    def get_common_name(cls):
        """"Return the human-readable, space-separated name for the class."""
        return re.sub(r"((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))", r" \1", cls.__name__)

    @classmethod
    def get_children(cls):
        """Return all inheriting children as a list."""
        return cls.__subclasses__()

    @classmethod
    def get_identifier(cls):
        return cls.__name__.lower()

    @classmethod
    def get_form(cls):
        return flask.render_template(cls.form_path)


class Grating(BaseStimulus):
    form_path = "stimuli/grating.html"

    def __init__(self, background, width, height, period=20, **kwargs):
        super().__init__(background, **kwargs)

        grating = Grating.sinusoid(int(width), int(height), int(period))
        sprite = pg.sprite.Sprite()
        sprite.image = pg.surfarray.make_surface(grating)
        sprite.rect = sprite.image.get_rect()
        sprite.area = self.screen.get_rect()

        self.add(sprite)

    @classmethod
    def sinusoid(cls, width: int, height: int, period: int):
        # generate 1-D sine wave of required period
        x = np.arange(width)
        y = np.sin(2 * np.pi * x / period)

        # offset sine wave by the max value to go out of negative range of sine
        y += max(y)

        # create 2-D array of sine-wave
        sinusoid = np.array([[y[j] for j in range(height)] for i in range(width)])
        return grayscale_array(sinusoid)


class MovingGrating(BaseStimulus):
    form_path = "stimuli/moving_grating.html"

    def __init__(self, background, width, height, period=20, **kwargs):
        super().__init__(background, **kwargs)

        grating = Grating.sinusoid(int(width), height, period)

        # To emulate the movement, we use two sprites that are offset by the screen width on the y axis.
        # Then with every update, add or subtract y from both sprites. Reset to original position once
        # an image has moved its entire height.
        sprites = [pg.sprite.Sprite(), pg.sprite.Sprite()]
        for idx, sprite in enumerate(sprites):
            sprite.image = pg.surfarray.make_surface(grating)
            sprite.rect = sprite.image.get_rect()
            sprite.rect.y = sprite.rect.height * idx  # Generate y-offset
            sprite.area = self.screen.get_rect()

        self.add(sprites)

    def update(self):
        for sprite in self.sprites():
            sprite.rect.move_ip(0, -1)
