from cryptography.hazmat.primitives.asymmetric import rsa as CrypRSA
import rsa
import os
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


class RSACipher:
    """
    A class for encrypting and decrypting data in RSA
    """
    KEY_SIZE = 1024

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

    @staticmethod
    def generate_keys():
        public_key, private_key = rsa.newkeys(RSACipher.KEY_SIZE)

        return public_key, private_key


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
        padded_data = self._pad(data, self.BLOCK_SIZE)
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
        decrypted = self._unpad(padded_data, self.BLOCK_SIZE)

        return decrypted

    @staticmethod
    def _pad(data: bytes, block_size: int) -> bytes:
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
    def _unpad(padded_data: bytes, block_size: int) -> bytes:
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
        """
        Generates a random 32 bytes combination
        :return: A random 32 bytes combination
        """
        return os.urandom(32)


if __name__ == '__main__':
    # Test aes
    aes = AESCipher()
    raw = 'ahdraokrlp\n'*20
    print(raw)
    key = AESCipher.generate_key()
    enc = aes.encrypt(raw.encode(), key)
    print('enc', len(enc))
    print('raw', len(raw.encode()))
    print('diff ', str(len(enc) - len(raw.encode())))
    dec = aes.decrypt(enc, key).decode()
    assert dec == raw

    # TESt rsa
    pub_key, priv_key = RSACipher.generate_keys()
    my_rsa = RSACipher(priv_key)
    raw = 'hello i am doron!'
    enc = my_rsa.encrypt(raw, pub_key)
    #print(enc)
    dec = my_rsa.decrypt(enc).decode()
    #print(dec)
    assert raw == dec
