import datetime
import os


class FileHandler:
    def __init__(self, base_path):
        self.base_path = base_path
        self.PFPS_PATH = '/profiles'

    def save_file(self, contents: bytes, path, file_name: str):
        with open(f'{path}\\{file_name}', 'wb') as f:
            f.write(contents)

    def save_pfp(self, contents: bytes, username: str):
        with open(f'{self.base_path}{self.PFPS_PATH}/{username}.png', 'wb') as f:
            f.write(contents)

    def load_pfp(self, username: str):
        with open(f'{self.base_path}{self.PFPS_PATH}/{username}.png', 'rb') as f:
            picture = f.read()
        return picture

    def load_file(self, path) -> bytes:
        data = b''
        with open(path, 'rb') as f:
            data = f.read()
        return data

    def get_pfps_info(self):
        infos = []
        # specify the directory path
        path = f'{self.base_path}{self.PFPS_PATH}'

        # use the listdir method from os module to get a list of filenames
        filenames = os.listdir(path)

        # loop through the filenames
        for name in filenames:
            full_path = os.path.join(path, name)
            creation_time = os.path.getctime(full_path)
            date = datetime.datetime.fromtimestamp(creation_time)
            infos.append((name.split('.')[0], date))

        return infos

