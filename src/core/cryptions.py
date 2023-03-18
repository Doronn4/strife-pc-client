import base64
import hashlib

from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_v1_5, AES
import os
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


class RSACipher:
    """
    A class for encrypting and decrypting data in RSA
    """
    KEY_SIZE = 1024*2

    def __init__(self):
        """
        Creates an ASYM object for encryption and decryption
        """
        self.RSA_key = RSA.generate(RSACipher.KEY_SIZE)
        self.RSA_cipher = PKCS1_v1_5.new(self.RSA_key)

    def encrypt(self, data, public_key):
        """
        Encrypts a message/data with the given public key
        :param data: The data to encrypt
        :param public_key: The public key
        :return: The encrypted data
        """
        if type(data) == str:
            data = data.encode()

        imported_key = RSA.import_key(public_key)
        # Encrypting data
        rsa_encryption_cipher = PKCS1_v1_5.new(imported_key)
        cipherbytes = rsa_encryption_cipher.encrypt(data)
        return cipherbytes

    def decrypt(self, data):
        """
        Decrypts a message/data with the private key
        :param data: The data to decrypt
        :return: The decrypted data
        """
        data = self.RSA_cipher.decrypt(data, None)
        return data

    def get_string_public_key(self) -> str:
        """
        Returns a string representation using PEM encoding for the server's public key
        """
        return self.RSA_key.publickey().exportKey().decode()

    def get_public_key_from_string(self, key):
        """
        Returns a public key from a PEM encoded string
        """
        return RSA.import_key(key)


class AESCipher:
    """
    A class for encrypting and decrypting using AES
    """
    BLOCK_SIZE = 16

    # AES 'pad' byte array to multiple of BLOCK_SIZE bytes
    @staticmethod
    def pad(byte_array):
        pad_len = AESCipher.BLOCK_SIZE - len(byte_array) % AESCipher.BLOCK_SIZE
        return byte_array + (bytes([pad_len]) * pad_len)

    # Remove padding at end of byte array
    @staticmethod
    def unpad(byte_array):
        last_byte = byte_array[-1]
        return byte_array[0:-last_byte]

    @staticmethod
    def encrypt(key, message):
        """
        Input String, return base64 encoded encrypted String
        """

        byte_array = message.encode("UTF-8")

        padded = AESCipher.pad(byte_array)

        # generate a random iv and prepend that to the encrypted result.
        # The recipient then needs to unpack the iv and use it.
        iv = os.urandom(AES.block_size)
        cipher = AES.new(key.encode("UTF-8"), AES.MODE_CBC, iv)
        encrypted = cipher.encrypt(padded)
        # Note we PREPEND the unencrypted iv to the encrypted message
        return base64.b64encode(iv + encrypted).decode("UTF-8")

    @staticmethod
    def encrypt_file(key, contents: bytes):
        padded = AESCipher.pad(contents)

        # generate a random iv and prepend that to the encrypted result.
        # The recipient then needs to unpack the iv and use it.
        iv = os.urandom(AES.block_size)
        cipher = AES.new(key.encode("UTF-8"), AES.MODE_CBC, iv)
        encrypted = cipher.encrypt(padded)
        # Note we PREPEND the unencrypted iv to the encrypted message
        return base64.b64encode(iv + encrypted)

    @staticmethod
    def decrypt(key, message):
        """
        Input encrypted bytes, return decrypted bytes, using iv and key
        """
        byte_array = base64.b64decode(message)

        iv = byte_array[0:16]  # extract the 16-byte initialization vector

        messagebytes = byte_array[16:]  # encrypted message is the bit after the iv

        cipher = AES.new(key.encode("UTF-8"), AES.MODE_CBC, iv)

        decrypted_padded = cipher.decrypt(messagebytes)

        decrypted = AESCipher.unpad(decrypted_padded)

        return decrypted.decode("UTF-8")

    @staticmethod
    def decrypt_file(key, contents: bytes):
        """
        Input encrypted bytes, return decrypted bytes, using iv and key
        """
        contents = base64.b64decode(contents)
        iv = contents[0:16]  # extract the 16-byte initialization vector

        messagebytes = contents[16:]  # encrypted message is the bit after the iv

        cipher = AES.new(key.encode("UTF-8"), AES.MODE_CBC, iv)

        decrypted_padded = cipher.decrypt(messagebytes)

        decrypted = AESCipher.unpad(decrypted_padded)

        return decrypted

    @staticmethod
    def generate_key():
        """
        Generates a random 32 bytes combination
        :return: A random 32 bytes combination
        """
        return hashlib.sha256(os.urandom(32)).hexdigest()[:32]

if __name__ == '__main__':
    # # Test aes
    # aes = AESCipher()
    # raw = 'ahdraokrlp\n'*20
    # print(raw)
    # key = AESCipher.generate_key()
    # print(len(key))
    # enc = aes.encrypt(raw.encode(), key)
    # print('enc', len(enc))
    # print('raw', len(raw.encode()))
    # print('diff ', str(len(enc) - len(raw.encode())))
    # dec = aes.decrypt(enc, key).decode()
    # assert dec == raw

    # TESt rsa
    my_rsa = RSACipher()
    raw = 'hello i am doron!'
    enc = my_rsa.encrypt(raw, my_rsa.get_string_public_key())
    #print(enc)
    dec = my_rsa.decrypt(enc).decode()
    #print(dec)
    assert raw == dec
