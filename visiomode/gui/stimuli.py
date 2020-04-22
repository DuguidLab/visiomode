"""Visual stimulus classes implemented """

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.
import os
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


def normalise_array(array: np.array):
    """Cast array to a UINT8 image matrix"""
    image = ((array - array.min()) / (array.max() - array.min())) * 255
    return image.astype(np.uint8)


class BaseStimulus(pg.sprite.Sprite):
    def __init__(self, *args):
        super().__init__(*args)


class Grating(BaseStimulus):
    def __init__(self, *args):
        super().__init__(*args)

        theta = np.pi / 4
        omega = [np.cos(theta), np.sin(theta)]

        array = self.gen_sinusoid((400, 600), 1, omega, np.pi / 2)
        self.image = pg.surfarray.make_surface(array)
        self.rect = self.image.get_rect()
        # self.image, self.rect = load_image("target.jpg")
        screen = pg.display.get_surface()
        self.area = screen.get_rect()

    @staticmethod
    def gen_sinusoid(sz, a, omega, rho):
        x = np.arange(400)  # generate 1-D sine wave of required period
        y = np.sin(2 * np.pi * x / 20)

        y += max(
            y
        )  # offset sine wave by the max value to go out of negative range of sine

        sinusoid = np.array(
            [[y[j] for j in range(400)] for i in range(600)]
        )  # create 2-D array of sine-wave
        return np.stack((normalise_array(sinusoid),) * 3, axis=-1)
