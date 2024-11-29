import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from Cryptodome.Cipher import AES
from Cryptodome.Hash import SHA256
from argon2 import PasswordHasher
from argon2.low_level import Type
from pynput import mouse


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


# Hachage des données de souris
def hash_mouse_data(mouse_data):
    hasher = SHA256.new()
    hasher.update(mouse_data.encode('utf-8'))
    return hasher.digest()  # Retourne le haché sous forme binaire


# Génération de clé avec Argon2
def generate_key_argon2(password, hashed_mouse_data):
    combined_data = password.encode('utf-8') + hashed_mouse_data
    ph = PasswordHasher(
        time_cost=2,
        memory_cost=102400,  # Mémoire utilisée (en kB)
        parallelism=8,       # Threads
        type=Type.ID         # Version Argon2id
    )
    return ph.hash(combined_data)[:32].encode('utf-8')  # Troncature à 32 octets


# Chiffrement AES
def encrypt_file_aes(file_path, password, hashed_mouse_data):
    salt = os.urandom(16)
    key = generate_key_argon2(password, hashed_mouse_data)
    cipher = AES.new(key, AES.MODE_EAX)

    with open(file_path, 'rb') as f:
        data = f.read()
    ciphertext, tag = cipher.encrypt_and_digest(data)

    encrypted_path = file_path + ".enc"
    with open(encrypted_path, 'wb') as f_enc:
        # Stocke : Sel (16 octets) + Haché des données de souris (32 octets) + Nonce + Tag + Ciphertext
        f_enc.write(salt)
        f_enc.write(hashed_mouse_data)
        f_enc.write(cipher.nonce)
        f_enc.write(tag)
        f_enc.write(ciphertext)

    # Supprime le fichier original une fois chiffré
    os.remove(file_path)

    messagebox.showinfo("Succès", f"Fichier chiffré avec succès et remplacé par {encrypted_path}.")


# Déchiffrement AES
def decrypt_file_aes(file_path, password):
    with open(file_path, 'rb') as f:
        salt = f.read(16)  # Récupère le sel
        hashed_mouse_data = f.read(32)  # Récupère le haché des données de souris
        nonce = f.read(16)  # Récupère le nonce AES
        tag = f.read(16)  # Récupère le tag d'intégrité
        ciphertext = f.read()  # Récupère les données chiffrées

    key = generate_key_argon2(password, hashed_mouse_data)
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)

    try:
        data = cipher.decrypt_and_verify(ciphertext, tag)
    except ValueError:
        messagebox.showerror("Erreur", "Échec du déchiffrement. Mot de passe ou données invalides.")
        return

    decrypted_path = file_path.replace(".enc", "")
    with open(decrypted_path, 'wb') as f_dec:
        f_dec.write(data)

    # Supprime le fichier chiffré une fois déchiffré
    os.remove(file_path)

    messagebox.showinfo("Succès", f"Fichier déchiffré avec succès et restauré en tant que {decrypted_path}.")


# Application CustomTkinter
class EncryptionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chiffrement Moderne")
        self.root.geometry("500x500")
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.mouse_collector = MouseDataCollector()
        self.mouse_data = ""
        self.hashed_mouse_data = None

        # Titre
        self.title_label = ctk.CTkLabel(root, text="Outil de chiffrement V2", font=("Arial", 18, "bold"))
        self.title_label.pack(pady=20)

        # Entrée mot de passe
        self.password_entry = ctk.CTkEntry(root, placeholder_text="Entrez votre mot de passe", show="*", width=300)
        self.password_entry.pack(pady=10)

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
        self.mouse_data = self.mouse_collector.get_data()
        self.hashed_mouse_data = hash_mouse_data(self.mouse_data)  # Hache les données de souris
        self.encrypt_button.configure(state="normal")
        messagebox.showinfo("Succès", "Données de la souris capturées et hachées avec succès !")

    # Sélectionner un fichier à chiffrer
    def select_file_encrypt(self):
        file_path = filedialog.askopenfilename(title="Sélectionnez un fichier à chiffrer")
        if file_path:
            password = self.password_entry.get()
            if not password:
                messagebox.showwarning("Erreur", "Veuillez entrer un mot de passe.")
                return
            encrypt_file_aes(file_path, password, self.hashed_mouse_data)

    # Sélectionner un fichier à déchiffrer
    def select_file_decrypt(self):
        file_path = filedialog.askopenfilename(title="Sélectionnez un fichier à déchiffrer", filetypes=[("Encrypted Files", "*.enc")])
        if file_path:
            password = self.password_entry.get()
            if not password:
                messagebox.showwarning("Erreur", "Veuillez entrer un mot de passe.")
                return
            decrypt_file_aes(file_path, password)


# Lancer l'application
if __name__ == "__main__":
    root = ctk.CTk()
    app = EncryptionApp(root)
    root.mainloop()
