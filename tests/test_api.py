import pytest

import json
import logging
from visiomode import stimuli, tasks, models
from visiomode.webpanel import api


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


def test_stimulus_api_get(client):
    teststimuli = list(stimuli.Stimulus.get_children())
    for stimulus in teststimuli:
        response = client.get(f"/api/stimulus-form/{stimulus.get_identifier()}")
        assert response.status_code == 200
    invalid_response = client.get("/api/stimulus-form/invalid")
    assert b"No Additional Options" in invalid_response.data


def test_task_api_get(client):
    testtasks = list(tasks.Task.get_children())
    for task in testtasks:
        response = client.get(f"/api/task-form/{task.get_identifier()}")
        assert response.status_code == 200
    invalid_response = client.get("/api/task-form/invalid")
    assert b"No Additional Options" in invalid_response.data


def test_hostname_api_get(client):
    response = client.get(f"/api/hostname")
    assert response.status_code == 200


def test_history_api_get_single_session(client, session, caplog):
    caplog.set_level(logging.ERROR)
    # Valid session
    response = client.get(f"/api/history?session_id={session}")
    session_data = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert session_data["session"]
    assert session_data["session"]["animal_id"] == "testanimal"

    # Invalid session
    response = client.get(f"/api/history?session_id=invalid")
    session_data = json.loads(response.get_data(as_text=True))
    for record in caplog.records:
        assert record.levelname == "ERROR"
    assert "Couldn't get session data" in caplog.text


def test_history_api_get_all_sessions(client, session):
    response = client.get(f"/api/history")
    sessions = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert sessions["sessions"]
    assert len(sessions["sessions"]) > 0


def test_history_api_post(client, session):
    # Test return 415 code for invalid content type
    response = client.post("/api/history", content_type="invalid")
    assert response.status_code == 415

    # Test session update
    response = client.post(
        "/api/history",
        json={
            "type": "update",
            "data": {
                "sessionId": session,
                "updatedSessionData": {"notes": "this is a test"},
            },
        },
    )
    assert response.status_code == 200

    # Attempt to update non-existent session
    response = client.post(
        "/api/history",
        json={
            "type": "update",
            "data": {
                "sessionId": "idontexist",
                "updatedSessionData": {"notes": "this is a test"},
            },
        },
    )
    assert response.status_code == 409

    # Try to update a field that's not notes (and therefore can't be changed)
    response = client.post(
        "/api/history",
        json={
            "type": "update",
            "data": {
                "sessionId": session,
                "updatedSessionData": {"animal_id": "blah"},
            },
        },
    )
    assert response.status_code == 400

    # Botch update request
    response = client.post(
        "/api/history",
        json={
            "type": "update",
            "data": {
                "sessionId": session,
                "keythatdoesntexist": {"blah": "blah"},
            },
        },
    )
    assert response.status_code == 500

    # Test session delete
    response = client.post(
        "/api/history", json={"type": "delete", "data": {"sessionId": session}}
    )
    assert response.status_code == 200

    # Try deleting a session that doesn't exist
    # Test session delete
    response = client.post(
        "/api/history", json={"type": "delete", "data": {"sessionId": "idontexist"}}
    )
    assert response.status_code == 409

    # Botch delete request
    # Test session delete
    response = client.post(
        "/api/history", json={"type": "delete", "data": {"hello": "blah"}}
    )
    assert response.status_code == 500


def test_download_api_get(client, session):
    # Test JSON export
    ftype = "json"
    response = client.get(f"/api/download/{ftype}/{session}.json")
    assert response.status_code == 200
    assert (
        response.headers["Content-Disposition"]
        == f"attachment; filename={session}.{ftype}"
    )

    # Test CSV export
    ftype = "csv"
    response = client.get(f"/api/download/{ftype}/{session}.json")
    assert response.status_code == 200
    assert (
        response.headers["Content-Disposition"]
        == f"attachment; filename={session}.{ftype}"
    )

    # Test NWB export
    ftype = "nwb"
    subject_id = session.split("sub-")[1].split("_")[0]
    session_date = session.split("date-")[1].split("T")[0].replace("-", "")
    nwb_fname = f"sub-{subject_id}_ses-{session_date}_behavior.nwb"
    response = client.get(f"/api/download/{ftype}/{session}.json")
    assert response.status_code == 200
    assert (
        response.headers["Content-Disposition"] == f"attachment; filename={nwb_fname}"
    )

    # Test invalid export request
    ftype = "invalid"
    response = client.get(f"/api/download/{ftype}/{session}.json")
    assert "not supported" in response.get_data(as_text=True)


def test_settings_api_get(client):
    ...


def test_settings_api_post(client):
    ...


def test_animals_api_get(client):
    ...


def test_animals_api_post(client):
    ...


def test_experimenters_api_get(client):
    ...


def test_experimenters_api_post(client):
    ...
