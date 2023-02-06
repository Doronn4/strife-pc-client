import queue
import pyaudio


class VoiceCall:
    """
    A class to represent a voice call and handle it
    """

    def __init__(self, chat_id):
        """
        Creates a new VoiceCall object to handle the voice call
        :param chat_id: The chat/group chat id of the call
        """
        # The voice port
        self.VOICE_PORT = 4000
        # The call's chat id
        self.chat_id = chat_id
        # A queue for the incoming messages from the server
        self.server_messages = queue.Queue()
        # Whether the call is active or not
        self.active = True
        # Whether the mic is muted
        self.muted = False

        # A dict of the current call members ips as the keys and their names as the value
        self.call_members = {}

        # A dict of the connected users' sockets as the values and their ips as the keys
        self.connected_clients = {}

        # Constants for the audio info
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 4096
        # Audio object
        self.audio = pyaudio.PyAudio()
        # The audio output object
        self.audio_output = self.audio.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE,
                                            output=True, frames_per_buffer=self.CHUNK)
        # The audio input object
        self.audio_input = self.audio.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE,
                                           input=True, frames_per_buffer=self.CHUNK)

    def send_audio(self):
        while True:
            data = self.audio_input.read(self.CHUNK)
            for soc in self.connected_clients.values():
                soc.send(data)