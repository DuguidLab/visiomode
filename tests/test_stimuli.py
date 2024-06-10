import unittest

import numpy as np
import parameterized
import pygame

import visiomode.stimuli as stimuli

STIMULUS_IDS = {
    ("grating",),
    ("isoluminantgray",),
    ("movinggrating",),
    ("solidcolour",),
    ("variablecontrastgrating",),
    ("variablecontrastmovinggrating",),
}


@parameterized.parameterized_class(("stimulus_id",), STIMULUS_IDS)
class StimulusTest(unittest.TestCase):
    background: pygame.SurfaceType

    stimulus_id: str
    stimulus: stimuli.Stimulus

    @classmethod
    def setUpClass(cls) -> None:
        # Ensure pygame has been initialised and there is a screen
        pygame.init()
        if pygame.display.get_surface() is None:
            # Create a screen but don't make the window visible
            pygame.display.set_mode((400, 400), flags=pygame.HIDDEN)

        # Set up a dummy background
        cls.background = pygame.Surface((400, 400))
        cls.background = cls.background.convert()
        cls.background.fill("black")

    def setUp(self) -> None:
        self.stimulus = stimuli.get_stimulus(self.stimulus_id)(
            type(self).background,
            colour="yellow",
        )

    def test_show(self) -> None:
        """Test `show` behaves as expected."""
        # Check this stimulus has the required attributes
        if not (hasattr(self.stimulus, "image") and hasattr(self.stimulus, "rect")):
            return

        stimulus_rect_top_left = self.stimulus.rect.topleft
        self.stimulus.show()

        self.assertFalse(self.stimulus.hidden)
        self.assertEqual(
            pygame.display.get_surface().get_at(stimulus_rect_top_left),
            self.stimulus.image.get_at(stimulus_rect_top_left),
        )

    def test_draw(self) -> None:
        """Test `draw` behaves as expected."""
        stimulus_rect_top_left = self.stimulus.rect.topleft
        self.stimulus.draw()

        # Check this stimulus has the required attributes
        if not (hasattr(self.stimulus, "image") and hasattr(self.stimulus, "rect")):
            return

        self.assertEqual(
            pygame.display.get_surface().get_at(stimulus_rect_top_left),
            self.stimulus.image.get_at(stimulus_rect_top_left),
        )

    def test_hide(self) -> None:
        """Test `hide` behaves as expected."""
        stimulus_rect_top_left = self.stimulus.rect.topleft
        self.stimulus.hide()

        self.assertTrue(self.stimulus.hidden)
        self.assertEqual(
            pygame.display.get_surface().get_at(stimulus_rect_top_left),
            self.stimulus.background.get_at(stimulus_rect_top_left),
        )

    def test_update(self) -> None:
        """Test `update` behaves as expected."""
        # The base call is a no-op, so test only makes sense if it is overridden
        if type(self.stimulus).update is stimuli.Stimulus.update:
            return

        stimulus_rect_top_left = self.stimulus.rect.topleft
        self.stimulus.update()

        # Check this stimulus has the required attributes
        if not (hasattr(self.stimulus, "image") and hasattr(self.stimulus, "rect")):
            return

        self.assertEqual(
            pygame.display.get_surface().get_at(stimulus_rect_top_left),
            self.stimulus.image.get_at(stimulus_rect_top_left),
        )

    def test_collision(self) -> None:
        """Test collision detection."""
        stimulus_rect_top_left = self.stimulus.rect.topleft

        # Check this stimulus has the required attributes
        if not hasattr(self.stimulus, "rect"):
            return

        self.assertFalse(
            self.stimulus.collision(
                stimulus_rect_top_left[0] - 1, stimulus_rect_top_left[1]
            )
        )
        self.assertTrue(
            self.stimulus.collision(
                stimulus_rect_top_left[0], stimulus_rect_top_left[1]
            )
        )

    def test_set_centerx(self) -> None:
        """Test `centerx` setter."""
        self.stimulus.set_centerx(10)

        # Check this stimulus has the required attributes
        if not hasattr(self.stimulus, "rect"):
            return

        self.assertEqual(self.stimulus.rect.centerx, 10)

    def test_get_details(self) -> None:
        """Test `details` getter."""
        details = self.stimulus.get_details()

        self.assertIsInstance(details, dict)

    def test_generate_new_trial(self) -> None:
        """Test new trial generation."""
        # The base call is a no-op, so test only makes sense if it is overridden
        if (
            type(self.stimulus).generate_new_trial
            is stimuli.Stimulus.generate_new_trial
        ):
            return

        # Check this stimulus has the required attributes
        if not hasattr(self.stimulus, "image"):
            return

        previous_trial_image = self.stimulus.image

        self.stimulus.generate_new_trial()

        self.assertIsNot(self.stimulus.image, previous_trial_image)


class StimuliFunctionsTest(unittest.TestCase):
    @parameterized.parameterized.expand(STIMULUS_IDS)
    def test_stimulus_loaded(self, stimulus_id: str) -> None:
        """Test stimulus is loaded properly."""
        self.assertIsNotNone(
            stimuli.get_stimulus(stimulus_id),
            msg=f"Stimulus '{stimulus_id}' was not loaded.",
        )

    def test_invalid_id(self) -> None:
        """Test `get_stimulus` returns None with invalid stimulus ID."""
        self.assertIsNone(stimuli.get_stimulus("this_is_an_invalid_id"))

    def test_normalise_array(self) -> None:
        """Test `normalise_array` returns a properly normalised array."""
        float_array = np.random.random(8 * 7).reshape(8, 7)
        normalised_array = stimuli.normalise_array(float_array)

        self.assertGreaterEqual(normalised_array.min(), 0)
        self.assertLess(normalised_array.max(), 2**8)
        self.assertEqual(normalised_array.dtype, np.uint8)

    def test_grayscale_array(self) -> None:
        """Test the returned array of `grayscale_array`."""
        float_array = np.random.random(8 * 7).reshape(8, 7)
        grayscale_array = stimuli.grayscale_array(float_array)

        self.assertEqual(grayscale_array.shape, (8, 7, 3))
        self.assertGreaterEqual(grayscale_array.min(), 0)
        self.assertLess(grayscale_array.max(), 2**8)
        self.assertEqual(grayscale_array.dtype, np.uint8)


if __name__ == "__main__":
    unittest.main()
