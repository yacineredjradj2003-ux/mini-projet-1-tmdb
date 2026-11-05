from datetime import date
from pathlib import Path

from exports import main

FICHIER_SUIVI = Path(__file__).resolve().parent / "data" / "derniere_maj.txt"


def mise_a_jour():
    aujourd_hui = date.today()

    if FICHIER_SUIVI.exists():
        derniere = date.fromisoformat(
            FICHIER_SUIVI.read_text().strip()
        )

        mois_ecoules = (
            (aujourd_hui.year - derniere.year) * 12
            + aujourd_hui.month - derniere.month
        )

        if mois_ecoules < 3:
            print("Mise à jour non nécessaire.")
            return

    print("Mise à jour des données TMDB...")
    main()

    FICHIER_SUIVI.write_text(aujourd_hui.isoformat())
    print("Date de mise à jour enregistrée.")


if __name__ == "__main__":
    mise_a_jour()