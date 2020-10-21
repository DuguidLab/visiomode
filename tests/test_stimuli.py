"""Test stimulus generation"""

import pytest
import pygame as pg
import visiomode.stimuli as stimuli


class TestStimulusGeneration:
    """Test stimulus classes."""

    pg.init()
    screen = pg.display.set_mode((720, 720))
    background = pg.Surface(screen.get_size())
    background = background.convert()
    background.fill((0, 0, 0))
    screen.blit(background, (0, 0))

    def test_grating(self):
        # Clean up screen
        self.screen.blit(self.background, (0, 0))
        pg.display.flip()

        # Generate stimulus
        grating = stimuli.Grating(self.background)
        grating.show()
        pg.display.flip()

    def test_moving_grating(self):
        pass

    def test_solid_colour(self):
        # Clean up screen
        self.screen.blit(self.background, (0, 0))
        pg.display.flip()

        # Generate stimulus
        colour = stimuli.SolidColour(self.background, (100, 100, 100))
        colour.show()
        pg.display.flip()

    def test_isoluminant_gray(self):
        pass


class TestStimulusHelpers:
    """Test module helper functions."""

    pass
