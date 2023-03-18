import hashlib
import os

import rsa
from cryptions import AESCipher, RSACipher


class KeysManager:
    # Define an exception for when the keys manager is not initialized yet
    NOT_INITIALIZED_YET = Exception('Keys manager not initialized yet')

    # Initialize the following variables as class variables:
    # public_key: stores the public key
    # private_key: stores the private key
    # server_key: stores the server key
    # chats_keys: a dictionary that will store the keys for each chat
    # aes: stores an instance of the AESCipher class, which will be used to encrypt and decrypt data
    # path: stores the path where the keys will be stored
    chats_keys = {}
    aes = None
    path = None
    last_password = None

    @staticmethod
    def initialize(keys_path: str):
        """
        A method that initializes the class variables aes and path with the given keys_path string
        """
        KeysManager.aes = AESCipher()
        KeysManager.path = keys_path

        if not os.path.exists(keys_path):
            os.mkdir(keys_path)

    @staticmethod
    def save_keys(password: str = None):
        """
        A method that saves the chats_keys dictionary to the file specified by the path variable, encrypted with the
        given password
        """
        if not password:
            password = KeysManager.last_password

        password_hash = hashlib.sha256(password.encode()).hexdigest()[:32]

        contents = ''
        for chat_id, key in KeysManager.chats_keys.items():
            contents += f'{chat_id}:{key}\n'

        encrypted = KeysManager.aes.encrypt(password_hash, contents)
        with open(KeysManager.path + f'\\{password_hash[:8]}.json', 'wb') as f:
            f.write(encrypted.encode())

    @staticmethod
    def load_keys(password: str):
        """
        A method that loads the chats_keys dictionary from the file specified by the path variable, decrypted with
        the given password
        """
        contents = None
        password_hash = hashlib.sha256(password.encode()).hexdigest()[:32]

        if not KeysManager.aes:
            raise KeysManager.NOT_INITIALIZED_YET

        if os.path.isfile(KeysManager.path + f'\\{password_hash[:8]}.json'):
            with open(KeysManager.path + f'\\{password_hash[:8]}.json', 'rb') as f:
                encrypted_contents = f.read()

            if encrypted_contents:
                contents = KeysManager.aes.decrypt(password_hash, encrypted_contents)

            for line in contents.splitlines():
                if len(line.split(':', 1)) == 2:
                    chat_id, key = line.split(':', 1)
                    KeysManager.chats_keys[int(chat_id)] = key

        KeysManager.last_password = password

    @staticmethod
    def get_chat_key(chat_id) -> str:
        """
        A method that returns the key for the given chat_id from the chats_keys dictionary
        """
        if len(KeysManager.chats_keys) == 0:
            raise KeysManager.NOT_INITIALIZED_YET

        return KeysManager.chats_keys[chat_id]

    @staticmethod
    def add_key(chat_id: int, key):
        KeysManager.chats_keys[chat_id] = key


if __name__ == '__main__':
    KeysManager.initialize('G:\\Cyber\Strife\\strife_pc_client\\keys')
    # KeysManager.add_key(69, AESCipher.generate_key())
    # KeysManager.add_key(420, AESCipher.generate_key())
    # KeysManager.save_keys('aaaa')
    KeysManager.load_keys('doron1234')
    print(KeysManager.get_chat_key(69))
    print(KeysManager.get_chat_key(420))



