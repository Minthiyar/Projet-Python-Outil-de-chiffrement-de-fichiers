import os

def read_file(file_path):
    """Lit le contenu d'un fichier binaire et le retourne."""
    with open(file_path, 'rb') as file:
        return file.read()

def write_file(file_path, data):
    """Écrit des données binaires dans un fichier."""
    with open(file_path, 'wb') as file:
        file.write(data)

def delete_file(file_path):
    """Supprime un fichier spécifié."""
    if os.path.exists(file_path):
        os.remove(file_path)
