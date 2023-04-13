import hashlib
import os

import rsa
from src.core.cryptions import AESCipher, RSACipher


class KeysManager:
    # Define an exception for when the keys manager is not initialized yet
    NOT_INITIALIZED_YET = Exception('Keys manager not initialized yet')

    # Initialize the following variables as class variables:
    # chats_keys: a dictionary that will store the keys for each chat
    chats_keys = {}
    last_password = None

    @staticmethod
    def load_keys(keys: list, chat_ids: list, password: str):

        password = password.zfill(32)

        for i in range(len(keys)):
            enc_key = keys[i]
            chat_id = chat_ids[i]
            key = AESCipher.decrypt(password, enc_key)
            KeysManager.chats_keys[chat_id] = key

        # Sets the last_password attribute to the given password.
        KeysManager.last_password = password

    @staticmethod
    def get_chat_key(chat_id) -> str:
        """
        Returns the key of a given chat_id.
        :param chat_id: An integer representing the chat_id.
        :type chat_id: int
        :return: The key of a given chat_id.
        :rtype: str
        """
        # Raises NOT_INITIALIZED_YET exception if chats_keys dictionary is empty.
        if len(KeysManager.chats_keys) == 0:
            raise KeysManager.NOT_INITIALIZED_YET

        return KeysManager.chats_keys[chat_id]

    @staticmethod
    def add_key(chat_id: int, key):
        """
        Adds a key for a specified chat_id to the chat keys dictionary.

        :param chat_id: an integer representing the chat id for which to add the key
        :type chat_id: int
        :param key: the key to add
        :type key: str
        :return: None
        """
        KeysManager.chats_keys[chat_id] = key


class OldKeysManager:
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
        Initializes the KeysManager class with a given keys_path directory.
        :param keys_path: A string representing the directory path.
        :type keys_path: str
        :return: None
        """
        # Initializes the AESCipher object
        KeysManager.aes = AESCipher()
        # Sets the keys_path attribute
        KeysManager.path = keys_path

        # Checks if the keys_path directory exists, if not creates the directory.
        if not os.path.exists(keys_path):
            os.mkdir(keys_path)

    @staticmethod
    def save_keys(password: str = None):
        """
        Saves the chats_keys dictionary as an encrypted file.
        :param password: A string representing the password.
        :type password: str
        :return: None
        """
        # If password is not given, use last_password attribute.
        if not password:
            password = KeysManager.last_password

        if not KeysManager.last_password:
            return

        # Hashes the password and takes the first 32 characters.
        password_hash = hashlib.sha256(password.encode()).hexdigest()[:32]

        contents = ''
        # Adds chat_id and its corresponding key to contents string.
        for chat_id, key in KeysManager.chats_keys.items():
            contents += f'{chat_id}:{key}\n'

        # Encrypts the contents string with the given password_hash.
        encrypted = KeysManager.aes.encrypt(password_hash, contents)

        # Writes the encrypted string to a file with the hashed password as filename.
        with open(KeysManager.path + f'\\{password_hash[:8]}.json', 'wb') as f:
            f.write(encrypted.encode())

    @staticmethod
    def load_keys(password: str):
        """
        Loads the encrypted file, decrypts its contents and stores the chat keys.
        :param password: A string representing the password.
        :type password: str
        :return: None
        """
        contents = None
        password_hash = hashlib.sha256(password.encode()).hexdigest()[:32]

        # Raises NOT_INITIALIZED_YET exception if AESCipher object has not been initialized yet.
        if not KeysManager.aes:
            raise KeysManager.NOT_INITIALIZED_YET

        # Checks if the file with hashed password exists, then reads and decrypts the file.
        if os.path.isfile(KeysManager.path + f'\\{password_hash[:8]}.json'):
            with open(KeysManager.path + f'\\{password_hash[:8]}.json', 'rb') as f:
                encrypted_contents = f.read()

            if encrypted_contents:
                contents = KeysManager.aes.decrypt(password_hash, encrypted_contents)

            # Parses contents string and updates the chats_keys dictionary.
            for line in contents.splitlines():
                if len(line.split(':', 1)) == 2:
                    chat_id, key = line.split(':', 1)
                    KeysManager.chats_keys[int(chat_id)] = key.strip()

        # Sets the last_password attribute to the given password.
        KeysManager.last_password = password

    @staticmethod
    def get_chat_key(chat_id) -> str:
        """
        Returns the key of a given chat_id.
        :param chat_id: An integer representing the chat_id.
        :type chat_id: int
        :return: The key of a given chat_id.
        :rtype: str
        """
        # Raises NOT_INITIALIZED_YET exception if chats_keys dictionary is empty.
        if len(KeysManager.chats_keys) == 0:
            raise KeysManager.NOT_INITIALIZED_YET

        return KeysManager.chats_keys[chat_id]

    @staticmethod
    def add_key(chat_id: int, key):
        """
        Adds a key for a specified chat_id to the chat keys dictionary.

        :param chat_id: an integer representing the chat id for which to add the key
        :type chat_id: int
        :param key: the key to add
        :type key: str
        :return: None
        """
        KeysManager.chats_keys[chat_id] = key
        KeysManager.save_keys()


