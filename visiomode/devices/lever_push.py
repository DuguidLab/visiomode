#  This file is part of visiomode.
#  Copyright (c) 2021 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import time
import datetime
import serial
import threading
import queue
import visiomode.devices as devices
import visiomode.models as models
import visiomode.config as conf

lever_response_map = {"R": "response", "P": "partial", "E": "error"}


class LeverPush(devices.InputDevice):
    def __init__(self, address, profile_path=None):
        super().__init__(address, profile_path)
        self.config = conf.Config()

        self.bus = serial.Serial(address, 9600, timeout=1)
        time.sleep(2)  # Allow the port enough time to do its thing after a reset

        self.listening = False
        self._response_q = queue.Queue()

        self.listen(threaded=True)

    def get_response(self):
        if not self._response_q.empty():
            self._response_q.get()  # Remove response from queue
            return models.Response(
                timestamp=datetime.datetime.now().isoformat(),
                pos_x=self.config.width / 2,
                pos_y=self.config.height / 2,
                dist_x=0,
                dist_y=0,
            )
        return None

    def lock_lever(self):
        self.bus.write(b"L\n")

    def unlock_lever(self):
        self.bus.write(b"U\n")

    def listen(self, threaded=True):
        self.listening = True
        if threaded:
            thread = threading.Thread(target=self._message_listener, daemon=True)
            return thread.start()
        self._message_listener()

    def stop_listening(self):
        self.listening = False

    def on_trial_start(self):
        self.unlock_lever()

    def on_trial_end(self):
        self.lock_lever()

    def test(self):
        self.bus.write(b"T\n")

    def _message_listener(self):
        while self.listening:
            raw_message = self.bus.readline().decode("utf-8")[0]
            message = lever_response_map.get(raw_message)
            if message == "response":
                self._response_q.put(message)
                time.sleep(0.2)
            elif message == "error":
                raise devices.DeviceError("Lever-push controller error.")

    def test(self):
        self.bus.write(b"T\n")
