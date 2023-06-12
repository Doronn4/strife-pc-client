import socket
import threading
import time
import cv2
import numpy
import config
from src.core.cryptions import AESCipher
from src.handlers.camera_handler import CameraHandler
import src.gui.gui_util as gui_util


class VideoCall:
    """
    A class to handle the video call
    """
    
    def __init__(self, parent, chat_id: int, key: str):
        """
        Creates a new VideoCall object to handle the video call
        :param chat_id: The chat id of the call
        :param key: The symmetrical key of the call
        """
        # The quality of the video frame
        self.QUALITY = 50
        # The amount of FPS
        self.FPS = 30
        # The video port
        self.port = config.video_port
        # The size of the video chunk
        self.BUFFER_SIZE = 1024 * 64
        # The camera handler object
        self.camera = None
        threading.Thread(target=self._initiate_camera).start()
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

    def _initiate_camera(self):
        """
        Initiates the camera handler object
        """
        self.camera = None
        try:
            self.camera = CameraHandler()
        except Exception:
            print('exception creating camera')
            self.transmit_video = False
            self.parent.onCameraToggle(None)
        else:
            self.transmit_video = True

    def send_video(self):
        """
        Sends the video to the other users in the call
        """

        while not self.camera:
            time.sleep(0.1)

        while self.active:
            # Send video only if the flag is on
            if self.transmit_video:

                frame = self.camera.read()

                if frame is None:
                    self.transmit_video = False
                    self.parent.onCameraToggle(None)
                    continue

                # Update the current user's video frame
                gui_util.User.this_user.update_video(frame)

                # Convert the frame from BGR to RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Compress the frame to jpg format
                ret, buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), self.QUALITY])
                # Encrypt the data using the call's symmetrical key
                data = self.aes.encrypt_bytes(self.key, buffer.tobytes())
                # The ips to send to
                ips = list(self.ips_users.keys())
                # Send the image to all the users in the call
                for ip in ips:
                    try:
                        self.socket.sendto(data, (ip, self.port))
                    except Exception:
                        break
            # Sleep 1/FPS of a second to send only the desired frame rate
            time.sleep((1/self.FPS))

    def receive_videos(self):
        """
        Receives the video from the other users in the call
        """
        while self.active:
            try:
                # Receive the frame
                data, addr = self.socket.recvfrom(self.BUFFER_SIZE)
            except Exception:
                continue

            # Decrypt the data using the call's symmetrical key
            data = self.aes.decrypt_bytes(self.key, data)

            # Convert the buffer received to an image
            buffer = numpy.frombuffer(data, numpy.uint8)
            frame = cv2.imdecode(buffer, cv2.IMREAD_COLOR)

            # Convert the frame from BGR to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            # Get the ip of the sender
            ip = addr[0]

            # If the user is not in the call, add him
            if ip not in self.ips_users.keys():
                # If the user is in the call members, add him
                if ip in self.parent.call_members.keys():
                    self.add_user(ip, self.parent.get_user_by_ip(ip))
                # If the user is not in the call members, don't add him
                else:
                    continue

            # Put the image/frame in the ips-videos dict
            self.ips_users[ip].update_video(frame)

    def add_user(self, ip, user):
        """
        Adds a user to the call
        """
        if ip not in self.ips_users.keys():
            self.ips_users[ip] = user

    def remove_user(self, ip):
        """
        Removes a user from the call
        """
        if ip in self.ips_users.keys():
            del self.ips_users[ip]

    def toggle_video(self):
        """
        Toggles the video transmission
        """
        if not self.camera:
            self.transmit_video = False
            return

        if not self.camera.active and not self.transmit_video:
            self._initiate_camera()
        else:
            self.transmit_video = not self.transmit_video

    def _start(self):
        """
        Starts the video call
        """
        self.active = True
        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.socket.bind(('0.0.0.0', self.port))

        threading.Thread(target=self.receive_videos).start()
        threading.Thread(target=self.send_video).start()

    def terminate(self):
        """
        Terminates the video call
        """
        self.active = False
        if self.camera:
            self.camera.close()
        self.socket.close()
