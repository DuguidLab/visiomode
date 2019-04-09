import socketserver
import carie_controller.core as rc
import carie_controller.interface.cli.cli_prompts as usr
import datetime
import json


class TCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for the TCP listener server.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.settings = usr.task_settings(as_json=False)
        while True:
            self.data = self.request.recv(1024)  # Only suitable for single clients!
            if not self.data:
                break
            print(
                "{}:{} wrote: {}".format(
                    self.client_address[0],
                    self.client_address[1],
                    str(self.data, "utf-8"),
                )
            )
            if (
                str(self.data, "utf-8") == "connect"
                or str(self.data, "utf-8") == "restore"
            ):
                # TODO assign session ID
                self.request.sendall(b"connected\n")
                self.start_session()
            if self.data == b"test":
                print("test water reward")
                rc.water_reward(delay=1000)
            if str(self.data, "utf-8").startswith("event"):
                print(str(self.data, "utf-8"))
                event = json.loads(str(self.data, "utf-8").strip("event:"))
                if event['event_type'] == 'hit':
                    rc.water_reward(delay=2000)  # TODO remove hardcoded value based off calibration
            if str(self.data, "utf-8").startswith("session_end"):
                self.end_session()
                self.start_session()  # Start new one

    def start_session(self):
        input("Press ENTER to begin session...")
        self.request.sendall(bytes(json.dumps(self.settings) + "\n", "utf-8"))
        print("---Session Start---")

    def end_session(self):
        print("---Session End---")
        path = input("Saved sessions directory: ") or "."
        _, timestamp, session_data = str(self.data, "utf-8").split(":", 2)
        with open(path + "/" + timestamp + ".json", "w") as f:
            try:
                json.dump(json.loads(session_data), f)
            except Exception as e:
                print(str(e))
                print(session_data, file=f)


if __name__ == "__main__":
    BIND_IP = "0.0.0.0"
    BIND_PORT = 5000

    socketserver.TCPServer.allow_reuse_address = True
    try:
        server = socketserver.TCPServer((BIND_IP, BIND_PORT), TCPHandler)
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.serve_forever()
    except Exception as e:
        print(str(e))
