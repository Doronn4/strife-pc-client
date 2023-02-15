import queue
import socket
import threading

import pyaudio

from code.core.cryptions import AESCipher


class VoiceCall:
    """
    A class to represent a voice call and handle it
    """

    def __init__(self, chat_id, key):
        """
        Creates a new VoiceCall object to handle the voice call
        :param chat_id: The chat/group chat id of the call
        """
        # The voice port
        self.PORT = 4000
        # The call's chat id
        self.chat_id = chat_id
        # A queue for the incoming messages from the server
        self.server_messages = queue.Queue()
        # Whether the call is active or not
        self.active = True
        # Whether the mic is muted
        self.muted = False

        # A dict of the current call members ips as the keys and their output streams as the values
        self.call_members = {}

        # Constants for the audio info
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 4096
        # Audio object
        self.audio = pyaudio.PyAudio()
        # The audio input object
        self.audio_input = self.audio.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE,
                                           input=True, frames_per_buffer=self.CHUNK)

        self.aes = AESCipher()
        self.key = key

        threading.Thread(target=self._main).start()

    def _main(self):
        # Creates a UDP socket
        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.socket.bind(('0.0.0.0', self.PORT))

        # TODO: add users...

        threading.Thread(target=self.receive_audio).start()
        threading.Thread(target=self.send_audio).start()

    def send_audio(self):
        while True:
            data = self.audio_input.read(self.CHUNK)

            # Encrypt the data using the call's symmetrical key
            data = self.aes.encrypt(data, self.key)

            for ip in self.call_members.keys():
                self.socket.sendto(data, (ip, self.PORT))

    def receive_audio(self):
        while True:
            data, addr = self.socket.recvfrom(self.CHUNK*2)

            # Decrypt the data using the call's symmetrical key
            data = self.aes.decrypt(data, self.key)

            ip = addr[0]
            self.call_members[ip].write(data)

    def add_user(self, ip):
        self.call_members[ip] = self.audio.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE,output=True, frames_per_buffer=self.CHUNK)
