import socketserver
import rodent_control.core as rc
import rodent_control.user.cli_prompts as usr
import time
import json


class TCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for the TCP listener server.
    """
    def handle(self):
        # self.request is the TCP socket connected to the client
        while True:
            self.data = self.request.recv(10240)  # Only suitable for single clients!
            if not self.data:
                break
            print("{}:{} wrote: {}".format(self.client_address[0], self.client_address[1], str(self.data, 'utf-8')))
            if str(self.data, 'utf-8') == 'connect' or str(self.data, 'utf-8') == 'restore':
                # TODO assign session ID
                self.request.sendall(b'connected\n')
                settings = usr.all_settings()
                self.request.sendall(bytes(settings + '\n', 'utf-8'))
                print('---Sesstion Start---')
            if self.data == b'test':
                print('test water reward')
                rc.water_reward(delay=1000)
            if str(self.data, 'utf-8').startswith('reward'):
                print('dispensing reward')
                rc.water_reward(delay=800)
            if str(self.data, 'utf-8').startswith('session'):
                print('---Session End---')
                path = input("Saved sessions directory: ") or "."
                _, timestamp, session_data = str(self.data, 'utf-8').split(':', 2)
                with open(path + '/' + timestamp + '.json', 'w') as f:
                    json.dump(json.loads(session_data), f)


if __name__ == '__main__':
    BIND_IP = '0.0.0.0'
    BIND_PORT = 5000

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer((BIND_IP, BIND_PORT), TCPHandler) as server:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.serve_forever()

