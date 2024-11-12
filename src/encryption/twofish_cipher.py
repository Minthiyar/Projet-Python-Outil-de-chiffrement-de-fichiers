from twofish import Twofish

class TwofishCipher:
    def __init__(self, key):
        self.key = key[:16]  # Twofish nécessite une clé de 128 bits (16 octets)
        self.cipher = Twofish(self.key)

    def encrypt(self, data):
        padded_data = data.ljust((len(data) + 15) // 16 * 16)  # Padding pour un bloc de 16 octets
        ciphertext = self.cipher.encrypt(padded_data)
        return ciphertext

    def decrypt(self, encrypted_data):
        plaintext = self.cipher.decrypt(encrypted_data).rstrip()  # Retirer le padding
        return plaintext
