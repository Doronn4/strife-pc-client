import rsa
from cryptions import AESCipher, RSACipher


class KeysManager:
    NOT_INITIALIZED_YET = Exception('Keys manager not initialized yet')
    public_key = None
    private_key = None
    server_key = None
    chats_keys = {}
    aes = None
    path = None

    @staticmethod
    def initialize(keys_path):
        KeysManager.aes = AESCipher()
        KeysManager.path = keys_path
        KeysManager._generate_keys()

    @staticmethod
    def save_keys(password: str):
        contents = ''
        for chat_id, key in KeysManager.chats_keys.items():
            contents += f'{chat_id}:{key}\n'

        encrypted = KeysManager.aes.encrypt(contents.encode(), password.zfill(32).encode())
        with open(KeysManager.path, 'wb') as f:
            f.write(encrypted)

    @staticmethod
    def load_keys(password: str):
        contents = None

        if not KeysManager.aes:
            raise KeysManager.NOT_INITIALIZED_YET

        with open(KeysManager.path, 'rb') as f:
            encrypted_contents = f.read()

        if encrypted_contents:
            contents = KeysManager.aes.decrypt(encrypted_contents, password.zfill(32).encode()).decode()

        for line in contents.splitlines():
            if len(line.split(':', 1)) == 2:
                chat_id, key = line.split(':', 1)
                KeysManager.chats_keys[int(chat_id)] = key

    @staticmethod
    def get_chat_key(chat_id) -> bytes:
        if len(KeysManager.chats_keys) == 0:
            raise KeysManager.NOT_INITIALIZED_YET

        return KeysManager.chats_keys[chat_id]

    @staticmethod
    def get_private_key():
        return KeysManager.private_key

    @staticmethod
    def set_server_key(key):
        KeysManager.server_key = key

    @staticmethod
    def _generate_keys():
        KeysManager.public_key, KeysManager.private_key = rsa.newkeys(RSACipher.KEY_SIZE)


if __name__ == '__main__':
    manager = KeysManager("G:\\TESTING\\keys\\keys.json")
    # manager.chats_keys[69] = os.urandom(32)
    # print(manager.chats_keys[69])
    # manager.save_keys('doron1234')
    manager.load_keys('doron1234')
    print(manager.get_chat_key(69))



