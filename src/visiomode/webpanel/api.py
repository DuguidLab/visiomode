"""API Module"""

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Copyright (c) 2024 Olivier Delree <odelree@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.
import os
import json
import logging
import queue
import socket
import glob
import flask
import flask.views
import pydantic

import visiomode.config as cfg
import visiomode.devices as devices
import visiomode.protocols as protocols
import visiomode.stimuli as stimuli
import visiomode.webpanel.export as export

from visiomode.models import Animal
import visiomode.database as db


class DeviceAPI(flask.views.MethodView):
    def post(self):
        request = json.loads(flask.request.data.decode("utf8"))
        devices.check_device_profile(request["profile"], request["address"])
        return json.dumps({"success": True}), 200, {"ContentType": "application/json"}


class SessionAPI(flask.views.MethodView):
    def __init__(self, action_q: queue.Queue, log_q: queue.Queue):
        self.action_q = action_q
        self.log_q = log_q

    def post(self):
        """Session management request."""
        request = flask.request.json
        logging.debug("Session POST request - {}".format(request))
        self.action_q.put(request)
        return json.dumps({"success": True}), 200, {"ContentType": "application/json"}

    def get(self):
        """Request for current session status."""
        self.action_q.put({"type": "status"})
        return self.log_q.get(timeout=200)


class StimulusAPI(flask.views.MethodView):
    def get(self, stimulus_id):
        idx = flask.request.args.get(
            "idx"
        )  # used to differentiate multiple stimuli on same page
        stimulus = stimuli.get_stimulus(stimulus_id)
        if stimulus and stimulus.form_path:
            return flask.render_template(stimulus.get_form(), idx=idx)
        return "No Additional Options"


class ProtocolAPI(flask.views.MethodView):
    def get(self, protocol_id):
        protocol = protocols.get_protocol(protocol_id)
        if protocol and protocol.form_path:
            return flask.render_template(
                protocol.get_form(),
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
                            "protocol": session["protocol"],
                            "experiment": session["experiment"],
                        }
                    )
                except:
                    logging.exception("Couldn't read session JSON file, wrong format?")
        return {"sessions": sessions}


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
            return "File format {} is not supported (yet)".format(filetype)


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

        print(request)
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
                logging.warning(
                    "Clearing app data directory. Will revert to default settings."
                )
                cfg.clear_data()
        return json.dumps({"success": True}), 200, {"ContentType": "application/json"}


class AnimalsAPI(flask.views.MethodView):
    """API for managing animal profiles."""

    database = db.get_database(Animal)

    def get(self):
        """Get animal profiles."""
        return {"animals": self.database.get_entries()}

    def post(self):
        request_type = flask.request.json.get("type")  # add, delete, update
        request = flask.request.json.get("data")
        print(request)
        if request_type == "delete":
            animal_id = request.get("id")
            if animal_id:
                self.database.delete_entry(animal_id)
            else:
                animals = self.database.get_entries()
                for animal in animals:
                    self.database.delete_entry(animal["animal_id"])
        elif (request_type == "update") or (request_type == "add"):
            try:
                animal = Animal(**request)
                self.database.save_entry(animal)
            except pydantic.ValidationError:
                logging.error(
                    f"Could not validate animal model from request data:\n{request}"
                )
                return (
                    json.dumps({"success": False}),
                    400,
                    {"ContentType": "application/json"},
                )
        return json.dumps({"success": True}), 200, {"ContentType": "application/json"}
