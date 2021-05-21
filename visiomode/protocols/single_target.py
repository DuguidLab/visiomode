#  This file is part of visiomode.
#  Copyright (c) 2021 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import pygame as pg

import stimuli as stim
import visiomode.protocols as protocols


class SingleTarget(protocols.Task):
    form_path = "protocols/single_target.html"

    def __init__(self, target, **kwargs):
        super(SingleTarget, self).__init__(**kwargs)

        self.background = pg.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((0, 0, 0))
        self.screen.blit(self.background, (0, 0))

        target = stim.get_stimulus(target)
        self.target = target(background=self.background, **kwargs)

    def update_stim(self):
        self.target.update()

    def show_stim(self):
        self.target.show()

    def hide_stim(self):
        self.target.hide()
