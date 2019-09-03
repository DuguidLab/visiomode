"""Phone communications over TCP"""
import json
import logging
import socketserver


class RequestServer(socketserver.BaseRequestHandler):
    """
    TCP request handler class for rpi-phone communication
    """
    def __init__(self, task_settings, path=".", **kwargs):
        super(RequestServer, self).__init__(self, **kwargs)
        self.data = None
        self.session = None
        self.path = path
        self.settings = task_settings

    def handle(self):
        while True:
            self.data = self.request.recv(1024)  # Only suitable for single clients
            if not self.data:
                break  # If client sends an empty request, kill the connection

            request = str(self.data, "utf-8")

            logging.info("%s:%s wrote: %s",
                         self.client_address[0],
                         self.client_address[1],
                         request)

            self.parse(request)

    def parse(self, request):
        pass

    def start_session(self, mouse_id, task_id):
        pass

    def end_session(self):
        pass

    @staticmethod
    def to_json(raw):
        return json.loads(str(raw, "utf-8"))