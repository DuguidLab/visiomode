#  This file is part of visiomode.
#  Copyright (c) 2021 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import pygame as pg

import visiomode.stimuli as stimuli
import visiomode.protocols as protocols


class TargetOnly(protocols.Task):
    form_path = "protocols/target_only.html"

    def __init__(self, target, **kwargs):
        super(TargetOnly, self).__init__(**kwargs)

        self.background = pg.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((0, 0, 0))
        self.screen.blit(self.background, (0, 0))

        target = stimuli.get_stimulus(target)
        self.target = target(background=self.background, **kwargs)

    def update_stimulus(self):
        self.target.update()

    def show_stimulus(self):
        self.target.show()

    def hide_stimulus(self):
        self.target.hide()
