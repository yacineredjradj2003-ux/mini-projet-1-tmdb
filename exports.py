import gzip
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import requests

DOSSIER = Path(__file__).resolve().parent / "data"
DOSSIER.mkdir(exist_ok=True)

BASE_EXPORT = "https://files.tmdb.org/p/exports"


def telecharger_export():
    """Télécharge le dernier export disponible des films."""

    # Les exports du jour peuvent ne pas être encore publiés.
    for jours_avant in range(3):
        date = datetime.now() - timedelta(days=jours_avant)
        nom = f"movie_ids_{date:%m_%d_%Y}.json.gz"
        chemin = DOSSIER / nom

        if chemin.exists():
            print(f"Fichier déjà présent : {nom}")
            return chemin

        url = f"{BASE_EXPORT}/{nom}"
        print(f"Tentative : {url}")

        reponse = requests.get(url, timeout=120)

        if reponse.status_code == 404:
            continue

        reponse.raise_for_status()
        chemin.write_bytes(reponse.content)

        print(f"Téléchargement réussi : {nom}")
        return chemin

    raise RuntimeError("Aucun export disponible sur les 3 derniers jours.")


def charger_dataframe(chemin):
    """Transforme le JSON compressé en DataFrame Pandas."""

    films = []

    with gzip.open(chemin, "rt", encoding="utf-8") as fichier:
        for ligne in fichier:
            if ligne.strip():
                films.append(json.loads(ligne))

    df = pd.DataFrame(films)

    print(f"\nNombre de films : {len(df)}")
    print("\nColonnes :", list(df.columns))
    print("\nLes 5 premiers films :")
    print(df.head().to_string(index=False))

    return df


def sauvegarder_sqlite(df):
    """Enregistre les films dans une base relationnelle SQLite."""

    chemin_db = DOSSIER / "tmdb.db"

    with sqlite3.connect(chemin_db) as connexion:
        df.to_sql(
            "films",
            connexion,
            if_exists="replace",
            index=False,
            chunksize=1000
        )

        nombre = connexion.execute(
            "SELECT COUNT(*) FROM films"
        ).fetchone()[0]

    print(f"\nBase créée : {chemin_db}")
    print(f"Nombre de lignes SQL : {nombre}")


def main():
    chemin = telecharger_export()
    df = charger_dataframe(chemin)
    sauvegarder_sqlite(df)
    print("\nTraitement terminé !")


if __name__ == "__main__":
    main()