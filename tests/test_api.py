import pytest

import os
import json
import logging
from visiomode import stimuli, tasks


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
    response = client.get("/api/settings")
    assert {
        "width",
        "height",
        "fps",
        "fullscreen",
        "data_dir",
        "cache_dir",
    } <= json.loads(response.get_data(as_text=True)).keys()


def test_settings_api_post(client):
    # Test config update
    response = client.post(
        "/api/settings",
        json={
            "type": "update",
            "data": {
                "width": 300,
                "height": 300,
                "fps": 60,
                "fullscreen": False,
            },
        },
    )
    assert response.status_code == 200

    # Check that config's actually been updated
    config = json.loads(client.get("/api/settings").get_data(as_text=True))
    assert config["width"] == 300
    assert config["height"] == 300
    assert config["fps"] == 60
    assert config["fullscreen"] == False

    # Test cache clearing
    response = client.post(
        "/api/settings", json={"type": "delete", "data": {"path": "cache"}}
    )
    assert response.status_code == 200
    assert not os.listdir(config["cache_dir"])

    # Test app data clearing
    response = client.post(
        "/api/settings", json={"type": "delete", "data": {"path": "app-data"}}
    )
    assert response.status_code == 200


def test_animals_api_get(client, animal):
    response = client.get("/api/animals")
    animal_data = json.loads(response.get_data(as_text=True))["animals"]
    assert animal_data
    assert len(animal_data) > 0


def test_animals_api_post(client):
    new_animal = {
        "id": "test123",
        "dob": "2024-05-02",
        "sex": "M",
        "species": "Mus musculus",
    }
    # Test add
    response_add = client.post("/api/animals", json={"type": "add", "data": new_animal})
    assert response_add.status_code == 200
    response_get = client.get("/api/animals")
    animal_data = json.loads(response_get.get_data(as_text=True))["animals"]
    assert new_animal["id"] in [animal["animal_id"] for animal in animal_data]

    # Test update
    response_update = client.post(
        "/api/animals",
        json={
            "type": "update",
            "data": {
                "id": new_animal["id"],
                "description": "hello",
            },
        },
    )
    assert response_update.status_code == 200
    response_get = client.get("/api/animals")
    animal_data = json.loads(response_get.get_data(as_text=True))["animals"]
    assert (
        "hello"
        == [
            animal["description"]
            for animal in animal_data
            if animal["animal_id"] == new_animal["id"]
        ][0]
    )

    # Test delete for a single animal
    response_delete = client.post(
        "/api/animals", json={"type": "delete", "data": {"id": new_animal["id"]}}
    )
    assert response_delete.status_code == 200
    response_get = client.get("/api/animals")
    animal_data = json.loads(response_get.get_data(as_text=True))["animals"]
    assert new_animal["id"] not in [animal["animal_id"] for animal in animal_data]

    # Test delete for all animals
    response_delete_all = client.post(
        "/api/animals",
        json={
            "type": "delete",
            "data": {},
        },
    )
    assert response_delete_all.status_code == 200
    response_get = client.get("/api/animals")
    animal_data = json.loads(response_get.get_data(as_text=True))["animals"]
    assert not animal_data


def test_experimenters_api_get(client, experimenter):
    response = client.get("/api/experimenters")
    experimenter_data = json.loads(response.get_data(as_text=True))["experimenters"]
    assert experimenter_data
    assert len(experimenter_data) > 0


def test_experimenters_api_post(client):
    ...
