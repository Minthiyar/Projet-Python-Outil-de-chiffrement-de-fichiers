# Projet Python : Outil de chiffrement de fichiers

## Description

Ce projet est un outil de chiffrement de fichiers en Python, conçu pour protéger la confidentialité des données et faciliter le partage sécurisé des fichiers. Il permet aux utilisateurs de chiffrer et de déchiffrer des fichiers en utilisant des algorithmes de chiffrement robustes (comme AES et Twofish) ainsi que des algorithmes de hachage pour assurer l'intégrité des données (SHA-256, SHA-512).

## Fonctionnalités

- **Chiffrement de fichiers** : Chiffrez vos fichiers avec des algorithmes sécurisés pour empêcher tout accès non autorisé.
- **Déchiffrement de fichiers** : Restaurez les fichiers chiffrés en utilisant la clé de déchiffrement appropriée.
- **Génération de clés aléatoires** : Utilisez les mouvements de la souris pour générer des clés de manière aléatoire, offrant une sécurité unique et renforcée.
- **Choix des algorithmes** : Sélectionnez entre AES et Twofish pour répondre à différents besoins en sécurité.
- **Journal d'activité** : Enregistre les actions (chiffrement, déchiffrement, génération de clés) pour un suivi sécurisé.

## Installation

### Prérequis

- Python 3.7 ou supérieur
- `pip` pour la gestion des packages

### Installation des dépendances

Clonez le dépôt et installez les dépendances :

```bash
git clone https://github.com/Minthiyar/Projet-Python-Outil-de-chiffrement-de-fichiers.git
cd Projet-Python-Outil-de-chiffrement-de-fichiers
pip install -r requirements.txt
```

## Utilisation

### Exécuter le programme

Vous pouvez lancer le programme principal avec :

```bash
python src/main.py
```

### Fonctionnalités principales

1. **Chiffrement** : Choisissez un fichier et un algorithme de chiffrement, puis générez une clé de chiffrement unique.
2. **Déchiffrement** : Fournissez le fichier chiffré et la clé pour restaurer le fichier original.
3. **Gestion des clés** : Utilisez les mouvements de la souris pour générer des clés aléatoires, ou sauvegardez et restaurez des clés de manière sécurisée.

## Exemple d’utilisation

### Chiffrement d'un fichier

```bash
python src/main.py --encrypt --file <chemin_du_fichier> --algo AES
```

### Déchiffrement d'un fichier

```bash
python src/main.py --decrypt --file <chemin_du_fichier_chiffré> --key <clé>
```

## Arborescence du Projet

Voici un aperçu de la structure du projet :

```plaintext
projet_chiffrement/
├── src/
│   ├── main.py                 # Point d'entrée principal
│   ├── encryption/             # Modules de chiffrement
│   │   ├── aes_cipher.py       # Chiffrement AES
│   │   ├── twofish_cipher.py   # Chiffrement Twofish
│   │   ├── multi_layer.py      # Chiffrement multi-couches (AES + Twofish)
│   │   └── __init__.py         # Initialisation du package
│   └── utils/                  # Fonctions utilitaires
│       ├── file_operations.py  # Opérations de fichiers
│       ├── key_generation.py   # Génération de clés
│       ├── config.py           # Configuration du projet
│       └── __init__.py         # Initialisation du package utils
├── tests/                      # Tests unitaires
├── docs/                       # Documentation
├── data/                       # Fichiers d'exemple
├── keys/                       # Clés de chiffrement (à sécuriser)
├── requirements.txt            # Dépendances
└── README.md                   # Ce fichier
```

## Contribuer

Les contributions sont les bienvenues ! Pour contribuer :

1. Forkez le projet
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/NouvelleFonctionnalite`)
3. Faites un commit (`git commit -m 'Ajout de NouvelleFonctionnalité'`)
4. Poussez votre branche (`git push origin feature/NouvelleFonctionnalité`)
5. Créez une Pull Request

## Licence

Ce projet est sous licence MIT. Consultez le fichier `LICENSE` pour plus d'informations.

## Contact

**Minthiyar**  
- GitHub : https://github.com/Minthiyar
- Email : mail@minthiyar.com

