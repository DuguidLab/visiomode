"""API Module"""
#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.
import flask.views


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
    pass


class ProtocolAPI(flask.views.MethodView):
    pass


class TaskAPI(flask.views.MethodView):
    pass


class PresentationAPI(flask.views.MethodView):
    pass
