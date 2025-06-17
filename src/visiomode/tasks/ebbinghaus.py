from visiomode.stimuli.ebbinghaus_circle import EbbinghausCircle
from visiomode import tasks

import random

import pygame as pg


class EbbinghausPsychometric(tasks.Task):
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

        # work out if it's an illusion trial
        self.is_illusion = True if self.target.center_radius == self.distractor.center_radius else False

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

    def on_correct(self):
        if self.is_illusion:
            # If it was an illusion trial, do nothing
            return
        return super().on_correct()


class EbbinghausInterleaved(tasks.Task):
    """Ebbinghaus illusion task where 10% of trials are illusion trials"""

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

        self.target = None
        self.distractor = None

        self.is_illusion = False

    def show_stimulus(self):
        # Determine stimulus parameters for the current trial
        if random.random() < 0.10:  # 10% of trials
            # Illusion trial
            target_center_size = [20]  # target: centre that looks smaller
            distractor_center_size = [20]  # distractor: centre that looks bigger

            # Set specific ratios
            target_ratios = [2]  # Bigger context circles for target
            distractor_ratios = [0.5]  # Smaller context circles for distractor

            self.is_illusion = True

        else:  # 90% of trials (standard case)
            # Target center 40px, Distractor center 20px (as before)
            target_center_size = [40]
            distractor_center_size = [20]

            # Default ratios for both (as before)
            target_ratios = [0.5, 1, 1.5, 2]
            distractor_ratios = [0.5, 1, 1.5, 2]

            self.is_illusion = False

        # Create new EbbinghausCircle instances with the determined parameters
        self.target = EbbinghausCircle(
            background=self.background,
            width=self.stimulus_width,
            center_size=target_center_size,
            ratios=target_ratios,
        )

        self.distractor = EbbinghausCircle(
            background=self.background,
            width=self.stimulus_width,
            center_size=distractor_center_size,
            ratios=distractor_ratios,
        )

        # Generate new trial for the newly created stimuli
        self.target.generate_new_trial()
        self.distractor.generate_new_trial()

        # Shuffle positions and show
        target_x, distr_x = self.shuffle_centerx()

        self.target.set_centerx(target_x)
        self.distractor.set_centerx(distr_x)

        self.target.show()
        self.distractor.show()

    def hide_stimulus(self):
        if self.target:
            self.target.hide()
        if self.distractor:
            self.distractor.hide()

    def update_stimulus(self):
        if self.distractor:
            self.distractor.update()
        if self.target:
            self.target.update()

    def shuffle_centerx(self):
        centers = (
            ((self.screen.get_width() / 2) - (self.separator_size / 2)) / 2,
            (self.screen.get_width() / 2) + (self.separator_size / 2) + (self.stimulus_width / 2),
        )
        return random.sample(centers, 2)

    def on_correct(self):
        if self.is_illusion:
            # If it was an illusion trial, do nothing
            return
        return super().on_correct()
