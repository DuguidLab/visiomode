import socket
import threading


BIND_IP = '0.0.0.0'
BIND_PORT = 5050


def listen():
    """listener loop"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((BIND_IP, BIND_PORT))
    server.listen(5)  # max connections

    print("Listening on {}:{}".format(BIND_IP, BIND_PORT))

    def client_connection(client_socket):
        request = client_socket.recv(1024)
        print("Received {}".format(request))

        # Some processing here

        return client_socket.close()

    while True:
        client_sock, address = server.accept()
        print("Connection from {}:{}".format(address[0], address[1]))
        client_handle = threading.Thread(
                target=client_connection,
                args=(client_sock,)
            )
        client_handle.start()


if __name__ == '__main__':
    try:
        listen()
    except KeyboardInterrupt:
        exit()
