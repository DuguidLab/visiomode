"""API Module"""

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Copyright (c) 2024 Olivier Delree <odelree@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.
import glob
import json
import logging
import os
import pathlib
import queue
import socket

import flask
import flask.views

import visiomode.config as cfg
from visiomode import devices, stimuli, tasks
from visiomode.models import Animal, Experimenter
from visiomode.webpanel import export


class DeviceAPI(flask.views.MethodView):
    def post(self):
        request = json.loads(flask.request.data.decode("utf8"))
        try:
            devices.check_device_profile(request["profile"], request["address"])
        except Exception as e:
            logging.exception(f"Error checking device profile: {e}")
            return (
                json.dumps({"success": False, "error": str(e), "profile": request}),
                500,
                {"ContentType": "application/json"},
            )
        return json.dumps({"success": True}), 200, {"ContentType": "application/json"}


class SessionAPI(flask.views.MethodView):
    def __init__(self, action_q: queue.Queue, log_q: queue.Queue):
        self.action_q = action_q
        self.log_q = log_q

    def post(self):
        """Session management request."""
        request = flask.request.json
        logging.debug(f"Session POST request - {request}")
        self.action_q.put(request)
        return json.dumps({"success": True}), 200, {"ContentType": "application/json"}

    def get(self):
        """Request for current session status."""
        self.action_q.put({"type": "status"})
        return self.log_q.get(timeout=200)


class StimulusAPI(flask.views.MethodView):
    def get(self, stimulus_id):
        idx = flask.request.args.get("idx")  # used to differentiate multiple stimuli on same page
        stimulus = stimuli.get_stimulus(stimulus_id)
        if stimulus and stimulus.form_path:
            return flask.render_template(stimulus.get_form(), idx=idx)
        return "No Additional Options"


class TaskAPI(flask.views.MethodView):
    def get(self, task_id):
        task = tasks.get_task(task_id)
        if task and task.form_path:
            return flask.render_template(
                task.get_form(),
                stimuli=list(stimuli.Stimulus.get_children()),
                reward_profiles=devices.OutputDevice.get_children(),
                response_profiles=devices.InputDevice.get_children(),
                serial_devices=devices.get_available_devices(),
            )
        return "No Additional Options"


class HostnameAPI(flask.views.MethodView):
    def get(self):
        return socket.gethostname()


class HistoryAPI(flask.views.MethodView):
    """Session history API."""

    def get(self):
        """Get stored session data."""
        config = cfg.Config()

        session_id = flask.request.args.get("session_id")
        if session_id:  # A specific session was requested
            session = {}
            try:
                with open(f"{config.data_dir}{os.sep}{session_id}.json") as handle:
                    session = json.load(handle)
            except Exception:
                logging.exception(f"Couldn't get session data for session '{session_id}'.")
            return {"session": session}
        else:  # All sessions were requested
            session_files = glob.glob(config.data_dir + os.sep + "*.json")
            sessions = []
            for session_file in session_files:
                with open(session_file) as f:
                    try:
                        session = json.load(f)
                        sessions.append(
                            {
                                "fname": session_file.split(os.sep)[-1],
                                "animal_id": session["animal_id"],
                                "date": session["timestamp"],
                                "task": session["task"],
                                "experiment": session["experiment"],
                                "session_id": pathlib.Path(session_file).stem,
                            }
                        )
                    except ValueError:
                        logging.exception("Couldn't read session JSON file, wrong format?")
            return {"sessions": sessions}

    def post(self):
        success = False
        return_code = 500

        config = cfg.Config()

        request = flask.request
        if request.content_type != "application/json":
            return_code = 415
            return (
                json.dumps({"success": success}),
                return_code,
                {"ContentType": "application/json"},
            )

        request_type = request.json.get("type")
        request_data = request.json.get("data")

        if request_type == "delete":
            try:
                session_id = request_data["sessionId"]
                try:
                    os.remove(f"{config.data_dir}{os.sep}{session_id}.json")
                    success = True
                    return_code = 200
                except (OSError, FileNotFoundError):
                    logging.error(f"Could not delete session '{session_id}'.")
                    return_code = 409
            except KeyError:
                logging.error("Malformed request data for request type 'DELETE'.")
        elif request_type == "update":
            try:
                session_id = request_data["sessionId"]
                updated_session_data = request_data["updatedSessionData"]

                try:
                    session_path = f"{config.data_dir}{os.sep}{session_id}.json"
                    with open(session_path) as handle:
                        session_data = json.load(handle)

                    # Currently only notes can be updated
                    session_data["notes"] = updated_session_data["notes"]

                    with open(session_path, "w") as handle:
                        json.dump(session_data, handle)

                    success = True
                    return_code = 200
                except (OSError, FileNotFoundError):
                    logging.error(f"Error handling session'{session_id}'.")
                    return_code = 409
                except KeyError:
                    logging.error("Error updating requested session attributes.")
                    return_code = 400
            except KeyError:
                logging.error("Malformed request data for request type 'UPDATE'.")

        return (
            json.dumps({"success": success}),
            return_code,
            {"ContentType": "application/json"},
        )


class DownloadAPI(flask.views.MethodView):
    """Download session data in whatever format the user wants."""

    def get(self, filetype, filename):
        config = cfg.Config()
        sessions_dir = os.path.abspath(config.data_dir)
        cache_dir = os.path.abspath(config.cache_dir)
        if filetype == "json":
            return flask.send_from_directory(sessions_dir, filename, as_attachment=True)
        elif filetype == "nwb":
            nwb_fname = export.to_nwb(sessions_dir + os.sep + filename)
            return flask.send_from_directory(cache_dir, nwb_fname, as_attachment=True)
        elif filetype == "csv":
            csv_fname = export.to_csv(sessions_dir + os.sep + filename)
            return flask.send_from_directory(cache_dir, csv_fname, as_attachment=True)
        else:
            return f"File format {filetype} is not supported (yet)"


class SettingsAPI(flask.views.MethodView):
    """API for saving and loading settings."""

    def get(self):
        """Get settings."""
        config = cfg.Config()
        return config.to_dict()

    def post(self):
        """Save settings."""
        request_type = flask.request.json.get("type")  # add, delete, update
        request = flask.request.json.get("data")
        config = cfg.Config()

        if request_type == "update":
            config.width = request.get("width", config.width)
            config.height = request.get("height", config.height)
            config.fps = request.get("fps", config.fps)
            config.fullscreen = request.get("fullscreen", config.fullscreen)
            config.data_dir = request.get("data_dir", config.data_dir)
            config.cache_dir = config.data_dir + os.sep + "cache"
            config.save()
        elif request_type == "delete":
            if request.get("path") == "cache":
                logging.warning("Clearing cache directory.")
                cfg.clear_cache()
            elif request.get("path") == "app-data":
                logging.warning("Clearing app data directory. Will revert to default settings.")
                cfg.clear_data()
        return json.dumps({"success": True}), 200, {"ContentType": "application/json"}


class AnimalsAPI(flask.views.MethodView):
    """API for managing animal profiles."""

    def get(self):
        """Get animal profiles."""
        return {"animals": Animal.get_animals()}

    def post(self):
        request_type = flask.request.json.get("type")  # add, delete, update
        request = flask.request.json.get("data")
        if request_type == "delete":
            animal_id = request.get("id")
            if animal_id:
                Animal.delete_animal(animal_id)
            else:
                animals = Animal.get_animals()
                for animal in animals:
                    Animal.delete_animal(animal["animal_id"])
        elif request_type in ("update", "add"):
            animal = Animal(
                animal_id=request.get("id"),
                date_of_birth=request.get("dob"),
                sex=request.get("sex"),
                species=request.get("species"),
                genotype=request.get("genotype"),
                description=request.get("description"),
                rfid=request.get("rfid"),
            )
            animal.save()
        return json.dumps({"success": True}), 200, {"ContentType": "application/json"}


class ExperimentersAPI(flask.views.MethodView):
    """API for managing experimenter profiles."""

    @staticmethod
    def get() -> dict:
        """Get experimenter profiles.

        Returns:
            Dictionary with a single key "experimenters" and a value corresponding
            to the list of experimenters metadata dictionaries.
        """
        return {"experimenters": Experimenter.get_experimenters()}

    @staticmethod
    def post() -> tuple[str, int, dict[str, str]]:
        """Carry out POST request."""
        request_type = flask.request.json.get("type") if flask.request.json else None  # add, delete, update
        request = flask.request.json.get("data") if flask.request.json else {}
        if request_type == "delete":
            experimenter_name = request.get("experimenter_name")
            if experimenter_name:
                Experimenter.delete_experimenter(experimenter_name)
            else:
                experimenters = Experimenter.get_experimenters()
                for experimenter in experimenters:
                    Experimenter.delete_experimenter(experimenter["experimenter_name"])
        elif request_type in ("update", "add"):
            if request_type == "update":
                previous_experimenter_name = str(request.get("previous_experimenter_name"))
                if Experimenter.get_experimenter(previous_experimenter_name):
                    Experimenter.delete_experimenter(previous_experimenter_name)
            new_experimenter = Experimenter(
                experimenter_name=str(request.get("experimenter_name")),
                laboratory_name=str(request.get("laboratory_name")),
                institution_name=str(request.get("institution_name")),
            )
            new_experimenter.save()
        return json.dumps({"success": True}), 200, {"ContentType": "application/json"}
