import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"


def get_movie_details(movie_id):
    """Récupère les informations d'un film depuis TMDB."""

    try:
        reponse = requests.get(
            f"{BASE_URL}/movie/{movie_id}",
            params={
                "api_key": API_KEY,
                "language": "fr-FR"
            },
            timeout=10
        )

        if reponse.status_code == 404:
            return None

        reponse.raise_for_status()
        data = reponse.json()

        return {
            "titre": data["title"],
            "date_sortie": data["release_date"],
            "genres": [g["name"] for g in data["genres"]],
            "popularite": data["popularity"],
            "note_moyenne": data["vote_average"]
        }

    except requests.exceptions.RequestException as erreur:
        print(f"Erreur API TMDB : {erreur}")
        return None