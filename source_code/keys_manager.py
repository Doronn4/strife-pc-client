import rsa
from cryptions import AESCipher, RSACipher


class KeysManager:
    def __init__(self, keys_path):
        self.aes = AESCipher()
        self.path = keys_path

        self.KEYS_NOT_LOADED_EXCEPTION = Exception('Keys not loaded yet')

        self.chats_keys = {}
        self.public_key = None
        self.private_key = None
        self.server_key = None

        self._generate_keys()

    def save_keys(self, password: str):
        contents = ''
        for chat_id, key in self.chats_keys:
            contents += f'{chat_id}:{key}\n'

        encrypted = self.aes.encrypt(contents.encode(), password.encode())
        with open(self.path, 'wb') as f:
            f.write(encrypted)

    def load_keys(self, password: str):
        contents = None

        with open(self.path, 'rb') as f:
            encrypted_contents = f.read()

        if encrypted_contents:
            contents = self.aes.decrypt(encrypted_contents, password.encode()).decode()

        return contents

    def get_chat_key(self, chat_id) -> bytes:
        if len(self.chats_keys) == 0:
            raise self.KEYS_NOT_LOADED_EXCEPTION

        return self.chats_keys[chat_id]

    def get_private_key(self):
        return self.private_key

    def set_server_key(self, key):
        self.server_key = key

    def _generate_keys(self):
        self.public_key, self.private_key = rsa.newkeys(RSACipher.KEY_SIZE)
