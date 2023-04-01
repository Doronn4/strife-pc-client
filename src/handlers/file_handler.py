import datetime
import os


class FileHandler:
    PFPS_PATH = '\\profiles'
    base_path = ''

    @staticmethod
    def initialize(base_path):
        """
        This method initializes the base path for the file handler.

        :param base_path: The base path for the file handler.
        :type base_path: str
        :return: None
        :rtype: None
        """
        FileHandler.base_path = base_path

        if not os.path.exists(FileHandler.base_path):
            os.mkdir(FileHandler.base_path)

        if not os.path.exists(FileHandler.base_path+FileHandler.PFPS_PATH):
            os.mkdir(FileHandler.base_path+FileHandler.PFPS_PATH)

    @staticmethod
    def save_file(contents: bytes, path):
        """
        This method saves a file to the specified path.

        :param contents: The contents of the file to be saved.
        :type contents: bytes
        :param path: The path to save the file to.
        :type path: str
        :param file_name: The name of the file to be saved.
        :type file_name: str
        :return: None
        :rtype: None
        """
        with open(path, 'wb') as f:
            f.write(contents)

    @staticmethod
    def save_pfp(contents: bytes, username: str):
        """
        This method saves a user's profile picture.

        :param contents: The contents of the profile picture to be saved.
        :type contents: bytes
        :param username: The username of the user whose profile picture is being saved.
        :type username: str
        :return: The path to the saved profile picture.
        :rtype: str
        """
        path = f'{FileHandler.base_path}{FileHandler.PFPS_PATH}\\{username}.png'
        with open(path, 'wb') as f:
            f.write(contents)
        return path

    @staticmethod
    def load_pfp(username: str):
        """
        This method loads a user's profile picture.

        :param username: The username of the user whose profile picture is being loaded.
        :type username: str
        :return: The contents of the loaded profile picture.
        :rtype: bytes
        """
        with open(f'{FileHandler.base_path}{FileHandler.PFPS_PATH}\\{username}.png', 'rb') as f:
            picture = f.read()
        return picture

    @staticmethod
    def get_pfp_path(username: str):
        """
        This method gets the path to a user's profile picture.

        :param username: The username of the user whose profile picture's path is being retrieved.
        :type username: str
        :return: The path to the user's profile picture, or None if it doesn't exist.
        :rtype: str or None
        """
        is_exist = os.path.exists(f'{FileHandler.base_path}{FileHandler.PFPS_PATH}\\{username}.png')
        return f'{FileHandler.base_path}{FileHandler.PFPS_PATH}\\{username}.png' if is_exist else None

    @staticmethod
    def load_file(path) -> bytes:
        """
        A static method to load a file from a given path and return its content as bytes.

        :param path: The path of the file to load.
        :type path: str
        :return: The content of the file as bytes.
        :rtype: bytes
        """
        data = b''
        with open(path, 'rb') as f:
            data = f.read()
        return data

    @staticmethod
    def get_pfps_info():
        """
        A static method to get information about all profile pictures (pfps) stored in the 'profiles' directory.

        :return: A list of tuples, each containing the name of a pfp file and its creation date.
        :rtype: list[tuple(str, datetime.datetime)]
        """
        infos = []
        # specify the directory path
        path = f'{FileHandler.base_path}{FileHandler.PFPS_PATH}'

        # use the listdir method from os module to get a list of filenames
        filenames = os.listdir(path)

        # loop through the filenames
        for name in filenames:
            full_path = os.path.join(path, name)
            # get the creation time of the file
            creation_time = os.path.getctime(full_path)
            # convert the creation time to a datetime object
            date = datetime.datetime.fromtimestamp(creation_time)
            # append a tuple with the file name (without the extension) and the creation date to the list of infos
            infos.append((name.split('.')[0], date))

        return infos


