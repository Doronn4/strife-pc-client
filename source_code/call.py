import pickle
import queue
import socket
import pyaudio
import threading
import time
import cv2
import numpy


class CameraHandler:
    """
    A class to handle the device's camera
    """

    def __init__(self):
        """
        Creates a new camera handler object. Raises an exception in case there is no camera available.
        """
        # The default camera height and width values
        self.DEFAULT_HEIGHT = 500
        self.DEFAULT_WIDTH = 500

        self.active = True

        # Try to create a new VideoCapture object
        try:
            # 0 - default camera
            self.cam = cv2.VideoCapture(0, cv2.CAP_MSMF)
        except Exception as e:
            raise Exception('No camera available')

        else:
            # Set the camera size
            self.set_size(self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT)

        # A black frame
        self.BLACK_FRAME = numpy.zeros((self.DEFAULT_HEIGHT, self.DEFAULT_WIDTH, 3), dtype=numpy.uint8)

    def read(self):
        """
        Reads the current frame on the camera
        :return: The current frame
        """
        # Check if the camera object is active
        if self.active:
            # Read a frame from the camera
            ret, image = self.cam.read()
            # If there is a problem with the camera
            if not ret:
                # Set the camera object to not active
                self.active = False
                # Try to switch to a different camera in the background
                threading.Thread(target=self._reinitiate_camera).start()
                # Put a black frame
                image = self.BLACK_FRAME

        # If the camera object is not active, return a black frame
        else:
            image = self.BLACK_FRAME

        return image

    def _reinitiate_camera(self):
        """
        Tries to reinitiate the camera object
        :return: -
        """
        # If the camera is working
        working = False
        # Run while the camera isn't working
        while not working:
            time.sleep(1.5)
            # Try to reinitiate the camera
            try:
                self.cam = cv2.VideoCapture(0, cv2.CAP_MSMF)
            except Exception as e:
                pass

            else:
                # If there is a camera available
                if self.cam.read()[0]:
                    working = True

        # Set the camera back to active
        self.active = working

    def set_size(self, width: int, height: int):
        """
        Changes the size of the camera frame
        :param width: The new width
        :param height: The new height
        :return: -
        """

        # Check if the dimensions are between 1-1280
        if width <= 0 or height <= 0:
            raise Exception('Invalid height or width')

        elif width > 1280 or height > 1280:
            raise Exception('Dimensions too big')

        # Change the dimensions
        else:
            try:
                self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            except Exception as e:
                raise Exception('Invalid height or width')

    def get_size(self) -> (int, int):
        """
        :return: The size of the camera frame (width, height)
        """
        # Get the size from the VideoCapture object
        width = self.cam.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT)

        return width, height

    def close(self):
        """
        Closes the camera
        :return: -
        """
        self.cam.release()


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

        # Constants for the audio info
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 4096

        # Audio object
        self.audio = pyaudio.PyAudio()
        # The audio input and output objects
        self.audio_output = self.audio.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE,
                                            output=True, frames_per_buffer=self.CHUNK)
        self.audio_input = self.audio.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE,
                                           input=True, frames_per_buffer=self.CHUNK)

        # A dict of the connected users' sockets as the values and their ips as the keys
        self.send_list = {}

        # Start the main function thread
        threading.Thread(target=self.main).start()

        # Start sending the audio in a thread
        threading.Thread(target=self.send_audio_stream).start()

    def audio_stream_callback(self, in_data, frame_count, time_info, status):
        """
        Transmits the user's microphone audio to every client in the call
        :param in_data: The audio data from the microphone
        :param frame_count: The frame count
        :param time_info: The time info
        :param status: THe status of the microphone
        :return: ---
        """
        # Check if mic is muted or not
        if not self.muted:
            # Iterate over all the sockets of the clients in the call and send them the microphone data
            for soc in self.send_list.values():
                soc.send(in_data)

        # Return these values for the audio input object
        return None, pyaudio.paContinue

    def receive_audio_stream(self, ip):
        """
        Receive the audio stream from a client
        :param ip: The ip to receive the audio from
        :return:
        """
        # Create a socket object to receive the incoming audio
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Try to connect to the client to receive from
        try:
            my_socket.connect((ip, self.VOICE_PORT))
        except Exception as e:
            # Remove the client if there was problem connecting to them
            self._remove_client(ip)
        else:
            try:
                while True:
                    # Receive the audio data from the client
                    data = my_socket.recv(self.CHUNK)
                    # Play the audio in the audio output
                    self.audio_output.write(data)
            except Exception as e:
                # Remove the client if there was problem communicating with them
                self._remove_client(ip)

    def send_audio_stream(self):
        """
        Handles accepting users into the voice server and adding them to the send list
        :return:
        """
        my_server = socket.socket()
        my_server.bind(('0.0.0.0', self.VOICE_PORT))
        my_server.listen(6)

        while self.active:
            user_soc, address = my_server.accept()
            ip = address[0]

            if ip in self.call_members.keys():
                self.send_list[ip] = user_soc
            else:
                self._remove_client(ip)

    def toggle_mute(self):
        self.muted = not self.muted

    def main(self):
        """
        Handles the incoming updates (User joined the call, call ended…)
        :return:
        """
        # Run while the call is active
        while self.active:
            # Get a message from the server messages queue
            server_message = self.server_messages.get()

            # Check if the chat id matches the call's chat id
            if server_message['chat_id'] == self.chat_id:

                # If YOU joined the voice call
                if server_message['opname'] == 'voice_call_info':
                    # Get all of the call members' usernames
                    usernames = server_message['usernames']
                    # Get all of the call members' ips
                    ips = server_message['ips']

                    # Assign each ip to a username in the call_members dict
                    for username, ip in zip(usernames, ips):
                        self.call_members[ip] = username
                        self.receive_audio_stream(ip)

                # If a user joined the voice call
                elif server_message['opname'] == 'voice_user_joined':
                    # Get the user's ip
                    user_ip = server_message['ip']
                    # Get the user's username
                    username = server_message['username']

                    # Add the user to the call_members dict
                    self.call_members[user_ip] = username

    def _remove_client(self, ip):
        """
        Removes a client from the call
        :param ip: The client's ip address
        :return: -
        """
        if ip in self.send_list.keys():
            # Close the user's socket
            self.send_list[ip].close()
            # Remove the user from the send list
            del self.send_list[ip]

        if ip in self.call_members.keys():
            # Remove the user from the call members
            del self.call_members[ip]

    def terminate(self):
        """
        Disconnects from the call
        :return: -
        """
        # Disconnect from all of the other clients in the call
        users_ips = self.call_members.keys()
        for user_ip in users_ips:
            self._remove_client(user_ip)

        self.active = False


class VideoCall(VoiceCall):
    def __init__(self, chat_id: int, videos_out: dict):
        """
        Creates a new VideoCall object to handle the video call
        :param chat_id: The chat id of the call
        :param videos_out: A dict of usernames and queues for each user's video

        """
        super().__init__(chat_id)

        # The amount of FPS
        self.FPS = 30
        # The video port
        self.VIDEO_PORT = 5000
        # The size of the video chunk
        self.VIDEO_CHUNK = 50000

        # The camera handler object
        self.camera = CameraHandler()
        # A dict of usernames and queues for each user's video
        self.videos_out = videos_out

        # A dict for storing the queues of the audio frames and the usernames
        self.audios_queues = {}
        # A dict for storing the queues of the video frames and the usernames
        self.videos_queues = {}
        # A lock for synchronizing access to the audio and video queues
        self.queue_lock = threading.Lock()
        # The size of the sliding window, in milliseconds
        self.window_size = 500

        threading.Thread(target=self.receive_video_streams).start()
        threading.Thread(target=self.send_video_streams).start()

    def send_video_streams(self):
        """
        Sends the camera’s video to every ip on the send list
        :return: -
        """
        # Create a UDP socket for sending the data
        my_soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Set the send buffer of the socket
        my_soc.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, self.VIDEO_CHUNK)

        # Run while the call is active
        while self.active:
            # Read the camera frame from the camera
            frame = self.camera.read()
            # Compress the frame to jpg format
            ret, buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
            # Convert the image to bytes
            frame_bytes = pickle.dumps(buffer)
            # Send the image to all of the users in the call
            for user_ip in self.send_list:
                my_soc.sendto(frame_bytes, (user_ip, self.VIDEO_PORT))

            # Wait 1/FPS of a second to send only the desired amount of FPS
            cv2.waitKey(int(1000 / self.FPS))

    def receive_audio_stream(self, ip):
        """
                Receive the audio stream from a client
                :param ip: The ip to receive the audio from
                :return:
                """
        # Create a socket object to receive the incoming audio
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Get the client's username
        client_username = self.call_members[ip]

        # Try to connect to the client to receive from
        try:
            my_socket.connect((ip, self.VOICE_PORT))
        except Exception as e:
            # Remove the client if there was problem connecting to them
            self._remove_client(ip)
        else:
            try:
                while True:
                    # Receive the audio data from the client
                    data = my_socket.recv(self.CHUNK)
                    # Get the current time
                    current_time = time.perf_counter()
                    # Store the audio frame in the audio queue, along with its timestamp
                    with self.queue_lock:
                        self.audios_queues[client_username].put((data, current_time))

            except Exception as e:
                # Remove the client if there was problem communicating with them
                self._remove_client(ip)

    def receive_video_streams(self):
        """
        Receives and plays back the incoming video streams
        :return: -
        """
        # Create a server socket to receive the incoming video data
        my_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Set the receiving buffer of the socket
        my_server.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.VIDEO_CHUNK)

        # Bind the server to the machine's ip and the video port
        my_server.bind(('0.0.0.0', self.VIDEO_PORT))

        # Run while the call is active
        while self.active:
            # Receive the video frame from the client
            data, address = my_server.recvfrom(self.VIDEO_CHUNK)
            # Get the client's ip
            client_ip = address[0]
            # Check if the client is in the call
            if client_ip in self.call_members.keys():
                # Convert the data back to an image
                data = pickle.loads(data)
                # Decode the jpg image
                frame = cv2.imdecode(data, cv2.IMREAD_COLOR)
                # Get the client's username
                client_username = self.call_members[client_ip]
                # Put the video frame received from the client in it's queue inside the dict of all the clients
                # queues
                self.videos_queues[client_username].put(frame)

    def synchronize_streams(self):
        """
        Synchronizes the audio and video streams by using a sliding window to compare the timestamps of the frames
        """
        while self.active:

            # Iterate for each user's video and audio queue
            for ((username, audio_queue), video_queue) in zip(self.audios_queues.items(), self.videos_queues.values()):
                # Get the current time
                current_time = time.perf_counter()

                # Try to get an audio frame from the queue
                try:
                    with self.queue_lock:
                        audio_frame, audio_timestamp = audio_queue.get(block=False)
                except queue.Empty:
                    audio_frame = None
                    audio_timestamp = None

                # Try to get a video frame from the queue
                try:
                    with self.queue_lock:
                        video_frame, video_timestamp = video_queue.get(block=False)
                except queue.Empty:
                    video_frame = None
                    video_timestamp = None

                    # If both an audio and video frame are available
                if audio_frame is not None and video_frame is not None:
                    # Calculate the difference in timestamps between the audio and video frames
                    time_difference = audio_timestamp - video_timestamp

                    # If the difference is within the sliding window size
                    if abs(time_difference) < self.window_size:
                        # Play the audio frame
                        self.audio_output.write(audio_frame)
                        # Display the video frame
                        self.videos_out[username].put(video_frame)
                    # If the audio frame is ahead of the video frame
                    elif time_difference > 0:
                        # Play the audio frame
                        self.audio_output.write(audio_frame)
                        # Store the video frame back in the queue
                        with self.queue_lock:
                            self.video_queue.put((video_frame, video_timestamp))
                    # If the video frame is ahead of the audio frame
                    else:
                        # Store the audio frame back in the queue
                        with self.queue_lock:
                            self.audio_queue.put((audio_frame, audio_timestamp))
                    # If only an audio frame is available
                elif audio_frame is not None:
                    # Play the audio frame
                    self.audio_output.write(audio_frame)
                    # If only a video frame is available
                elif video_frame is not None:
                    # Display the video frame
                    self.videos_out[username].put(video_frame)
                    # If no frames are available, sleep for a short time before checking again
                else:
                    time.sleep(0.01)

    def main(self):
        """
                Handles the incoming updates (User joined the call, call ended…)
                :return: -
                """
        # Run while the call is active
        while self.active:
            # Get a message from the server messages queue
            server_message = self.server_messages.get()

            # Check if the chat id matches the call's chat id
            if server_message['chat_id'] == self.chat_id:

                # If YOU joined the video call
                if server_message['opname'] == 'voice_call_info' or server_message['opname'] == 'video_call_info':
                    # Get all of the call members' usernames
                    usernames = server_message['usernames']
                    # Get all of the call members' ips
                    ips = server_message['ips']

                    # Assign each ip to a username in the call_members dict
                    for username, ip in zip(usernames, ips):
                        # Create a queue for audio and a queue for video for the user
                        self.audios_queues[username] = queue.Queue()
                        self.videos_queues[username] = queue.Queue()
                        # Assign the ip to the username in the call members dict
                        self.call_members[ip] = username
                        # Start receiving audio from the user
                        self.receive_audio_stream(ip)

                # If a user joined the video call
                elif server_message['opname'] == 'voice_user_joined' or server_message['opname'] == 'video_user_joined':
                    # Get the user's ip
                    user_ip = server_message['ip']
                    # Get the user's username
                    username = server_message['username']

                    # Add the user to the call_members dict
                    self.call_members[user_ip] = username
                    # Create a queue for audio and a queue for video for the user
                    self.audios_queues[username] = queue.Queue()
                    self.videos_queues[username] = queue.Queue()

    def terminate(self):
        # Disconnect from all of the other clients in the call
        users_ips = self.call_members.keys()
        for user_ip in users_ips:
            self._remove_client(user_ip)

        # Closes the camera
        self.camera.close()
        # Sets the call to not active
        self.active = False
