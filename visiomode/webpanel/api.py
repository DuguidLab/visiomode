"""API Module"""
#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.
import flask.views
import visiomode.devices as devices
import visiomode.protocols as protocols
import visiomode.stimuli as stimuli


class DeviceAPI(flask.views.MethodView):
    def get(self, device_id):
        if device_id:
            # return a single device
            pass
        # return list of devices
        pass

    def post(self):
        # create new device
        pass

    def put(self):
        # update device
        pass

    def delete(self):
        # delete device
        pass


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
            )
        return "No Additional Options"
