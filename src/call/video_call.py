import socket
import threading
import time
import cv2
import numpy
from src.core.cryptions import AESCipher
from src.handlers.camera_handler import CameraHandler
import src.gui.main_gui as main_gui


class VideoCall:
    def __init__(self, parent, chat_id: int, key: str):
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
        self.ips_users = {}
        # Whether to send video or not
        self.transmit_video = True
        self.parent = parent

        self.aes = AESCipher()
        self.key = key

        # Creates a UDP socket
        self.socket = None

        self._start()

    def send_video(self):
        while self.active:
            # Send video only if the flag is on
            if self.transmit_video:
                frame = self.camera.read()
                # Compress the frame to jpg format
                ret, buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), self.QUALITY])
                # Encrypt the data using the call's symmetrical key
                data = self.aes.encrypt_bytes(self.key, buffer.tobytes())
                # The ips to send to
                ips = list(self.ips_users.keys())
                # Send the image to all the users in the call
                for ip in ips:
                    self.socket.sendto(data, (ip, self.PORT))
                # Sleep 1/FPS of a second to send only the desired frame rate
                time.sleep((1/self.FPS))

    def receive_videos(self):
        while self.active:
            try:
                # Receive the frame
                data, addr = self.socket.recvfrom(self.BUFFER_SIZE)
            except Exception as e:
                print(e)
                continue

            # Decrypt the data using the call's symmetrical key
            data = self.aes.decrypt_bytes(self.key, data)

            # Convert the buffer received to an image
            buffer = numpy.frombuffer(data, numpy.uint8)
            frame = cv2.imdecode(buffer, cv2.IMREAD_COLOR)

            # Get the ip of the sender
            ip = addr[0]
            
            if ip not in self.ips_users.keys():
                if ip in self.parent.call_members.keys():
                    self.add_user(ip, self.parent.get_user_by_ip(ip))
                else:
                    continue

            # Put the image/frame in the ips-videos dict
            self.ips_users[ip].update_video(frame)

    def add_user(self, ip, user):
        if ip not in self.ips_users.keys():
            self.ips_users[ip] = user

    def remove_user(self, ip):
        if ip in self.ips_users.keys():
            del self.ips_users[ip]

    def toggle_video(self):
        self.transmit_video = not self.transmit_video

    def _start(self):
        self.active = True
        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.socket.bind(('0.0.0.0', self.PORT))

        threading.Thread(target=self.receive_videos).start()
        threading.Thread(target=self.send_video).start()

    def terminate(self):
        self.active = False
        self.camera.close()
        self.socket.close()
