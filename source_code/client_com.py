import socket
import threading
import queue


class ClientCom:

    def __init__(self, server_port: int, server_ip: str, message_queue: queue.Queue):
        self.server_port = server_port
        self.server_ip = server_ip
        self.message_queue = message_queue
        self.socket = socket.socket()

        self.CONNECTION_EXCEPTION = Exception('Connection to server failed')
        self.NOT_RUNNING_EXCEPTION = Exception('Not running')

        # Try to connect to the server
        try:
            self.socket.connect((self.server_ip, self.server_port))
        except Exception:
            raise self.CONNECTION_EXCEPTION

        self.running = True
        # Start the main thread
        self.main_thread = threading.Thread(target=self._main_loop)
        self.main_thread.start()

    def send_data(self, data):
        """
        Send the data to the server
        :param data: The data to send
        :return: -
        """
        # Check if the client com is running
        if not self.running:
            raise self.NOT_RUNNING_EXCEPTION

        # Encode the data if needed
        if type(data) != bytes:
            data = data.encode()

        # Get the size of the data and convert it to a string with a length of 2
        size = str(len(data)).zfill(2)
        # Send the size first
        self.socket.send(size.encode())

        # Send the data
        self.socket.send(data)

    def recv_file(self, file_size: int):
        pass

    def _main_loop(self):
        """
        The main loop which receives data from the server and puts it in a queue
        :return: -
        """
        # Run while the client_com object is running
        while self.running:
            try:
                # Receive the size of the data and convert it to an int
                size = int(self.socket.recv(2).decode())
                # Receive the data
                data = self.socket.recv(size).decode()
            # Invalid size exception
            except ValueError:
                print('invalid size')
                self.running = False
            # Socket exception
            except socket.error:
                print('socket error')
                self.running = False
            else:
                # Put the received data inside the message queue
                self.message_queue.put(data)
