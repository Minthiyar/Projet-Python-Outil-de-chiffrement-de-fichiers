import customtkinter as ctk
from tkinter import filedialog, messagebox
from Cryptodome.Cipher import AES
from Cryptodome.Hash import SHA256, SHA512
from Cryptodome.Protocol.KDF import PBKDF2
from twofish import Twofish  # Ajouter le module Twofish
from pynput import mouse
import os

# Classe pour capturer les mouvements de la souris
class MouseDataCollector:
    def __init__(self):
        self.coordinates = []
        self.collecting = False
        self.listener = None

    def start_collection(self):
        self.coordinates = []
        self.collecting = True
        self.listener = mouse.Listener(on_move=self.on_move)
        self.listener.start()

    def stop_collection(self):
        self.collecting = False
        if self.listener is not None:
            self.listener.stop()

    def on_move(self, x, y):
        if self.collecting:
            self.coordinates.append((x, y))
            if len(self.coordinates) >= 5000:
                self.stop_collection()

    def get_data(self):
        return ''.join(f"{x}{y}" for x, y in self.coordinates)

# Génération de clé
def generate_key(password, salt, hash_algo):
    if hash_algo == "SHA-256":
        return PBKDF2(password, salt, dkLen=32, count=100000)
    elif hash_algo == "SHA-512":
        return PBKDF2(password, salt, dkLen=32, count=100000)

# Chiffrement AES
def encrypt_file_aes(file_path, password, hash_algo):
    salt = os.urandom(16)
    key = generate_key(password, salt, hash_algo)
    cipher = AES.new(key, AES.MODE_EAX)

    with open(file_path, 'rb') as f:
        data = f.read()
    ciphertext, tag = cipher.encrypt_and_digest(data)

    with open(file_path + ".enc", 'wb') as f_enc:
        f_enc.write(salt + cipher.nonce + tag + ciphertext)
    messagebox.showinfo("Succès", "Fichier chiffré avec AES avec succès !")

# Déchiffrement AES
def decrypt_file_aes(file_path, password, hash_algo):
    with open(file_path, 'rb') as f:
        salt = f.read(16)
        nonce = f.read(16)
        tag = f.read(16)
        ciphertext = f.read()

    key = generate_key(password, salt, hash_algo)
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    data = cipher.decrypt_and_verify(ciphertext, tag)

    decrypted_path = file_path.replace(".enc", "")
    with open(decrypted_path, 'wb') as f_dec:
        f_dec.write(data)
    messagebox.showinfo("Succès", "Fichier déchiffré avec AES avec succès !")

# Chiffrement Twofish
def encrypt_file_twofish(file_path, password, hash_algo):
    salt = os.urandom(16)
    key = generate_key(password, salt, hash_algo)[:16]  # Twofish utilise une clé de 16 octets (128 bits)
    cipher = Twofish(key)

    with open(file_path, 'rb') as f:
        data = f.read()
    ciphertext = cipher.encrypt(data.ljust((len(data) + 15) // 16 * 16))  # Padding au multiple de 16 octets

    with open(file_path + ".enc", 'wb') as f_enc:
        f_enc.write(salt + ciphertext)
    messagebox.showinfo("Succès", "Fichier chiffré avec Twofish avec succès !")

# Déchiffrement Twofish
def decrypt_file_twofish(file_path, password, hash_algo):
    with open(file_path, 'rb') as f:
        salt = f.read(16)
        ciphertext = f.read()

    key = generate_key(password, salt, hash_algo)[:16]
    cipher = Twofish(key)
    data = cipher.decrypt(ciphertext).rstrip()  # Suppression du padding

    decrypted_path = file_path.replace(".enc", "")
    with open(decrypted_path, 'wb') as f_dec:
        f_dec.write(data)
    messagebox.showinfo("Succès", "Fichier déchiffré avec Twofish avec succès !")

# Application CustomTkinter
class EncryptionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chiffrement Moderne")
        self.root.geometry("500x500")
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.mouse_collector = MouseDataCollector()

        # Titre
        self.title_label = ctk.CTkLabel(root, text="Outil de chiffrement V2", font=("Arial", 18, "bold"))
        self.title_label.pack(pady=20)

        # Entrée mot de passe
        self.password_entry = ctk.CTkEntry(root, placeholder_text="Entrez votre mot de passe", show="*", width=300)
        self.password_entry.pack(pady=10)

        # Menu de sélection pour l'algorithme de hachage
        self.hash_algo = ctk.StringVar(value="SHA-256")
        self.hash_menu = ctk.CTkOptionMenu(root, variable=self.hash_algo, values=["SHA-256", "SHA-512"])
        self.hash_menu.pack(pady=10)

        # Menu déroulant pour sélectionner l'algorithme de chiffrement
        self.encrypt_algo = ctk.StringVar(value="AES")
        self.encrypt_menu = ctk.CTkOptionMenu(root, variable=self.encrypt_algo, values=["AES", "Twofish"])
        self.encrypt_menu.pack(pady=10)

        # Barre de progression pour la souris
        self.progress_bar = ctk.CTkProgressBar(root, orientation="horizontal", mode="determinate", width=300)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=10)

        # Boutons pour les actions
        self.generate_button = ctk.CTkButton(root, text="Générer données souris", command=self.start_mouse_data_collection)
        self.generate_button.pack(pady=10)

        self.encrypt_button = ctk.CTkButton(root, text="Chiffrer un fichier", command=self.select_file_encrypt, state="disabled")
        self.encrypt_button.pack(pady=10)

        self.decrypt_button = ctk.CTkButton(root, text="Déchiffrer un fichier", command=self.select_file_decrypt)
        self.decrypt_button.pack(pady=10)

    # Lancer la collecte des mouvements de souris
    def start_mouse_data_collection(self):
        self.mouse_collector.start_collection()
        self.update_progress_bar()

    # Mise à jour de la barre de progression
    def update_progress_bar(self):
        progress = len(self.mouse_collector.coordinates) / 5000
        self.progress_bar.set(progress)
        if progress >= 1:
            self.finish_data_generation()
        else:
            self.root.after(100, self.update_progress_bar)

    # Finaliser la collecte et activer le chiffrement
    def finish_data_generation(self):
        self.mouse_collector.stop_collection()
        self.encrypt_button.configure(state="normal")
        messagebox.showinfo("Succès", "Données de la souris capturées avec succès !")

    # Sélectionner un fichier à chiffrer
    def select_file_encrypt(self):
        file_path = filedialog.askopenfilename(title="Sélectionnez un fichier à chiffrer")
        if file_path:
            password = self.password_entry.get()
            hash_algo = self.hash_algo.get()
            algo = self.encrypt_algo.get()
            if not password:
                messagebox.showwarning("Erreur", "Veuillez entrer un mot de passe.")
                return
            if algo == "AES":
                encrypt_file_aes(file_path, password, hash_algo)
            elif algo == "Twofish":
                encrypt_file_twofish(file_path, password, hash_algo)

    # Sélectionner un fichier à déchiffrer
    def select_file_decrypt(self):
        file_path = filedialog.askopenfilename(title="Sélectionnez un fichier à déchiffrer", filetypes=[("Encrypted Files", "*.enc")])
        if file_path:
            password = self.password_entry.get()
            hash_algo = self.hash_algo.get()
            algo = self.encrypt_algo.get()
            if not password:
                messagebox.showwarning("Erreur", "Veuillez entrer un mot de passe.")
                return
            try:
                if algo == "AES":
                    decrypt_file_aes(file_path, password, hash_algo)
                elif algo == "Twofish":
                    decrypt_file_twofish(file_path, password, hash_algo)
            except (ValueError, KeyError):
                messagebox.showerror("Erreur", "Échec du déchiffrement. Mot de passe ou fichier invalide.")

# Lancer l'application
if __name__ == "__main__":
    root = ctk.CTk()
    app = EncryptionApp(root)
    root.mainloop()
