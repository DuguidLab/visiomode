"""API Module"""
#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.
import os
import json
import logging
import queue
import socket
import glob
import flask
import flask.views
import visiomode.config as cfg
import visiomode.devices as devices
import visiomode.protocols as protocols
import visiomode.stimuli as stimuli


class DeviceAPI(flask.views.MethodView):
    def post(self):
        request = json.loads(flask.request.data.decode("utf8"))
        devices.check_device_profile(request["profile"], request["address"])
        return "OK"


class SessionAPI(flask.views.MethodView):
    def __init__(self, action_q: queue.Queue, log_q: queue.Queue):
        self.action_q = action_q
        self.log_q = log_q

    def post(self):
        """Session management request."""
        request = flask.request.json
        logging.debug("Session POST request - {}".format(request))
        self.action_q.put(request)
        return "OK"

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
        """Get stored session data.
        """
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
        if filetype == "json":
            return flask.send_from_directory(sessions_dir, filename, as_attachment=True)
        else:
            return "File format {} is not supported (yet)".format(filetype)
