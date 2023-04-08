import threading
import cv2
import numpy
import time


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

    def get_size(self):
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
