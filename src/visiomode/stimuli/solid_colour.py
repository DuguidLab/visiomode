#  This file is part of visiomode.
#  Copyright (c) 2021 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import pygame as pg

from visiomode import stimuli


class SolidColour(stimuli.Stimulus):
    form_path = "stimuli/solid_colour.html"

    def __init__(self, background, colour, **kwargs):
        super().__init__(background, **kwargs)
        self.colour = colour
        rgb = pg.Color(colour)

        self.image = pg.Surface((self.width, self.height))
        self.image.fill(rgb)
        self.rect = self.image.get_rect()
        self.area = self.screen.get_rect()

    def get_details(self):
        """Returns a dictionary of stimulus attributes."""
        return {
            "id": self.get_identifier(),
            "common_name": self.get_common_name(),
            "width": self.width,
            "height": self.height,
            "center_x": self.rect.centerx,
            "center_y": self.rect.centery,
            "colour": self.colour,
        }
