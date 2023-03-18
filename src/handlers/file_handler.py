import datetime
import os


class FileHandler:
    PFPS_PATH = '\\profiles'
    base_path = ''

    @staticmethod
    def initialize(base_path):
        FileHandler.base_path = base_path

        if not os.path.exists(FileHandler.base_path):
            os.mkdir(FileHandler.base_path)

        if not os.path.exists(FileHandler.base_path+FileHandler.PFPS_PATH):
            os.mkdir(FileHandler.base_path+FileHandler.PFPS_PATH)

    @staticmethod
    def save_file(contents: bytes, path, file_name: str):
        with open(f'{path}\\{file_name}', 'wb') as f:
            f.write(contents)

    @staticmethod
    def save_pfp(contents: bytes, username: str):
        path = f'{FileHandler.base_path}{FileHandler.PFPS_PATH}\\{username}.png'
        with open(path, 'wb') as f:
            f.write(contents)
        return path

    @staticmethod
    def load_pfp(username: str):
        with open(f'{FileHandler.base_path}{FileHandler.PFPS_PATH}\\{username}.png', 'rb') as f:
            picture = f.read()
        return picture

    @staticmethod
    def get_pfp_path(username: str):
        is_exist = os.path.exists(f'{FileHandler.base_path}{FileHandler.PFPS_PATH}\\{username}.png')
        return f'{FileHandler.base_path}{FileHandler.PFPS_PATH}\\{username}.png' if is_exist else None

    @staticmethod
    def load_file(path) -> bytes:
        data = b''
        with open(path, 'rb') as f:
            data = f.read()
        return data

    @staticmethod
    def get_pfps_info():
        infos = []
        # specify the directory path
        path = f'{FileHandler.base_path}{FileHandler.PFPS_PATH}'

        # use the listdir method from os module to get a list of filenames
        filenames = os.listdir(path)

        # loop through the filenames
        for name in filenames:
            full_path = os.path.join(path, name)
            creation_time = os.path.getctime(full_path)
            date = datetime.datetime.fromtimestamp(creation_time)
            infos.append((name.split('.')[0], date))

        return infos

