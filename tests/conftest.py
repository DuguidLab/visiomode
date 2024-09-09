"""Configuration & fixtures for pytest."""

import pytest
import queue
from typing import Generator

import pygame

import visiomode.webpanel as webpanel


@pytest.fixture(scope="module")
def pygame_init() -> Generator[None, None, None]:
    """Ensure pygame is initialised before running tests."""
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture(scope="module")
def test_action_q() -> Generator[queue.Queue, None, None]:
    """Queue for action messages."""
    yield queue.Queue()


@pytest.fixture(scope="module")
def test_log_q() -> Generator[queue.Queue, None, None]:
    """Queue for log messages."""
    yield queue.Queue()


@pytest.fixture()
def webapp(test_action_q, test_log_q):
    app = webpanel.create_app(test_action_q, test_log_q)
    app.config.update(
        {
            "TESTING": True,
        }
    )

    yield app


@pytest.fixture()
def client(webapp):
    return webapp.test_client()


@pytest.fixture()
def runner(webapp):
    return webapp.test_cli_runner()
