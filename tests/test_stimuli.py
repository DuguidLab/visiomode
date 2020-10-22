"""Test stimulus generation"""

import pytest
import pygame as pg
import visiomode.stimuli as stimuli


class TestGrating:
    """Test Grating generation, updating, centering and hiding."""

    pg.init()
    screen = pg.display.set_mode((720, 720))
    background = pg.Surface(screen.get_size())
    background = background.convert()
    background.fill((0, 0, 0))
    screen.blit(background, (0, 0))

    grating = stimuli.Grating(background)

    def test_show(self):
        self.grating.show()
        pg.display.flip()
        assert not self.grating.hidden

    def test_update(self):
        # Update stimulus
        self.grating.update()
        pg.display.flip()

    def test_centerx(self):
        # Set stimulus center-x
        self.grating.set_centerx(200)
        pg.display.flip()

    def test_hide(self):
        # Hide stimulus
        self.grating.hide()
        pg.display.flip()
        assert self.grating.hidden


class TestMovingGrating:
    pg.init()
    screen = pg.display.set_mode((720, 720))
    background = pg.Surface(screen.get_size())
    background = background.convert()
    background.fill((0, 0, 0))
    screen.blit(background, (0, 0))

    moving_grating = stimuli.MovingGrating(background)

    def test_show(self):
        self.moving_grating.show()
        pg.display.flip()
        assert not self.moving_grating.hidden

    def test_update(self):
        # Update stimulus
        self.moving_grating.update()
        pg.display.flip()

    def test_centerx(self):
        # Set stimulus center-x
        self.moving_grating.set_centerx(200)
        pg.display.flip()

    def test_hide(self):
        self.moving_grating.show()
        self.moving_grating.hide()
        pg.display.flip()
        assert self.moving_grating.hidden

    def test_move(self):
        """Test sprite movement. If visible, the y pos should change after an update."""
        self.moving_grating.show()
        original_y = [sprite.rect.y for sprite in self.moving_grating.sprites()]
        self.moving_grating.update()
        new_y = [sprite.rect.y for sprite in self.moving_grating.sprites()]
        assert new_y != original_y

    def test_move_hidden(self):
        """Test sprite movement when group is hidden. Movement should be skipped."""
        self.moving_grating.hide()
        original_y = [sprite.rect.y for sprite in self.moving_grating.sprites()]
        self.moving_grating.update()
        new_y = [sprite.rect.y for sprite in self.moving_grating.sprites()]
        assert new_y == original_y

    def test_move_past_height(self):
        """Test sprite movement past image height. y position should come back down so the sprite repeats."""
        self.moving_grating.show()

    def test_move_timedelta(self):
        """Test sprite movement with timedelta. y position should be proportional to timedelta."""
        self.moving_grating.show()


class TestSolidColour:
    pg.init()
    screen = pg.display.set_mode((720, 720))
    background = pg.Surface(screen.get_size())
    background = background.convert()
    background.fill((0, 0, 0))
    screen.blit(background, (0, 0))

    solid_colour = stimuli.SolidColour(background, (100, 100, 100))

    def test_show(self):
        self.solid_colour.show()
        pg.display.flip()
        assert not self.solid_colour.hidden

    def test_update(self):
        # Update stimulus
        self.solid_colour.update()
        pg.display.flip()

    def test_centerx(self):
        # Set stimulus center-x
        self.solid_colour.set_centerx(200)
        pg.display.flip()

    def test_hide(self):
        self.solid_colour.show()
        self.solid_colour.hide()
        pg.display.flip()
        assert self.solid_colour.hidden


class TestIsoluminantGray:
    pg.init()
    screen = pg.display.set_mode((720, 720))
    background = pg.Surface(screen.get_size())
    background = background.convert()
    background.fill((0, 0, 0))
    screen.blit(background, (0, 0))

    gray = stimuli.IsoluminantGray(background)

    def test_show(self):
        self.gray.show()
        pg.display.flip()
        assert not self.gray.hidden

    def test_update(self):
        # Update stimulus
        self.gray.update()
        pg.display.flip()

    def test_centerx(self):
        # Set stimulus center-x
        self.gray.set_centerx(200)
        pg.display.flip()

    def test_hide(self):
        self.gray.show()
        self.gray.hide()
        pg.display.flip()
        assert self.gray.hidden


class TestStimulusHelpers:
    """Test module helper functions."""

    pass
