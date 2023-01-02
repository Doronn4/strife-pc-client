import socket
import threading
import queue
import logging


class ClientCom:

    def __init__(self, server_port: int, server_ip: str, message_queue: queue.Queue):
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
        # Start the main thread
        self.main_thread = threading.Thread(target=self._main)
        self.main_thread.start()

    def send_data(self, data):
        pass

    def recv_file(self, file_size: int):
        pass

    def _main(self):
        while self.running:
            try:
                size = int(self.socket.recv(2).decode())
                data = self.socket.recv(size).decode()
            except ValueError:
                logging.error(f'Invalid size received')
                self.running = False
            except socket.error:
                self.running = False
            else:
                self.message_queue.put(data)


