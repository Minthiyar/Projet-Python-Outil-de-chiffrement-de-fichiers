from Cryptodome.Cipher import AES

class AESCipher:
    def __init__(self, key):
        self.key = key[:32]  # AES-256 nécessite une clé de 32 octets

    def encrypt(self, data):
        cipher = AES.new(self.key, AES.MODE_EAX)
        nonce = cipher.nonce
        ciphertext, tag = cipher.encrypt_and_digest(data)
        return nonce + tag + ciphertext

    def decrypt(self, encrypted_data):
        nonce = encrypted_data[:16]  # Les 16 premiers octets pour le nonce
        tag = encrypted_data[16:32]  # Les 16 suivants pour le tag
        ciphertext = encrypted_data[32:]  # Le reste est le texte chiffré
        cipher = AES.new(self.key, AES.MODE_EAX, nonce=nonce)
        return cipher.decrypt_and_verify(ciphertext, tag)
