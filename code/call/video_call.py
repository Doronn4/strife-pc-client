import socket
import threading
import time
import cv2
import numpy
from code.core.cryptions import AESCipher
from code.handlers.camera_handler import CameraHandler


class VideoCall:
    def __init__(self, chat_id: int, key: bytes):
        """
        Creates a new VideoCall object to handle the video call
        :param chat_id: The chat id of the call
        """
        # The quality of the video frame
        self.QUALITY = 60
        # The amount of FPS
        self.FPS = 30
        # The video port
        self.PORT = 5000
        # The size of the video chunk
        self.BUFFER_SIZE = 1024 * 64
        # The camera handler object
        self.camera = CameraHandler()
        # The call's chat id
        self.chat_id = chat_id
        # Is call active
        self.active = False
        # A dict of the call members' ips as the keys, and the video frames received from them as the values
        self.ips_videos = {}

        self.aes = AESCipher()
        self.key = key

        # Creates a UDP socket
        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.socket.bind(('0.0.0.0', self.PORT))

    def send_video(self):
        while self.active:
            frame = self.camera.read()
            # Compress the frame to jpg format
            ret, buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), self.QUALITY])
            # Encrypt the data using the call's symmetrical key
            data = self.aes.encrypt(buffer.tobytes(), self.key)
            # Send the image to all of the users in the call
            for ip in self.ips_videos.keys():
                self.socket.sendto(data, (ip, self.PORT))
            # Sleep 1/FPS of a second to send only the desired frame rate
            time.sleep((1/self.FPS))

    def receive_videos(self):
        while self.active:
            # Receive the frame
            data, addr = self.socket.recvfrom(self.BUFFER_SIZE)

            # Decrypt the data using the call's symmetrical key
            data = self.aes.decrypt(data, self.key)

            # Get the ip of the sender
            ip = addr[0]
            # Convert the buffer received to an image
            buffer = numpy.frombuffer(data, numpy.uint8)
            frame = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
            # Put the image/frame in the ips-videos dict
            self.ips_videos[ip] = frame

    def start(self):
        self.active = True
        threading.Thread(target=self.receive_videos).start()
        threading.Thread(target=self.send_video).start()

    def terminate(self):
        self.active = False
        self.camera.close()
