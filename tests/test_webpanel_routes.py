import pytest


def test_index(client):
    response = client.get("/")
    assert response.status_code == 200


def test_history(client):
    response = client.get("/history")
    assert response.status_code == 200


def test_settings(client):
    response = client.get("/settings")
    assert response.status_code == 200


def test_settings_animals(client):
    response = client.get("/settings-animals")
    assert response.status_code == 200


def test_settings_experimenters(client):
    response = client.get("/settings-experimenters")
    assert response.status_code == 200


def test_help(client):
    response = client.get("/help")
    assert response.status_code == 200


def test_about(client):
    response = client.get("/about")
    assert response.status_code == 200


def test_invalid_route(client):
    response = client.get("/idontexist")
    assert response.status_code == 200  # Renders custom template
