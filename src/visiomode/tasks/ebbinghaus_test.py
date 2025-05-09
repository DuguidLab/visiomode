from visiomode.stimuli.ebbinghaus_circle import EbbinghausCircle
from visiomode import tasks

import random

import pygame as pg


class EbbinghausTestDay(tasks.Task):
    form_path = "tasks/task.html"

    def __init__(self, **kwargs):
        super().__init__(iti=2000, stimulus_duration=10000, **kwargs)

        self.background = pg.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((0, 0, 0))
        self.screen.blit(self.background, (0, 0))

        self.corrections_enabled = False

        self.separator_size = 50  # pixels
        self.separator = pg.Rect(((0, 0), (self.separator_size, self.screen.get_height())))
        self.separator.centerx = self.screen.get_rect().centerx

        self.stimulus_width = (self.screen.get_size()[0] - self.separator_size) // 2

        self.target = EbbinghausCircle(
            background=self.background,
            width=self.stimulus_width,
            center_size=[20, 25, 30],
            ratios=[0.5, 1, 2],
        )

        self.distractor = EbbinghausCircle(
            background=self.background,
            width=self.stimulus_width,
            center_size=[10, 15, 20],
            ratios=[0.5, 1, 2],
        )

    def show_stimulus(self):
        self.target.generate_new_trial()
        self.distractor.generate_new_trial()

        target_x, distr_x = self.shuffle_centerx()

        self.target.set_centerx(target_x)
        self.distractor.set_centerx(distr_x)

        self.target.show()
        self.distractor.show()

    def hide_stimulus(self):
        self.target.hide()
        self.distractor.hide()
        # self.screen.blit(self.background, (0, 0))

    def update_stimulus(self):
        self.distractor.update()
        self.target.update()

    def shuffle_centerx(self):
        # centers = [
        #     0 - (self.separator_size / 2),
        #     self.screen.get_width() + (self.separator_size / 2),
        # ]
        centers = (
            ((self.screen.get_width() / 2) - (self.separator_size / 2)) / 2,
            (self.screen.get_width() / 2) + (self.separator_size / 2) + (self.stimulus_width / 2),
        )
        return random.sample(centers, 2)
