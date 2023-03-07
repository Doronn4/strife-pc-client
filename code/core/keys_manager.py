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
    public_key = None
    private_key = None
    server_key = None
    chats_keys = {}
    aes = None
    path = None

    @staticmethod
    def initialize(keys_path: str):
        """
        A method that initializes the class variables aes and path with the given keys_path string
        """
        KeysManager.aes = AESCipher()
        KeysManager.path = keys_path

    @staticmethod
    def save_keys(password: str):
        """
        A method that saves the chats_keys dictionary to the file specified by the path variable, encrypted with the
        given password
        """
        contents = ''
        for chat_id, key in KeysManager.chats_keys.items():
            contents += f'{chat_id}:{key}\n'

        encrypted = KeysManager.aes.encrypt(contents.encode(), password.zfill(32).encode())
        with open(KeysManager.path, 'wb') as f:
            f.write(encrypted)

    @staticmethod
    def load_keys(password: str):
        """
        A method that loads the chats_keys dictionary from the file specified by the path variable, decrypted with
        the given password
        """
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
        """
        A method that returns the key for the given chat_id from the chats_keys dictionary
        """
        if len(KeysManager.chats_keys) == 0:
            raise KeysManager.NOT_INITIALIZED_YET

        return KeysManager.chats_keys[chat_id]


if __name__ == '__main__':
    manager = KeysManager("G:\\TESTING\\keys\\keys.json")
    # manager.chats_keys[69] = os.urandom(32)
    # print(manager.chats_keys[69])
    # manager.save_keys('doron1234')
    manager.load_keys('doron1234')
    print(manager.get_chat_key(69))



