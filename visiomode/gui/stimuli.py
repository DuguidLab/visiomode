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


class BaseStimulus(pg.sprite.Sprite):
    def __init__(self, *args):
        super().__init__(*args)


class Grating(BaseStimulus):
    def __init__(self, x, y, *args):
        super().__init__(*args)
        array = np.zeros((600, 400, 3), np.int32)
        array[:] = (0, 0, 0)
        array[:, ::5] = (255, 255, 255)
        self.image = pg.surfarray.make_surface(array)
        self.rect = self.image.get_rect()
        # self.image, self.rect = load_image("target.jpg")
        screen = pg.display.get_surface()
        self.area = screen.get_rect()
