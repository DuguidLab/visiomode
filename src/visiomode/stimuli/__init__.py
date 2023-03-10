#  This file is part of visiomode.
#  Copyright (c) 2021 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

"""Visual stimulus classes implemented """
import os
import logging
import numpy as np
import pygame as pg
import visiomode.config as conf
import visiomode.mixins as mixins
import visiomode.plugins as plugins

config = conf.Config()


def get_stimulus(stimulus_id):
    return Stimulus.get_child(stimulus_id)


def load_image(name):
    """Load image and return image object"""
    fullname = os.path.join("visiomode/gui/res", name)
    try:
        image = pg.image.load(fullname)
        if image.get_alpha is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
    except pg.error as message:
        logging.error("Cannot load image: {}".format(fullname))
        raise SystemExit(message)
    return image, image.get_rect()


def normalise_array(array, contrast=1.0, background_px=127):
    """Cast array to a UINT8 image matrix."""
    contrast_min = (1 - contrast) * background_px
    contrast_max = (1 + contrast) * background_px

    image = np.interp(array, (array.min(), array.max()), (contrast_min, contrast_max))

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

        self.hidden = True

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

    def get_details(self):
        """Returns a dictionary of stimulus attributes."""
        return {"id": self.get_identifier(), "common_name": self.get_common_name()}

    def generate_new_trial(self):
        """Regenerate stimuli for a fresh trial"""


plugins.load_modules_dir(__path__[0])
