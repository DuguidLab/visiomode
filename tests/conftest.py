"""Configuration & fixtures for pytest."""

import pytest
from typing import Generator

import pygame


@pytest.fixture(scope="module")
def pygame_init() -> Generator[None, None, None]:
    """Ensure pygame is initialised before running tests."""
    pygame.init()
    yield
    pygame.quit()
