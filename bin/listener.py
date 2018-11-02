import socketserver
#import rodent_control.core as rc
import rodent_control.user.cli_prompts as usr
import time


class TCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for the TCP listener server.
    """
    def handle(self):
        # self.request is the TCP socket connected to the client
        while True:
            self.data = self.request.recv(1024)  # Only suitable for single clients!
            if not self.data:
                break
            print("{}:{} wrote: {}".format(self.client_address[0], self.client_address[1], str(self.data, 'utf-8')))
            if str(self.data, 'utf-8') == 'connect':
                # TODO assign session ID
                self.request.sendall(b'connected\n')
                self.request.sendall(bytes(usr.all_settings() + '\n', 'utf-8'))
            if self.data == b'test':
                print('test water reward')
                #rc.water_reward(delay=1000)


if __name__ == '__main__':
    BIND_IP = '0.0.0.0'
    BIND_PORT = 5000

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer((BIND_IP, BIND_PORT), TCPHandler) as server:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.serve_forever()

