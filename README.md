# Mini Projet 1 — TMDB

Projet Python utilisant l'API The Movie Database (TMDB).

## Fonctionnalités

- Récupération des informations d'un film via son ID TMDB
- Gestion des films inexistants et des erreurs HTTP
- Téléchargement des Daily ID Exports au format JSON.GZ
- Décompression et transformation JSON en DataFrame Pandas
- Importation des données dans une base SQLite
- Script de mise à jour trimestrielle

## Structure

- logique.py : communication avec l'API TMDB
- cli.py : tests de récupération des films
- exports.py : téléchargement, traitement et stockage SQLite
- mise_a_jour.py : contrôle des mises à jour trimestrielles

## Installation

Créer un environnement virtuel :

python3 -m venv .venv
source .venv/bin/activate

Installer les dépendances :

pip install -r requirements.txt

Créer un fichier .env contenant :

TMDB_API_KEY=votre_cle_api

## Exécution

python cli.py
python exports.py
python mise_a_jour.py

## Base de données

La base SQLite est créée dans data/tmdb.db.

Elle contient une table films avec les identifiants,
titres originaux, popularités et autres champs de l'export TMDB.

## Sécurité

Le fichier .env, les données téléchargées et
l'environnement virtuel sont exclus du dépôt Git.
