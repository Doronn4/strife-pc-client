import pickle
import queue
import socket
import struct
import numpy
import pyaudio
import threading
import time
import cv2
from camera_handler import CameraHandler


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


class VideoCall:
    def __init__(self, chat_id: int, port: int):
        """
        Creates a new VideoCall object to handle the video call
        :param chat_id: The chat id of the call

        """

        # The amount of FPS
        self.FPS = 30
        # The video port
        self.port = port
        # The size of the video chunk
        self.BUFFER_SIZE = 60000
        # The camera handler object
        self.camera = CameraHandler()

        self.chat_id = chat_id
        self.group_ip = '224.1.2.8'

        # This creates a UDP socket
        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP, fileno=None)
        self.socket.bind(('0.0.0.0', self.VIDEO_PORT))

        request = struct.pack("=4s4s", socket.inet_aton(self.group_ip), bytes(socket.INADDR_ANY))
        self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, request)

    def send_video(self):
        while True:
            frame = self.camera.read()
            # Compress the frame to jpg format
            ret, buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 60])
            # Send the image to all of the users in the call
            self.socket.sendto(buffer.tobytes(), (self.group_ip, self.port))
            # Sleep 1/FPS of a second to send only the desired frame rate
            time.sleep((1/self.FPS))

    def receive_videos(self):
        while True:
            data, addr = self.socket.recvfrom(self.BUFFER_SIZE)
            bufffer = numpy.frombuffer(data, numpy.uint8)
            frame = cv2.imdecode(bufffer, cv2.IMREAD_COLOR)
            # TODO: pass the frame onto something...

