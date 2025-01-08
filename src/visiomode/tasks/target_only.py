#  This file is part of visiomode.
#  Copyright (c) 2021 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import pygame as pg

from visiomode import stimuli, tasks


class TargetOnly(tasks.Task):
    form_path = "tasks/target_only.html"

    def __init__(self, target, **kwargs):
        super().__init__(**kwargs)

        self.background = pg.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((0, 0, 0))
        self.screen.blit(self.background, (0, 0))

        target = stimuli.get_stimulus(target)
        self.target = target(background=self.background, **kwargs)

    def update_stimulus(self):
        self.target.update()

    def show_stimulus(self):
        self.target.generate_new_trial()
        self.target.show()

    def hide_stimulus(self):
        self.target.hide()
