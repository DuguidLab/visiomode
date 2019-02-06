"""Phone communications over TCP"""
import logging
import socketserver
import carie_controller.hardware.phone.parser as parser


class RequestHandler(socketserver.BaseRequestHandler):
    """
    TCP request handler class for rpi-phone communication
    """

    def handle(self):
        while True:
            self.data = self.request.recv(1024)  # Only suitable for single clients
            if not self.data:
                break  # If client sends an empty request, kill the connection

            logging.info(
                "%s:%s wrote: %s",
                self.client_address[0],
                self.client_address[1],
                str(self.data, "utf-8"),  # dump raw request
            )

            request = parser.parse(self.data)
