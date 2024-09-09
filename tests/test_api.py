import pytest

import json
from visiomode.webpanel import api
from visiomode.devices import Device


def test_device_api_post(client):
    invalid_response = client.post(
        "/api/device",
        json={"profile": "leverpush", "address": "/dev/null"},
    )
    assert invalid_response.status_code == 500


def test_session_api_get(client, test_log_q, test_action_q):
    test_log_q.put({"status": "test", "data": "test"})
    response = client.get("/api/session")
    assert response.status_code == 200
    assert json.loads(response.get_data()) == {
        "status": "test",
        "data": "test",
    }
    assert test_action_q.get() == {"type": "status"}


def test_session_api_post(client, test_action_q):
    response = client.post("/api/session", json={"hello": "test"})
    assert test_action_q.get() == {"hello": "test"}
    assert response.status_code == 200
