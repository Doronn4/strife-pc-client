import queue
import socket
import threading
import time
import wx
import wx.adv
import pyaudio
from src.core.cryptions import AESCipher
import config


class VoiceCall:
    """
    A class to represent a voice call and handle it
    """
    # Constants for the audio info
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 4096
    CALL_TIMEOUT = 3  # The amount of seconds to wait for a response from a call member

    def __init__(self, parent, chat_id, key):
        """
        Creates a new VoiceCall object to handle the voice call
        :param chat_id: The chat/group chat id of the call
        :param key: The symmetrical key of the call
        """
        # The voice port
        self.port = config.voice_port
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

        self.audio_input = None
        self._init_mic()
        
        self.aes = AESCipher()
        self.key = key

        self._start()

    def _init_mic(self):
        """
        Initiates the mic
        :return: -
        """
        if not self.active:
            return
        # The audio input objects
        if self.audio_input:
            self.audio_input.close()
        self.audio_input = None
        try:
            self.audio_input = self.audio.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE,
                                               input=True, frames_per_buffer=self.CHUNK)
        except Exception:
            self.muted = True
            self.parent.onMuteToggle(None)
        else:
            self.muted = False

    def _start(self):
        """
        Starts the call
        """
        # Creates a UDP socket
        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.socket.bind(('0.0.0.0', self.port))

        threading.Thread(target=self.receive_audio).start()
        threading.Thread(target=self.send_audio).start()
        threading.Thread(target=self.check_users).start()

    def check_users(self):
        """
        Checks if the users are still in the call, and removes the ones that aren't
        """
        while self.active:
            # A copy of the call members dict
            call_members_copy = self.call_members.copy()
            # Check if the users are still in the call
            for ip, user in call_members_copy.items():
                # If the user hasn't updated his last_audio_update in the last CALL_TIMEOUT seconds
                if user.last_audio_update + VoiceCall.CALL_TIMEOUT < time.time():
                    # Remove the user from the call
                    self.parent.remove_user(ip)

            # Check every second
            time.sleep(1)

    def send_audio(self):
        """
        Sends the audio to the other users in the call
        """
        while self.active:
            if not self.muted:
                try:
                    data = self.audio_input.read(self.CHUNK)
                except Exception:
                    self._init_mic()
                    continue
            else:
                # If the mic is muted, send silence
                data = b'\x00' * self.CHUNK * 2

            # Encrypt the data using the call's symmetrical key
            data = self.aes.encrypt_bytes(self.key, data)
            # The ips to send to
            ips = list(self.call_members.keys())
            # send the data to the ips
            for ip in ips:
                try:
                    self.socket.sendto(data, (ip, self.port))
                except Exception:
                    break

    def receive_audio(self):
        """
        Receives the audio from the other users in the call
        """
        while self.active:
            try:
                data, addr = self.socket.recvfrom(self.CHUNK*2 + 32)
            except Exception as e:
                continue

            # Decrypt the data using the call's symmetrical key
            data = self.aes.decrypt_bytes(self.key, data)

            ip = addr[0]

            # If the user is not in the call, add them
            if ip not in self.call_members.keys():
                if ip in self.parent.call_members.keys():
                    self.add_user(ip, self.parent.get_user_by_ip(ip))
                else:
                    continue

            # Update the user's audio
            self.call_members[ip].update_audio(data)

    def add_user(self, ip, user):
        """
        Adds a user to the call
        """
        self.call_members[ip] = user
        wx.CallAfter(self.parent.call_grid.add_user, user)

        # Initiate the user's last_audio_update
        user.last_audio_update = time.time()

        # Open the user audio
        user.open_audio()

        join_sound = wx.GetApp().GetTopWindow().main_panel.call_join_sound
        # Play the sound
        join_sound.Play(wx.adv.SOUND_ASYNC)

    def remove_user(self, ip):
        """
        Removes a user from the call
        """
        if ip in self.call_members.keys():
            # Close the user's audio
            self.call_members[ip].close_audio()
            # Remove the user from the call
            del self.call_members[ip]
            # Create a sound object
            leave_sound = wx.GetApp().GetTopWindow().main_panel.call_leave_sound
            # Play the sound
            leave_sound.Play(wx.adv.SOUND_ASYNC)

    def toggle_mute(self):
        """
        Toggles the mic mute
        """
        if self.audio_input is None and self.muted:
            self.muted = True
            self._init_mic()
        else:
            self.muted = not self.muted

    def terminate(self):
        """
        Terminates the call
        """
        self.active = False
        if self.audio_input:
            self.audio_input.close()
        for user in self.call_members.values():
            user.close_audio()

        self.socket.close()
