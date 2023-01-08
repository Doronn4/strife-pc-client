import socket
import threading
import queue


class ClientCom:

    def __init__(self, server_port: int, server_ip: str, message_queue: queue.Queue):
        self.CHUNK_SIZE = 4096
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

        # Send the data
        self.socket.send(data)

    def recv_large(self, size: int):
        """
        Receives a large sized data object (For example a picture)
        :param size: The size of the data
        :return: The data
        """
        # Check if the client com is running
        if not self.running:
            raise self.NOT_RUNNING_EXCEPTION

        # Initialize an empty bytearray to store the file data
        file_data = bytearray()

        # Keep receiving data until the entire file has been received
        while len(file_data) < size:
            try:
                chunk = self.socket.recv(self.CHUNK_SIZE)
            # Handle exceptions
            except socket.error:
                file_data = None
                self.close()
                break

            # Check if there was anything received
            if not chunk:
                break

            file_data += chunk

        return file_data

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
    
    def close(self):
        pass