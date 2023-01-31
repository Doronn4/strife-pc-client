import datetime
import os


class FileHandler:
    def __init__(self, base_path):
        self.base_path = base_path
        self.PFPS_PATH = '/profiles'
        # self.KEYS_PATH = '/keys.json'
        # self.aes = AESCipher()

    # def save_keys(self, password: str, keys_ids):
    #     contents = ''
    #     for chat_id, key in keys_ids:
    #         contents += f'{chat_id}:{key}\n'
    #
    #     encrypted = self.aes.encrypt(contents.encode(), password.encode())
    #     with open(f'{self.base_path}{self.KEYS_PATH}', 'wb') as f:
    #         f.write(encrypted)
    #
    # def load_keys(self, password: str):
    #     contents = None
    #
    #     with open(f'{self.base_path}{self.KEYS_PATH}', 'rb') as f:
    #         encrypted_contents = f.read()
    #
    #     if encrypted_contents:
    #         contents = self.aes.decrypt(encrypted_contents, password.encode()).decode()
    #
    #     return contents

    def save_file(self, contents: bytes, path, file_name: str):
        pass

    def save_pfp(self, contents: bytes, username: str):
        with open(f'{self.base_path}{self.PFPS_PATH}/{username}.png', 'wb') as f:
            f.write(contents)

    def load_pfp(self, username: str):
        with open(f'{self.base_path}{self.PFPS_PATH}/{username}.png', 'rb') as f:
            picture = f.read()
        return picture

    def load_file(self, path):
        pass

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

