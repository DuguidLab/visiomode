#  This file is part of visiomode.
#  Copyright (c) 2021 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import random

import pygame as pg

from visiomode import stimuli

# class VariableColourFixedRange(stimuli.Stimulus):
#     form_path = "stimuli/variable_colour_fixed.html"

#     def __init__(self, background, base_colour, saturations, luminances, **kwargs):
#         super().__init__(background, **kwargs)

#         self.colour = base_colour
#         self.rgb = pg.Color(base_colour)

#         self.image = pg.Surface((self.width, self.height))
#         self.image.fill(self.rgb)
#         self.rect = self.image.get_rect()
#         self.area = self.screen.get_rect()

#     def get_details(self):
#         """Returns a dictionary of stimulus attributes."""
#         return {
#             "id": self.get_identifier(),
#             "common_name": self.get_common_name(),
#             "width": self.width,
#             "height": self.height,
#             "center_x": self.rect.centerx,
#             "center_y": self.rect.centery,
#             "colour_hex": self.colour,
#             "colour_rgba": str(self.rgb),
#             "hue": self.rgb.hsla[0],
#             "saturation": self.rgb.hsla[1],
#             "luminance": self.rgb.hsla[2],
#             "alpha": self.rgb.hsla[3],
#         }


class VariableColourUniformRange(stimuli.Stimulus):
    form_path = "stimuli/variable_colour_uniform.html"

    def __init__(
        self,
        background,
        hue: float,
        saturation_min: float,
        saturation_max: float,
        luminance_min: float,
        luminance_max: float,
        **kwargs,
    ):
        super().__init__(background, **kwargs)

        self.hue = float(hue)
        if self.hue < 0:  # pygame.Color hates negative values
            self.hue = 360 - abs(self.hue)
        self.saturation_min = float(saturation_min)
        self.saturation_max = float(saturation_max)
        self.luminance_min = float(luminance_min)
        self.luminance_max = float(luminance_max)

        self.colour = pg.Color(0, 0, 0)
        self.colour.hsla = (self.hue, self.saturation_min, self.luminance_min, 100)

        self.image = pg.Surface((self.width, self.height))
        # self.image.fill(self.colour)
        self.rect = self.image.get_rect()
        self.area = self.screen.get_rect()

    def generate_new_trial(self):
        super().generate_new_trial()
        self.trial_luminance = random.uniform(self.luminance_min, self.luminance_max)  # noqa: S311
        self.trial_saturation = random.uniform(self.saturation_min, self.saturation_max)  # noqa: S311

        self.colour.hsla = (self.hue, self.trial_saturation, self.trial_luminance, 100)
        self.image.fill(self.colour)

    def get_details(self):
        """Returns a dictionary of stimulus attributes."""
        return {
            "id": self.get_identifier(),
            "common_name": self.get_common_name(),
            "width": self.width,
            "height": self.height,
            "center_x": self.rect.centerx,
            "center_y": self.rect.centery,
            "colour_rgba": str(self.colour),
            "hue": self.hue,
            "saturation": self.colour.hsla[1],
            "luminance": self.colour.hsla[2],
            "alpha": self.colour.hsla[3],
        }
