from .aes_cipher import AESCipher
from .twofish_cipher import TwofishCipher

class MultiLayerCipher:
    def __init__(self, key):
        self.aes_cipher = AESCipher(key)
        self.twofish_cipher = TwofishCipher(key)

    def encrypt(self, data):
        # Chiffrement en deux couches : AES suivi de Twofish
        aes_encrypted = self.aes_cipher.encrypt(data)
        twofish_encrypted = self.twofish_cipher.encrypt(aes_encrypted)
        return twofish_encrypted

    def decrypt(self, encrypted_data):
        # Déchiffrement en deux couches : Twofish suivi d'AES
        twofish_decrypted = self.twofish_cipher.decrypt(encrypted_data)
        aes_decrypted = self.aes_cipher.decrypt(twofish_decrypted)
        return aes_decrypted
