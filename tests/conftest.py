"""Configuration & fixtures for pytest."""

import pytest
from typing import Generator

import pygame

import visiomode.webpanel as webpanel


@pytest.fixture(scope="module")
def pygame_init() -> Generator[None, None, None]:
    """Ensure pygame is initialised before running tests."""
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture()
def webapp():
    app = webpanel.create_app()
    app.config.update(
        {
            "TESTING": True,
        }
    )

    # other setup can go here

    yield app

    # clean up / reset resources here


@pytest.fixture()
def client(webapp):
    return webapp.test_client()


@pytest.fixture()
def runner(webapp):
    return webapp.test_cli_runner()
