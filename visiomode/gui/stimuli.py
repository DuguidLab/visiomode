"""Visual stimulus classes implemented """

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.
import os
import pygame


def load_image(name):
    """ Load image and return image object"""
    fullname = os.path.join("visiomode/gui/res", name)
    try:
        image = pygame.image.load(fullname)
        if image.get_alpha is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
    except pygame.error as message:
        print("Cannot load image:", fullname)
        raise SystemExit(message)
    return image, image.get_rect()


class BaseStimulus(pygame.sprite.Sprite):
    def __init__(self, *args):
        super(BaseStimulus, self).__init__(*args)


class Grating(BaseStimulus):
    def __init__(self, x, y, *args):
        super(Grating, self).__init__(*args)
        self.image, self.rect = load_image("target.jpg")
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
