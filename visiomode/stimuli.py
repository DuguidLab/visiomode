"""Visual stimulus classes implemented """

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.
import os
import re
import flask
import numpy as np
import pygame as pg


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


class BaseStimulus(pg.sprite.Sprite):
    form_path = "stimuli/stimulus.html"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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

    def __init__(self, width, height, period=20, **kwargs):
        super().__init__(**kwargs)

        array = self.sinusoid(width, height, period)
        self.image = pg.surfarray.make_surface(array)
        self.rect = self.image.get_rect()
        screen = pg.display.get_surface()
        self.area = screen.get_rect()

    @staticmethod
    def sinusoid(width, height, period):
        # generate 1-D sine wave of required period
        x = np.arange(width)
        y = np.sin(2 * np.pi * x / period)

        # offset sine wave by the max value to go out of negative range of sine
        y += max(y)

        # create 2-D array of sine-wave
        sinusoid = np.array([[y[j] for j in range(height)] for i in range(width)])
        return grayscale_array(sinusoid)
