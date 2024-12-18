"""Configuration & fixtures for pytest."""

import pytest
import queue
from typing import Generator

import pygame

from visiomode import webpanel, models, tasks, stimuli
import visiomode.config as cfg


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
def config(tmp_path):
    test_config = cfg.Config()
    test_data_dir = tmp_path / "visiomode_data"
    test_data_dir.mkdir()
    test_config.data_dir = str(test_data_dir)
    test_config.save(str(tmp_path / ".visiomode.json"))

    return test_config


@pytest.fixture()
def client(webapp, config):
    return webapp.test_client()


@pytest.fixture()
def runner(webapp):
    return webapp.test_cli_runner()


@pytest.fixture()
def session(config):
    """Generate test session data and save in the expected path."""

    session = models.Session(
        animal_id="test_animal",
        experimenter_name="test",
        experiment="test_exp",
        duration=30,
    )
    return session.save(config.data_dir)
