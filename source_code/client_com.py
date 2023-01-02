import socket


class ClientCom:

    def __init__(self, server_port, server_ip, message_queue):
        self.server_port = server_port
        self.server_ip = server_ip
        self.message_queue = message_queue
        self.socket = socket.socket()

        # Try to connect to the server
        try:
            self.socket.connect((self.server_ip, self.server_port))
        except Exception:
            raise Exception('Connection to server failed')

        self.running = True

    def send_data(self, data):
        pass

