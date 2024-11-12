import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from Cryptodome.Cipher import AES
from Cryptodome.Hash import SHA256, SHA512
from twofish import Twofish
from pynput import mouse
import os

# Classe pour capturer les mouvements de la souris et générer des données aléatoires
class MouseDataCollector:
    def __init__(self):
        self.coordinates = []
        self.collecting = False
        self.listener = None  # Initialiser le listener ici

    def start_collection(self):
        self.coordinates = []
        self.collecting = True
        # Démarre un listener global pour les mouvements de la souris
        self.listener = mouse.Listener(on_move=self.on_move)
        self.listener.start()

    def stop_collection(self):
        self.collecting = False
        if self.listener is not None:
            self.listener.stop()

    def on_move(self, x, y):
        if self.collecting:
            self.coordinates.append((x, y))
            if len(self.coordinates) >= 5000:  # Limite pour arrêter la capture après 5000 positions
                self.stop_collection()

    def get_data(self):
        return ''.join(f"{x}{y}" for x, y in self.coordinates)

# Fonction pour générer une clé à partir du mot de passe et des données de la souris
def generate_key(password, mouse_data, hash_algo):
    combined_data = password + mouse_data
    if hash_algo == "SHA-256":
        key = SHA256.new(combined_data.encode()).digest()
    elif hash_algo == "SHA-512":
        key = SHA512.new(combined_data.encode()).digest()
    return key[:32]  # Tronquer la clé à 32 octets (256 bits) pour AES

# Fonction de chiffrement AES
def encrypt_file_aes(file_path, key):
    cipher = AES.new(key, AES.MODE_EAX)
    with open(file_path, 'rb') as f:
        data = f.read()
    ciphertext, tag = cipher.encrypt_and_digest(data)

    with open(file_path + ".enc", 'wb') as f_enc:
        f_enc.write(cipher.nonce + tag + ciphertext)

    messagebox.showinfo("Succès", "Le fichier a été chiffré avec succès avec AES !")

# Fonction de déchiffrement AES
def decrypt_file_aes(file_path, key):
    with open(file_path, 'rb') as f:
        nonce = f.read(16)
        tag = f.read(16)
        ciphertext = f.read()
    
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    data = cipher.decrypt_and_verify(ciphertext, tag)

    decrypted_path = file_path.replace(".enc", "")
    with open(decrypted_path, 'wb') as f_dec:
        f_dec.write(data)

    messagebox.showinfo("Succès", "Le fichier a été déchiffré avec succès avec AES !")

# Fonction de chiffrement Twofish
def encrypt_file_twofish(file_path, key):
    cipher = Twofish(key[:16])  # Twofish utilise une clé de 128 bits (16 octets)
    with open(file_path, 'rb') as f:
        data = f.read()
    ciphertext = cipher.encrypt(data.ljust((len(data) + 15) // 16 * 16))

    with open(file_path + ".enc", 'wb') as f_enc:
        f_enc.write(ciphertext)

    messagebox.showinfo("Succès", "Le fichier a été chiffré avec succès avec Twofish !")

# Fonction de déchiffrement Twofish
def decrypt_file_twofish(file_path, key):
    cipher = Twofish(key[:16])
    with open(file_path, 'rb') as f:
        ciphertext = f.read()
    data = cipher.decrypt(ciphertext).rstrip()  # Suppression du padding

    decrypted_path = file_path.replace(".enc", "")
    with open(decrypted_path, 'wb') as f_dec:
        f_dec.write(data)

    messagebox.showinfo("Succès", "Le fichier a été déchiffré avec succès avec Twofish !")

# Interface graphique
class EncryptionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Outil de chiffrement de fichiers")
        self.root.geometry("400x400")

        self.mouse_collector = MouseDataCollector()

        # Label et champ pour le mot de passe
        tk.Label(root, text="Mot de passe:").pack(pady=5)
        self.password_entry = tk.Entry(root, show="*", width=30)
        self.password_entry.pack(pady=5)

        # Menu pour sélectionner l'algorithme de hachage
        tk.Label(root, text="Choisissez l'algorithme de hachage :").pack(pady=5)
        self.hash_algo = tk.StringVar()
        self.hash_algo.set("SHA-256")  # Valeur par défaut
        self.hash_menu = ttk.Combobox(root, textvariable=self.hash_algo, values=["SHA-256", "SHA-512"])
        self.hash_menu.pack(pady=5)

        # Menu pour sélectionner l'algorithme de chiffrement
        tk.Label(root, text="Choisissez l'algorithme de chiffrement :").pack(pady=5)
        self.encrypt_algo = tk.StringVar()
        self.encrypt_algo.set("AES")  # Valeur par défaut
        self.encrypt_menu = ttk.Combobox(root, textvariable=self.encrypt_algo, values=["AES", "Twofish"])
        self.encrypt_menu.pack(pady=5)

        # Barre de progression
        tk.Label(root, text="Mouvements de souris pour générer la clé :").pack(pady=5)
        self.progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack(pady=5)
        self.progress_bar["maximum"] = 5000  # Mettre le même seuil que dans MouseDataCollector

        # Boutons de génération de clé, chiffrement et déchiffrement
        tk.Button(root, text="Générer Clé", command=self.start_mouse_data_collection).pack(pady=10)
        self.encrypt_button = tk.Button(root, text="Chiffrer un fichier", command=self.select_file_encrypt, state="disabled")
        self.encrypt_button.pack(pady=10)
        tk.Button(root, text="Déchiffrer un fichier", command=self.select_file_decrypt).pack(pady=10)

    # Lancer la collecte des mouvements de la souris
    def start_mouse_data_collection(self):
        self.mouse_collector.start_collection()
        self.update_progress_bar()

    # Mise à jour de la barre de progression
    def update_progress_bar(self):
        current_length = len(self.mouse_collector.coordinates)
        self.progress_bar["value"] = current_length
        if current_length >= 5000:  # Même seuil que dans MouseDataCollector
            self.finish_key_generation()
        else:
            self.root.after(100, self.update_progress_bar)

    # Finaliser la génération de clé et l'enregistrer dans un fichier
    def finish_key_generation(self):
        mouse_data = self.mouse_collector.get_data()
        password = self.password_entry.get()
        hash_algo = self.hash_algo.get()
        
        if not password:
            messagebox.showwarning("Attention", "Veuillez entrer un mot de passe.")
            return
        
        self.key = generate_key(password, mouse_data, hash_algo)
        
        with open("key.bin", "wb") as key_file:
            key_file.write(self.key)

        messagebox.showinfo("Clé générée", f"La clé de chiffrement a été générée avec succès en utilisant {hash_algo} et sauvegardée !")
        self.encrypt_button["state"] = "normal"

    # Sélectionner un fichier pour le chiffrement
    def select_file_encrypt(self):
        file_path = filedialog.askopenfilename(title="Sélectionnez un fichier à chiffrer")
        if file_path:
            algo = self.encrypt_algo.get()
            if algo == "AES":
                encrypt_file_aes(file_path, self.key)
            elif algo == "Twofish":
                encrypt_file_twofish(file_path, self.key)

    # Sélectionner un fichier pour le déchiffrement
    def select_file_decrypt(self):
        file_path = filedialog.askopenfilename(title="Sélectionnez un fichier à déchiffrer", filetypes=[("Encrypted Files", "*.enc")])
        if file_path:
            algo = self.encrypt_algo.get()
            if algo == "AES":
                decrypt_file_aes(file_path, self.key)
            elif algo == "Twofish":
                decrypt_file_twofish(file_path, self.key)

# Lancer l'application
if __name__ == "__main__":
    root = tk.Tk()
    app = EncryptionApp(root)
    root.mainloop()