import socketserver
#import rodent_control.core as rc
import time


class TCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    def handle(self):
        # self.request is the TCP socket connected to the client
        while True:
            self.data = self.request.recv(1024)  # Only suitable for single clients!
            if not self.data:
                break
            if str(self.data, 'utf-8') == 'connect':
                print('thing')
                self.request.sendall(b'test\n')
                time.sleep(1)
                self.request.sendall(b'{"something": "a", "thing": "b"}\n')
            if self.data == b'test':
                print('test water reward')
                #rc.water_reward(delay=1000)
            print("{}:{} wrote: {}".format(self.client_address[0], self.client_address[1], str(self.data, 'utf-8')))


if __name__ == '__main__':
    BIND_IP = '0.0.0.0'
    BIND_PORT = 5000

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer((BIND_IP, BIND_PORT), TCPHandler) as server:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.serve_forever()

