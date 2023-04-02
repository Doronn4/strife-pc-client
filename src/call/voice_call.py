import queue
import socket
import threading
import pyaudio
from src.core.cryptions import AESCipher


class VoiceCall:
    """
    A class to represent a voice call and handle it
    """
    # Constants for the audio info
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 4096

    def __init__(self, parent, chat_id, key):
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

        self.parent = parent

        # A dict of the current call members ips as the keys and their users as the values
        self.call_members = {}

        # Audio object
        self.audio = pyaudio.PyAudio()
        # The audio input objects
        self.audio_input = self.audio.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE,
                                           input=True, frames_per_buffer=self.CHUNK)
        
        self.aes = AESCipher()
        self.key = key

        self._start()

    def _start(self):
        # Creates a UDP socket
        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.socket.bind(('0.0.0.0', self.PORT))

        threading.Thread(target=self.receive_audio).start()
        threading.Thread(target=self.send_audio).start()

    def send_audio(self):
        while self.active:
            if not self.muted:
                data = self.audio_input.read(self.CHUNK)
                # Encrypt the data using the call's symmetrical key
                data = self.aes.encrypt_bytes(self.key, data)
                # The ips to send to
                ips = list(self.call_members.keys())
                # send the data to the ips
                for ip in ips:
                    self.socket.sendto(data, (ip, self.PORT))

    def receive_audio(self):
        while self.active:
            try:
                data, addr = self.socket.recvfrom(self.CHUNK*2)
            except Exception:
                continue

            # Decrypt the data using the call's symmetrical key
            data = self.aes.decrypt_bytes(self.key, data)

            ip = addr[0]
            
            print('received audio from ', ip)
            if ip not in self.call_members.keys():
                self.add_user(ip, self.parent.get_user_by_ip(ip))

            self.call_members[ip].update_audio(data)

    def add_user(self, ip, user):
        self.call_members[ip] = user
        print('added user to voice', ip, user)

    def remove_user(self, ip):
        if ip in self.call_members.keys():
            del self.call_members[ip]

    def toggle_mute(self):
        self.muted = not self.muted

    def terminate(self):
        self.active = False
        self.audio_input.close()
        for user in self.call_members.values():
            user.audio_output.close()
            user.audio_output = None
        
        self.socket.close()
