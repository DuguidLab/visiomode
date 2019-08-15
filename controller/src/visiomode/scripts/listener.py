import socketserver
import visiomode.core as rc
import visiomode.interface.cli.cli_prompts as usr
import visiomode.experiment.sessions as sess
import threading
import json


class TCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for the TCP listener server.
    """
    session = None  # Experiment session placeholder
    path = input("Sessions path: ") or "."
    settings = usr.task_settings(as_json=False)
    data = None

    def handle(self):
        # self.request is the TCP socket connected to the client
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
                str(self.data, "utf-8") == "connect" or
                str(self.data, "utf-8") == "restore"
            ):
                self.request.sendall(b"connected\n")
                self.start_session()
            if self.data == b"test":
                print("test water reward")
                rc.water_reward(delay=1000)
            if str(self.data, "utf-8").startswith("event"):
                print(str(self.data, "utf-8"))
                try:
                    event = json.loads(str(self.data, "utf-8").strip("event:"))
                except Exception as e:
                    print("Could not parse event - {}".format(str(e)))
                    continue
                if event['event_type'] == 'hit' or event['event_type'] == 'correction_hit':
                    reward = threading.Thread(target=rc.water_reward,
                                              kwargs={'delay': self.settings['iti_min']})
                    reward.start()
                if self.session:
                    self.session.add_trial(sess.Trial(**event))
                    self.session.save(self.path)
            if str(self.data, "utf-8").startswith("session_end"):
                self.end_session()
                self.start_session()  # Start new one

    def start_session(self):
        self.session = sess.Session(
            mouse=input("Mouse ID: "),
            task=input("Task ID: ")
        )
        input("Press ENTER to begin session...")
        self.request.sendall(bytes(json.dumps(self.settings) + "\n", "utf-8"))
        print("---Session Start---")

    def end_session(self):
        print("---Session End---")
        try:
            self.session.save(self.path)
        except Exception as e:
            print(str(e))
            print(self.session)
        self.session = None


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
