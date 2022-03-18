"""API Module"""
#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.
import json
import queue
import socket
import flask
import flask.views
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
        print(request)
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
