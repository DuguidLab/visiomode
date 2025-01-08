import copy

import numpy as np
import pygame
import pytest

from visiomode import stimuli

teststimuli = list(stimuli.Stimulus.get_children())


@pytest.fixture(scope="module")
def background(pygame_init):
    if pygame.display.get_surface() is None:
        pygame.display.set_mode((400, 400), flags=pygame.HIDDEN)

    background = pygame.Surface((400, 400))
    background = background.convert()
    background.fill("black")
    yield background


@pytest.mark.parametrize("stimulus", teststimuli)
def test_show(background, stimulus):
    stimulus_instance = stimulus(background, colour="yellow")
    stimulus_instance.show()

    assert not stimulus_instance.hidden
    assert pygame.display.get_surface().get_at(stimulus_instance.rect.topleft) == stimulus_instance.image.get_at(
        stimulus_instance.rect.topleft
    )


@pytest.mark.parametrize("stimulus", teststimuli)
def test_draw(background, stimulus):
    stimulus_instance = stimulus(background, colour="yellow")
    stimulus_instance.draw()

    assert pygame.display.get_surface().get_at(stimulus_instance.rect.topleft) == stimulus_instance.image.get_at(
        stimulus_instance.rect.topleft
    )


@pytest.mark.parametrize("stimulus", teststimuli)
def test_hide(background, stimulus):
    stimulus_instance = stimulus(background, colour="yellow")
    stimulus_instance.show()
    stimulus_instance.hide()

    assert stimulus_instance.hidden
    assert pygame.display.get_surface().get_at(stimulus_instance.rect.topleft) == stimulus_instance.background.get_at(
        stimulus_instance.rect.topleft
    )


@pytest.mark.parametrize("stimulus", teststimuli)
def test_update(background, stimulus):
    stimulus_instance = stimulus(background, colour="yellow")
    stimulus_instance.show()
    stimulus_instance.update()

    if stimulus_instance.get_identifier().startswith("moving"):
        assert pygame.display.get_surface().get_at(stimulus_instance.rect.center) != stimulus_instance.image.get_at(
            stimulus_instance.rect.center
        )
        return

    assert pygame.display.get_surface().get_at(stimulus_instance.rect.center) == stimulus_instance.image.get_at(
        stimulus_instance.rect.center
    )


@pytest.mark.parametrize("stimulus", teststimuli)
def test_collision(background, stimulus):
    stimulus_instance = stimulus(background, colour="yellow")
    assert not stimulus_instance.collision(stimulus_instance.rect.topleft[0] - 1, stimulus_instance.rect.topleft[1])
    assert stimulus_instance.collision(stimulus_instance.rect.topleft[0], stimulus_instance.rect.topleft[1])


@pytest.mark.parametrize("stimulus", teststimuli)
def test_set_centerx(background, stimulus):
    stimulus_instance = stimulus(background, colour="yellow")
    stimulus_instance.set_centerx(10)

    assert stimulus_instance.rect.centerx == 10


@pytest.mark.parametrize("stimulus", teststimuli)
def test_get_details(background, stimulus):
    stimulus_instance = stimulus(background, colour="yellow")
    details = stimulus_instance.get_details()

    assert isinstance(details, dict)


@pytest.mark.parametrize("stimulus", teststimuli)
def test_generate_new_trial(background, stimulus):
    stimulus_instance = stimulus(background, colour="yellow")
    previous_trial_image = copy.copy(stimulus_instance.image)

    stimulus_instance.generate_new_trial()

    assert stimulus_instance.image != previous_trial_image


@pytest.mark.parametrize("stimulus", teststimuli)
def test_stimulus_loaded(stimulus):
    assert stimuli.get_stimulus(stimulus.get_identifier()) is not None


def test_invalid_id():
    assert stimuli.get_stimulus("this_is_an_invalid_id") is None


def test_normalise_array():
    float_array = np.random.random(8 * 7).reshape(8, 7)
    normalised_array = stimuli.normalise_array(float_array)

    assert normalised_array.min() >= 0
    assert normalised_array.max() < 2**8
    assert normalised_array.dtype == np.uint8


def test_grayscale_array():
    float_array = np.random.random(8 * 7).reshape(8, 7)
    grayscale_array = stimuli.grayscale_array(float_array)

    assert grayscale_array.shape == (8, 7, 3)
    assert grayscale_array.min() >= 0
    assert grayscale_array.max() < 2**8
    assert grayscale_array.dtype == np.uint8
