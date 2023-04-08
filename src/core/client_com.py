import base64
import socket
import threading
import queue
from src.core.cryptions import RSACipher, AESCipher


class ClientCom:
    """
    Represents a TCP based communication class
    """

    def __init__(self, server_port: int, server_ip: str, message_queue: queue.Queue, com_type='general'):
        """
        Initializes the client communication object.

        :param server_port: The port number of the server.
        :type server_port: int
        :param server_ip: The IP address of the server.
        :type server_ip: str
        :param message_queue: The queue to put received messages.
        :type message_queue: queue.Queue
        :param com_type: The type of communication (e.g. 'general' or 'files').
        :type com_type: str
        """
        self.CHUNK_SIZE = 1024
        self.server_port = server_port
        self.server_ip = server_ip
        self.message_queue = message_queue
        self.socket = socket.socket()
        self.com_type = com_type

        self.server_key = None
        self.rsa = RSACipher()
        self.aes_key = None

        self.CONNECTION_EXCEPTION = Exception('Connection to server failed')
        self.NOT_RUNNING_EXCEPTION = Exception('Not running')
        self.INVALID_TYPE_EXCEPTION = Exception('Invalid data type')

        self.running = False

        # Start the main thread
        self.main_thread = threading.Thread(target=self._main_loop)
        self.main_thread.start()

    def send_data(self, data):
        """
        Sends data to the server.

        :param data: The data to send.
        :type data: str or bytes
        :raises: NOT_RUNNING_EXCEPTION if client com is not running
        :raises: INVALID_TYPE_EXCEPTION if data is not a str or bytes object
        :raises: CONNECTION_EXCEPTION if the socket connection fails
        """
        # Check if the client com is running
        if not self.running:
            raise self.NOT_RUNNING_EXCEPTION

        # Encode the data if needed
        if type(data) == bytes:
            try:
                data = data.encode()
            except Exception:
                raise self.INVALID_TYPE_EXCEPTION

        try:
            enc_data = AESCipher.encrypt(self.aes_key, data).encode()

            # send data length
            str_len = str(len(enc_data)).zfill(10) if self.com_type == 'files' else\
                str(len(enc_data)).zfill(4)

            self.socket.send(str_len.encode())

            # Send the data
            self.socket.send(enc_data)
        except Exception:
            raise self.CONNECTION_EXCEPTION

    def _main_loop(self):
        """
        The main loop which receives data from the server and puts it in a queue
        :return: -
        """

        # Try to connect to the server
        try:
            self.socket.connect((self.server_ip, self.server_port))
        except Exception:
            raise self.CONNECTION_EXCEPTION

        # Change keys with server
        try:
            self.switch_keys()  # Switch encryption keys with server
        except Exception as e:
            raise self.CONNECTION_EXCEPTION

        self.running = True

        # Run while the client_com object is running
        while self.running:
            try:
                if self.com_type == 'files':
                    size_length = 10
                else:
                    size_length = 4

                # Receive the size of the data and convert it to an int
                size = int(self.socket.recv(size_length).decode())
                # Receive the data
                if self.com_type == 'files':
                    data = self.receive_file(size)  # Receive file data
                else:
                    data = self.socket.recv(size)

            # Invalid size exception
            except ValueError:
                self.running = False
            # Socket exception
            except socket.error:
                self.running = False
            else:
                try:
                    dec_data = AESCipher.decrypt(self.aes_key, data.decode())
                except Exception:
                    pass
                else:
                    # Put the received data inside the message queue
                    self.message_queue.put(dec_data)

    def receive_file(self, file_size, chunk_size=1024):
        """
        Receives file data from the server
        :param file_size: The size of the file to receive
        :type file_size: int
        :param chunk_size: The size of each chunk of data to receive
        :type chunk_size: int
        :return: The received file data
        :rtype: bytes
        """
        data = b''
        bytes_received = 0

        while bytes_received < file_size:
            chunk = self.socket.recv(min(chunk_size, file_size - bytes_received))
            if not chunk:
                raise ConnectionError("Connection closed prematurely.")
            data += chunk
            bytes_received += len(chunk)

        return data

    def switch_keys(self):
        """
        Switches encryption keys with the server
        :return: -
        :rtype: -
        """
        key = self.socket.recv(1024).decode()  # Receive server's public key
        self.server_key = key
        self.socket.send(self.rsa.get_string_public_key().encode())  # Send client's public key
        aes_key_enc = self.socket.recv(256)  # Receive encrypted AES key
        self.aes_key = self.rsa.decrypt(aes_key_enc).decode()  # Decrypt AES key

    def close(self):
        """
        Closes the client communication object
        :return: -
        :rtype: -
        """
        self.running = False
        self.socket = None  # Close socket connection

    def reconnect(self):
        """
        Reconnects to the server
        :return: -
        :rtype: -
        """
        # Close the socket connection and reset the variables
        self.running = False
        self.socket.close()
        self.server_key = None
        self.rsa = RSACipher()
        self.aes_key = None
        self.socket = socket.socket()

        # Start the main thread
        self.main_thread = threading.Thread(target=self._main_loop)
        self.main_thread.start()
