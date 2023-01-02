import rsa
import os
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


class RSACipher:
    """
    A class for encrypting and decrypting data in RSA
    """

    def __init__(self, private_key):
        """
        Creates an ASYM object for encryption and decryption
        :param private_key: The private key to use for decrypting messages
        """
        self.private_key = private_key
        self.RSA = rsa

    def encrypt(self, data, public_key):
        """
        Encrypts a message/data with the given public key
        :param data: The data to encrypt
        :param public_key: The public key
        :return: The encrypted data
        """
        if type(data) == bytes:
            encrypted = self.RSA.encrypt(data, public_key)
        else:
            encrypted = self.RSA.encrypt(data.encode(), public_key)

        return encrypted

    def decrypt(self, data):
        """
        Decrypts a message/data with the private key
        :param data: The data to decrypt
        :return: The decrypted data
        """
        decrypted = self.RSA.decrypt(data, self.private_key)
        return decrypted


class AESCipher:
    """
    A class for encrypting and decrypting using AES
    """

    def __init__(self):
        # AES block size
        self.BLOCK_SIZE = 128

    def encrypt(self, data: bytes, key: bytes) -> bytes:
        """
        Encrypts the data with the given key using AES
        :param data: The data to encrypt
        :param key: The key to encrypt with
        :return: The encrypted data
        """
        # Generate a random initialization vector (IV)
        iv = os.urandom(16)

        # Create a cipher object using the key and IV
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())

        # Encrypt the data
        encryptor = cipher.encryptor()
        padded_data = self.pad(data, self.BLOCK_SIZE)
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()

        # Return the IV and ciphertext as a single message
        return iv + ciphertext

    def decrypt(self, data: bytes, key: bytes) -> bytes:
        """
        Decrypts the data with the given key using AES
        :param data: The data to decrypt
        :param key: The key to decrypt with
        :return: The decrypted data
        """
        # Split the message into the IV and ciphertext
        iv = data[:16]
        cipher_data = data[16:]

        # Create a cipher object using the key and IV
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())

        # Decrypt the ciphertext
        decrypter = cipher.decryptor()
        padded_data = decrypter.update(cipher_data) + decrypter.finalize()

        # Remove padding
        decrypted = self.unpad(padded_data, self.BLOCK_SIZE)

        return decrypted

    @staticmethod
    def pad(data: bytes, block_size: int) -> bytes:
        """
        Pads the data to the specified block size
        :param data: The data to pad
        :param block_size: The block size
        :return: The padded data
        """
        # Use PKCS#7 padding
        padder = padding.PKCS7(block_size).padder()
        padded_data = padder.update(data)
        padded_data += padder.finalize()
        return padded_data

    @staticmethod
    def unpad(padded_data: bytes, block_size: int) -> bytes:
        """
        Unpads the data
        :param padded_data: The padded data
        :param block_size: The block size
        :return: The unpadded data
        """
        # Use PKCS#7 padding
        unpadder = padding.PKCS7(block_size).unpadder()
        data = unpadder.update(padded_data)
        data += unpadder.finalize()
        return data

    @staticmethod
    def generate_key():
        return os.urandom(32)
