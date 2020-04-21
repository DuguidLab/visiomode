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
        """http://vision.psych.umn.edu/users/kersten
        /kersten-lab/courses/Psy5036W2017/Lectures/17_PythonForVision/Demos/html/2b.Gabor.html"""
        # Generate Sinusoid grating
        # sz: size of generated image (width, height)
        radius = (int(sz[0] / 2.0), int(sz[1] / 2.0))
        [x, y] = np.meshgrid(
            range(-radius[0], radius[0] + 1), range(-radius[1], radius[1] + 1),
        )

        sinusoid = a * np.cos(omega[0] * x + omega[1] * y + rho)
        print(sinusoid.astype(np.int8))
        return sinusoid
